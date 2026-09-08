#!/usr/bin/env python3

"""Validate an approved project before it can become deployment ready."""

from pathlib import Path
import re
import subprocess
import sys


FACTORY_ROOT = Path(__file__).resolve().parent.parent
IGNORED_PARTS = {".git", ".vercel", "node_modules", "__pycache__"}
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
    ("Stripe live key", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("Slack access token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b")),
    ("Google API key", re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b")),
)
GENERIC_SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:export\s+)?(?:api[_-]?key|access[_-]?token|auth[_-]?token|"
    r"client[_-]?secret|password|secret[_-]?key)\s*[:=]\s*['\"]?([^'\"\s#]{12,})"
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
)
APPROVAL_DECISION = re.compile(r"(?mi)^\s*-\s+\*\*Decision:\*\*\s+APPROVED\s*$")
APPROVAL_TIME = re.compile(
    r"(?mi)^\s*-\s+\*\*Recorded at:\*\*\s+\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\s*$"
)
APPROVAL_EVIDENCE = re.compile(
    r"(?mi)^\s*-\s+\*\*Evidence:\*\*\s+`?reports/LAUNCH-READINESS\.md`?\s*$"
)


class Results:
    def __init__(self):
        self.items = []

    def pass_check(self, message):
        self.items.append((True, message))

    def fail_check(self, message):
        self.items.append((False, message))

    @property
    def failures(self):
        return [message for passed, message in self.items if not passed]

    def display(self, project_name):
        print(f"Validating release readiness: {project_name}")
        for passed, message in self.items:
            label = "PASS" if passed else "FAIL"
            print(f"  [{label}] {message}")

        if self.failures:
            print(f"\nNOT READY: {len(self.failures)} release requirement(s) failed.", file=sys.stderr)
            print("No deployment was performed.", file=sys.stderr)
            return 1

        print("\nPASSED: release requirements are satisfied.")
        print("No deployment was performed.")
        return 0


def read_sections(path):
    text = path.read_text(encoding="utf-8")
    sections = {}
    heading = None
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            sections[heading] = []
        elif heading is not None:
            sections[heading].append(line)
    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
    }


def first_content_line(value):
    return next((line.strip() for line in value.splitlines() if line.strip()), "")


def run_tool(command):
    return subprocess.run(command, capture_output=True, text=True, check=False)


def validate_status(project_directory, results):
    status_file = project_directory / "PROJECT-STATUS.md"
    if not status_file.is_file():
        results.fail_check("PROJECT-STATUS.md is missing")
        return

    try:
        sections = read_sections(status_file)
    except (OSError, UnicodeDecodeError) as error:
        results.fail_check(f"PROJECT-STATUS.md cannot be read: {error}")
        return

    stage = first_content_line(sections.get("Current Stage", ""))
    if stage in ("Approved", "Deployment Ready"):
        results.pass_check(f"project stage is {stage}")
    else:
        results.fail_check(
            f"project stage is '{stage or 'not documented'}', expected Approved or Deployment Ready"
        )

    blockers = first_content_line(sections.get("Blockers", ""))
    if blockers.lower().startswith(("none", "no blocker")):
        results.pass_check("PROJECT-STATUS.md has no active blockers")
    else:
        results.fail_check("PROJECT-STATUS.md contains active or undocumented blockers")

    approval = sections.get("Human Decisions Required", "")
    if APPROVAL_DECISION.search(approval):
        results.pass_check("explicit APPROVED decision is recorded")
    else:
        results.fail_check("human approval record is missing an explicit APPROVED decision")
    if APPROVAL_TIME.search(approval):
        results.pass_check("human approval record includes a UTC timestamp")
    else:
        results.fail_check("human approval record is missing a valid UTC timestamp")
    if APPROVAL_EVIDENCE.search(approval):
        results.pass_check("human approval cites the launch-readiness evidence")
    else:
        results.fail_check("human approval does not cite reports/LAUNCH-READINESS.md")


def validate_deployment_plan(project_name, project_directory, results):
    validator = FACTORY_ROOT / "tools" / "validate-stage.py"
    if not validator.is_file():
        results.fail_check("tools/validate-stage.py is missing")
        return

    outcome = run_tool(
        [sys.executable, str(validator), project_name, str(project_directory), "Approved"]
    )
    if outcome.returncode == 0:
        results.pass_check("deployment and rollback documentation passes stage validation")
    else:
        results.fail_check(
            f"deployment documentation is incomplete; run './factory validate-stage {project_name}'"
        )


def validate_project_checks(project_name, project_directory, results):
    checker = FACTORY_ROOT / "tools" / "check-project.py"
    site_directory = project_directory / "src"
    if not checker.is_file():
        results.fail_check("tools/check-project.py is missing")
        return
    if not (site_directory / "index.html").is_file():
        results.fail_check("release checks require a src/index.html entry page")
        return

    outcome = run_tool([sys.executable, str(checker), project_name, str(site_directory)])
    if outcome.returncode == 0:
        results.pass_check("HTML, links, assets, JavaScript, and CSS checks pass")
    else:
        results.fail_check(f"project checks are failing; run './factory check {project_name}'")


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


def secret_findings(project_directory):
    findings = []
    for path in sorted(project_directory.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        relative_path = path.relative_to(project_directory)
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
            if pattern.search(text):
                findings.append(f"possible {label} in {relative_path}")
        if likely_secret_assignments(text):
            findings.append(f"possible hard-coded secret assignment in {relative_path}")
    return findings


def validate_secrets(project_directory, results):
    findings = secret_findings(project_directory)
    if findings:
        for finding in findings[:20]:
            results.fail_check(finding)
        if len(findings) > 20:
            results.fail_check(f"{len(findings) - 20} additional possible secret finding(s) omitted")
    else:
        results.pass_check("no sensitive filenames or high-confidence secret patterns were found")


def validate_release(project_name, project_directory):
    results = Results()
    validate_status(project_directory, results)
    validate_deployment_plan(project_name, project_directory, results)
    validate_project_checks(project_name, project_directory, results)
    validate_secrets(project_directory, results)
    return results.display(project_name)


def main():
    if len(sys.argv) != 3:
        print("Usage: validate-release.py <project-name> <project-directory>", file=sys.stderr)
        return 2

    project_name = sys.argv[1]
    project_directory = Path(sys.argv[2]).resolve()
    if not project_directory.is_dir():
        print(f"Error: project directory does not exist at {project_directory}.", file=sys.stderr)
        return 1
    return validate_release(project_name, project_directory)


if __name__ == "__main__":
    raise SystemExit(main())
