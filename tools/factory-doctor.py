#!/usr/bin/env python3

"""Run read-only health checks for the AI Website Factory."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


FACTORY_ROOT = Path(__file__).resolve().parent.parent
MINIMUM_PYTHON = (3, 8)

REQUIRED_DIRECTORIES = (
    "agents",
    "documentation",
    "projects",
    "templates",
    "tools",
    "workflows",
)

REQUIRED_FILES = (
    "CLAUDE.md",
    "README.md",
    "factory",
    "templates/PROJECT-BRIEF.md",
    "templates/PROJECT-STRUCTURE.md",
    "templates/site-draft/index.html.tmpl",
    "tools/check-project.py",
    "tools/deployment-adapter.py",
    "tools/factory-doctor.py",
    "tools/factory_stages.py",
    "tools/init-project.sh",
    "tools/local_backend.py",
    "tools/project-intake.py",
    "tools/preview-server.py",
    "tools/project-status.py",
    "tools/secret_scan.py",
    "tools/test-factory.py",
    "tools/validate-brief.py",
    "tools/validate-release.py",
    "tools/validate-stage.py",
    "tools/workflow-controller.py",
    "templates/security/nextjs/middleware.ts",
    "templates/security/nextjs/lib/security.ts",
    "templates/security/nextjs/lib/rate-limit.ts",
    "templates/security/nextjs/lib/with-secure-route.ts",
    ".env.example",
    "workflows/WEBSITE-BUILD.md",
)

REQUIRED_AGENT_FILES = (
    "agents/Frontend-developer/AGENT.md",
    "agents/accessibility-specialist/AGENT.md",
    "agents/backend-developer/AGENT.md",
    "agents/debug-fixer/AGENT.md",
    "agents/performance-optimizer/AGENT.md",
    "agents/project-orchestrator/AGENT.md",
    "agents/qa-tester/AGENT.md",
    "agents/security-auditor/AGENT.md",
    "agents/seo-content/AGENT.md",
    "agents/ui-ux-designer/AGENT.md",
    "agents/website-architect/AGENT.md",
)

EXECUTABLE_FILES = (
    "factory",
    "tools/init-project.sh",
)

PROJECT_DIRECTORIES = (
    "architecture",
    "design",
    "design/assets",
    "documentation",
    "reports",
    "src",
    "tests",
)

PROJECT_FILES = (
    "PROJECT-BRIEF.md",
    "PROJECT-STATUS.md",
    "README.md",
    "architecture/ARCHITECTURE.md",
    "design/UI-UX-SPEC.md",
    "documentation/CHANGELOG.md",
    "documentation/DEPLOYMENT.md",
    "documentation/DEVELOPMENT.md",
    "reports/ACCESSIBILITY-REPORT.md",
    "reports/PERFORMANCE-REPORT.md",
    "reports/QA-REPORT.md",
    "reports/SECURITY-REPORT.md",
    "reports/SEO-REPORT.md",
)


class Results:
    def __init__(self):
        self.items = []

    def passed(self, message):
        self.items.append(("PASS", message))

    def warned(self, message):
        self.items.append(("WARN", message))

    def failed(self, message):
        self.items.append(("FAIL", message))

    def info(self, message):
        self.items.append(("INFO", message))

    @property
    def failures(self):
        return [message for level, message in self.items if level == "FAIL"]

    @property
    def warnings(self):
        return [message for level, message in self.items if level == "WARN"]

    def display(self):
        print("AI Website Factory doctor")
        print("  Mode: read-only; no installs, authentication, or network checks")
        for level, message in self.items:
            print(f"  [{level}] {message}")

        print()
        if self.failures:
            print(
                f"UNHEALTHY: {len(self.failures)} required check(s) failed; "
                f"{len(self.warnings)} warning(s).",
                file=sys.stderr,
            )
            print("No files were changed and no network service was contacted.", file=sys.stderr)
            return 1

        if self.warnings:
            print(f"HEALTHY WITH WARNINGS: all required checks passed; {len(self.warnings)} warning(s).")
        else:
            print("HEALTHY: all required checks passed.")
        print("No files were changed and no network service was contacted.")
        return 0


def comma_separated(values):
    return ", ".join(str(value) for value in values)


def check_runtime(results):
    version = sys.version_info[:3]
    if version[:2] < MINIMUM_PYTHON:
        results.failed(
            f"Python {version[0]}.{version[1]}.{version[2]} is too old; "
            f"Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}+ is required"
        )
    else:
        results.passed(f"Python {version[0]}.{version[1]}.{version[2]} is available")

    bash = shutil.which("bash")
    if bash:
        results.passed("Bash is available for the factory launcher")
    else:
        results.failed("Bash is unavailable; the ./factory launcher cannot run")

    git = shutil.which("git")
    if not git:
        results.failed("Git is unavailable")
    else:
        try:
            repository = subprocess.run(
                [git, "-C", str(FACTORY_ROOT), "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            results.failed("Git could not inspect the factory repository")
        else:
            reported_root = repository.stdout.strip()
            if repository.returncode != 0 or not reported_root:
                results.failed("The factory root is not inside a Git working tree")
            elif Path(reported_root).resolve() != FACTORY_ROOT.resolve():
                results.failed(f"Git reports a different repository root: {reported_root}")
            else:
                results.passed("Git is available and the factory repository root is valid")

    if shutil.which("node"):
        results.passed("Node.js is available for checking JavaScript projects")
    else:
        results.warned("Node.js is unavailable; JavaScript syntax checks will be skipped")

    if shutil.which("vercel"):
        results.passed("Vercel CLI is available for explicitly authorized production actions")
    else:
        results.warned("Vercel CLI is unavailable; local factory workflows still work")


def check_factory_structure(results):
    missing_directories = []
    unsafe_directories = []
    for relative_path in REQUIRED_DIRECTORIES:
        path = FACTORY_ROOT / relative_path
        if path.is_symlink():
            unsafe_directories.append(relative_path)
        elif not path.is_dir():
            missing_directories.append(relative_path)

    if missing_directories:
        results.failed(f"Required factory directories are missing: {comma_separated(missing_directories)}")
    if unsafe_directories:
        results.failed(f"Required factory directories must not be symbolic links: {comma_separated(unsafe_directories)}")
    if not missing_directories and not unsafe_directories:
        results.passed(f"All {len(REQUIRED_DIRECTORIES)} required factory directories are present")

    missing_files = []
    unsafe_files = []
    unreadable_files = []
    required_files = REQUIRED_FILES + REQUIRED_AGENT_FILES
    for relative_path in required_files:
        path = FACTORY_ROOT / relative_path
        if path.is_symlink():
            unsafe_files.append(relative_path)
        elif not path.is_file():
            missing_files.append(relative_path)
        else:
            try:
                if not path.read_bytes():
                    unreadable_files.append(f"{relative_path} (empty)")
            except OSError:
                unreadable_files.append(f"{relative_path} (unreadable)")

    if missing_files:
        results.failed(f"Required factory files are missing: {comma_separated(missing_files)}")
    if unsafe_files:
        results.failed(f"Required factory files must not be symbolic links: {comma_separated(unsafe_files)}")
    if unreadable_files:
        results.failed(f"Required factory files are unusable: {comma_separated(unreadable_files)}")
    if not missing_files and not unsafe_files and not unreadable_files:
        results.passed(f"All {len(required_files)} required factory and agent files are usable")

    non_executable = [
        relative_path
        for relative_path in EXECUTABLE_FILES
        if not os.access(FACTORY_ROOT / relative_path, os.X_OK)
    ]
    if non_executable:
        results.failed(f"Required launchers are not executable: {comma_separated(non_executable)}")
    else:
        results.passed("Factory launchers have executable permissions")


def read_status_stage(status_file):
    try:
        lines = status_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None, "PROJECT-STATUS.md is unreadable"

    try:
        heading_index = lines.index("## Current Stage")
    except ValueError:
        return None, "PROJECT-STATUS.md is missing the Current Stage section"

    for line in lines[heading_index + 1:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped:
            return stripped, None
    return None, "PROJECT-STATUS.md has an empty Current Stage section"


def vercel_link_error(project_directory):
    candidates = (
        project_directory / ".vercel" / "project.json",
        project_directory / "src" / ".vercel" / "project.json",
    )
    configured = []
    for candidate in candidates:
        if candidate.parent.is_symlink() or candidate.is_symlink():
            return None, f"{candidate.relative_to(project_directory)} must not be a symbolic link"
        if candidate.exists():
            configured.append(candidate)

    if not configured:
        return False, None
    if len(configured) > 1:
        return None, "multiple Vercel project links are configured"

    link_file = configured[0]
    if not link_file.is_file():
        return None, f"{link_file.relative_to(project_directory)} is not a regular file"
    try:
        link = json.loads(link_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, f"{link_file.relative_to(project_directory)} is unreadable or invalid"

    if not isinstance(link, dict) or not all(
        isinstance(link.get(key), str) and link[key].strip()
        for key in ("orgId", "projectId")
    ):
        return None, f"{link_file.relative_to(project_directory)} lacks organization or project identifiers"
    return True, None


def check_projects(results):
    projects_root = FACTORY_ROOT / "projects"
    try:
        entries = sorted(
            (path for path in projects_root.iterdir() if not path.name.startswith(".")),
            key=lambda path: path.name.lower(),
        )
    except OSError:
        results.failed("The projects directory could not be read")
        return

    if not entries:
        results.info("No projects yet; use './factory create <project-name>' when ready")
        results.info("Vercel links: none configured (optional until deployment)")
        return

    valid_projects = 0
    linked_projects = 0
    for project_directory in entries:
        name = project_directory.name
        project_errors = []
        if project_directory.is_symlink():
            results.failed(f"Project {name}: project directory must not be a symbolic link")
            continue
        if not project_directory.is_dir():
            results.failed(f"Unexpected item in projects/: {name} is not a directory")
            continue

        missing_directories = [
            relative_path
            for relative_path in PROJECT_DIRECTORIES
            if not (project_directory / relative_path).is_dir()
        ]
        missing_files = [
            relative_path
            for relative_path in PROJECT_FILES
            if not (project_directory / relative_path).is_file()
        ]
        unsafe_paths = [
            relative_path
            for relative_path in PROJECT_DIRECTORIES + PROJECT_FILES
            if (project_directory / relative_path).is_symlink()
        ]

        if missing_directories:
            project_errors.append(f"missing directories: {comma_separated(missing_directories)}")
        if missing_files:
            project_errors.append(f"missing files: {comma_separated(missing_files)}")
        if unsafe_paths:
            project_errors.append(f"symbolic links are not allowed for required paths: {comma_separated(unsafe_paths)}")

        status_file = project_directory / "PROJECT-STATUS.md"
        if status_file.is_file() and not status_file.is_symlink():
            stage, status_error = read_status_stage(status_file)
            if status_error:
                project_errors.append(status_error)
            elif stage:
                results.info(f"Project {name}: current stage is {stage}")

        linked, link_error = vercel_link_error(project_directory)
        if link_error:
            project_errors.append(link_error)
        elif linked:
            linked_projects += 1

        if project_errors:
            for error in project_errors:
                results.failed(f"Project {name}: {error}")
        else:
            valid_projects += 1

    if valid_projects == len(entries):
        results.passed(f"Projects: all {valid_projects} project scaffold(s) are structurally complete")
    elif valid_projects:
        results.passed(f"Projects: {valid_projects} of {len(entries)} project scaffold(s) are structurally complete")

    if linked_projects:
        results.passed(f"Vercel links: {linked_projects} valid project link(s)")
    else:
        results.info("Vercel links: none configured (optional until deployment)")


def main():
    if len(sys.argv) != 1:
        print("Usage: factory-doctor.py", file=sys.stderr)
        return 2

    results = Results()
    check_runtime(results)
    check_factory_structure(results)
    check_projects(results)
    return results.display()


if __name__ == "__main__":
    raise SystemExit(main())
