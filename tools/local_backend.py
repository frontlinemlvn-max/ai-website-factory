#!/usr/bin/env python3

"""
Local vertical-slice backend for the Claude Design frontend prototype.

Serves frontend/ as static files and a small JSON API on the same origin
and port, so the browser never needs cross-origin requests:

  GET  /api/health
  POST /api/projects
  GET  /api/projects/<slug>/status
  POST /api/generate
  GET  /api/domains/check
  POST /api/checkout
  GET  /api/checkout/verify
  POST /api/auth/signup
  POST /api/auth/login
  POST /api/auth/logout
  GET  /api/auth/me

Project creation and status both delegate to the existing factory
(tools/init-project.sh and each project's PROJECT-STATUS.md) rather than
reimplementing scaffolding or workflow logic. /api/generate calls the real
Anthropic API server-side (ANTHROPIC_API_KEY), /api/domains/check calls
Vercel's Domains Registrar API (VERCEL_TOKEN), and /api/checkout creates a
real Square-hosted checkout for the one-time export or, for a signed-in
account, the recurring Studio subscription (SQUARE_ACCESS_TOKEN,
SQUARE_LOCATION_ID, SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID) — every one of
these fails closed with a clear error when its credentials are absent,
rather than silently falling back to fake output. Accounts are real (a
local SQLite file, .factory-users.db, at the factory root — passwords are
salted and hashed, never stored or logged in plain text) but exist only to
gate the Studio subscription; there is no other use of accounts in this
prototype. Domain purchase, actual deployment, and downloads are NOT
implemented here — the frontend continues to simulate those, as documented
in frontend/README.md.

Reuses the same safety posture as tools/preview-server.py: loopback-only
bind, path-traversal guards, sliding-window rate limiting (tighter for
routes that cost money or gate accounts), and standard security headers.
Never contacts a network service other than the local factory, Anthropic,
Vercel, and Square, and never echoes a credential, password, or session
token back to the client body or logs.
"""

from collections import deque
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from string import Template
import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import secrets
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


SECURITY_HEADERS = (
    (
        "Content-Security-Policy",
        "default-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "object-src 'none'; "
        # 'unsafe-eval' is required because this prototype loads Babel Standalone
        # from unpkg to transform JSX-like markup at runtime (see frontend/support.js).
        "script-src 'self' 'unsafe-eval' https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
        "font-src 'self' https://fonts.gstatic.com https://unpkg.com; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "upgrade-insecure-requests",
    ),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("X-XSS-Protection", "0"),
)

MAX_PATH_LENGTH = 2048
MAX_BODY_BYTES = 16 * 1024
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 180

SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
MAX_NAME_LENGTH = 120
MAX_TEXT_FIELD_LENGTH = 2000
MAX_LIST_ITEMS = 20

STATUS_FIELDS = (
    "Current Stage",
    "Current Owner",
    "Active Work",
    "Blockers",
    "Known Issues",
    "Human Decisions Required",
    "Next Action",
)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
ANTHROPIC_MODEL = "claude-haiku-4-5"
ANTHROPIC_TIMEOUT_SECONDS = 30
GENERATE_RATE_LIMIT_WINDOW_SECONDS = 60
GENERATE_RATE_LIMIT_MAX_REQUESTS = 5

VERCEL_API_BASE = "https://api.vercel.com"
VERCEL_TIMEOUT_SECONDS = 15
DOMAIN_RATE_LIMIT_WINDOW_SECONDS = 60
DOMAIN_RATE_LIMIT_MAX_REQUESTS = 20
# A domain label (before the first dot) per RFC 1035: letters, digits, and
# internal hyphens, 1-63 characters, not starting or ending with a hyphen.
DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
)

SQUARE_API_VERSION = "2026-09-16"
SQUARE_TIMEOUT_SECONDS = 15
SQUARE_ENVIRONMENTS = {
    "sandbox": "https://connect.squareupsandbox.com",
    "production": "https://connect.squareup.com",
}
CHECKOUT_RATE_LIMIT_WINDOW_SECONDS = 60
CHECKOUT_RATE_LIMIT_MAX_REQUESTS = 10
# Price is fixed here, server-side, and never taken from the request body —
# a client-supplied price would let anyone buy the export for any amount
# they chose. This must be the only source of truth for what gets charged.
EXPORT_PRICE_CENTS = 3900
EXPORT_CURRENCY = "CAD"
# Same reasoning as EXPORT_PRICE_CENTS above: fixed here, server-side, and
# must match the price configured on the Square subscription plan variation
# (SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID) - never taken from the request.
STUDIO_PRICE_CENTS = 2900
STUDIO_CURRENCY = "CAD"

AUTH_RATE_LIMIT_WINDOW_SECONDS = 60
AUTH_RATE_LIMIT_MAX_REQUESTS = 10
SESSION_COOKIE_NAME = "wf_session"
SESSION_TTL_SECONDS = 30 * 24 * 60 * 60
PASSWORD_HASH_ITERATIONS = 200_000
PASSWORD_SALT_BYTES = 16
MIN_PASSWORD_LENGTH = 8
MAX_EMAIL_LENGTH = 254
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def load_dotenv(path):
    """Load KEY=VALUE lines from a .env file into os.environ, without
    overriding a variable the shell already set. No third-party dependency;
    intentionally minimal (no quoting, escaping, or multi-line values)."""
    if not path.is_file():
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class BackendError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class SlidingWindowLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.events = {}

    def allow(self, key):
        now = time.monotonic()
        bucket = self.events.setdefault(key, deque())
        cutoff = now - self.window_seconds
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True


def slugify(name):
    lowered = name.strip().lower()
    collapsed = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return collapsed


