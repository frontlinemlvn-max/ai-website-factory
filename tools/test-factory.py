#!/usr/bin/env python3

"""Run isolated end-to-end regression tests for the factory command."""

from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FACTORY_ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = "suite-project"

VALID_INDEX = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Factory Suite</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main id="main">
    <h1>Factory suite project</h1>
    <a href="#main">Return to main content</a>
  </main>
</body>
</html>
"""

VALID_LAUNCH_REPORT = """# Launch Readiness

## Project Summary

This disposable static website exists to verify the AI Website Factory command line workflow. It contains one semantic page, local styling, and a working navigation target, with no production data or external service dependency.

## Pipeline Status

The required factory stages are represented by isolated test evidence. Static source checks pass, the workflow files are readable, and every transition exercised here remains confined to the temporary test project created for this run.

## Outstanding Issues

No blocking issue is open for this temporary fixture. The site is intentionally small because its only purpose is deterministic regression coverage for command routing, validation, approval, and release safety behavior.

## Deployment Readiness

READY FOR HUMAN APPROVAL. The local source and supporting records satisfy the structural gates used by this test. This verdict permits an explicit human decision but does not itself authorize or perform any production deployment.

## Remaining Risks

The fixture does not represent a real customer site and does not test an external hosting network. Those limits are intentional so the regression suite stays fast, repeatable, offline, and unable to affect production resources.

## Deployment Plan

Use the documented Vercel target only after release validation passes and the exact deployment confirmation is supplied. During this suite, a local fake executable replaces Vercel and refuses authentication before any deployment action.

## Rollback

If this were a real release, restore the previously verified production deployment through the hosting provider and repeat the post-deployment checks. The temporary fixture itself is deleted automatically after the test run finishes.

## Next Action

Present this evidence at the human approval gate. After approval, validate the release package, advance only to Deployment Ready, and use the dry run to inspect the intended target without contacting a service.
"""

VALID_DEPLOYMENT = """# Deployment

## Deployment Platform

Vercel using organization `team_FactorySuite` and project `prj_FactorySuite`. The linked identifiers are test-only values stored inside the temporary fixture and do not identify a real hosting account or project.

## Build Process

This static site requires no compilation. The deployable directory contains the checked HTML and CSS files together with the project documentation used by the workflow gates. Local integrity checks must pass before release.

## Environment Variables

No environment variables are required by this static fixture. Authentication values are never stored in the project, passed on the command line, printed by the suite, or requested from a real provider.

## Deployment Procedure

Run the factory deployment dry run first and review the displayed organization, project, root directory, and file count. A live action requires the separate exact DEPLOY confirmation and an existing authenticated provider session.

## Post-Deployment Verification

Verified production URL: https://suite-production.invalid. After a real release, confirm that the returned HTTPS address responds successfully with an HTML document and record the result. The regression suite uses local fakes and performs no remote release.

## Rollback

Restore the last verified provider deployment if production verification fails, then confirm the HTTPS page and document the recovery. No rollback action is needed for this disposable fixture because nothing is remotely deployed.
"""

VALID_INTAKE_INPUT = "\n".join(
    (
        "Factory Test Brand",
        "Static marketing website",
        "2030-01-01",
        "Verify that factory commands work safely in isolation.",
        "Confirm repeatable project setup, Protect human approval boundaries",
        "Factory maintainers testing local changes",
        "Internal development environment",
        "Clear command results, Confidence that real projects remain unchanged",
        "1",
        "1, 4",
        "Semantic static page, Working in-page navigation",
        "Factory Test Brand",
        "No",
        "Navy and white",
        "Neutral slate",
        "System sans serif",
        "Clear and reliable",
        "Minimal responsive technical interface",
        "Factory maintainers",
        "suite.invalid",
        "Vercel test target",
        "Semantic HTML and CSS",
        "None required for this static test",
        "None required for this static test",
        "None required for this static test",
        "factory regression testing",
        "Internal development environment",
        "Internal test allocation",
        "Complete during the local test run",
        "Standard-library tooling only",
        "Never touch a real project or production service",
        "y",
    )
) + "\n"


class TestFailure(AssertionError):
    """A regression expectation was not satisfied."""


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + self.stderr


def require(condition, message):
    if not condition:
        raise TestFailure(message)


def fingerprint_tree(root):
    """Return a content fingerprint without following symbolic links."""
    digest = hashlib.sha256()
    if not root.exists():
        digest.update(b"missing")
        return digest.hexdigest()

    for current_root, directory_names, file_names in os.walk(root, followlinks=False):
        directory_names.sort()
        file_names.sort()
        current = Path(current_root)
        for name in directory_names + file_names:
            path = current / name
            relative = path.relative_to(root).as_posix()
            digest.update(relative.encode("utf-8", errors="surrogateescape"))
            if path.is_symlink():
                digest.update(b"L")
                digest.update(os.readlink(path).encode("utf-8", errors="surrogateescape"))
            elif path.is_file():
                digest.update(b"F")
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
            else:
                digest.update(b"D")
    return digest.hexdigest()


def write_text(path, content, executable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR)


def copy_factory(destination):
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    for name in ("agents", "documentation", "templates", "tools", "workflows", "frontend"):
        source = FACTORY_ROOT / name
        shutil.copytree(source, destination / name, symlinks=True, ignore=ignore)
    for name in ("factory", "CLAUDE.md", "README.md", ".env.example"):
        shutil.copy2(FACTORY_ROOT / name, destination / name)
    (destination / "projects").mkdir()

    git = shutil.which("git")
    require(git is not None, "git is required to prepare the isolated doctor test")
    initialized = subprocess.run(
        [git, "init", "--quiet", str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    require(initialized.returncode == 0, f"isolated Git repository setup failed: {initialized.stderr}")


def status_document(stage):
    return f"""# Project Status

## Project

{PROJECT_NAME}

## Current Stage

{stage}

## Current Owner

Project Orchestrator

## Completed Stages

- Intake through Final Review represented by isolated suite evidence.

## Active Work

Exercise the selected workflow gate in the disposable test project.

## Blockers

None identified.

## Known Issues

None identified.

## Human Decisions Required

Explicit human approval is required before release preparation.

## Next Action

