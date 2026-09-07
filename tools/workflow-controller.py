#!/usr/bin/env python3

"""Guide and safely advance AI Website Factory project stages."""

from pathlib import Path
import os
import stat
import subprocess
import sys
import tempfile


FACTORY_ROOT = Path(__file__).resolve().parent.parent

STAGES = {
    "Intake": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Complete and validate the project brief.",
        "output": "PROJECT-BRIEF.md",
    },
    "Architecture": {
        "owner": "Website Architect",
        "agent": "agents/website-architect/AGENT.md",
        "action": "Define the sitemap, user journeys, technical architecture, integrations, risks, and assumptions.",
        "output": "architecture/ARCHITECTURE.md",
    },
    "Design": {
        "owner": "UI/UX Designer",
        "agent": "agents/ui-ux-designer/AGENT.md",
        "action": "Complete the responsive UI/UX specification and component behavior.",
        "output": "design/UI-UX-SPEC.md",
    },
    "Development": {
        "owner": "Frontend Developer",
        "agent": "agents/Frontend-developer/AGENT.md",
        "action": "Implement the approved architecture and design in the project source directory.",
        "output": "src/index.html and supporting source files",
    },
    "Backend": {
        "owner": "Backend Developer",
        "agent": "agents/backend-developer/AGENT.md",
        "action": "Implement only the server-side functionality required by the approved architecture.",
        "output": "backend implementation and documentation",
    },
    "QA": {
        "owner": "QA Tester",
        "agent": "agents/qa-tester/AGENT.md",
        "action": "Independently test requirements, journeys, responsive behavior, forms, and regressions.",
        "output": "reports/QA-REPORT.md",
    },
    "Debugging": {
        "owner": "Debug Fixer",
        "agent": "agents/debug-fixer/AGENT.md",
        "action": "Fix verified defects and return the project to QA for independent retesting.",
        "output": "documented fixes and updated source",
    },
    "SEO": {
        "owner": "SEO & Content Agent",
        "agent": "agents/seo-content/AGENT.md",
        "action": "Review content, metadata, structure, indexing, internal links, and search intent.",
        "output": "reports/SEO-REPORT.md",
    },
    "Security": {
        "owner": "Security Auditor",
        "agent": "agents/security-auditor/AGENT.md",
        "action": "Review applicable security risks and document findings with evidence and severity.",
        "output": "reports/SECURITY-REPORT.md",
    },
    "Performance": {
        "owner": "Performance Optimizer",
        "agent": "agents/performance-optimizer/AGENT.md",
        "action": "Measure and improve performance without breaking functionality or accessibility.",
        "output": "reports/PERFORMANCE-REPORT.md",
    },
    "Accessibility": {
        "owner": "Accessibility Specialist",
        "agent": "agents/accessibility-specialist/AGENT.md",
        "action": "Review the project against its accessibility target and document verified findings.",
        "output": "reports/ACCESSIBILITY-REPORT.md",
    },
    "Final Review": {
        "owner": "QA Tester",
        "agent": "agents/qa-tester/AGENT.md",
        "action": "Run final regression testing and produce the launch-readiness decision.",
        "output": "reports/LAUNCH-READINESS.md",
    },
    "Ready for Human Approval": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Present final evidence, risks, known issues, and the deployment plan for an explicit human decision.",
        "output": "explicit APPROVED or NOT APPROVED human decision",
    },
    "Approved": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Prepare the approved release for the deployment-readiness gate.",
        "output": "verified deployment plan and rollback procedure",
    },
    "Deployment Ready": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Await an explicit deployment instruction and use the configured deployment adapter.",
        "output": "verified production deployment",
    },
    "Deployed": {
        "owner": "None",
        "agent": None,
        "action": "Project is deployed; perform post-deployment verification when changes are released.",
        "output": "production verification record",
    },
    "Blocked": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Resolve and document the blocking issue before resuming downstream work.",
        "output": "resolved blocker and an explicit next state",
    },
}

NEXT_STAGE = {
    "Intake": "Architecture",
    "Architecture": "Design",
    "Design": "Development",
    "Development": "QA",
    "Backend": "QA",
    "QA": "SEO",
    "Debugging": "QA",
    "SEO": "Security",
    "Security": "Performance",
    "Performance": "Accessibility",
    "Accessibility": "Final Review",
    "Final Review": "Ready for Human Approval",
    "Ready for Human Approval": "Approved",
    "Approved": "Deployment Ready",
    "Deployment Ready": "Deployed",
}

ALIASES = {
    "SEO & Content": "SEO",
    "Final QA": "Final Review",
    "Human Approval": "Ready for Human Approval",
    "Complete": "Deployed",
}


def read_sections(status_file):
    text = status_file.read_text(encoding="utf-8")
    sections = {}
    current_heading = None

    for line in text.splitlines():
        if line.startswith("## "):
            current_heading = line[3:].strip()
            sections[current_heading] = []
        elif current_heading is not None:
            sections[current_heading].append(line)

    return text, {
        heading: "\n".join(lines).strip()
        for heading, lines in sections.items()
    }


def current_stage(sections):
    value = sections.get("Current Stage", "").strip()
    first_line = next((line.strip() for line in value.splitlines() if line.strip()), "")
    return ALIASES.get(first_line, first_line)


def has_blockers(sections):
    blockers = sections.get("Blockers", "").strip()
    if not blockers:
        return False
    first_line = blockers.splitlines()[0].strip().lower()
    return not first_line.startswith(("none", "no blocker"))


