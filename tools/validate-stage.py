#!/usr/bin/env python3

"""Validate whether a project stage has a substantive, usable deliverable."""

from pathlib import Path
import re
import subprocess
import sys

from factory_stages import ALIASES, SUPPORTED_STAGES


FACTORY_ROOT = Path(__file__).resolve().parent.parent

PLACEHOLDER_PATTERNS = (
    re.compile(r"\bto be completed(?: by [^.]+)?\.?$", re.IGNORECASE),
    re.compile(r"\bto be documented\.?$", re.IGNORECASE),
    re.compile(r"\bto be determined(?: by [^.]+)?\.?$", re.IGNORECASE),
    re.compile(r"\bnone documented yet\.?$", re.IGNORECASE),
)

FILE_SCAFFOLD_PATTERNS = (
    re.compile(r"\bstatus:\s*not started\b", re.IGNORECASE),
)

ARCHITECTURE_CONCEPTS = {
    "sitemap": ("sitemap", "information architecture"),
    "user journeys": ("journey",),
    "technology stack": ("technology stack", "technical stack"),
    "frontend architecture": ("frontend architecture", "recommended technology stack", "technology stack"),
    "backend requirements": ("backend", "server-side", "authentication", "data requirements", "recommended technology stack"),
    "integrations": ("integration",),
    "risks or open decisions": ("risk", "assumption", "open decision", "security requirement"),
    "assumptions": ("assumption",),
}

DESIGN_CONCEPTS = {
    "page layouts": ("layout",),
    "responsive behavior": ("responsive",),
    "component system": ("component",),
    "navigation": ("navigation",),
    "forms": ("form",),
    "interaction states": ("interaction", "state"),
    "typography": ("typography",),
    "color system": ("color", "colour"),
    "accessibility": ("accessibility",),
}

REPORT_RULES = {
    "QA": {
        "path": "reports/QA-REPORT.md",
        "minimum_words": 100,
        "concepts": {
            "summary": ("summary",),
            "test results": ("test result", "test coverage"),
            "defects or findings": ("defect", "finding"),
            "readiness or handoff": ("readiness", "launch status", "handoff"),
        },
    },
    "SEO": {
        "path": "reports/SEO-REPORT.md",
        "minimum_words": 80,
        "concepts": {
            "summary": ("summary",),
            "metadata": ("metadata", "meta"),
            "headings or content": ("heading", "content"),
            "technical SEO": ("technical seo", "index", "sitemap"),
            "handoff": ("handoff", "recommendation"),
        },
    },
    "Security": {
        "path": "reports/SECURITY-REPORT.md",
        "minimum_words": 80,
        "concepts": {
            "summary": ("summary",),
            "findings": ("finding",),
            "data or secrets": ("data", "secret"),
            "dependencies or integrations": ("dependency", "integration"),
            "readiness or handoff": ("readiness", "handoff", "remediation"),
        },
    },
    "Performance": {
        "path": "reports/PERFORMANCE-REPORT.md",
        "minimum_words": 80,
        "concepts": {
            "baseline or measurements": ("baseline", "measurement", "metric"),
            "optimizations": ("optimization", "performance"),
            "Core Web Vitals or targets": ("core web vital", "target"),
            "handoff": ("handoff", "recommendation"),
        },
    },
    "Accessibility": {
        "path": "reports/ACCESSIBILITY-REPORT.md",
        "minimum_words": 80,
        "concepts": {
            "summary": ("summary",),
            "findings": ("finding",),
            "keyboard": ("keyboard",),
            "forms or interactions": ("form", "interaction"),
            "screen reader": ("screen reader",),
            "readiness or handoff": ("readiness", "handoff"),
        },
    },
}

FINAL_REVIEW_CONCEPTS = {
    "project summary": ("project summary",),
    "pipeline status": ("pipeline status",),
    "outstanding issues": ("outstanding issue", "known issue"),
    "deployment readiness": ("deployment readiness",),
    "remaining risks": ("remaining risk", "risk"),
    "deployment plan": ("deployment plan",),
    "rollback": ("rollback",),
    "next action": ("next action",),
}

DEPLOYMENT_CONCEPTS = {
    "deployment platform": ("deployment platform", "platform"),
    "build process": ("build process", "build"),
    "deployment procedure": ("deployment procedure", "procedure"),
    "post-deployment verification": ("post-deployment verification", "verification"),
    "rollback": ("rollback",),
}


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

    def display(self, project_name, stage):
        print(f"Validating stage: {project_name} — {stage}")
        for passed, message in self.items:
            label = "PASS" if passed else "FAIL"
            print(f"  [{label}] {message}")

        sys.stdout.flush()

        if self.failures:
            print(f"\nNOT READY: {len(self.failures)} stage requirement(s) failed.", file=sys.stderr)
            return 1

        print("\nPASSED: the current stage deliverable is ready for its workflow gate.")
        print("This structural validation does not replace specialist review or human approval.")
        return 0


def normalize_heading(heading):
    heading = re.sub(r"^\d+\.\s*", "", heading).strip().lower()
    return re.sub(r"[`*_]", "", heading)