Run the next isolated factory gate without contacting a production service.
"""


class FactorySuite:
    def __init__(self, sandbox_root):
        self.root = sandbox_root
        self.factory = sandbox_root / "factory"
        self.project = sandbox_root / "projects" / PROJECT_NAME
        self.status_file = self.project / "PROJECT-STATUS.md"
        self.deployment_file = self.project / "documentation" / "DEPLOYMENT.md"
        self.vercel_log = sandbox_root / "fake-vercel.log"
        self.fake_bin = sandbox_root / "fake-bin"
        self.passed = 0
        self.failures = []
        self.environment = os.environ.copy()
        self.environment["PYTHONDONTWRITEBYTECODE"] = "1"
        self.environment["NO_COLOR"] = "1"

    def run(self, *arguments, timeout=20, environment=None, input_text=None):
        active_environment = self.environment.copy()
        if environment:
            active_environment.update(environment)
        result = subprocess.run(
            [str(self.factory), *arguments],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=active_environment,
            input=input_text,
        )
        return CommandResult(result.returncode, result.stdout, result.stderr)

    def expect(self, result, returncode, *fragments):
        require(
            result.returncode == returncode,
            f"expected exit {returncode}, received {result.returncode}\n{result.output[-1200:]}",
        )
        for fragment in fragments:
            require(fragment in result.output, f"missing output {fragment!r}\n{result.output[-1200:]}")

    def case(self, name, operation):
        try:
            operation()
        except Exception as error:  # Keep running to report independent regressions together.
            self.failures.append((name, str(error)))
            print(f"  [FAIL] {name}")
        else:
            self.passed += 1
            print(f"  [PASS] {name}")

    def prepare_fake_vercel(self):
        script = """#!/bin/sh
printf '%s\\n' "$*" >> "$FACTORY_TEST_VERCEL_LOG"
if [ "${FACTORY_TEST_VERCEL_MODE:-}" = "inspect" ]; then
  if [ "$1" = "whoami" ]; then
    printf '%s\\n' "factory-suite-user"
    exit 0
  fi
  if [ "$1" = "api" ]; then
    printf '%s\\n' '{"id":"dpl_PreviousFactorySuite","url":"suite-previous.vercel.app","projectId":"prj_FactorySuite","team":{"id":"team_FactorySuite"},"readyState":"READY","target":"production"}'
    exit 0
  fi
fi
if [ "${FACTORY_TEST_VERCEL_MODE:-}" = "mismatch" ]; then
  if [ "$1" = "whoami" ]; then
    printf '%s\\n' "factory-suite-user"
    exit 0
  fi
  if [ "$1" = "api" ]; then
    printf '%s\\n' '{"id":"dpl_PreviousFactorySuite","url":"other-project.vercel.app","projectId":"prj_OtherProject","team":{"id":"team_FactorySuite"},"readyState":"READY","target":"production"}'
    exit 0
  fi
fi
if [ "${FACTORY_TEST_VERCEL_MODE:-}" = "missing-org" ]; then
  if [ "$1" = "whoami" ]; then
    printf '%s\n' "factory-suite-user"
    exit 0
  fi
  if [ "$1" = "api" ]; then
    printf '%s\n' '{"id":"dpl_PreviousFactorySuite","url":"suite-previous.vercel.app","projectId":"prj_FactorySuite","readyState":"READY","target":"production"}'
    exit 0
  fi
fi
if [ "${FACTORY_TEST_VERCEL_MODE:-}" = "wrong-url" ]; then
  if [ "$1" = "whoami" ]; then
    printf '%s\n' "factory-suite-user"
    exit 0
  fi
  if [ "$1" = "api" ]; then
    printf '%s\n' '{"id":"dpl_PreviousFactorySuite","url":"different.vercel.app","projectId":"prj_FactorySuite","team":{"id":"team_FactorySuite"},"readyState":"READY","target":"production"}'
    exit 0
  fi