def run_tool(command):
    return subprocess.run(command, capture_output=True, text=True, check=False)


def gate_errors(project_name, project_directory, stage, sections):
    errors = []
    if has_blockers(sections):
        errors.append("PROJECT-STATUS.md contains active blockers")

    validator = FACTORY_ROOT / "tools" / "validate-stage.py"
    if not validator.is_file():
        errors.append("project stage validator is missing")
    else:
        result = run_tool([sys.executable, str(validator), project_name, str(project_directory), stage])
        if result.returncode != 0:
            errors.append(f"stage validation is failing; run './factory validate-stage {project_name}'")

    if stage == "Ready for Human Approval":
        errors.append("generic advancement cannot grant human approval")
    elif stage == "Approved":
        errors.append("the release-readiness gate is not built yet")
    elif stage == "Deployment Ready":
        errors.append("generic advancement cannot deploy a production project")
    elif stage == "Blocked":
        errors.append("resolve the documented blocker and set an explicit recovery state")

    return errors


def replace_section(text, heading, new_body):
    lines = text.splitlines()
    heading_line = f"## {heading}"

    try:
        heading_index = lines.index(heading_line)
    except ValueError as error:
        raise ValueError(f"PROJECT-STATUS.md is missing the '{heading}' section") from error

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


def write_status(status_file, text):
    original_mode = stat.S_IMODE(status_file.stat().st_mode)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=status_file.parent,
            prefix=".PROJECT-STATUS.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(text)
            temporary_path = Path(temporary_file.name)
        os.chmod(temporary_path, original_mode)
        os.replace(temporary_path, status_file)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_project(project_name, project_directory):
    status_file = project_directory / "PROJECT-STATUS.md"
    if not status_file.is_file():
        raise ValueError(f"project '{project_name}' has no PROJECT-STATUS.md file")

    try:
        text, sections = read_sections(status_file)
    except (OSError, UnicodeDecodeError) as error:
        raise ValueError(f"could not read {status_file}: {error}") from error

    stage = current_stage(sections)
    if stage not in STAGES:
        raise ValueError(f"unrecognized current stage '{stage or 'empty'}'")
    return status_file, text, sections, stage


def show_next(project_name, project_directory):
    _, _, sections, stage = load_project(project_name, project_directory)
    details = STAGES[stage]

    print(f"Project: {project_name}")
    print(f"Current stage: {stage}")
    print(f"Current owner: {details['owner']}")

    if stage == "Deployed":
        print("Workflow status: COMPLETE")
        print("Next stage: None")
        return 0
    if stage == "Blocked":
        print("Workflow status: BLOCKED")
        print(f"Next action: {details['action']}")
        return 1

    destination = NEXT_STAGE.get(stage)
    if destination is None:
        raise ValueError(f"no transition is configured from '{stage}'")

    destination_details = STAGES[destination]
    errors = gate_errors(project_name, project_directory, stage, sections)

    print(f"Next stage: {destination}")
    print(f"Next owner: {destination_details['owner']}")
    if destination_details["agent"]:
        print(f"Agent instructions: {destination_details['agent']}")
    print(f"Required output: {details['output']}")

    if errors:
        print("Gate: BLOCKED")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Gate: READY")
    print(f"Advance with: ./factory advance {project_name}")
    return 0


def advance(project_name, project_directory):
    status_file, text, sections, stage = load_project(project_name, project_directory)
    if stage == "Deployed":
        print(f"Project '{project_name}' is already deployed; no workflow transition was made.", file=sys.stderr)
        return 1

    destination = NEXT_STAGE.get(stage)
    if destination is None:
        print(f"Project '{project_name}' cannot advance from '{stage}'.", file=sys.stderr)
        return 1

    errors = gate_errors(project_name, project_directory, stage, sections)
    if errors:
        print(f"NOT ADVANCED: {project_name} remains in {stage}.", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    destination_details = STAGES[destination]
    completed = completed_stages_body(sections.get("Completed Stages", ""), stage)
    next_action = (
        f"{destination_details['action']} Required output: {destination_details['output']}. "
        f"When complete, run './factory next {project_name}'."
    )

    try:
        text = replace_section(text, "Current Stage", destination)
        text = replace_section(text, "Current Owner", destination_details["owner"])
        text = replace_section(text, "Completed Stages", completed)
        text = replace_section(text, "Active Work", destination_details["action"])
        text = replace_section(text, "Next Action", next_action)
        if destination == "Ready for Human Approval":
            text = replace_section(
                text,
                "Human Decisions Required",
                "Explicit human approval is required before any production deployment.",
            )
        write_status(status_file, text)
    except (OSError, ValueError) as error:
        print(f"Error: could not update PROJECT-STATUS.md ({error}).", file=sys.stderr)
        return 1

    print(f"Advanced {project_name}: {stage} -> {destination}")
    print(f"Owner: {destination_details['owner']}")
    print(f"Next action: {destination_details['action']}")
    print(f"Required output: {destination_details['output']}")
    return 0


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("next", "advance"):
        print(
            "Usage: workflow-controller.py <next|advance> <project-name> <project-directory>",
            file=sys.stderr,
        )
        return 2

    command = sys.argv[1]
    project_name = sys.argv[2]
    project_directory = Path(sys.argv[3]).resolve()

    try:
        if command == "next":
            return show_next(project_name, project_directory)
        return advance(project_name, project_directory)
    except ValueError as error:
        print(f"Error: {error}.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