def read_status_sections(status_file):
    text = status_file.read_text(encoding="utf-8")
    sections = {}
    heading = None
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            sections[heading] = []
        elif heading is not None:
            sections[heading].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def clean_text(value, max_length):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise BackendError(400, "expected a string field")
    stripped = value.strip()
    if len(stripped) > max_length:
        raise BackendError(400, f"a text field exceeds {max_length} characters")
    return stripped


def clean_list(value, max_items, max_item_length):
    if value is None:
        return []
    if not isinstance(value, list):
        raise BackendError(400, "expected a list field")
    if len(value) > max_items:
        raise BackendError(400, f"a list field exceeds {max_items} items")
    cleaned = []
    for item in value:
        if not isinstance(item, str):
            raise BackendError(400, "list items must be strings")
        text = item.strip()
        if len(text) > max_item_length:
            raise BackendError(400, f"a list item exceeds {max_item_length} characters")
        if text:
            cleaned.append(text)
    return cleaned


def build_copy_prompt(name, brief, who, action, extras):
    summary = "\n".join(
        [
            "Business name: " + (name or "(not given)"),
            "What they do, in the owner's words: " + (brief or "(not given)"),
            "Who the site is for: " + (", ".join(who) or "(not specified)"),
            "Main action a visitor should take: " + (action or "(not specified)"),
            "Extra sections requested: " + (", ".join(extras) or "none"),
        ]
    )
    return (
        summary
        + "\n\nWrite the home page copy for this business's website. "
        "Everything must be specific to THIS business and its actual industry — if it is a "
        "tax filing service write about tax filing, if it is a clothing brand write about the "
        "clothing. Never mention bicycles or any business other than this one. Plain, "
        "matter-of-fact voice. No exclamation marks, no buzzwords, no em dashes.\n\n"
        "Reply with ONLY a JSON object, no code fence, in this exact shape:\n"
        '{"kicker":"3-6 words, e.g. a location or specialism","title":"headline, max 12 words",'
        '"body":"2 sentences, max 40 words","ctaLabel":"2-4 words matching the main action",'
        '"nav":["3 one-word or two-word page names"],'
        '"services":[{"title":"2-4 words","body":"1 sentence, max 22 words","price":"short price or scope line"}],'
        '"closeTitle":"4-8 words inviting the main action","closeNote":"1 short line, max 16 words",'
        '"palette":{"paper":"#rrggbb very light page background","ink":"#rrggbb near-black text",'
        '"accent":"#rrggbb brand accent","band":"#rrggbb light tinted band"}}\n'
        "Give exactly 3 services, drawn from what they said they do. The palette must suit this "
        "industry (a tax firm is not a bakery): paper and band stay very light, ink stays dark "
        "enough to read at 4.5:1, accent carries the brand."
    )