fi
exit 1
"""
        write_text(self.fake_bin / "vercel", script, executable=True)
        return {
            "PATH": f"{self.fake_bin}{os.pathsep}{self.environment.get('PATH', '')}",
            "FACTORY_TEST_VERCEL_LOG": str(self.vercel_log),
        }

    def preview_works(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]

        process = subprocess.Popen(
            [str(self.factory), "preview", PROJECT_NAME, str(port)],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=self.environment,
        )
        served = False
        headers = {}
        output = ""
        try:
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    with urlopen(f"http://127.0.0.1:{port}/", timeout=0.5) as response:
                        body = response.read().decode("utf-8")
                        headers = dict(response.headers)
                    served = response.status == 200 and "Factory suite project" in body
                    if served:
                        break
                except (URLError, TimeoutError, OSError):
                    time.sleep(0.05)
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                output = process.communicate(timeout=3)[0]
            except subprocess.TimeoutExpired:
                process.kill()
                output = process.communicate(timeout=3)[0]
        require(served, f"preview did not serve the fixture\n{output[-1200:]}")
        csp = headers.get("Content-Security-Policy") or headers.get("content-security-policy") or ""
        require("default-src 'self'" in csp, f"preview omitted CSP header\n{headers}")
        require(
            (headers.get("X-Content-Type-Options") or headers.get("x-content-type-options") or "") == "nosniff",
            "preview omitted X-Content-Type-Options",
        )


def run_suite(suite):
    fake_environment = suite.prepare_fake_vercel()

    def help_case():
        result = suite.run("--help")
        suite.expect(
            result,
            0,
            "./factory doctor",
            "./factory create",
            "./factory intake",
            "./factory deploy",
            "./factory rollback",
            "./factory preview",
            "./factory scan-secrets",
            "./factory test",
        )

    suite.case("help lists every public command", help_case)
    suite.case(
        "test command rejects unexpected arguments",
        lambda: suite.expect(suite.run("test", "unexpected"), 1, "Usage:"),
    )
    suite.case(
        "doctor rejects unexpected arguments",
        lambda: suite.expect(suite.run("doctor", "unexpected"), 1, "Usage:"),
    )

    def empty_factory_doctor_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.root)
        result = suite.run("doctor", environment=fake_environment)
        suite.expect(result, 0, "AI Website Factory doctor", "HEALTHY", "No projects yet")
        require(not suite.vercel_log.exists(), "doctor invoked the Vercel executable")
        require(fingerprint_tree(suite.root) == before, "doctor changed the factory")

    suite.case("doctor passes read-only checks on a healthy empty factory", empty_factory_doctor_case)

    def invalid_name_case():
        result = suite.run("create", "../escaped")
        suite.expect(result, 1, "project name must start")
        require(not (suite.root / "escaped").exists(), "invalid name escaped the projects directory")

    suite.case("create rejects unsafe project names", invalid_name_case)

    def create_case():
        result = suite.run("create", PROJECT_NAME)
        suite.expect(result, 0, "Project created successfully")
        require(suite.status_file.is_file(), "project status file was not created")
        require((suite.project / "PROJECT-BRIEF.md").is_file(), "project brief was not created")
        require((suite.project / ".env.example").is_file(), "project env template was not created")
        require((suite.project / ".gitignore").is_file(), "project gitignore was not created")
        require((suite.project / "src" / "vercel.json").is_file(), "security headers config was not created in the deploy root")
        require(not (suite.project / "vercel.json").exists(), "security headers config was created outside the deploy root, where Vercel ignores it")

    suite.case("create builds the standard project scaffold", create_case)
    suite.case(
        "create refuses to overwrite a project",
        lambda: suite.expect(suite.run("create", PROJECT_NAME), 1, "already exists"),
    )
    suite.case(
        "list reports the isolated project",
        lambda: suite.expect(suite.run("list"), 0, PROJECT_NAME, "Intake"),
    )
    suite.case(
        "status reads the isolated project state",
        lambda: suite.expect(suite.run("status", PROJECT_NAME), 0, "Current Stage: Intake"),
    )

    def project_doctor_case():
        before = fingerprint_tree(suite.root)
        result = suite.run("doctor", environment=fake_environment)
        suite.expect(result, 0, "Projects: all 1 project scaffold(s) are structurally complete")
        require(fingerprint_tree(suite.root) == before, "project health check changed the factory")

    suite.case("doctor accepts a complete project scaffold", project_doctor_case)

    def broken_status_doctor_case():
        original = suite.status_file.read_text(encoding="utf-8")
        write_text(suite.status_file, "# Broken project status\n")
        try:
            before = fingerprint_tree(suite.root)
            result = suite.run("doctor", environment=fake_environment)
            suite.expect(result, 1, "UNHEALTHY", "PROJECT-STATUS.md is missing the Current Stage section")
            require(fingerprint_tree(suite.root) == before, "failed doctor check changed the factory")
        finally:
            write_text(suite.status_file, original)

    suite.case("doctor reports a malformed project status", broken_status_doctor_case)
    suite.case(
        "brief validator rejects untouched placeholders",
        lambda: suite.expect(suite.run("validate-brief", PROJECT_NAME), 1, "NOT READY"),
    )

    def cancelled_intake_case():
        before = fingerprint_tree(suite.project)
        result = suite.run("intake", PROJECT_NAME, input_text="CANCEL\n")
        suite.expect(result, 0, "INTAKE CANCELLED", "No changes were saved")
        require(fingerprint_tree(suite.project) == before, "cancelled intake changed project files")

    suite.case("guided intake can be cancelled without changes", cancelled_intake_case)

    def completed_intake_case():
        status_before = suite.status_file.read_bytes()
        result = suite.run("intake", PROJECT_NAME, input_text=VALID_INTAKE_INPUT)
        suite.expect(result, 0, "Intake saved", "READY: the brief contains")
        brief = (suite.project / "PROJECT-BRIEF.md").read_text(encoding="utf-8")
        require(f"**Project Name:** {PROJECT_NAME}" in brief, "intake did not set the project name")
        require("- [x] Landing Page" in brief, "intake did not record the website type")
        require("- [x] Contact" in brief, "intake did not record selected pages")
        require(suite.status_file.read_bytes() == status_before, "intake changed workflow status")

    suite.case("guided intake creates a validator-ready brief", completed_intake_case)

    def preserved_intake_case():
        before = fingerprint_tree(suite.project)
        result = suite.run("intake", PROJECT_NAME, input_text="\n" * 31)
        suite.expect(result, 0, "No changes requested", "READY: the brief contains")
        require(fingerprint_tree(suite.project) == before, "intake rerun changed preserved answers")

    suite.case("guided intake preserves existing answers by default", preserved_intake_case)

    write_text(suite.project / "src" / "index.html", VALID_INDEX)
    write_text(suite.project / "src" / "styles.css", "body { color: #172033; background: #ffffff; }\n")
    write_text(suite.project / "reports" / "LAUNCH-READINESS.md", VALID_LAUNCH_REPORT)
    write_text(suite.deployment_file, VALID_DEPLOYMENT)

    suite.case(
        "brief validator accepts complete intake data",
        lambda: suite.expect(suite.run("validate-brief", PROJECT_NAME), 0, "READY:"),
    )
    suite.case(
        "stage validator accepts a completed intake stage",
        lambda: suite.expect(suite.run("validate-stage", PROJECT_NAME), 0, "PASSED:"),
    )
    suite.case(
        "next reports the ready Architecture transition",
        lambda: suite.expect(suite.run("next", PROJECT_NAME), 0, "Next stage: Architecture", "Gate: READY"),
    )

    def handoff_case():
        before = suite.status_file.read_bytes()
        result = suite.run("handoff", PROJECT_NAME)
        suite.expect(result, 0, "Created handoff", "Intake -> Architecture")
        require((suite.project / "HANDOFF.md").is_file(), "handoff file was not created")
        require(suite.status_file.read_bytes() == before, "handoff changed project status")

    suite.case("handoff creates an assignment without advancing", handoff_case)

    def advance_case():
        result = suite.run("advance", PROJECT_NAME)
        suite.expect(result, 0, "Intake -> Architecture")
        require("\nArchitecture\n" in suite.status_file.read_text(encoding="utf-8"), "advance did not update the stage")

    suite.case("advance moves exactly one validated stage", advance_case)

    def late_intake_case():
        before = fingerprint_tree(suite.project)
        result = suite.run("intake", PROJECT_NAME)
        suite.expect(result, 1, "expected Intake", "no answers were changed")
        require(fingerprint_tree(suite.project) == before, "late intake changed project files")

    suite.case("guided intake cannot rewrite requirements after Intake", late_intake_case)

    write_text(suite.status_file, status_document("Ready for Human Approval"))

    def generic_approval_case():
        before = suite.status_file.read_bytes()
        result = suite.run("advance", PROJECT_NAME)
        suite.expect(result, 1, "generic advancement cannot grant human approval")
        require(suite.status_file.read_bytes() == before, "generic advance changed approval state")

    suite.case("advance cannot bypass human approval", generic_approval_case)

    def wrong_approval_case():
        before = suite.status_file.read_bytes()
        result = suite.run("approve", PROJECT_NAME, "approved")
        suite.expect(result, 1, "exactly 'APPROVED'")
        require(suite.status_file.read_bytes() == before, "wrong approval token changed status")

    suite.case("approval requires the exact confirmation", wrong_approval_case)

    def missing_approval_release_case():
        write_text(suite.status_file, status_document("Approved"))
        before = suite.status_file.read_bytes()
        result = suite.run("validate-release", PROJECT_NAME)
        suite.expect(result, 1, "approval record is missing an explicit APPROVED decision", "No deployment was performed")
        require(suite.status_file.read_bytes() == before, "release validation changed status")
        write_text(suite.status_file, status_document("Ready for Human Approval"))

    suite.case("release validation rejects a missing approval record", missing_approval_release_case)

    def unapproved_deploy_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run("deploy", PROJECT_NAME, "--confirm", "DEPLOY", environment=fake_environment)
        suite.expect(result, 1, "release validation is failing")
        require(not suite.vercel_log.exists(), "Vercel was invoked before human approval")
        require(fingerprint_tree(suite.project) == before, "refused deployment changed project files")

    suite.case("deployment cannot bypass human approval", unapproved_deploy_case)

    def approval_case():
        result = suite.run("approve", PROJECT_NAME, "APPROVED")
        suite.expect(result, 0, "Ready for Human Approval -> Approved", "No deployment was performed")
        status = suite.status_file.read_text(encoding="utf-8")
        require("**Decision:** APPROVED" in status, "approval decision was not recorded")

    suite.case("approve records an explicit human decision", approval_case)
    suite.case(
        "release validator accepts the approved package",
        lambda: suite.expect(suite.run("validate-release", PROJECT_NAME), 0, "PASSED:", "No deployment was performed"),
    )

    def release_advance_case():
        result = suite.run("advance", PROJECT_NAME)
        suite.expect(result, 0, "Approved -> Deployment Ready")

    suite.case("advance enters Deployment Ready only after release validation", release_advance_case)
    suite.case(
        "deployment stage documentation validates",
        lambda: suite.expect(suite.run("validate-stage", PROJECT_NAME), 0, "Deployment Ready", "PASSED:"),
    )

    def generic_deployment_case():
        before = suite.status_file.read_bytes()
        result = suite.run("advance", PROJECT_NAME)
        suite.expect(result, 1, "generic advancement cannot deploy a production project")
        require(suite.status_file.read_bytes() == before, "generic advance changed deployment state")

    suite.case("advance cannot bypass explicit deployment", generic_deployment_case)

    write_text(
        suite.project / ".vercel" / "project.json",
        '{"orgId":"team_FactorySuite","projectId":"prj_FactorySuite"}\n',
    )

    def linked_project_doctor_case():
        before = fingerprint_tree(suite.root)
        result = suite.run("doctor", environment=fake_environment)
        suite.expect(result, 0, "Vercel links: 1 valid project link(s)")
        require(fingerprint_tree(suite.root) == before, "Vercel link health check changed the factory")

    suite.case("doctor validates an existing Vercel project link", linked_project_doctor_case)

    def invalid_link_doctor_case():
        link_file = suite.project / ".vercel" / "project.json"
        original = link_file.read_text(encoding="utf-8")
        write_text(link_file, '{"orgId":"","projectId":"prj_FactorySuite"}\n')
        try:
            before = fingerprint_tree(suite.root)
            result = suite.run("doctor", environment=fake_environment)
            suite.expect(result, 1, "UNHEALTHY", "lacks organization or project identifiers")
            require(fingerprint_tree(suite.root) == before, "invalid link check changed the factory")
        finally:
            write_text(link_file, original)

    suite.case("doctor reports an invalid Vercel project link", invalid_link_doctor_case)

    def dry_run_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run("deploy", PROJECT_NAME, "--dry-run", environment=fake_environment)
        suite.expect(result, 0, "DRY RUN PASSED", "team_FactorySuite", "prj_FactorySuite")
        require(not suite.vercel_log.exists(), "dry run invoked the Vercel executable")
        require(fingerprint_tree(suite.project) == before, "dry run changed project files")

    suite.case("deployment dry run is read-only and offline", dry_run_case)

    def wrong_deploy_confirmation_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run("deploy", PROJECT_NAME, "--confirm", "deploy", environment=fake_environment)
        suite.expect(result, 1, "confirmation must be exactly 'DEPLOY'")
        require(not suite.vercel_log.exists(), "wrong confirmation invoked Vercel")
        require(fingerprint_tree(suite.project) == before, "wrong confirmation changed project files")

    suite.case("deployment requires the exact confirmation", wrong_deploy_confirmation_case)

    def unauthenticated_deploy_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run("deploy", PROJECT_NAME, "--confirm", "DEPLOY", environment=fake_environment)
        suite.expect(result, 1, "Vercel CLI is not authenticated")
        invocations = suite.vercel_log.read_text(encoding="utf-8").splitlines()
        require(any(line.startswith("whoami ") for line in invocations), "authentication was not checked")
        require(not any(line.startswith("deploy ") for line in invocations), "deployment ran after failed authentication")
        require(fingerprint_tree(suite.project) == before, "failed authentication changed project files")

    suite.case("deployment stops safely when authentication fails", unauthenticated_deploy_case)

    rollback_target = "dpl_PreviousFactorySuite"
    inspected_environment = {**fake_environment, "FACTORY_TEST_VERCEL_MODE": "inspect"}
    mismatch_environment = {**fake_environment, "FACTORY_TEST_VERCEL_MODE": "mismatch"}
    missing_org_environment = {**fake_environment, "FACTORY_TEST_VERCEL_MODE": "missing-org"}
    wrong_url_environment = {**fake_environment, "FACTORY_TEST_VERCEL_MODE": "wrong-url"}

    def undeployed_rollback_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            rollback_target,
            "--dry-run",
            environment=inspected_environment,
        )
        suite.expect(result, 1, "expected Deployed")
        require(not suite.vercel_log.exists(), "Vercel was invoked for a project that is not deployed")
        require(fingerprint_tree(suite.project) == before, "refused rollback changed project files")

    suite.case("rollback requires a Deployed project", undeployed_rollback_case)
    write_text(suite.status_file, status_document("Deployed"))

    suite.case(
        "deployed project validates before rollback",
        lambda: suite.expect(suite.run("validate-stage", PROJECT_NAME), 0, "Deployed", "PASSED:"),
    )

    def unsafe_target_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            "https://suite-previous.vercel.app/path?unexpected=yes",
            "--dry-run",
            environment=inspected_environment,
        )
        suite.expect(result, 1, "plain HTTPS deployment URL")
        require(not suite.vercel_log.exists(), "invalid target invoked Vercel")

    suite.case("rollback rejects ambiguous target URLs", unsafe_target_case)

    def wrong_rollback_confirmation_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            rollback_target,
            "--confirm",
            "rollback",
            environment=inspected_environment,
        )
        suite.expect(result, 1, "confirmation must be exactly 'ROLLBACK'")
        require(not suite.vercel_log.exists(), "wrong rollback confirmation invoked Vercel")
        require(fingerprint_tree(suite.project) == before, "wrong confirmation changed project files")

    suite.case("rollback requires the exact confirmation", wrong_rollback_confirmation_case)

    def mismatched_target_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            rollback_target,
            "--dry-run",
            environment=mismatch_environment,
        )
        suite.expect(result, 1, "belongs to a different Vercel project")
        invocations = suite.vercel_log.read_text(encoding="utf-8").splitlines()
        require(any(line.startswith("api ") for line in invocations), "rollback target was not inspected")
        require(not any(line.startswith("rollback ") for line in invocations), "mismatched target was rolled back")
        require(fingerprint_tree(suite.project) == before, "target mismatch changed project files")

    suite.case("rollback rejects a deployment from another project", mismatched_target_case)

    def missing_organization_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            rollback_target,
            "--dry-run",
            environment=missing_org_environment,
        )
        suite.expect(result, 1, "belongs to a different Vercel organization")
        invocations = suite.vercel_log.read_text(encoding="utf-8").splitlines()
        require(not any(line.startswith("rollback ") for line in invocations), "unscoped target was rolled back")
        require(fingerprint_tree(suite.project) == before, "missing organization changed project files")

    suite.case("rollback requires matching organization evidence", missing_organization_case)

    def mismatched_url_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            "https://suite-previous.vercel.app",
            "--dry-run",
            environment=wrong_url_environment,
        )
        suite.expect(result, 1, "returned a different deployment")
        invocations = suite.vercel_log.read_text(encoding="utf-8").splitlines()
        require(not any(line.startswith("rollback ") for line in invocations), "mismatched URL was rolled back")
        require(fingerprint_tree(suite.project) == before, "URL mismatch changed project files")

    suite.case("rollback requires an exact deployment URL match", mismatched_url_case)

    def rollback_dry_run_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            rollback_target,
            "--dry-run",
            environment=inspected_environment,
        )
        suite.expect(
            result,
            0,
            "Rollback dry run",
            "DRY RUN PASSED",
            rollback_target,
            "prj_FactorySuite",
        )
        invocations = suite.vercel_log.read_text(encoding="utf-8").splitlines()
        require(any(line.startswith("whoami ") for line in invocations), "authentication was not checked")
        require(any(line.startswith("api ") for line in invocations), "rollback target was not inspected")
        require(not any(line.startswith("rollback ") for line in invocations), "dry run requested a rollback")
        require(fingerprint_tree(suite.project) == before, "rollback dry run changed project files")

    suite.case("rollback dry run inspects the exact target without mutation", rollback_dry_run_case)

    def failed_rollback_case():
        if suite.vercel_log.exists():
            suite.vercel_log.unlink()
        before = fingerprint_tree(suite.project)
        result = suite.run(
            "rollback",
            PROJECT_NAME,
            rollback_target,
            "--confirm",
            "ROLLBACK",
            environment=inspected_environment,
        )
        suite.expect(result, 1, "ROLLBACK REQUIRES ATTENTION")
        invocations = suite.vercel_log.read_text(encoding="utf-8").splitlines()
        require(any(line.startswith(f"rollback {rollback_target} ") for line in invocations), "rollback was not requested")
        require(fingerprint_tree(suite.project) == before, "failed rollback changed local records")

    suite.case("rollback surfaces unknown remote state without local changes", failed_rollback_case)

    def successful_rollback_record_case():
        module_path = suite.root / "tools" / "deployment-adapter.py"
        specification = importlib.util.spec_from_file_location("factory_deployment_adapter_test", module_path)
        require(specification is not None and specification.loader is not None, "adapter could not be loaded")
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)

        calls = []
        original_which = module.shutil.which
        original_run_vercel = module.run_vercel
        original_verify = module.verify_deployment

        def fake_run_vercel(command, link, timeout=None):
            calls.append(command)
            if command[1] == "api":
                payload = {
                    "id": rollback_target,
                    "url": "suite-previous.vercel.app",
                    "projectId": "prj_FactorySuite",
                    "team": {"id": "team_FactorySuite"},
                    "readyState": "READY",
                    "target": "production",
                }
                return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")
            return SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

        try:
            module.shutil.which = lambda command: "/fake/vercel" if command == "vercel" else original_which(command)
            module.run_vercel = fake_run_vercel
            module.verify_deployment = lambda url: (200, url)
            module.rollback(PROJECT_NAME, suite.project, rollback_target, "ROLLBACK")
        finally:
            module.shutil.which = original_which
            module.run_vercel = original_run_vercel
            module.verify_deployment = original_verify

        rollback_calls = [command for command in calls if len(command) > 1 and command[1] == "rollback"]
        require(any(command[2] == rollback_target for command in rollback_calls), "rollback command was not issued")
        require(any("--non-interactive" in command for command in rollback_calls), "rollback was interactive")
        deployment_record = suite.deployment_file.read_text(encoding="utf-8")
        status_record = suite.status_file.read_text(encoding="utf-8")
        require(f"**Restored deployment:** `{rollback_target}`" in deployment_record, "rollback was not recorded")
        require("HTTP 200" in deployment_record, "production verification was not recorded")
        require("\nDeployed\n" in status_record, "rollback changed the deployed workflow stage")

    suite.case("verified rollback is recorded while staying Deployed", successful_rollback_record_case)
    suite.case(
        "rollback record still passes deployed-stage validation",
        lambda: suite.expect(suite.run("validate-stage", PROJECT_NAME), 0, "Deployed", "PASSED:"),
    )

    suite.case(
        "check accepts a valid static site",
        lambda: suite.expect(suite.run("check", PROJECT_NAME), 0, "PASSED:"),
    )

    def broken_link_case():
        index_file = suite.project / "src" / "index.html"
        original = index_file.read_text(encoding="utf-8")
        write_text(index_file, original.replace('href="#main"', 'href="missing.html"'))
        try:
            suite.expect(suite.run("check", PROJECT_NAME), 1, "missing local file", "FAILED")
        finally:
            write_text(index_file, original)

    suite.case("check reports a broken local link", broken_link_case)
    suite.case("preview serves only the isolated site", suite.preview_works)

    def secret_scan_clean_case():
        result = suite.run("scan-secrets", PROJECT_NAME)
        suite.expect(result, 0, "PASSED: secret scan is clean", "No secret values were displayed")

    suite.case("secret scan passes a clean project", secret_scan_clean_case)

    def secret_scan_detects_key_case():
        planted = suite.project / "src" / "leaked.js"
        secret_value = "sk-proj-" + ("B" * 48)
        write_text(planted, f"const token = '{secret_value}';\n")
        try:
            result = suite.run("scan-secrets", PROJECT_NAME)
            suite.expect(result, 1, "possible OpenAI API key", "No secret values were displayed")
            require(secret_value not in result.output, "secret scanner printed a secret value")
        finally:
            if planted.exists():
                planted.unlink()

    suite.case("secret scan reports a planted key without printing it", secret_scan_detects_key_case)

    def website_type_case():
        typed_project = "typed-project"
        result = suite.run("create", typed_project, "--type", "restaurant")
        suite.expect(result, 0, "Project created successfully", "Website type starting point applied: restaurant")
        brief = (suite.root / "projects" / typed_project / "PROJECT-BRIEF.md").read_text(encoding="utf-8")
        require(
            "Website Type Starting Point — Restaurant" in brief,
            "website-type starter content was not appended to the brief",
        )
        require(
            "Reservation request" in brief,
            "restaurant starter's suggested features were not appended to the brief",
        )
        after_validate = suite.run("validate-brief", typed_project)
        require(
            "Traceback" not in after_validate.output,
            "validate-brief crashed on a brief with appended website-type content",
        )

    suite.case("create applies a website-type starting point", website_type_case)

    def invalid_website_type_case():
        result = suite.run("create", "typed-project-invalid", "--type", "not-a-real-type")
        suite.expect(result, 1, "unknown website type", "restaurant")
        require(
            not (suite.root / "projects" / "typed-project-invalid").exists(),
            "an invalid website type still created a project directory",
        )

    suite.case("create rejects an unknown website type", invalid_website_type_case)

    def local_backend_case():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        base = f"http://127.0.0.1:{port}"

        # Never let a real key from the developer's shell reach this test: it
        # must stay fully offline and never contact Anthropic, Vercel's
        # registrar API, or trigger any real, paid call.
        no_external_key_environment = dict(suite.environment)
        no_external_key_environment.pop("ANTHROPIC_API_KEY", None)
        no_external_key_environment.pop("VERCEL_TOKEN", None)
        no_external_key_environment.pop("VERCEL_TEAM_ID", None)
        no_external_key_environment.pop("SQUARE_ACCESS_TOKEN", None)
        no_external_key_environment.pop("SQUARE_LOCATION_ID", None)
        no_external_key_environment.pop("SQUARE_ENVIRONMENT", None)

        process = subprocess.Popen(
            [str(suite.factory), "frontend", str(port)],
            cwd=suite.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=no_external_key_environment,
        )

        last_response_headers = {}

        def request(method, path, payload=None, headers=None):
            data = json.dumps(payload).encode("utf-8") if payload is not None else None
            req = Request(base + path, data=data, method=method)
            if data is not None:
                req.add_header("Content-Type", "application/json")
            for name, value in (headers or {}).items():
                req.add_header(name, value)
            try:
                with urlopen(req, timeout=2) as response:
                    last_response_headers.clear()
                    last_response_headers.update(response.headers.items())
                    return response.status, json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                last_response_headers.clear()
                last_response_headers.update(error.headers.items())
                return error.code, json.loads(error.read().decode("utf-8"))

        try:
            deadline = time.monotonic() + 8
            ready = False
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    status, body = request("GET", "/api/health")
                    ready = status == 200 and body.get("status") == "ok"
                    if ready:
                        break
                except (URLError, TimeoutError, OSError):
                    time.sleep(0.05)

            if not ready:
                output = process.communicate(timeout=3)[0] if process.poll() is None else ""
                raise TestFailure(f"local backend did not become healthy\n{output[-1200:]}")

            with urlopen(base + "/", timeout=2) as response:
                index_status = response.status
                index_body = response.read().decode("utf-8")
            require(index_status == 200, "backend did not serve the frontend index page")
            require("Website Factory App" in index_body, "backend served unexpected content at /")

            status, body = request(
                "POST",
                "/api/projects",
                {
                    "name": "Backend Test Cafe",
                    "brief": "A test business created by the isolated suite.",
                    "who": ["Local walk-ins"],
                    "action": "Book a slot",
                    "extras": ["Price list"],
                },
            )
            require(status == 201, f"project creation failed: {status} {body}")
            require(body.get("slug") == "backend-test-cafe", f"unexpected slug: {body}")

            brief_file = suite.root / "projects" / "backend-test-cafe" / "PROJECT-BRIEF.md"
            require(brief_file.is_file(), "backend did not create a real project via init-project.sh")
            brief_text = brief_file.read_text(encoding="utf-8")
            require(
                "Customer-Submitted Intake (unverified)" in brief_text and "Backend Test Cafe" in brief_text,
                "backend did not append the customer intake summary to the brief",
            )

            status, body = request("GET", "/api/projects/backend-test-cafe/status")
            require(status == 200, f"status lookup failed: {status} {body}")
            require(body.get("stage") == "Intake", f"unexpected stage: {body}")

            status, body = request("POST", "/api/projects", {"name": "Backend Test Cafe"})
            require(status == 409, f"duplicate project creation should be rejected: {status} {body}")

            status, body = request("GET", "/api/projects/does-not-exist/status")
            require(status == 404, f"missing project status should 404: {status} {body}")

            status, body = request("GET", "/api/projects/..%2f..%2fetc/status")
            require(status == 400, f"path-traversal slug should be rejected: {status} {body}")

            status, body = request("POST", "/api/projects", {"name": "!!!"})
            require(status == 400, f"unslugifiable name should be rejected: {status} {body}")

            status, body = request("POST", "/api/projects", {})
            require(status == 400, f"missing name should be rejected: {status} {body}")

            # /api/generate must fail closed (never fabricate copy) when no
            # ANTHROPIC_API_KEY is configured, which is guaranteed above. This
            # first call is request 1 of the endpoint's 5-per-minute limit.
            status, body = request("POST", "/api/generate", {"name": "Test Cafe", "brief": "coffee"})
            require(status == 503, f"generate without a configured key should fail closed: {status} {body}")
            require(
                "ANTHROPIC_API_KEY" in (body.get("error") or ""),
                f"unconfigured-key error should name the required variable: {body}",
            )

            # local_backend.py limits /api/generate to 5 requests/minute; the
            # call above was request 1, so 4 more (requests 2-5) should still
            # be allowed through to the fail-closed check, and the 6th must
            # be rate-limited instead.
            for _ in range(4):
                status, _ = request("POST", "/api/generate", {"name": "x"})
                require(status == 503, "expected requests within the limit to still reach the fail-closed check")
            status, body = request("POST", "/api/generate", {"name": "x"})
            require(status == 429, f"generate should apply its own strict rate limit: {status} {body}")

            # Providing 'copy' directly (without needing a real Anthropic call)
            # exercises the draft-site renderer, including real multi-page
            # generation and HTML-escaping of a deliberately malicious
            # payload on both the home page and a secondary nav page. Exactly
            # 3 nav items (matching MAX_NAV_PAGES, so the slice limit doesn't
            # also mask the effect being tested): "Empty" has no body and
            # must NOT become a page; "Menu" and "menu!" deliberately slugify
            # to the same value and must be deduplicated, not overwrite each
            # other.
            status, body = request(
                "POST",
                "/api/projects",
                {
                    "name": "Draft Site Cafe",
                    "copy": {
                        "kicker": "Fresh",
                        "title": "<script>alert(1)</script>",
                        "body": "<img src=x onerror=alert(2)>",
                        "ctaLabel": "Order now",
                        "nav": [
                            {"label": "Empty", "body": ""},
                            {"label": "Menu", "body": "What's on the menu today."},
                            {"label": "menu!", "body": "<svg onload=alert(5)>A second, colliding menu label."},
                        ],
                        "services": [{"title": "<svg onload=alert(3)>", "body": "test", "price": "$1"}],
                        "closeTitle": "Come by",
                        "closeNote": "Open daily.",
                        "palette": {"accent": "javascript:alert(4)"},
                    },
                },
            )
            require(status == 201, f"project creation with copy failed: {status} {body}")
            require(body.get("draftSiteGenerated") is True, f"expected a draft site to be generated: {body}")
            # index.html + Menu + menu! (deduplicated); "Empty" is skipped
            # since it has no body content to build a page from.
            require(body.get("draftPagesGenerated") == 3, f"expected 3 generated pages: {body}")

            src_dir = suite.root / "projects" / "draft-site-cafe" / "src"
            site_file = src_dir / "index.html"
            require(site_file.is_file(), "draft site index.html was not written")
            site_html = site_file.read_text(encoding="utf-8")
            # The attribute text (e.g. "onerror=alert(2)") legitimately survives
            # as inert escaped text content — html.escape() only neutralizes the
            # surrounding angle brackets, which is what actually matters here.
            require("<script>alert(1)</script>" not in site_html, "draft site did not escape a script tag payload")
            require("<img src=x onerror=alert(2)>" not in site_html, "draft site left an executable <img onerror> tag unescaped")
            require("<svg onload=alert(3)>" not in site_html, "draft site left an executable <svg onload> tag unescaped")
            require("javascript:alert(4)" not in site_html, "draft site accepted an unsafe palette color value")
            require("&lt;script&gt;" in site_html, "expected the escaped title to still appear in the page")
            require("onerror=alert(2)" in site_html, "expected the neutralized payload text to still render as inert content")
            require('<a href="menu.html">Menu</a>' in site_html, f"expected the home page nav to link to the real built page:\n{site_html}")
            require(
                "Empty" not in site_html.split('aria-label="Primary"')[1].split("</nav>")[0],
                "the empty-body nav item should not appear as a built page link",
            )

            menu_file = src_dir / "menu.html"
            menu_2_file = src_dir / "menu-2.html"
            require(menu_file.is_file(), "the Menu nav page was not written")
            require(menu_2_file.is_file(), "the colliding 'menu!' slug should be deduplicated to menu-2.html, not dropped")
            require(
                not (src_dir / "empty.html").exists(),
                "the empty-body nav item should not have produced a page file",
            )

            menu_2_html = menu_2_file.read_text(encoding="utf-8")
            require("<svg onload=alert(5)>" not in menu_2_html, "a secondary page left an executable <svg onload> tag unescaped")
            require("onload=alert(5)" in menu_2_html, "expected the neutralized payload text to still render on the secondary page")
            require(
                '<span class="nav-current">' in menu_2_html and 'href="index.html">Home</a>' in menu_2_html,
                "expected the secondary page's own nav to mark itself current and link back home",
            )

            shutil.rmtree(suite.root / "projects" / "draft-site-cafe", ignore_errors=True)

            # /api/domains/check must fail closed (never fabricate
            # availability/price) when no VERCEL_TOKEN is configured, which
            # is guaranteed by no_external_key_environment above.
            status, body = request("GET", "/api/domains/check?name=example.com")
            require(status == 503, f"domain check without a configured token should fail closed: {status} {body}")
            require(
                "VERCEL_TOKEN" in (body.get("error") or ""),
                f"unconfigured-token error should name the required variable: {body}",
            )

            status, body = request("GET", "/api/domains/check?name=not_a_valid_domain")
            require(status == 503, f"format validation runs after the token check: {status} {body}")

            # /api/checkout must fail closed (never create a real order or
            # imply a checkout is available) when Square isn't configured,
            # which is guaranteed by no_external_key_environment above.
            status, body = request("POST", "/api/checkout", {"plan": "once"})
            require(status == 503, f"checkout without Square configured should fail closed: {status} {body}")
            require(
                "SQUARE_ACCESS_TOKEN" in (body.get("error") or ""),
                f"unconfigured-checkout error should name the required variable: {body}",
            )

            status, body = request("GET", "/api/checkout/verify?orderId=abc123")
            require(status == 503, f"verify without Square configured should fail closed: {status} {body}")

            # The Studio subscription checkout must also fail closed the
            # same way when Square isn't configured at all.
            status, body = request("POST", "/api/checkout", {"plan": "studio"})
            require(status == 503, f"studio checkout without Square configured should fail closed: {status} {body}")

            status, body = request("GET", "/api/checkout/verify?plan=studio")
            require(status == 503, f"studio verify without Square configured should fail closed: {status} {body}")

            # Real accounts: signup, /api/auth/me, duplicate rejection, wrong
            # password, and logout — all against the sandboxed
            # .factory-users.db this backend process created for this test
            # run only, never a shared or real database.
            status, body = request("POST", "/api/auth/signup", {"email": "not-an-email", "password": "long-enough-1"})
            require(status == 400, f"signup should reject an invalid email: {status} {body}")

            status, body = request("POST", "/api/auth/signup", {"email": "owner@example.com", "password": "short"})
            require(status == 400, f"signup should reject a too-short password: {status} {body}")

            status, body = request(
                "POST", "/api/auth/signup", {"email": "Owner@Example.com", "password": "a-strong-password"}
            )
            require(status == 200, f"signup should succeed with a valid email and password: {status} {body}")
            require(body.get("email") == "owner@example.com", f"signup should normalize and return the email: {body}")
            session_cookie = last_response_headers.get("Set-Cookie")
            require(session_cookie, "signup should set a session cookie")
            session_cookie = session_cookie.split(";")[0]

            status, body = request(
                "POST", "/api/auth/signup", {"email": "owner@example.com", "password": "a-strong-password"}
            )
            require(status == 409, f"signup should reject a duplicate email: {status} {body}")

            status, body = request("GET", "/api/auth/me", headers={"Cookie": session_cookie})
            require(
                status == 200 and body.get("email") == "owner@example.com",
                f"me should reflect the signed-in account: {status} {body}",
            )

            status, body = request("GET", "/api/auth/me")
            require(status == 401, f"me without a session cookie should be rejected: {status} {body}")

            status, body = request(
                "POST", "/api/auth/login", {"email": "owner@example.com", "password": "wrong-password"}
            )
            require(status == 401, f"login should reject a wrong password: {status} {body}")

            status, body = request(
                "POST", "/api/auth/login", {"email": "owner@example.com", "password": "a-strong-password"}
            )
            require(status == 200, f"login should succeed with the correct password: {status} {body}")

            status, body = request("POST", "/api/auth/logout", headers={"Cookie": session_cookie})
            require(status == 200, f"logout should succeed: {status} {body}")

            status, body = request("GET", "/api/auth/me", headers={"Cookie": session_cookie})
            require(status == 401, f"me should be rejected after logout: {status} {body}")
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=3)
            shutil.rmtree(suite.root / "projects" / "backend-test-cafe", ignore_errors=True)

    suite.case(
        "local backend serves the frontend, a validated project API, and fail-closed generation",
        local_backend_case,
    )

    def studio_subscription_login_gate_case():
        # With Square fully "configured" (dummy sandbox values only — never
        # real credentials), starting or verifying a Studio checkout must
        # still be rejected before any network call if the requester isn't
        # signed in. The login check happens before any Square API call, so
        # this never reaches the network regardless of the fake token.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        base = f"http://127.0.0.1:{port}"

        environment = dict(suite.environment)
        environment.pop("ANTHROPIC_API_KEY", None)
        environment.pop("VERCEL_TOKEN", None)
        environment.pop("VERCEL_TEAM_ID", None)
        environment["SQUARE_ACCESS_TOKEN"] = "test-sandbox-token"
        environment["SQUARE_LOCATION_ID"] = "test-location-id"
        environment["SQUARE_SUBSCRIPTION_PLAN_VARIATION_ID"] = "test-plan-variation-id"
        environment["SQUARE_ENVIRONMENT"] = "sandbox"

        process = subprocess.Popen(
            [str(suite.factory), "frontend", str(port)],
            cwd=suite.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=environment,
        )

        def request(method, path, payload=None):
            data = json.dumps(payload).encode("utf-8") if payload is not None else None
            req = Request(base + path, data=data, method=method)
            if data is not None:
                req.add_header("Content-Type", "application/json")
            try:
                with urlopen(req, timeout=2) as response:
                    return response.status, json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                return error.code, json.loads(error.read().decode("utf-8"))

        try:
            deadline = time.monotonic() + 8
            ready = False
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    status, body = request("GET", "/api/health")
                    ready = status == 200 and body.get("status") == "ok"
                    if ready:
                        break
                except (URLError, TimeoutError, OSError):
                    time.sleep(0.05)

            if not ready:
                output = process.communicate(timeout=3)[0] if process.poll() is None else ""
                raise TestFailure(f"local backend did not become healthy\n{output[-1200:]}")

            status, body = request("POST", "/api/checkout", {"plan": "studio"})
            require(status == 401, f"studio checkout without signing in should be rejected: {status} {body}")

            status, body = request("GET", "/api/checkout/verify?plan=studio")
            require(status == 401, f"studio verify without signing in should be rejected: {status} {body}")
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=3)

    suite.case(
        "studio subscription checkout requires signing in even when Square is configured",
        studio_subscription_login_gate_case,
    )

    def buy_domain_safety_case():
        # Every path here must be rejected before any real Vercel call or
        # spend could occur — this test never provides a valid token, contact
        # file, or reaches the confirmation stage with correct arguments.
        #
        # suite.run()'s `environment` kwarg is MERGED onto the developer's
        # real environment (dict.update()), not a replacement — an inherited
        # real VERCEL_TOKEN would survive a naive {} override. Explicitly set
        # both to empty strings so the effective value is always falsy,
        # regardless of what the developer's own shell has exported.
        no_vercel = {"VERCEL_TOKEN": "", "VERCEL_TEAM_ID": ""}
        with_fake_token = {"VERCEL_TOKEN": "fake-test-token", "VERCEL_TEAM_ID": ""}

        result = suite.run("buy-domain", PROJECT_NAME, "example.com", "--dry-run", environment=no_vercel)
        suite.expect(result, 1, "VERCEL_TOKEN is not set")

        result = suite.run(
            "buy-domain", "does-not-exist-project", "example.com", "--dry-run", environment=with_fake_token,
        )
        suite.expect(result, 1, "does not exist")

        result = suite.run(
            "buy-domain", PROJECT_NAME, "not_a_valid_domain", "--dry-run", environment=with_fake_token,
        )
        suite.expect(result, 1, "not a valid domain name")

        result = suite.run(
            "buy-domain", PROJECT_NAME, "example.com", "--confirm", "WRONG", "--expected-price", "12.99",
            environment=no_vercel,
        )
        suite.expect(result, 1, "confirmation must be exactly 'PURCHASE'")

        # Correct confirmation, but still no VERCEL_TOKEN and no contact
        # file: must stop before any purchase, never reach the network.
        result = suite.run(
            "buy-domain", PROJECT_NAME, "example.com", "--confirm", "PURCHASE", "--expected-price", "12.99",
            environment=no_vercel,
        )
        suite.expect(result, 1, "VERCEL_TOKEN is not set")
        require(
            "orderId" not in result.output and "Domain registered" not in result.output,
            "buy-domain must never report success without a real token",
        )

    suite.case("buy-domain rejects every unsafe path before any purchase could occur", buy_domain_safety_case)


def main():
    real_projects = FACTORY_ROOT / "projects"
    before = fingerprint_tree(real_projects)
    suite = None

    print("Factory regression suite")
    print("  Mode: isolated temporary project")
    print("  Production deployment: disabled")

    try:
        with tempfile.TemporaryDirectory(prefix="ai-website-factory-tests-") as temporary_directory:
            sandbox_root = Path(temporary_directory) / "factory"
            sandbox_root.mkdir()
            copy_factory(sandbox_root)
            suite = FactorySuite(sandbox_root)
            run_suite(suite)
    except Exception as error:
        if suite is None:
            print(f"  [FAIL] suite setup: {error}")
            failures = [("suite setup", str(error))]
            passed = 0
        else:
            suite.failures.append(("suite execution", str(error)))
            print("  [FAIL] suite execution")
            failures = suite.failures
            passed = suite.passed
    else:
        failures = suite.failures
        passed = suite.passed

    if fingerprint_tree(real_projects) == before:
        passed += 1
        print("  [PASS] real projects remain unchanged")
    else:
        failures.append(("real projects remain unchanged", "the real projects tree changed during the suite"))
        print("  [FAIL] real projects remain unchanged")

    print()
    if failures:
        print(f"FAILED: {len(failures)} of {passed + len(failures)} tests failed.", file=sys.stderr)
        for name, detail in failures:
            print(f"  - {name}: {detail}", file=sys.stderr)
        print("No production deployment was performed.", file=sys.stderr)
        return 1

    print(f"PASSED: all {passed} factory tests succeeded.")
    print("Real projects were unchanged. No production deployment was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
