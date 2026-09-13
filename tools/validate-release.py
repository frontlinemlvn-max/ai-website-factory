#!/usr/bin/env python3

"""Validate an approved project before it can become deployment ready."""

from pathlib import Path
import re
import subprocess
import sys

from secret_scan import secret_findings


FACTORY_ROOT = Path(__file__).resolve().parent.parent
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