def markdown_sections(text):
    sections = []
    current_heading = None
    body = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((normalize_heading(current_heading), "\n".join(body).strip()))
            current_heading = line[3:].strip()
            body = []
        elif current_heading is not None:
            body.append(line)

    if current_heading is not None:
        sections.append((normalize_heading(current_heading), "\n".join(body).strip()))
    return sections


def status_stage(project_directory):
    status_file = project_directory / "PROJECT-STATUS.md"
    if not status_file.is_file():
        raise ValueError("PROJECT-STATUS.md is missing")

    text = status_file.read_text(encoding="utf-8")
    sections = markdown_sections(text)
    current = next((body for heading, body in sections if heading == "current stage"), "")
    first_line = next((line.strip() for line in current.splitlines() if line.strip()), "")
    stage = ALIASES.get(first_line, first_line)
    if stage not in SUPPORTED_STAGES:
        raise ValueError(f"unrecognized current stage '{stage or 'empty'}'")
    return stage


def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def body_is_substantive(body):
    if word_count(body) < 3:
        return False
    meaningful_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and line.strip() != "---"
    ]
    if not meaningful_lines:
        return False
    return not all(any(pattern.search(line) for pattern in PLACEHOLDER_PATTERNS) for line in meaningful_lines)


def find_concept(sections, alternatives):
    for heading, body in sections:
        if any(alternative in heading for alternative in alternatives):
            return heading, body
    return None


def load_markdown(project_directory, relative_path, results, minimum_words):
    path = project_directory / relative_path
    if not path.is_file():
        results.fail_check(f"missing required artifact: {relative_path}")
        return None, None

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        results.fail_check(f"cannot read {relative_path}: {error}")
        return None, None

    if word_count(text) < minimum_words:
        results.fail_check(
            f"{relative_path} is too sparse to be a completed deliverable "
            f"({word_count(text)} words; expected at least {minimum_words})"
        )
    else:
        results.pass_check(f"{relative_path} contains substantive content")

    if any(pattern.search(line.strip()) for line in text.splitlines() for pattern in FILE_SCAFFOLD_PATTERNS):
        results.fail_check(f"{relative_path} still contains unfinished scaffold language")

    return text, markdown_sections(text)


def validate_concepts(sections, concepts, relative_path, results):
    if sections is None:
        return

    for label, alternatives in concepts.items():
        match = find_concept(sections, alternatives)
        if match is None:
            results.fail_check(f"{relative_path} is missing a {label} section")
        elif not body_is_substantive(match[1]):
            results.fail_check(f"{relative_path} has no substantive content for {label}")
        else:
            results.pass_check(f"{label} is documented")


def run_tool(command):
    return subprocess.run(command, capture_output=True, text=True, check=False)


def validate_intake(project_name, project_directory, results):
    validator = FACTORY_ROOT / "tools" / "validate-brief.py"
    brief = project_directory / "PROJECT-BRIEF.md"
    if not validator.is_file():
        results.fail_check("tools/validate-brief.py is missing")
        return
    if not brief.is_file():
        results.fail_check("missing required artifact: PROJECT-BRIEF.md")
        return

    outcome = run_tool([sys.executable, str(validator), project_name, str(brief)])
    if outcome.returncode == 0:
        results.pass_check("PROJECT-BRIEF.md passes the project brief validator")
    else:
        results.fail_check(f"PROJECT-BRIEF.md is incomplete; run './factory validate-brief {project_name}'")


def validate_architecture(project_directory, results):
    _, sections = load_markdown(
        project_directory,
        "architecture/ARCHITECTURE.md",
        results,
        minimum_words=100,
    )
    validate_concepts(sections, ARCHITECTURE_CONCEPTS, "architecture/ARCHITECTURE.md", results)


def validate_design(project_directory, results):
    _, sections = load_markdown(
        project_directory,
        "design/UI-UX-SPEC.md",
        results,
        minimum_words=120,
    )
    validate_concepts(sections, DESIGN_CONCEPTS, "design/UI-UX-SPEC.md", results)


def validate_source(project_name, project_directory, results):
    checker = FACTORY_ROOT / "tools" / "check-project.py"
    site_directory = project_directory / "src"
    if not checker.is_file():
        results.fail_check("tools/check-project.py is missing")
        return
    if not (site_directory / "index.html").is_file():
        results.fail_check("missing required artifact: src/index.html")
        return

    outcome = run_tool([sys.executable, str(checker), project_name, str(site_directory)])
    if outcome.returncode == 0:
        results.pass_check("source passes HTML, link, asset, JavaScript, and CSS checks")
    else:
        results.fail_check(f"source checks are failing; run './factory check {project_name}'")


def validate_development(project_name, project_directory, results):
    validate_source(project_name, project_directory, results)
    _, sections = load_markdown(
        project_directory,
        "documentation/DEVELOPMENT.md",
        results,
        minimum_words=40,
    )
    validate_concepts(
        sections,
        {
            "technology stack": ("technology stack",),
            "development instructions": ("development",),
            "build instructions": ("build",),
            "testing instructions": ("testing", "test"),
        },
        "documentation/DEVELOPMENT.md",
        results,
    )


