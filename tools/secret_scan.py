#!/usr/bin/env python3

"""Scan factory or project files for sensitive names and high-confidence secrets.

Findings name the file and pattern class only. Secret values are never printed.
"""

from pathlib import Path
import re
import sys


FACTORY_ROOT = Path(__file__).resolve().parent.parent
IGNORED_PARTS = {".git", ".vercel", "node_modules", "__pycache__", ".next", "dist", "coverage"}
SAFE_ENV_FILES = {".env.example", ".env.sample", ".env.template"}
SENSITIVE_NAMES = {
    ".env",
    "credentials.json",
    "secrets.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
}
SENSITIVE_SUFFIXES = {".key", ".p12", ".pfx", ".pem"}
SECRET_SIGNATURES = (
    ("private key material", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("GitHub access token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("Stripe live key", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("Slack access token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b")),
    ("Google API key", re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b")),
)
GENERIC_SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:export\s+)?(?:api[_-]?key|access[_-]?token|auth[_-]?token|"
    r"auth[_-]?secret|client[_-]?secret|password|secret[_-]?key|"
    r"database_url|redis_url|mongodb_uri|upstash[_-]?redis[_-]?rest[_-]?(?:url|token))\s*"
    r"[:=]\s*['\"]?([^'\"\s#]{12,})"
)
PLACEHOLDER_WORDS = (
    "example",
    "placeholder",
    "replace",
    "your_",
    "your-",
    "changeme",
    "dummy",
    "redacted",
    "xxxx",
)


def ignored_path(relative_path):
    return any(part in IGNORED_PARTS for part in relative_path.parts)


def sensitive_filename(path):
    name = path.name.lower()
    if name in SAFE_ENV_FILES:
        return False
    if name in SENSITIVE_NAMES or (name.startswith(".env.") and name not in SAFE_ENV_FILES):
        return True
    return path.suffix.lower() in SENSITIVE_SUFFIXES


def likely_secret_assignments(text):
    for match in GENERIC_SECRET_ASSIGNMENT.finditer(text):
        value = match.group(1).lower()
        if not any(placeholder in value for placeholder in PLACEHOLDER_WORDS):
            return True
    return False


def secret_findings(root):
    findings = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if ignored_path(relative_path):
            continue

        if sensitive_filename(path):
            findings.append(f"sensitive file present: {relative_path}")

        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for label, pattern in SECRET_SIGNATURES:
            for match in pattern.finditer(text):
                snippet = match.group(0).lower()
                if any(placeholder in snippet for placeholder in PLACEHOLDER_WORDS):
                    continue
                findings.append(f"possible {label} in {relative_path}")
                break
        if likely_secret_assignments(text):
            findings.append(f"possible hard-coded secret assignment in {relative_path}")
    return findings


def display_findings(root, findings):
    print(f"Scanning secrets: {root}")
    if not findings:
        print("  [PASS] no sensitive filenames or high-confidence secret patterns were found")
        print("\nPASSED: secret scan is clean.")
        print("No secret values were displayed.")
        return 0

    for finding in findings[:50]:
        print(f"  [FAIL] {finding}")
    omitted = len(findings) - 50
    if omitted > 0:
        print(f"  [FAIL] {omitted} additional possible secret finding(s) omitted")
    print(f"\nNOT READY: {min(len(findings), 50) + (1 if omitted else 0)} secret finding(s).", file=sys.stderr)
    print("Move credentials into a gitignored .env file. No secret values were displayed.", file=sys.stderr)
    return 1


def resolve_scan_root(argument):
    if argument in (None, ".", "factory"):
        return FACTORY_ROOT
    project_directory = FACTORY_ROOT / "projects" / argument
    if not project_directory.is_dir():
        print(f"Error: project '{argument}' does not exist in {FACTORY_ROOT / 'projects'}.", file=sys.stderr)
        return None
    return project_directory


def main():
    if len(sys.argv) > 2:
        print("Usage: secret_scan.py [project-name|.]", file=sys.stderr)
        return 2

    argument = sys.argv[1] if len(sys.argv) == 2 else None
    root = resolve_scan_root(argument)
    if root is None:
        return 1
    return display_findings(root, secret_findings(root))


if __name__ == "__main__":
    raise SystemExit(main())
