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
from urllib.error import URLError
from urllib.request import urlopen


FACTORY_ROOT = Path(__file__).resolve().parent.parent
PROJECT_NAME = "suite-project"

VALID_BRIEF = f"""# Project Brief

## 1. Project Information

**Project Name:** {PROJECT_NAME}
**Client / Brand:** Factory Test Brand
**Project Type:** Static marketing website
**Target Launch Date:** 2030-01-01

## 2. Project Goal

**Primary Goal:** Verify that factory commands work safely in isolation.

**Secondary Goals:**
- Confirm repeatable project setup and validation.
- Protect human approval and deployment boundaries.

## 3. Target Audience

**Primary Audience:** Factory maintainers testing local changes.
**Location / Market:** Internal development environment

**Audience Needs:**
- Clear command results and safe failure messages.
- Confidence that real projects remain unchanged.

## 4. Website Type

- [x] Landing Page
- [ ] Business Website

## 5. Required Pages

- [x] Home
- [ ] Contact

## 6. Required Features

- A semantic static page with local styling.
- A working in-page navigation link.

## 7. Branding

**Brand Name:** Factory Test Brand
**Logo Available:** No
**Primary Colors:** Navy and white
**Secondary Colors:** Neutral slate
**Typography:** System sans serif
**Brand Personality:** Clear, reliable, and practical

## 8. Design Direction

**Desired Style:** Minimal responsive technical interface

## 9. Content

**Content Provided By:** Factory maintainers

## 10. Technical Requirements

**Domain:** suite.invalid
**Hosting / Platform:** Vercel test target
**Frontend:** Semantic HTML and CSS
**Backend:** None required for this static test
**Database:** None required for this static test
**Third-Party Integrations:** None required for this static test

## 11. SEO Requirements

**Primary Keywords:** factory regression testing
**Target Location:** Internal development environment

## 12. Accessibility

The page uses semantic landmarks, visible text, and keyboard-accessible links.

## 13. Performance

The page is intentionally small and uses no remote runtime dependencies.

## 14. Deliverables

The deliverable is a disposable static site used only by this regression suite.

## 15. Constraints

**Budget:** Internal test allocation
**Deadline:** Complete during the local test run
**Platform Restrictions:** Standard-library tooling only
**Other Constraints:** Never touch a real project or production service

## 16. Human Approval

Production approval is intentionally handled by the workflow gate test.
"""

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
    for name in ("agents", "documentation", "templates", "tools", "workflows"):
        source = FACTORY_ROOT / name
        shutil.copytree(source, destination / name, symlinks=True, ignore=ignore)
    for name in ("factory", "CLAUDE.md", "README.md"):
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

    def run(self, *arguments, timeout=20, environment=None):
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
        output = ""
        try:
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    with urlopen(f"http://127.0.0.1:{port}/", timeout=0.5) as response:
                        body = response.read().decode("utf-8")
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


def run_suite(suite):
    fake_environment = suite.prepare_fake_vercel()

    def help_case():
        result = suite.run("--help")
        suite.expect(
            result,
            0,
            "./factory doctor",
            "./factory create",
            "./factory deploy",
            "./factory rollback",
            "./factory preview",
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

    write_text(suite.project / "PROJECT-BRIEF.md", VALID_BRIEF)
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
