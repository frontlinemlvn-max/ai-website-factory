#!/usr/bin/env python3

"""Serve a project src directory with security headers and basic abuse controls."""

from collections import deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import os
import posixpath
import sys
import time
import urllib.parse


SECURITY_HEADERS = (
    (
        "Content-Security-Policy",
        "default-src 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "object-src 'none'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'",
        # No 'upgrade-insecure-requests': this server only ever speaks plain
        # HTTP on loopback and never runs behind TLS. Chrome exempts
        # 127.0.0.1/localhost from that directive's upgrade, but Safari does
        # not — it upgrades every sub-resource request to https and then
        # fails with a TLS error, since nothing here serves HTTPS. See the
        # matching fix and explanation in tools/local_backend.py.
    ),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("X-XSS-Protection", "0"),
    ("Cache-Control", "no-store"),
)

MAX_PATH_LENGTH = 2048
MAX_QUERY_LENGTH = 1024
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 180


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


class SecurePreviewHandler(SimpleHTTPRequestHandler):
    limiter = SlidingWindowLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)

    def end_headers(self):
        for name, value in SECURITY_HEADERS:
            self.send_header(name, value)
        super().end_headers()

    def log_message(self, format, *args):
        message = format % args
        if "\n" in message or "\r" in message:
            return
        super().log_message("%s", message[:300])

    def translate_path(self, path):
        parsed = urllib.parse.urlsplit(path)
        clean = urllib.parse.unquote(parsed.path)
        if "\x00" in clean:
            return ""
        collapsed = posixpath.normpath(clean)
        if collapsed.startswith("..") or "/../" in collapsed:
            return ""
        return super().translate_path(path)

    def list_directory(self, path):
        self.send_error(403, "Directory listing is disabled")
        return None

    def do_GET(self):
        if not self._request_is_safe():
            return
        super().do_GET()

    def do_HEAD(self):
        if not self._request_is_safe():
            return
        super().do_HEAD()

    def do_POST(self):
        self.send_error(405, "Method not allowed")

    def do_PUT(self):
        self.send_error(405, "Method not allowed")

    def do_DELETE(self):
        self.send_error(405, "Method not allowed")

    def _request_is_safe(self):
        client = self.client_address[0] if self.client_address else "unknown"
        if not self.limiter.allow(client):
            self.send_error(429, "Too many requests")
            return False

        parsed = urllib.parse.urlsplit(self.path)
        if len(self.path) > MAX_PATH_LENGTH or len(parsed.query) > MAX_QUERY_LENGTH:
            self.send_error(414, "Request-URI too long")
            return False
        if "\x00" in self.path:
            self.send_error(400, "Invalid request")
            return False

        translated = self.translate_path(self.path)
        root = Path(self.directory).resolve()
        if not translated:
            self.send_error(400, "Invalid path")
            return False
        try:
            candidate = Path(translated).resolve()
            candidate.relative_to(root)
        except (OSError, ValueError):
            self.send_error(400, "Invalid path")
            return False
        return True


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Serve a factory project with security headers.")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--bind", default="127.0.0.1")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    directory = Path(args.directory).resolve()
    if not directory.is_dir():
        print(f"Error: preview directory does not exist at {directory}.", file=sys.stderr)
        return 1
    if args.bind not in {"127.0.0.1", "localhost", "::1"}:
        print("Error: preview server may only bind to a loopback address.", file=sys.stderr)
        return 1

    os.chdir(directory)
    handler = SecurePreviewHandler
    handler.directory = str(directory)
    server = ThreadingHTTPServer((args.bind, args.port), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPreview stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
