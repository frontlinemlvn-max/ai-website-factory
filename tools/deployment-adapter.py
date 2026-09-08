#!/usr/bin/env python3

"""Safely preview or perform a confirmed production deployment."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


FACTORY_ROOT = Path(__file__).resolve().parent.parent
SKIPPED_PARTS = {".git", ".vercel", "node_modules", "__pycache__"}
DEPLOYMENT_URL = re.compile(r"https://[^\s]+")


class DeploymentError(Exception):
    """A deployment prerequisite or operation failed safely."""


class DeploymentUnverified(DeploymentError):
    """A remote deployment may exist but needs human attention."""


def run_tool(command, timeout=None):
    environment = os.environ.copy()
    environment["NO_COLOR"] = "1"
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        env=environment,
    )


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
    return text, {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
    }


def first_content_line(value):
    return next((line.strip() for line in value.splitlines() if line.strip()), "")


def replace_section(text, heading, new_body):
    lines = text.splitlines()
    heading_line = f"## {heading}"
    try:
        heading_index = lines.index(heading_line)
    except ValueError as error:
        raise DeploymentError(f"required file is missing the '{heading}' section") from error

    end_index = len(lines)
    for index in range(heading_index + 1, len(lines)):
        if lines[index].startswith("## "):
            end_index = index
            break

    replacement = [heading_line, "", *new_body.splitlines(), ""]
    return "\n".join(lines[:heading_index] + replacement + lines[end_index:]).rstrip() + "\n"


def completed_stages_body(existing, completed_stage):
    normalized = existing.strip()
    if normalized.lower() in ("", "none", "none identified."):
        lines = []
    else:
        lines = normalized.splitlines()
    entry = f"- {completed_stage}"
    if entry not in lines:
        lines.append(entry)
    return "\n".join(lines)


def write_atomic(path, text, prefix):
    original_mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=prefix,
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(text)
            temporary_path = Path(temporary_file.name)
        os.chmod(temporary_path, original_mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def require_release_readiness(project_name, project_directory):
    validator = FACTORY_ROOT / "tools" / "validate-release.py"
    if not validator.is_file():
        raise DeploymentError("release validator is missing")
    result = run_tool([sys.executable, str(validator), project_name, str(project_directory)])
    if result.returncode != 0:
        raise DeploymentError(f"release validation is failing; run './factory validate-release {project_name}'")


def vercel_deployment_root(project_directory):
    candidates = (project_directory, project_directory / "src")
    linked_roots = [candidate for candidate in candidates if (candidate / ".vercel" / "project.json").is_file()]
    if not linked_roots:
        raise DeploymentError(
            "no existing Vercel project link was found; link the intended directory manually before deploying"
        )
    if len(linked_roots) > 1:
        raise DeploymentError("multiple Vercel project links were found; keep only the intended deployment root")

    deployment_root = linked_roots[0].resolve()
    try:
        deployment_root.relative_to(project_directory.resolve())
    except ValueError as error:
        raise DeploymentError("the linked deployment root resolves outside the project directory") from error
    return deployment_root


def validate_vercel_link(deployment_root):
    link_file = deployment_root / ".vercel" / "project.json"
    if link_file.is_symlink():
        raise DeploymentError("the Vercel project link must not be a symbolic link")
    try:
        link = json.loads(link_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DeploymentError("the Vercel project link is unreadable or invalid") from error
    if not all(isinstance(link.get(key), str) and link[key].strip() for key in ("orgId", "projectId")):
        raise DeploymentError("the Vercel project link is missing its organization or project identifier")
    return link


def validate_documented_target(platform_documentation, link):
    documented_projects = set(re.findall(r"\bprj_[A-Za-z0-9]+\b", platform_documentation))
    documented_organizations = set(re.findall(r"\b(?:team|org)_[A-Za-z0-9]+\b", platform_documentation))
    if documented_projects and link["projectId"] not in documented_projects:
        raise DeploymentError("the linked Vercel project does not match the project documented in DEPLOYMENT.md")
    if documented_organizations and link["orgId"] not in documented_organizations:
        raise DeploymentError("the linked Vercel organization does not match the organization documented in DEPLOYMENT.md")


def deployment_file_count(deployment_root):
    count = 0
    for path in deployment_root.rglob("*"):
        relative_path = path.relative_to(deployment_root)
        if any(part in SKIPPED_PARTS for part in relative_path.parts):
            continue
        if path.is_symlink():
            raise DeploymentError(f"deployment root contains a symbolic link: {relative_path}")
        if not path.is_file():
            continue
        count += 1
    if count == 0:
        raise DeploymentError("the deployment root contains no deployable files")
    return count


def prepare(project_name, project_directory):
    projects_root = (FACTORY_ROOT / "projects").resolve()
    if project_directory.is_symlink():
        raise DeploymentError("project directory must not be a symbolic link")
    try:
        project_directory.resolve().relative_to(projects_root)
    except ValueError as error:
        raise DeploymentError("project directory resolves outside the factory projects directory") from error

    require_release_readiness(project_name, project_directory)

    status_file = project_directory / "PROJECT-STATUS.md"
    deployment_file = project_directory / "documentation" / "DEPLOYMENT.md"
    try:
        status_text, status_sections = read_sections(status_file)
        deployment_text, deployment_sections = read_sections(deployment_file)
    except (OSError, UnicodeDecodeError) as error:
        raise DeploymentError(f"required deployment documentation could not be read: {error}") from error

    stage = first_content_line(status_sections.get("Current Stage", ""))
    if stage != "Deployment Ready":
        raise DeploymentError(f"project stage is '{stage or 'not documented'}', expected Deployment Ready")

    platform_documentation = deployment_sections.get("Deployment Platform", "")
    platform = first_content_line(platform_documentation)
    platform = platform.lstrip("*_ ")
    if not re.match(r"(?i)^vercel\b", platform):
        raise DeploymentError("the documented deployment platform is not a supported Vercel target")

    deployment_root = vercel_deployment_root(project_directory)
    link = validate_vercel_link(deployment_root)
    validate_documented_target(platform_documentation, link)
    file_count = deployment_file_count(deployment_root)

    # Confirm sections needed after success exist before any remote action.
    preview_text = status_text
    for heading in ("Current Stage", "Current Owner", "Completed Stages", "Active Work", "Next Action"):
        preview_text = replace_section(preview_text, heading, status_sections.get(heading, ""))
    if "Post-Deployment Verification" not in deployment_sections:
        raise DeploymentError("DEPLOYMENT.md is missing the 'Post-Deployment Verification' section")

    return {
        "status_file": status_file,
        "status_text": status_text,
        "status_sections": status_sections,
        "deployment_file": deployment_file,
        "deployment_text": deployment_text,
        "deployment_sections": deployment_sections,
        "deployment_root": deployment_root,
        "vercel_link": link,
        "file_count": file_count,
    }


def display_dry_run(project_name, project_directory, prepared):
    relative_root = prepared["deployment_root"].relative_to(project_directory.resolve())
    root_label = f"projects/{project_name}"
    if str(relative_root) != ".":
        root_label += f"/{relative_root}"
    print(f"Deployment dry run: {project_name}")
    print("  Stage: Deployment Ready")
    print("  Platform: Vercel")
    print(f"  Deployment root: {root_label}")
    print(f"  Vercel organization: {prepared['vercel_link']['orgId']}")
    print(f"  Vercel project: {prepared['vercel_link']['projectId']}")
    print(f"  Deployable files: {prepared['file_count']}")
    if shutil.which("vercel"):
        print("  Vercel CLI: installed")
    else:
        print("  Vercel CLI: not installed (required only for a live deployment)")
    print(f"  Live command: ./factory deploy {project_name} --confirm DEPLOY")
    print("DRY RUN PASSED: no deployment or project update was performed.")


def deployment_url(stdout):
    matches = DEPLOYMENT_URL.findall(stdout)
    if not matches:
        raise DeploymentError("Vercel completed without returning a deployment URL")
    url = matches[-1].rstrip(".,;)")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise DeploymentError("Vercel returned an invalid or non-HTTPS deployment URL")
    return url


def verify_deployment(url):
    request = Request(url, headers={"User-Agent": "AI-Website-Factory/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            status_code = response.status
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "").lower()
            body = response.read(1_000_000)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise DeploymentError("the returned production URL could not be verified") from error

    if not 200 <= status_code < 400:
        raise DeploymentError(f"production verification returned HTTP {status_code}")
    if urlsplit(final_url).scheme != "https":
        raise DeploymentError("production verification redirected to a non-HTTPS URL")
    if "text/html" not in content_type and b"<html" not in body.lower():
        raise DeploymentError("production verification did not return an HTML page")
    return status_code, final_url


def deployment_records(prepared, url, status_code, recorded_at):
    previous_verification = prepared["deployment_sections"].get("Post-Deployment Verification", "").strip()
    verification = "\n".join(
        (
            f"Confirmed automatically on {recorded_at} after an explicitly authorized production deployment.",
            "",
            f"- **Production URL:** {url}",
            "- **HTTPS:** confirmed",
            f"- **HTTP response:** {status_code}",
            "- **HTML response:** confirmed",
            "- **Deployment provider:** Vercel",
            "",
            "### Pre-deployment verification plan",
            "",
            previous_verification or "No additional verification plan was documented.",
        )
    )
    deployment_text = replace_section(
        prepared["deployment_text"],
        "Post-Deployment Verification",
        verification,
    )

    status_sections = prepared["status_sections"]
    completed = completed_stages_body(status_sections.get("Completed Stages", ""), "Deployment Ready")
    status_text = prepared["status_text"]
    status_text = replace_section(status_text, "Current Stage", "Deployed")
    status_text = replace_section(status_text, "Current Owner", "None — deployment complete.")
    status_text = replace_section(status_text, "Completed Stages", completed)
    status_text = replace_section(
        status_text,
        "Active Work",
        f"None. Production deployment completed and verified at {url}.",
    )
    status_text = replace_section(
        status_text,
        "Next Action",
        "Monitor the production site. Route any verified production defect through QA → Debugging → QA.",
    )
    return deployment_text, status_text


def deploy(project_name, project_directory, confirmation):
    if confirmation != "DEPLOY":
        raise DeploymentError(
            f"confirmation must be exactly 'DEPLOY'; use './factory deploy {project_name} --confirm DEPLOY'"
        )

    prepared = prepare(project_name, project_directory)
    vercel = shutil.which("vercel")
    if not vercel:
        raise DeploymentError("Vercel CLI is not installed; install it manually and run 'vercel login' first")

    try:
        identity = run_tool(
            [vercel, "whoami", "--cwd", str(prepared["deployment_root"]), "--no-color"],
            timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        raise DeploymentError("Vercel authentication check timed out") from error
    if identity.returncode != 0:
        raise DeploymentError("Vercel CLI is not authenticated; run 'vercel login' manually")

    try:
        result = run_tool(
            [
                vercel,
                "deploy",
                "--prod",
                "--yes",
                "--cwd",
                str(prepared["deployment_root"]),
                "--no-color",
            ],
            timeout=900,
        )
    except subprocess.TimeoutExpired as error:
        raise DeploymentUnverified(
            "the deployment command timed out and production state is unknown; check Vercel before retrying"
        ) from error
    if result.returncode != 0:
        raise DeploymentError("Vercel deployment failed; no local workflow state was changed")

    try:
        url = deployment_url(result.stdout)
        status_code, final_url = verify_deployment(url)
    except DeploymentError as error:
        raise DeploymentUnverified(
            f"Vercel accepted the deployment, but post-deployment verification failed ({error}); "
            "check Vercel before retrying"
        ) from error
    recorded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    deployment_text, status_text = deployment_records(prepared, final_url, status_code, recorded_at)

    try:
        write_atomic(prepared["deployment_file"], deployment_text, ".DEPLOYMENT.")
        write_atomic(prepared["status_file"], status_text, ".PROJECT-STATUS.")
    except OSError as error:
        raise DeploymentUnverified(
            f"deployment succeeded at {final_url}, but the local deployment record could not be completed: {error}"
        ) from error

    print(f"Production deployment verified: {project_name}")
    print(f"URL: {final_url}")
    print(f"HTTP: {status_code}")
    print("Workflow stage: Deployed")


def main():
    if len(sys.argv) not in (4, 5) or sys.argv[1] not in ("dry-run", "deploy"):
        print(
            "Usage: deployment-adapter.py dry-run <project-name> <project-directory>\n"
            "       deployment-adapter.py deploy <project-name> <project-directory> DEPLOY",
            file=sys.stderr,
        )
        return 2

    mode = sys.argv[1]
    project_name = sys.argv[2]
    project_directory = Path(sys.argv[3]).absolute()
    if not project_directory.is_dir():
        print(f"Error: project directory does not exist at {project_directory}.", file=sys.stderr)
        return 1

    try:
        if mode == "dry-run":
            if len(sys.argv) != 4:
                raise DeploymentError("dry-run does not accept a confirmation value")
            prepared = prepare(project_name, project_directory)
            display_dry_run(project_name, project_directory, prepared)
        else:
            if len(sys.argv) != 5:
                raise DeploymentError("live deployment requires the exact DEPLOY confirmation")
            deploy(project_name, project_directory, sys.argv[4])
        return 0
    except DeploymentUnverified as error:
        print(f"DEPLOYMENT REQUIRES ATTENTION: {error}.", file=sys.stderr)
        return 1
    except DeploymentError as error:
        print(f"NOT DEPLOYED: {error}.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