def call_anthropic(anthropic_key, prompt):
    payload = json.dumps(
        {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 900,
            "system": "You are a copywriter. You return only valid JSON matching the requested shape.",
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": anthropic_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=ANTHROPIC_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:300]
        sys.stderr.write(f"Anthropic API error {error.code}: {detail}\n")
        raise BackendError(502, f"the AI provider returned an error (HTTP {error.code})") from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise BackendError(502, "could not reach the AI provider") from error
    except json.JSONDecodeError as error:
        raise BackendError(502, "the AI provider returned an unreadable response") from error

    try:
        raw_text = body["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise BackendError(502, "the AI provider response was missing the expected content") from error

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise BackendError(502, "the AI response could not be parsed as JSON")

    try:
        data = json.loads(raw_text[start : end + 1])
    except json.JSONDecodeError as error:
        raise BackendError(502, "the AI response was not valid JSON") from error

    services = data.get("services")
    services = [s for s in services if isinstance(s, dict) and s.get("title")] if isinstance(services, list) else []
    nav = data.get("nav")
    nav = [{"label": str(item)} for item in nav[:3]] if isinstance(nav, list) else []

    return {
        "kicker": str(data.get("kicker") or ""),
        "title": str(data.get("title") or ""),
        "body": str(data.get("body") or ""),
        "ctaLabel": str(data.get("ctaLabel") or ""),
        "nav": nav,
        "services": [
            {
                "title": str(item.get("title") or ""),
                "body": str(item.get("body") or ""),
                "price": str(item.get("price") or ""),
            }
            for item in services[:3]
        ],
        "closeTitle": str(data.get("closeTitle") or ""),
        "closeNote": str(data.get("closeNote") or ""),
        "palette": data.get("palette") if isinstance(data.get("palette"), dict) else None,
    }


def call_vercel_api(method, path, vercel_token, team_id=None, body=None):
    """Call the Vercel REST API. Never logs or returns the token. Raises
    BackendError with a safe, generic message on any failure — callers must
    not leak Vercel's raw error body to the client."""
    query = f"?teamId={urllib.parse.quote(team_id)}" if team_id else ""
    url = f"{VERCEL_API_BASE}{path}{query}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {vercel_token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=VERCEL_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:300]
        sys.stderr.write(f"Vercel API error {error.code} on {method} {path}: {detail}\n")
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or parsed.get("message") or f"HTTP {error.code}"
        except (json.JSONDecodeError, AttributeError):
            message = f"HTTP {error.code}"
        raise BackendError(502, f"Vercel rejected the request: {message}") from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise BackendError(502, "could not reach Vercel") from error
    except json.JSONDecodeError as error:
        raise BackendError(502, "Vercel returned an unreadable response") from error


def check_domain(domain, vercel_token, team_id=None):
    """Real availability + price lookup via Vercel's Domains Registrar API.
    Read-only: never purchases anything. Returns a normalized dict."""
    availability = call_vercel_api(
        "POST",
        "/v1/registrar/domains/availability",
        vercel_token,
        team_id,
        body={"domains": [domain]},
    )
    results = availability.get("results") or []
    match = next((r for r in results if r.get("domain") == domain), None)
    available = bool(match and match.get("available"))

    if not available:
        return {"domain": domain, "available": False}

    price_data = call_vercel_api(
        "GET",
        f"/v1/registrar/domains/{urllib.parse.quote(domain)}/price",
        vercel_token,
        team_id,
    )
    return {
        "domain": domain,
        "available": True,
        "years": price_data.get("years"),
        "purchasePrice": price_data.get("purchasePrice"),
        "renewalPrice": price_data.get("renewalPrice"),
    }


def call_square_api(method, path, square_access_token, environment, body=None):
    base_url = SQUARE_ENVIRONMENTS.get(environment)
    if not base_url:
        raise BackendError(500, "SQUARE_ENVIRONMENT must be 'sandbox' or 'production'")

    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {square_access_token}",
            "Content-Type": "application/json",
            "Square-Version": SQUARE_API_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=SQUARE_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        sys.stderr.write(f"Square API error {error.code} on {method} {path}: {detail}\n")
        try:
            parsed = json.loads(detail)
            errors = parsed.get("errors") or []
            message = errors[0].get("detail") if errors else f"HTTP {error.code}"
        except (json.JSONDecodeError, AttributeError, IndexError):
            message = f"HTTP {error.code}"
        raise BackendError(502, f"Square rejected the request: {message}") from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise BackendError(502, "could not reach Square") from error
    except json.JSONDecodeError as error:
        raise BackendError(502, "Square returned an unreadable response") from error


def create_export_checkout(square_access_token, environment, location_id, redirect_url):
    """Creates a real Square-hosted checkout page for the fixed-price
    one-time export purchase. Never accepts a client-supplied price."""
    result = call_square_api(
        "POST",
        "/v2/online-checkout/payment-links",
        square_access_token,
        environment,
        body={
            "idempotency_key": uuid.uuid4().hex,
            "quick_pay": {
                "name": "Website export (one-time)",
                "price_money": {"amount": EXPORT_PRICE_CENTS, "currency": EXPORT_CURRENCY},
                "location_id": location_id,
            },
            "checkout_options": {"redirect_url": redirect_url},
        },
    )
    link = result.get("payment_link") or {}
    checkout_url = link.get("url") or link.get("long_url")
    order_id = link.get("order_id")
    if not checkout_url or not order_id:
        raise BackendError(502, "Square did not return a usable checkout link")
    return {"checkoutUrl": checkout_url, "orderId": order_id}


def verify_export_payment(square_access_token, environment, location_id, order_id):
    """Confirms a specific order actually completed payment for the exact
    expected amount, currency, and location — never trusts order state
    alone without cross-checking the charged amount matches what we set."""
    result = call_square_api("GET", f"/v2/orders/{urllib.parse.quote(order_id)}", square_access_token, environment)
    order = result.get("order") or {}
    if order.get("location_id") != location_id:
        return False
    if order.get("state") != "COMPLETED":
        return False
    total = order.get("total_money") or {}
    return total.get("amount") == EXPORT_PRICE_CENTS and total.get("currency") == EXPORT_CURRENCY


def create_studio_checkout(square_access_token, environment, plan_variation_id, buyer_email, redirect_url):
    """Creates a Square-hosted checkout link for the recurring Studio plan.
    Pre-populating buyer_email lets us find the resulting Square customer
    (and their subscription) by email during verification, since — unlike
    the one-time export — Square does not hand back an order/subscription
    id we can carry through the redirect."""
    result = call_square_api(
        "POST", "/v2/online-checkout/payment-links", square_access_token, environment,
        body={
            "idempotency_key": uuid.uuid4().hex,
            "subscription_plan_id": plan_variation_id,
            "price_money": {"amount": STUDIO_PRICE_CENTS, "currency": STUDIO_CURRENCY},
            "checkout_options": {"redirect_url": redirect_url},
            "pre_populated_data": {"buyer_email": buyer_email},
        },
    )
    link = result.get("payment_link") or {}
    checkout_url = link.get("url") or link.get("long_url")
    if not checkout_url:
        raise BackendError(502, "Square did not return a usable checkout link")
    return {"checkoutUrl": checkout_url}


def verify_studio_subscription(square_access_token, environment, location_id, plan_variation_id, buyer_email):
    """Looks up the buyer's Square customer by the email used at checkout,
    then confirms an ACTIVE subscription exists for the expected plan
    variation and location. Returns the customer/subscription ids on
    success, or None if nothing active is found yet."""
    customers_result = call_square_api(
        "POST", "/v2/customers/search", square_access_token, environment,
        body={"query": {"filter": {"email_address": {"exact": buyer_email}}}},
    )
    customers = customers_result.get("customers") or []
    if not customers:
        return None
    customer_id = customers[0].get("id")
    if not customer_id:
        return None
    subscriptions_result = call_square_api(
        "POST", "/v2/subscriptions/search", square_access_token, environment,
        body={"query": {"filter": {"customer_ids": [customer_id], "location_ids": [location_id]}}},
    )
    for subscription in subscriptions_result.get("subscriptions") or []:
        if subscription.get("plan_variation_id") != plan_variation_id:
            continue
        if subscription.get("status") == "ACTIVE":
            return {"customerId": customer_id, "subscriptionId": subscription.get("id")}
    return None


def hash_password(password):
    salt = secrets.token_bytes(PASSWORD_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS)
    return salt.hex(), digest.hex()


def verify_password(password, salt_hex, hash_hex):
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS)
    return secrets.compare_digest(actual, expected)


def normalize_email(value):
    email = (value or "").strip().lower() if isinstance(value, str) else ""
    if not email or len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        return None
    return email


def open_users_db(users_db_path):
    connection = sqlite3.connect(users_db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_users_db(users_db_path):
    """Creates the accounts/sessions/subscriptions tables if they don't
    already exist. Safe to call every time the backend starts."""
    connection = open_users_db(users_db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY REFERENCES users(id),
                square_customer_id TEXT,
                square_subscription_id TEXT,
                status TEXT NOT NULL DEFAULT 'inactive',
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def create_session(connection, user_id):
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now.timestamp() + SESSION_TTL_SECONDS
    connection.execute(
        "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (
            token,
            user_id,
            now.isoformat(),
            datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    return token


def get_session_user(connection, token):
    if not token:
        return None
    row = connection.execute(
        "SELECT users.id, users.email, sessions.expires_at FROM sessions "
        "JOIN users ON users.id = sessions.user_id WHERE sessions.token = ?",
        (token,),
    ).fetchone()
    if not row:
        return None
    user_id, email, expires_at = row
    if datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
        connection.execute("DELETE FROM sessions WHERE token = ?", (token,))
        connection.commit()
        return None
    return {"id": user_id, "email": email}


def get_subscription_status(connection, user_id):
    row = connection.execute(
        "SELECT status FROM subscriptions WHERE user_id = ?", (user_id,)
    ).fetchone()
    return row[0] if row else "inactive"


def record_active_subscription(connection, user_id, customer_id, subscription_id):
    connection.execute(
        """
        INSERT INTO subscriptions (user_id, square_customer_id, square_subscription_id, status, updated_at)
        VALUES (?, ?, ?, 'active', ?)
        ON CONFLICT(user_id) DO UPDATE SET
            square_customer_id = excluded.square_customer_id,
            square_subscription_id = excluded.square_subscription_id,
            status = 'active',
            updated_at = excluded.updated_at
        """,
        (user_id, customer_id, subscription_id, datetime.now(timezone.utc).isoformat()),
    )
    connection.commit()


def build_session_cookie(token, max_age):
    cookie = SimpleCookie()
    cookie[SESSION_COOKIE_NAME] = token
    morsel = cookie[SESSION_COOKIE_NAME]
    morsel["httponly"] = True
    morsel["samesite"] = "Lax"
    morsel["path"] = "/"
    morsel["max-age"] = max_age
    return morsel.OutputString()


SITE_DRAFT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "site-draft" / "index.html.tmpl"

# Matches yyz-caregivers' verified-accessible pilot palette (see
# projects/yyz-caregivers/design/UI-UX-SPEC.md) as a safe fallback whenever
# the AI response omits a palette or supplies something unusable.
DEFAULT_PALETTE = {
    "paper": "#FFFCF7",
    "ink": "#18252D",
    "accent": "#0B675F",
    "band": "#DDF2EE",
}
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")


def safe_hex_color(value, fallback):
    if isinstance(value, str) and HEX_COLOR_PATTERN.match(value.strip()):
        return value.strip()
    return fallback


def render_service_cards(services):
    if not services:
        return ""
    cards = []
    for service in services:
        cards.append(
            "<article class=\"service-card\">"
            f"<h3>{html.escape(service.get('title', ''))}</h3>"
            f"<p>{html.escape(service.get('body', ''))}</p>"
            f"<p class=\"price\">{html.escape(service.get('price', ''))}</p>"
            "</article>"
        )
    return (
        '<section class="services"><div class="container">'
        "<h2>What we offer</h2>"
        f'<div class="service-grid">{"".join(cards)}</div>'
        "</div></section>"
    )


def render_planned_pages(nav):
    labels = [item.get("label", "") for item in nav if isinstance(item, dict) and item.get("label")]
    if not labels:
        return "<span>Home (this page)</span>"
    return "".join(f"<span>{html.escape(label)}</span>" for label in labels)


def render_draft_site(business_name, copy_data):
    """Render a single-page static HTML draft from generated copy. Every
    interpolated value is HTML-escaped — this content originates from an AI
    response (or a client-submitted fallback draft) and must never be
    trusted as safe markup."""
    if not SITE_DRAFT_TEMPLATE.is_file():
        raise BackendError(500, "the site draft template is missing")

    palette_in = copy_data.get("palette") or {}
    palette = {
        "paper": safe_hex_color(palette_in.get("paper"), DEFAULT_PALETTE["paper"]),
        "ink": safe_hex_color(palette_in.get("ink"), DEFAULT_PALETTE["ink"]),
        "accent": safe_hex_color(palette_in.get("accent"), DEFAULT_PALETTE["accent"]),
        "band": safe_hex_color(palette_in.get("band"), DEFAULT_PALETTE["band"]),
    }

    context = {
        "business_name": html.escape(business_name or "Untitled business"),
        "meta_description": html.escape((copy_data.get("body") or "")[:160]),
        "color_paper": palette["paper"],
        "color_ink": palette["ink"],
        "color_accent": palette["accent"],
        "color_band": palette["band"],
        "kicker": html.escape(copy_data.get("kicker") or ""),
        "title": html.escape(copy_data.get("title") or business_name or "Welcome"),
        "body": html.escape(copy_data.get("body") or ""),
        "cta_label": html.escape(copy_data.get("ctaLabel") or "Get in touch"),
        "services_section": render_service_cards(copy_data.get("services") or []),
        "close_title": html.escape(copy_data.get("closeTitle") or "Ready when you are"),
        "close_note": html.escape(copy_data.get("closeNote") or ""),
        "planned_pages_html": render_planned_pages(copy_data.get("nav") or []),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }

    template_text = SITE_DRAFT_TEMPLATE.read_text(encoding="utf-8")
    return Template(template_text).safe_substitute(context)


class BackendHandler(BaseHTTPRequestHandler):
    limiter = SlidingWindowLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
    generate_limiter = SlidingWindowLimiter(GENERATE_RATE_LIMIT_MAX_REQUESTS, GENERATE_RATE_LIMIT_WINDOW_SECONDS)
    domain_limiter = SlidingWindowLimiter(DOMAIN_RATE_LIMIT_MAX_REQUESTS, DOMAIN_RATE_LIMIT_WINDOW_SECONDS)
    checkout_limiter = SlidingWindowLimiter(CHECKOUT_RATE_LIMIT_MAX_REQUESTS, CHECKOUT_RATE_LIMIT_WINDOW_SECONDS)
    auth_limiter = SlidingWindowLimiter(AUTH_RATE_LIMIT_MAX_REQUESTS, AUTH_RATE_LIMIT_WINDOW_SECONDS)
    frontend_dir = None
    projects_dir = None
    init_script = None
    users_db_path = None

    def log_message(self, format, *args):  # noqa: A002 (matches http.server signature)
        message = format % args
        if "\n" in message or "\r" in message:
            return
        sys.stderr.write(f"{message[:300]}\n")

    def end_headers(self):
        for name, value in SECURITY_HEADERS:
            self.send_header(name, value)
        super().end_headers()

    def _rate_limited(self):
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.limiter.allow(client):
            self._send_json(429, {"error": "Too many requests."})
            return True
        return False

    def _send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in extra_headers or ():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _session_token(self):
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
        except Exception:
            return None
        morsel = cookie.get(SESSION_COOKIE_NAME)
        return morsel.value if morsel else None

    def _current_user(self):
        connection = open_users_db(self.users_db_path)
        try:
            return get_session_user(connection, self._session_token())
        finally:
            connection.close()

    def _read_json_body(self):
        declared_length = int(self.headers.get("Content-Length", "0") or "0")
        if declared_length <= 0:
            raise BackendError(400, "a JSON request body is required")
        if declared_length > MAX_BODY_BYTES:
            raise BackendError(413, "request body is too large")
        raw = self.rfile.read(declared_length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise BackendError(400, "request body is not valid JSON") from error
        if not isinstance(data, dict):
            raise BackendError(400, "request body must be a JSON object")
        return data

    # -- routing -----------------------------------------------------

    def do_GET(self):
        if self._rate_limited():
            return
        parsed = urllib.parse.urlsplit(self.path)
        if len(self.path) > MAX_PATH_LENGTH:
            self._send_json(414, {"error": "Request path is too long."})
            return

        if parsed.path == "/api/health":
            self._send_json(200, {"status": "ok"})
            return

        status_match = re.fullmatch(r"/api/projects/([^/]+)/status", parsed.path)
        if status_match:
            self._handle_status(status_match.group(1))
            return

        if parsed.path == "/api/domains/check":
            self._handle_domain_check(urllib.parse.parse_qs(parsed.query))
            return

        if parsed.path == "/api/checkout/verify":
            self._handle_checkout_verify(urllib.parse.parse_qs(parsed.query))
            return

        if parsed.path == "/api/auth/me":
            self._handle_auth_me()
            return

        if parsed.path.startswith("/api/"):
            self._send_json(404, {"error": "Unknown API route."})
            return

        self._serve_static(parsed.path)

    def do_POST(self):
        if self._rate_limited():
            return
        parsed = urllib.parse.urlsplit(self.path)

        if parsed.path == "/api/projects":
            self._handle_create_project()
            return

        if parsed.path == "/api/generate":
            self._handle_generate()
            return

        if parsed.path == "/api/checkout":
            self._handle_checkout_create()
            return

        if parsed.path == "/api/auth/signup":
            self._handle_auth_signup()
            return

        if parsed.path == "/api/auth/login":
            self._handle_auth_login()
            return

        if parsed.path == "/api/auth/logout":
            self._handle_auth_logout()
            return

        if parsed.path.startswith("/api/"):
            self._send_json(404, {"error": "Unknown API route."})
            return

        self._send_json(405, {"error": "Method not allowed."})

    def do_PUT(self):
        self._send_json(405, {"error": "Method not allowed."})

    def do_DELETE(self):
        self._send_json(405, {"error": "Method not allowed."})

    # -- API handlers --------------------------------------------------

    def _handle_create_project(self):
        try:
            data = self._read_json_body()
            name = clean_text(data.get("name"), MAX_NAME_LENGTH)
            if not name:
                raise BackendError(400, "'name' is required")
            brief = clean_text(data.get("brief"), MAX_TEXT_FIELD_LENGTH)
            action = clean_text(data.get("action"), 200)
            who = clean_list(data.get("who"), MAX_LIST_ITEMS, 200)
            extras = clean_list(data.get("extras"), MAX_LIST_ITEMS, 200)
            website_type = clean_text(data.get("websiteType"), 60)
            copy_data = data.get("copy")
            if copy_data is not None and not isinstance(copy_data, dict):
                raise BackendError(400, "'copy' must be a JSON object if provided")

            slug = slugify(name)
            if not slug or not SLUG_PATTERN.match(slug):
                raise BackendError(400, "could not derive a valid project name from 'name'")

            project_dir = (self.projects_dir / slug).resolve()
            try:
                project_dir.relative_to(self.projects_dir.resolve())
            except ValueError as error:
                raise BackendError(400, "invalid project name") from error
            if project_dir.exists():
                raise BackendError(409, f"a project named '{slug}' already exists")

            command = [str(self.init_script), slug]
            if website_type:
                command.append(website_type)
            result = subprocess.run(
                command,
                cwd=str(self.init_script.parent.parent),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if result.returncode != 0:
                raise BackendError(500, "the factory could not create the project")

            self._append_intake_summary(project_dir, name, brief, who, action, extras)

            draft_site_generated = False
            if copy_data:
                site_html = render_draft_site(name, copy_data)
                src_dir = project_dir / "src"
                src_dir.mkdir(parents=True, exist_ok=True)
                (src_dir / "index.html").write_text(site_html, encoding="utf-8")
                self._append_draft_site_note(project_dir)
                draft_site_generated = True

            self._send_json(
                201,
                {
                    "slug": slug,
                    "status": "created",
                    "statusUrl": f"/api/projects/{slug}/status",
                    "draftSiteGenerated": draft_site_generated,
                },
            )
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
        except subprocess.TimeoutExpired:
            self._send_json(500, {"error": "project creation timed out"})
        except Exception:  # noqa: BLE001 - never leak internals to the client
            self._send_json(500, {"error": "an unexpected error occurred"})

    @staticmethod
    def _append_intake_summary(project_dir, name, brief, who, action, extras):
        brief_file = project_dir / "PROJECT-BRIEF.md"
        if not brief_file.is_file():
            return
        lines = [
            "",
            "---",
            "",
            "## Customer-Submitted Intake (unverified)",
            "",
            "Submitted through the frontend prototype's onboarding form. This is raw",
            "customer input, not a validated brief — review and confirm before treating",
            "any of it as approved.",
            "",
            f"- Business name: {name or '(not given)'}",
            f"- What they do, in their own words: {brief or '(not given)'}",
            f"- Who the site is for: {', '.join(who) if who else '(not specified)'}",
            f"- Main action for a visitor: {action or '(not specified)'}",
            f"- Extra sections requested: {', '.join(extras) if extras else 'none'}",
            "",
        ]
        with brief_file.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines))

    @staticmethod
    def _append_draft_site_note(project_dir):
        brief_file = project_dir / "PROJECT-BRIEF.md"
        if not brief_file.is_file():
            return
        note = (
            "\n\n## Auto-Generated Draft Site (unreviewed)\n\n"
            "src/index.html was generated automatically from AI-drafted copy and a generic "
            "template. It is a single-page starting point only: no business fact, service "
            "claim, or navigation destination in it has been verified, and no other pages "
            "exist yet. Treat it exactly like any other Intake-stage output — it still needs "
            "the full factory pipeline (Architecture, Design, Development, QA, and every "
            "specialist review) before any of it is trustworthy or launch-ready.\n"
        )
        with brief_file.open("a", encoding="utf-8") as handle:
            handle.write(note)

    def _handle_generate(self):
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.generate_limiter.allow(client):
            self._send_json(429, {"error": "Too many generation requests. Try again shortly."})
            return

        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not anthropic_key:
            self._send_json(
                503,
                {
                    "error": "AI generation is not configured. Set ANTHROPIC_API_KEY in the "
                    "environment or in a .env file at the factory root, then restart "
                    "./factory frontend."
                },
            )
            return

        try:
            data = self._read_json_body()
            name = clean_text(data.get("name"), MAX_NAME_LENGTH)
            brief = clean_text(data.get("brief"), MAX_TEXT_FIELD_LENGTH)
            action = clean_text(data.get("action"), 200)
            who = clean_list(data.get("who"), MAX_LIST_ITEMS, 200)
            extras = clean_list(data.get("extras"), MAX_LIST_ITEMS, 200)

            prompt = build_copy_prompt(name, brief, who, action, extras)
            copy_data = call_anthropic(anthropic_key, prompt)
            self._send_json(200, copy_data)
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
        except Exception:  # noqa: BLE001 - never leak internals to the client
            self._send_json(500, {"error": "an unexpected error occurred"})

    def _handle_domain_check(self, query):
        """Read-only: checks real availability and price via Vercel's
        Domains Registrar API. Never purchases anything — buying a domain is
        intentionally a separate, explicitly-confirmed CLI step
        (./factory buy-domain), never something a browser request can
        trigger, since this server has no authentication of its own."""
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.domain_limiter.allow(client):
            self._send_json(429, {"error": "Too many domain checks. Try again shortly."})
            return

        vercel_token = os.environ.get("VERCEL_TOKEN", "").strip()
        if not vercel_token:
            self._send_json(
                503,
                {
                    "error": "Domain checking is not configured. Set VERCEL_TOKEN in the "
                    "environment or in a .env file at the factory root, then restart "
                    "./factory frontend."
                },
            )
            return

        domain = (query.get("name", [""])[0] or "").strip().lower()
        if not domain or not DOMAIN_PATTERN.match(domain) or len(domain) > 253:
            self._send_json(400, {"error": "provide a valid domain name, e.g. example.com"})
            return

        try:
            team_id = os.environ.get("VERCEL_TEAM_ID", "").strip() or None
            result = check_domain(domain, vercel_token, team_id)
            self._send_json(200, result)
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
        except Exception:  # noqa: BLE001 - never leak internals to the client
            self._send_json(500, {"error": "an unexpected error occurred"})

    def _handle_checkout_create(self):
        """Creates a real Square-hosted checkout page for either the
        fixed-price one-time export purchase or the recurring Studio
        subscription. Both prices are fixed server-side (EXPORT_PRICE_CENTS,
        STUDIO_PRICE_CENTS) and never taken from the request. Studio also
        requires a signed-in account, since a recurring charge needs
        somewhere to attach the resulting subscription."""
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.checkout_limiter.allow(client):
            self._send_json(429, {"error": "Too many checkout attempts. Try again shortly."})
            return

        square_access_token = os.environ.get("SQUARE_ACCESS_TOKEN", "").strip()
        location_id = os.environ.get("SQUARE_LOCATION_ID", "").strip()
        environment = os.environ.get("SQUARE_ENVIRONMENT", "sandbox").strip().lower() or "sandbox"
        if not square_access_token or not location_id:
            self._send_json(
                503,
                {
                    "error": "Checkout is not configured. Set SQUARE_ACCESS_TOKEN and "
                    "SQUARE_LOCATION_ID in the environment or in a .env file at the factory "
                    "root, then restart ./factory frontend."
                },
            )
            return

        try:
            data = self._read_json_body()
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
            return

        plan = clean_text(data.get("plan"), 40) if isinstance(data, dict) else ""
        host = self.headers.get("Host", "127.0.0.1")

        if plan == "once":
            redirect_url = f"http://{host}/"
            try:
                result = create_export_checkout(square_access_token, environment, location_id, redirect_url)
                self._send_json(200, result)
            except BackendError as error:
                self._send_json(error.status, {"error": error.message})
            except Exception:  # noqa: BLE001 - never leak internals to the client
                self._send_json(500, {"error": "an unexpected error occurred"})
            return

        if plan == "studio":
            plan_variation_id = os.environ.get("SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID", "").strip()
            if not plan_variation_id:
                self._send_json(
                    503,
                    {
                        "error": "Studio subscriptions are not configured. Set "
                        "SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID in the environment or in a .env "
                        "file at the factory root, then restart ./factory frontend."
                    },
                )
                return

            user = self._current_user()
            if not user:
                self._send_json(401, {"error": "sign in or create an account first to subscribe to Studio"})
                return

            # Square never hands back a subscription/order id through the
            # redirect the way it does for the one-time export, so this
            # marker is what tells restoreFromCheckoutRedirect which flow to
            # verify (see verify_studio_subscription — it identifies the
            # buyer by their still-valid session, not by anything in the URL).
            redirect_url = f"http://{host}/?wf_checkout=studio"
            try:
                result = create_studio_checkout(
                    square_access_token, environment, plan_variation_id, user["email"], redirect_url
                )
                self._send_json(200, result)
            except BackendError as error:
                self._send_json(error.status, {"error": error.message})
            except Exception:  # noqa: BLE001 - never leak internals to the client
                self._send_json(500, {"error": "an unexpected error occurred"})
            return

        self._send_json(400, {"error": "unknown plan"})

    def _handle_checkout_verify(self, query):
        """Confirms a completed purchase before the caller unlocks anything.
        This is the only source of truth for whether a purchase is real —
        the frontend must never infer success from the redirect alone.
        Branches on plan: the one-time export is verified by order id; the
        Studio subscription is verified via the signed-in account's email,
        since Square never hands back a subscription id through the
        redirect."""
        square_access_token = os.environ.get("SQUARE_ACCESS_TOKEN", "").strip()
        location_id = os.environ.get("SQUARE_LOCATION_ID", "").strip()
        environment = os.environ.get("SQUARE_ENVIRONMENT", "sandbox").strip().lower() or "sandbox"
        plan = (query.get("plan", ["once"])[0] or "once").strip().lower()

        if plan == "studio":
            plan_variation_id = os.environ.get("SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID", "").strip()
            if not square_access_token or not location_id or not plan_variation_id:
                self._send_json(503, {"error": "Studio subscriptions are not configured."})
                return

            connection = open_users_db(self.users_db_path)
            try:
                user = get_session_user(connection, self._session_token())
                if not user:
                    self._send_json(401, {"error": "sign in first"})
                    return
                try:
                    result = verify_studio_subscription(
                        square_access_token, environment, location_id, plan_variation_id, user["email"]
                    )
                except BackendError as error:
                    self._send_json(error.status, {"error": error.message})
                    return
                except Exception:  # noqa: BLE001 - never leak internals to the client
                    self._send_json(500, {"error": "an unexpected error occurred"})
                    return
                if result:
                    record_active_subscription(connection, user["id"], result["customerId"], result["subscriptionId"])
                self._send_json(200, {"paid": bool(result)})
            finally:
                connection.close()
            return

        if not square_access_token or not location_id:
            self._send_json(503, {"error": "Checkout is not configured."})
            return

        order_id = (query.get("orderId", [""])[0] or "").strip()
        if not order_id or not re.match(r"^[A-Za-z0-9_-]{1,192}$", order_id):
            self._send_json(400, {"error": "provide a valid orderId"})
            return

        try:
            paid = verify_export_payment(square_access_token, environment, location_id, order_id)
            self._send_json(200, {"paid": paid})
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
        except Exception:  # noqa: BLE001 - never leak internals to the client
            self._send_json(500, {"error": "an unexpected error occurred"})

    def _handle_auth_signup(self):
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.auth_limiter.allow(client):
            self._send_json(429, {"error": "Too many attempts. Try again shortly."})
            return

        try:
            data = self._read_json_body()
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
            return

        email = normalize_email(data.get("email"))
        password = data.get("password") if isinstance(data.get("password"), str) else ""
        if not email:
            self._send_json(400, {"error": "provide a valid email address"})
            return
        if len(password) < MIN_PASSWORD_LENGTH:
            self._send_json(400, {"error": f"password must be at least {MIN_PASSWORD_LENGTH} characters"})
            return

        connection = open_users_db(self.users_db_path)
        try:
            existing = connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                self._send_json(409, {"error": "an account with that email already exists"})
                return
            salt, digest = hash_password(password)
            cursor = connection.execute(
                "INSERT INTO users (email, password_salt, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (email, salt, digest, datetime.now(timezone.utc).isoformat()),
            )
            connection.commit()
            token = create_session(connection, cursor.lastrowid)
        finally:
            connection.close()

        cookie = build_session_cookie(token, SESSION_TTL_SECONDS)
        self._send_json(200, {"email": email, "subscriptionActive": False}, extra_headers=[("Set-Cookie", cookie)])

    def _handle_auth_login(self):
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.auth_limiter.allow(client):
            self._send_json(429, {"error": "Too many attempts. Try again shortly."})
            return

        try:
            data = self._read_json_body()
        except BackendError as error:
            self._send_json(error.status, {"error": error.message})
            return

        email = normalize_email(data.get("email"))
        password = data.get("password") if isinstance(data.get("password"), str) else ""
        if not email or not password:
            self._send_json(401, {"error": "invalid email or password"})
            return

        connection = open_users_db(self.users_db_path)
        try:
            row = connection.execute(
                "SELECT id, password_salt, password_hash FROM users WHERE email = ?", (email,)
            ).fetchone()
            if not row or not verify_password(password, row[1], row[2]):
                self._send_json(401, {"error": "invalid email or password"})
                return
            user_id = row[0]
            token = create_session(connection, user_id)
            status = get_subscription_status(connection, user_id)
        finally:
            connection.close()

        cookie = build_session_cookie(token, SESSION_TTL_SECONDS)
        self._send_json(
            200,
            {"email": email, "subscriptionActive": status == "active"},
            extra_headers=[("Set-Cookie", cookie)],
        )

    def _handle_auth_logout(self):
        token = self._session_token()
        if token:
            connection = open_users_db(self.users_db_path)
            try:
                connection.execute("DELETE FROM sessions WHERE token = ?", (token,))
                connection.commit()
            finally:
                connection.close()
        cookie = build_session_cookie("", 0)
        self._send_json(200, {"ok": True}, extra_headers=[("Set-Cookie", cookie)])

    def _handle_auth_me(self):
        connection = open_users_db(self.users_db_path)
        try:
            user = get_session_user(connection, self._session_token())
            if not user:
                self._send_json(401, {"error": "not signed in"})
                return
            status = get_subscription_status(connection, user["id"])
        finally:
            connection.close()
        self._send_json(200, {"email": user["email"], "subscriptionActive": status == "active"})

    def _handle_status(self, slug):
        if not SLUG_PATTERN.match(slug):
            self._send_json(400, {"error": "invalid project slug"})
            return

        project_dir = (self.projects_dir / slug).resolve()
        try:
            project_dir.relative_to(self.projects_dir.resolve())
        except ValueError:
            self._send_json(400, {"error": "invalid project slug"})
            return

        status_file = project_dir / "PROJECT-STATUS.md"
        if not status_file.is_file():
            self._send_json(404, {"error": f"no project named '{slug}' was found"})
            return

        try:
            sections = read_status_sections(status_file)
        except (OSError, UnicodeDecodeError):
            self._send_json(500, {"error": "the project status file could not be read"})
            return

        payload = {"slug": slug}
        key_map = {
            "Current Stage": "stage",
            "Current Owner": "owner",
            "Active Work": "activeWork",
            "Blockers": "blockers",
            "Known Issues": "knownIssues",
            "Human Decisions Required": "humanDecisions",
            "Next Action": "nextAction",
        }
        for heading in STATUS_FIELDS:
            payload[key_map[heading]] = sections.get(heading, "").strip()

        self._send_json(200, payload)

    # -- static file serving --------------------------------------------

    def _serve_static(self, url_path):
        clean = urllib.parse.unquote(url_path.split("?", 1)[0])
        if "\x00" in clean:
            self._send_json(400, {"error": "invalid path"})
            return

        if clean == "/":
            clean = "/index.html"

        collapsed = posixpath.normpath(clean)
        if collapsed.startswith("..") or "/../" in collapsed:
            self._send_json(400, {"error": "invalid path"})
            return

        root = self.frontend_dir.resolve()
        candidate = (root / collapsed.lstrip("/")).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            self._send_json(400, {"error": "invalid path"})
            return

        if candidate.is_dir():
            self._send_json(403, {"error": "directory listing is disabled"})
            return
        if not candidate.is_file():
            self._send_json(404, {"error": "not found"})
            return

        content_type = self._guess_content_type(candidate)
        try:
            body = candidate.read_bytes()
        except OSError:
            self._send_json(500, {"error": "could not read file"})
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _guess_content_type(path):
        suffix = path.suffix.lower()
        return {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".woff2": "font/woff2",
            ".ico": "image/x-icon",
        }.get(suffix, "application/octet-stream")


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Serve the frontend prototype and its local backend API.")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--frontend-dir", required=True)
    parser.add_argument("--projects-dir", required=True)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.bind not in {"127.0.0.1", "localhost", "::1"}:
        print("Error: the backend may only bind to a loopback address.", file=sys.stderr)
        return 1

    frontend_dir = Path(args.frontend_dir).resolve()
    if not frontend_dir.is_dir():
        print(f"Error: frontend directory does not exist at {frontend_dir}.", file=sys.stderr)
        return 1

    projects_dir = Path(args.projects_dir).resolve()
    if not projects_dir.is_dir():
        print(f"Error: projects directory does not exist at {projects_dir}.", file=sys.stderr)
        return 1

    load_dotenv(projects_dir.parent / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        print(
            "Note: ANTHROPIC_API_KEY is not set. /api/generate will return 503 until it is "
            "set in the environment or in a .env file at the factory root.",
            file=sys.stderr,
        )

    if not os.environ.get("SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID", "").strip():
        print(
            "Note: SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID is not set. The Studio subscription "
            "checkout will return 503 until it is set in the environment or in a .env file at "
            "the factory root.",
            file=sys.stderr,
        )

    init_script = projects_dir.parent / "tools" / "init-project.sh"
    if not init_script.is_file():
        print(f"Error: project initializer is missing at {init_script}.", file=sys.stderr)
        return 1

    users_db_path = projects_dir.parent / ".factory-users.db"
    init_users_db(users_db_path)

    BackendHandler.frontend_dir = frontend_dir
    BackendHandler.projects_dir = projects_dir
    BackendHandler.init_script = init_script
    BackendHandler.users_db_path = users_db_path

    server = ThreadingHTTPServer((args.bind, args.port), BackendHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBackend stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
