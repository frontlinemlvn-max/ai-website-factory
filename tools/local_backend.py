#!/usr/bin/env python3

"""
Local vertical-slice backend for the Claude Design frontend prototype.

Serves frontend/ as static files and a small JSON API on the same origin
and port, so the browser never needs cross-origin requests:

  GET  /api/health
  POST /api/projects
  GET  /api/projects/<slug>/status
  POST /api/generate

Project creation and status both delegate to the existing factory
(tools/init-project.sh and each project's PROJECT-STATUS.md) rather than
reimplementing scaffolding or workflow logic. /api/generate calls the real
Anthropic API server-side, so the key never reaches the browser; it reads
ANTHROPIC_API_KEY from the environment (or a .env file at the factory
root — see load_dotenv) and fails closed with a clear error when absent,
rather than silently falling back to fake output. Domain purchase,
payments, publishing, deployment, and downloads are NOT implemented here —
the frontend continues to simulate those, as documented in
frontend/README.md.

Reuses the same safety posture as tools/preview-server.py: loopback-only
bind, path-traversal guards, sliding-window rate limiting (tighter for
/api/generate, since each call costs real money), and standard security
headers. Never contacts a network service other than the local factory and
the Anthropic API, and never echoes the API key back to the client or logs.
"""

from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


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


class BackendHandler(BaseHTTPRequestHandler):
    limiter = SlidingWindowLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
    generate_limiter = SlidingWindowLimiter(GENERATE_RATE_LIMIT_MAX_REQUESTS, GENERATE_RATE_LIMIT_WINDOW_SECONDS)
    frontend_dir = None
    projects_dir = None
    init_script = None

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

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

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

            self._send_json(
                201,
                {
                    "slug": slug,
                    "status": "created",
                    "statusUrl": f"/api/projects/{slug}/status",
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

    init_script = projects_dir.parent / "tools" / "init-project.sh"
    if not init_script.is_file():
        print(f"Error: project initializer is missing at {init_script}.", file=sys.stderr)
        return 1

    BackendHandler.frontend_dir = frontend_dir
    BackendHandler.projects_dir = projects_dir
    BackendHandler.init_script = init_script

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