def validate_backend(project_name, project_directory, results):
    validate_source(project_name, project_directory, results)
    _, sections = load_markdown(
        project_directory,
        "documentation/DEVELOPMENT.md",
        results,
        minimum_words=60,
    )
    validate_concepts(
        sections,
        {
            "technology stack": ("technology stack",),
            "installation": ("installation",),
            "development instructions": ("development",),
            "testing instructions": ("testing", "test"),
        },
        "documentation/DEVELOPMENT.md",
        results,
    )


def validate_debugging(project_name, project_directory, results):
    validate_source(project_name, project_directory, results)
    load_markdown(
        project_directory,
        "documentation/CHANGELOG.md",
        results,
        minimum_words=20,
    )


def validate_report(stage, project_directory, results):
    rule = REPORT_RULES[stage]
    _, sections = load_markdown(
        project_directory,
        rule["path"],
        results,
        minimum_words=rule["minimum_words"],
    )
    validate_concepts(sections, rule["concepts"], rule["path"], results)

    if stage == "QA" and sections is not None:
        verdict_section = find_concept(sections, ("launch readiness", "launch status", "handoff"))
        verdict = verdict_section[1].lower() if verdict_section else ""
        if "not ready" in verdict or "blocked" in verdict:
            results.fail_check("QA readiness verdict blocks progression")
        elif "ready" in verdict or "passed" in verdict:
            results.pass_check("QA includes a positive readiness verdict")
        else:
            results.fail_check("QA report is missing a clear readiness verdict")


def validate_final_review(project_directory, results):
    relative_path = "reports/LAUNCH-READINESS.md"
    _, sections = load_markdown(
        project_directory,
        relative_path,
        results,
        minimum_words=140,
    )
    validate_concepts(sections, FINAL_REVIEW_CONCEPTS, relative_path, results)

    if sections is None:
        return
    readiness = find_concept(sections, ("deployment readiness",))
    verdict = readiness[1].lower() if readiness else ""
    if "not ready" in verdict or "ready after fixes" in verdict:
        results.fail_check("launch-readiness verdict does not permit human approval")
    elif "ready for human approval" in verdict:
        results.pass_check("launch-readiness verdict is READY FOR HUMAN APPROVAL")
    else:
        results.fail_check("launch-readiness report lacks a recognized readiness verdict")


def validate_deployment(project_directory, results, require_verification):
    relative_path = "documentation/DEPLOYMENT.md"
    text, sections = load_markdown(
        project_directory,
        relative_path,
        results,
        minimum_words=80,
    )
    validate_concepts(sections, DEPLOYMENT_CONCEPTS, relative_path, results)

    if require_verification and text is not None:
        verification = find_concept(sections, ("post-deployment verification", "verification"))
        verification_text = verification[1].lower() if verification else ""
        if "https://" not in text:
            results.fail_check("deployment record does not include a production HTTPS URL")
        else:
            results.pass_check("deployment record includes a production HTTPS URL")
        if not any(word in verification_text for word in ("confirmed", "verified", "passed", "200")):
            results.fail_check("post-deployment verification lacks recorded evidence")
        else:
            results.pass_check("post-deployment verification includes recorded evidence")


def validate_stage(project_name, project_directory, stage):
    results = Results()

    if stage == "Intake":
        validate_intake(project_name, project_directory, results)
    elif stage == "Architecture":
        validate_architecture(project_directory, results)
    elif stage == "Design":
        validate_design(project_directory, results)
    elif stage == "Development":
        validate_development(project_name, project_directory, results)
    elif stage == "Backend":
        validate_backend(project_name, project_directory, results)
    elif stage in REPORT_RULES:
        validate_report(stage, project_directory, results)
    elif stage == "Debugging":
        validate_debugging(project_name, project_directory, results)
    elif stage in ("Final Review", "Ready for Human Approval"):
        validate_final_review(project_directory, results)
    elif stage in ("Approved", "Deployment Ready"):
        validate_deployment(project_directory, results, require_verification=False)
    elif stage == "Deployed":
        validate_deployment(project_directory, results, require_verification=True)
    elif stage == "Blocked":
        results.fail_check("project is in the Blocked state; resolve the documented blocker first")

    return results.display(project_name, stage)


def main():
    if len(sys.argv) not in (3, 4):
        print(
            "Usage: validate-stage.py <project-name> <project-directory> [stage]",
            file=sys.stderr,
        )
        return 2

    project_name = sys.argv[1]
    project_directory = Path(sys.argv[2]).resolve()

    try:
        stage = sys.argv[3] if len(sys.argv) == 4 else status_stage(project_directory)
        stage = ALIASES.get(stage, stage)
        if stage not in SUPPORTED_STAGES:
            raise ValueError(f"unsupported stage '{stage}'")
        return validate_stage(project_name, project_directory, stage)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(f"Error: {error}.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
