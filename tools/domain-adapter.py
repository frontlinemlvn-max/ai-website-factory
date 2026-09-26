#!/usr/bin/env python3

"""
Safely preview or perform a real domain registration via Vercel's Domains
Registrar API.

This is a deliberate, separate CLI step — never reachable from the browser
(tools/local_backend.py only ever performs the read-only availability/price
check, never a purchase), because a purchase is a real, non-refundable
financial transaction and this factory has no user-authentication system
that could safely gate who is allowed to spend money from an open web
endpoint.

Registrant contact information (required by the registrar) is read from a
local, gitignored JSON file — never printed, logged, or embedded in any
recorded file. See CONTACT_FILE_PATH below.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


FACTORY_ROOT = Path(__file__).resolve().parent.parent
CONTACT_FILE_PATH = FACTORY_ROOT / ".domain-contact.json"
VERCEL_API_BASE = "https://api.vercel.com"
VERCEL_TIMEOUT_SECONDS = 15
DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$"
)
REQUIRED_CONTACT_FIELDS = (
    "firstName", "lastName", "email", "phone", "address1", "city", "state", "zip", "country",
)


class DomainError(Exception):
    """A domain purchase prerequisite or operation failed safely."""


class DomainUnverified(DomainError):
    """A purchase may have gone through but local recording failed; check
    the Vercel dashboard before retrying."""


def load_dotenv(path):
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


def call_vercel_api(method, path, vercel_token, team_id=None, body=None):
    query = f"?teamId={urllib.parse.quote(team_id)}" if team_id else ""
    url = f"{VERCEL_API_BASE}{path}{query}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {vercel_token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=VERCEL_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or parsed.get("message") or f"HTTP {error.code}"
            code = parsed.get("error", {}).get("code") or parsed.get("code") or ""
        except (json.JSONDecodeError, AttributeError):
            message, code = f"HTTP {error.code}", ""
        raise DomainError(f"Vercel rejected the request ({code or error.code}): {message}") from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise DomainError("could not reach Vercel") from error
    except json.JSONDecodeError as error:
        raise DomainError("Vercel returned an unreadable response") from error


def require_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise DomainError(
            f"{name} is not set; add it to the environment or to .env at the factory root"
        )
    return value


def load_contact_information():
    if not CONTACT_FILE_PATH.is_file():
        raise DomainError(
            f"registrant contact file is missing at {CONTACT_FILE_PATH}. Create it (gitignored, "
            "never committed) as a JSON object with: "
            + ", ".join(REQUIRED_CONTACT_FIELDS)
            + " (companyName, address2, fax optional). This information is sent only to Vercel's "
            "registrar API, exactly as required to register the domain."
        )
    try:
        data = json.loads(CONTACT_FILE_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DomainError(f"registrant contact file is unreadable or invalid: {error}") from error
    if not isinstance(data, dict):
        raise DomainError("registrant contact file must contain a JSON object")
    missing = [field for field in REQUIRED_CONTACT_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        raise DomainError(
            "registrant contact file is missing required field(s): " + ", ".join(missing)
        )
    return data


def check_domain(domain, vercel_token, team_id):
    availability = call_vercel_api(
        "POST", "/v1/registrar/domains/availability", vercel_token, team_id,
        body={"domains": [domain]},
    )
    results = availability.get("results") or []
    match = next((r for r in results if r.get("domain") == domain), None)
    if not match or not match.get("available"):
        raise DomainError(f"'{domain}' is not available to register")

    price_data = call_vercel_api(
        "GET", f"/v1/registrar/domains/{urllib.parse.quote(domain)}/price", vercel_token, team_id,
    )
    price = price_data.get("purchasePrice")
    years = price_data.get("years") or 1
    if not isinstance(price, (int, float)) or price <= 0:
        raise DomainError("Vercel did not return a usable price for this domain")
    return {"price": float(price), "years": int(years), "renewalPrice": price_data.get("renewalPrice")}


def project_dir_for(project_name):
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", project_name):
        raise DomainError("project name must start with a letter or number and contain only letters, numbers, hyphens, and underscores")
    project_directory = (FACTORY_ROOT / "projects" / project_name).resolve()
    try:
        project_directory.relative_to((FACTORY_ROOT / "projects").resolve())
    except ValueError as error:
        raise DomainError("invalid project name") from error
    if not project_directory.is_dir():
        raise DomainError(f"project '{project_name}' does not exist in {FACTORY_ROOT / 'projects'}")
    return project_directory


def display_dry_run(project_name, domain, vercel_token, team_id):
    project_dir_for(project_name)  # raises if the project doesn't exist
    contact = load_contact_information()
    quote = check_domain(domain, vercel_token, team_id)

    print(f"Domain purchase dry run: {project_name} / {domain}")
    print(f"  Available: yes")
    print(f"  Price: ${quote['price']:.2f} USD for {quote['years']} year(s)")
    if quote.get("renewalPrice") is not None:
        print(f"  Renewal price: ${quote['renewalPrice']} USD/year (may differ at renewal time)")
    print(f"  Registrant contact: loaded from {CONTACT_FILE_PATH} ({contact.get('country', '?')})")
    print("  Terms: domain registrations are non-refundable. Auto-renew is on by default and can")
    print("         be changed later in the Vercel dashboard. Vercel's own terms apply.")
    print(f"  Live command: ./factory buy-domain {project_name} {domain} --confirm PURCHASE --expected-price {quote['price']:.2f}")
    print("DRY RUN PASSED: no purchase was made.")


def buy(project_name, domain, confirmation, expected_price):
    if confirmation != "PURCHASE":
        raise DomainError(
            f"confirmation must be exactly 'PURCHASE'; use "
            f"'./factory buy-domain {project_name} {domain} --confirm PURCHASE --expected-price <price>'"
        )
    if expected_price is None:
        raise DomainError("--expected-price is required with --confirm PURCHASE; run --dry-run first to get it")

    project_directory = project_dir_for(project_name)
    vercel_token = require_env("VERCEL_TOKEN")
    team_id = os.environ.get("VERCEL_TEAM_ID", "").strip() or None
    contact = load_contact_information()

    quote = check_domain(domain, vercel_token, team_id)
    try:
        expected = float(expected_price)
    except ValueError as error:
        raise DomainError("--expected-price must be a number") from error
    if abs(quote["price"] - expected) > 0.01:
        raise DomainError(
            f"the live price (${quote['price']:.2f}) no longer matches --expected-price "
            f"(${expected:.2f}); re-run --dry-run and try again with the current price"
        )

    result = call_vercel_api(
        "POST", f"/v1/registrar/domains/{urllib.parse.quote(domain)}/buy", vercel_token, team_id,
        body={
            "autoRenew": True,
            "years": quote["years"],
            "expectedPrice": quote["price"],
            "contactInformation": contact,
        },
    )
    order_id = result.get("orderId")
    if not order_id:
        raise DomainUnverified(
            "Vercel accepted the request but returned no order ID; check the Vercel dashboard "
            "before assuming this succeeded or retrying"
        )

    recorded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    record = (
        f"\n\n## Registered Domain — {recorded_at}\n\n"
        f"- Domain: {domain}\n"
        f"- Order ID: {order_id}\n"
        f"- Price paid: ${quote['price']:.2f} USD for {quote['years']} year(s)\n"
        f"- Purchased via: `./factory buy-domain` (Vercel Domains Registrar API)\n"
        "- Auto-renew: on (manage in the Vercel dashboard)\n"
        "- Registrant contact: recorded with the registrar; not duplicated in this repository\n"
    )
    deployment_file = project_directory / "documentation" / "DEPLOYMENT.md"
    try:
        if deployment_file.is_file():
            with deployment_file.open("a", encoding="utf-8") as handle:
                handle.write(record)
    except OSError as error:
        raise DomainUnverified(
            f"the domain was purchased (order {order_id}) but the local record could not be "
            f"written: {error}. Add it to {deployment_file} manually."
        ) from error

    print(f"Domain registered: {domain}")
    print(f"Order ID: {order_id}")
    print(f"Price: ${quote['price']:.2f} USD for {quote['years']} year(s)")
    print(f"Recorded in: {deployment_file}")


def main():
    usage = (
        "Usage: domain-adapter.py dry-run <project-name> <domain>\n"
        "       domain-adapter.py buy <project-name> <domain> PURCHASE <expected-price>"
    )
    valid_shape = (
        len(sys.argv) == 4 and sys.argv[1] == "dry-run"
        or len(sys.argv) == 6 and sys.argv[1] == "buy"
    )
    if not valid_shape:
        print(usage, file=sys.stderr)
        return 2

    load_dotenv(FACTORY_ROOT / ".env")
    mode = sys.argv[1]
    project_name = sys.argv[2]
    domain = sys.argv[3].strip().lower()
    if not DOMAIN_PATTERN.match(domain):
        print(f"Error: '{domain}' is not a valid domain name.", file=sys.stderr)
        return 1

    try:
        if mode == "dry-run":
            vercel_token = require_env("VERCEL_TOKEN")
            team_id = os.environ.get("VERCEL_TEAM_ID", "").strip() or None
            display_dry_run(project_name, domain, vercel_token, team_id)
        else:
            buy(project_name, domain, sys.argv[4], sys.argv[5])
        return 0
    except DomainUnverified as error:
        print(f"PURCHASE REQUIRES ATTENTION: {error}.", file=sys.stderr)
        return 1
    except DomainError as error:
        print(f"NOT PURCHASED: {error}.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
