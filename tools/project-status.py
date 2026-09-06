#!/usr/bin/env python3

"""List factory projects and display their structured status files."""

from pathlib import Path
import sys


STATUS_FIELDS = (
    "Current Stage",
    "Current Owner",
    "Active Work",
    "Blockers",
    "Known Issues",
    "Human Decisions Required",
    "Next Action",
)


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

    return {
        heading: "\n".join(lines).strip()
        for heading, lines in sections.items()
    }


def stage_for(project_directory):
    status_file = project_directory / "PROJECT-STATUS.md"
    if not status_file.is_file():
        return "Status file missing"

    try:
        sections = read_sections(status_file)
    except (OSError, UnicodeDecodeError):
        return "Status file unreadable"

    stage = sections.get("Current Stage", "").strip()
    if not stage:
        return "Stage not documented"
    return next((line.strip() for line in stage.splitlines() if line.strip()), "Stage not documented")


def list_projects(projects_directory):
    if not projects_directory.is_dir():
        print(f"Error: projects directory does not exist at {projects_directory}.", file=sys.stderr)
        return 1

    projects = sorted(
        (
            entry
            for entry in projects_directory.iterdir()
            if entry.is_dir() and not entry.name.startswith(".")
        ),
        key=lambda entry: entry.name.lower(),
    )

    if not projects:
        print("No projects found.")
        print("Create one with: ./factory create <project-name>")
        return 0

    rows = [(project.name, stage_for(project)) for project in projects]
    name_width = max(len("PROJECT"), *(len(name) for name, _ in rows))

    print(f"Projects ({len(rows)}):")
    print(f"  {'PROJECT':<{name_width}}  STAGE")
    print(f"  {'-' * name_width}  -----")
    for name, stage in rows:
        print(f"  {name:<{name_width}}  {stage}")
    return 0


def print_field(label, value):
    if not value:
        value = "Not documented"

    lines = value.splitlines()
    if len(lines) == 1:
        print(f"{label}: {lines[0]}")
        return

    print(f"{label}:")
    for line in lines:
        print(f"  {line}" if line else "")


def show_status(project_name, project_directory):
    status_file = project_directory / "PROJECT-STATUS.md"
    if not status_file.is_file():
        print(f"Error: project '{project_name}' has no PROJECT-STATUS.md file.", file=sys.stderr)
        return 1

    try:
        sections = read_sections(status_file)
    except (OSError, UnicodeDecodeError) as error:
        print(f"Error: could not read {status_file} ({error}).", file=sys.stderr)
        return 1

    print(f"Project: {project_name}")
    print(f"Status file: projects/{project_name}/PROJECT-STATUS.md")
    print()

    for index, field in enumerate(STATUS_FIELDS):
        if index:
            print()
        print_field(field, sections.get(field, ""))
    return 0


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "list":
        return list_projects(Path(sys.argv[2]).resolve())
    if len(sys.argv) == 4 and sys.argv[1] == "show":
        return show_status(sys.argv[2], Path(sys.argv[3]).resolve())

    print(
        "Usage: project-status.py list <projects-directory>\n"
        "       project-status.py show <project-name> <project-directory>",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
