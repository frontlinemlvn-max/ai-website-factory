#!/usr/bin/env python3

"""Safely guide a project brief through the factory intake requirements."""

import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile


FACTORY_ROOT = Path(__file__).resolve().parent.parent
FIELD_PATTERN = re.compile(r"^\*\*(?P<label>.+?):\*\*\s*(?P<value>.*)$")
CHECKBOX_PATTERN = re.compile(r"^(?P<indent>\s*)-\s*\[(?P<mark>[ xX])\]\s*(?P<label>.+?)\s*$")
BULLET_PATTERN = re.compile(r"^\s*-\s*(?P<value>.*?)\s*$")

UNANSWERED_VALUES = {
    "",
    "-",
    "tbd",
    "todo",
    "unknown",
    "not sure",
    "yes / no",
    "yes/no",
    "to be completed",
}

FIELD_STEPS = (
    ("Project Information", "Client / Brand"),
    ("Project Information", "Project Type"),
    ("Project Information", "Target Launch Date"),
    ("Project Goal", "Primary Goal"),
    ("Target Audience", "Primary Audience"),
    ("Target Audience", "Location / Market"),
    ("Branding", "Brand Name"),
    ("Branding", "Logo Available"),
    ("Branding", "Primary Colors"),
    ("Branding", "Secondary Colors"),
    ("Branding", "Typography"),
    ("Branding", "Brand Personality"),
    ("Design Direction", "Desired Style"),
    ("Content", "Content Provided By"),
    ("Technical Requirements", "Domain"),
    ("Technical Requirements", "Hosting / Platform"),
    ("Technical Requirements", "Frontend"),
    ("Technical Requirements", "Backend"),
    ("Technical Requirements", "Database"),
    ("Technical Requirements", "Third-Party Integrations"),
    ("SEO Requirements", "Primary Keywords"),
    ("SEO Requirements", "Target Location"),
    ("Constraints", "Budget"),
    ("Constraints", "Deadline"),
    ("Constraints", "Platform Restrictions"),
    ("Constraints", "Other Constraints"),
)

WEBSITE_TYPES = (
    "Landing Page",
    "Business Website",
    "Portfolio",
    "E-commerce",
    "SaaS / Web App",
    "PWA",
    "Membership Website",
    "Other",
)

PAGE_TYPES = (
    "Home",
    "About",
    "Services",
    "Contact",
    "FAQ",
    "Privacy Policy",
    "Terms",
    "Other",
)


class IntakeError(Exception):
    """The intake cannot proceed safely."""


class IntakeCancelled(Exception):
    """The user cancelled before the brief was saved."""


def normalized_section_name(heading):
    return re.sub(r"^\d+\.\s*", "", heading).strip()


def section_bounds(lines, section_name):
    starts = [
        index
        for index, line in enumerate(lines)
        if line.startswith("## ") and normalized_section_name(line[3:]) == section_name
    ]
    if len(starts) != 1:
        raise IntakeError(f"PROJECT-BRIEF.md must contain exactly one '{section_name}' section")
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return start, end


def field_index(lines, section_name, label):
    start, end = section_bounds(lines, section_name)
    matches = []
    for index in range(start + 1, end):
        match = FIELD_PATTERN.match(lines[index].strip())
        if match and match.group("label").strip() == label:
            matches.append(index)
    if len(matches) != 1:
        raise IntakeError(
            f"PROJECT-BRIEF.md must contain exactly one '{label}' field in {section_name}"
        )
    return matches[0]


def field_value(lines, section_name, label):
    match = FIELD_PATTERN.match(lines[field_index(lines, section_name, label)].strip())
    return match.group("value").strip()


def set_field_value(lines, section_name, label, value):
    index = field_index(lines, section_name, label)
    lines[index] = f"**{label}:** {value}"


def is_answered(value):
    normalized = re.sub(r"\s+", " ", value.strip()).lower()
    if normalized in UNANSWERED_VALUES:
        return False
    return not bool(re.fullmatch(r"[_\.\s]+", normalized))


def read_answer(prompt):
    try:
        answer = input(prompt).strip()
    except EOFError as error:
        raise IntakeCancelled("input ended before intake was complete") from error
    if answer.casefold() == "cancel":
        raise IntakeCancelled("cancelled by user")
    return answer


def prompt_field(label, current):
    while True:
        current_hint = f" [{current}]" if is_answered(current) else ""
        answer = read_answer(f"{label}{current_hint}: ")
        if not answer and is_answered(current):
            return current
        if is_answered(answer):
            if label == "Logo Available" and answer.casefold() not in ("yes", "no"):
                print("  Please answer Yes or No.")
                continue
            return answer
        print("  An answer is required. Use 'None required' when something does not apply.")


def list_values(lines, section_name, label=None, before_marker=None):
    start, end = section_bounds(lines, section_name)
    if label is not None:
        anchor = field_index(lines, section_name, label)
        start = anchor + 1
    if before_marker is not None:
        marker = next(
            (index for index in range(start, end) if lines[index].strip() == before_marker),
            None,
        )
        if marker is None:
            raise IntakeError(f"PROJECT-BRIEF.md is missing the '{before_marker}' marker")
        end = marker

    values = []
    for index in range(start, end):
        stripped = lines[index].strip()
        if label is not None and (stripped == "---" or FIELD_PATTERN.match(stripped)):
            break
        match = BULLET_PATTERN.match(lines[index])
        if match:
            value = match.group("value").strip()
            if value and not value.startswith("["):
                values.append(value)
    return values


def prompt_list(label, current):
    while True:
        current_hint = f" [{'; '.join(current)}]" if current else ""
        answer = read_answer(f"{label} (comma-separated){current_hint}: ")
        if not answer and current:
            return current
        values = [value.strip() for value in answer.split(",") if value.strip()]
        if values and all(is_answered(value) for value in values):
            return values
        print("  Provide at least one item. Use 'None required' when something does not apply.")


def replace_bullets(lines, section_name, values, label=None, before_marker=None):
    start, end = section_bounds(lines, section_name)
    if label is not None:
        start = field_index(lines, section_name, label) + 1
    if before_marker is not None:
        marker = next(
            (index for index in range(start, end) if lines[index].strip() == before_marker),
            None,
        )
        if marker is None:
            raise IntakeError(f"PROJECT-BRIEF.md is missing the '{before_marker}' marker")
        end = marker

    region_end = end
    if label is not None:
        for index in range(start, end):
            stripped = lines[index].strip()
            if stripped == "---" or FIELD_PATTERN.match(stripped):
                region_end = index
                break

    bullet_indices = [
        index
        for index in range(start, region_end)
        if BULLET_PATTERN.match(lines[index]) and not lines[index].lstrip().startswith("- [")
    ]
    replacement = [f"- {value}" for value in values]
    if bullet_indices:
        first = bullet_indices[0]
        bullet_index_set = set(bullet_indices)
        rewritten = []
        inserted = False
        for index in range(start, region_end):
            if index in bullet_index_set:
                if not inserted:
                    rewritten.extend(replacement)
                    inserted = True
            else:
                rewritten.append(lines[index])
        lines[start:region_end] = rewritten
        return

    insertion_index = start
    while insertion_index < region_end and not lines[insertion_index].strip():
        insertion_index += 1
    lines[insertion_index:insertion_index] = replacement


def checkbox_choices(lines, section_name):
    start, end = section_bounds(lines, section_name)
    selected = []
    available = []
    for index in range(start + 1, end):
        match = CHECKBOX_PATTERN.match(lines[index])
        if not match:
            continue
        label = match.group("label").strip()
        base_label = label.split(":", 1)[0].strip() if label.casefold().startswith("other") else label
        available.append(base_label)
        if match.group("mark").casefold() == "x":
            if base_label == "Other" and ":" in label:
                detail = label.split(":", 1)[1].strip()
                if detail:
                    selected.append(f"Other: {detail}")
            elif base_label != "Other":
                selected.append(label)
    return available, selected


def parse_choices(answer, options):
    selected = []
    lookup = {option.casefold(): option for option in options if option != "Other"}
    for token in (part.strip() for part in answer.split(",")):
        if not token:
            continue
        if token.isdigit():
            position = int(token)
            if not 1 <= position <= len(options):
                return None
            option = options[position - 1]
            if option == "Other":
                return None
            selected.append(option)
        elif token.casefold().startswith("other:"):
            detail = token.split(":", 1)[1].strip()
            if not detail:
                return None
            selected.append(f"Other: {detail}")
        elif token.casefold() in lookup:
            selected.append(lookup[token.casefold()])
        else:
            return None

    deduplicated = []
    for value in selected:
        if value.casefold() not in {existing.casefold() for existing in deduplicated}:
            deduplicated.append(value)
    return deduplicated or None


def prompt_choices(section_name, options, current):
    print(f"\n{section_name} choices:")
    for index, option in enumerate(options, start=1):
        suffix = " (enter as Other: description)" if option == "Other" else ""
        print(f"  {index}. {option}{suffix}")
    while True:
        current_hint = f" [{'; '.join(current)}]" if current else ""
        answer = read_answer(f"Select numbers or names, comma-separated{current_hint}: ")
        if not answer and current:
            return current
        selected = parse_choices(answer, options)
        if selected:
            return selected
        print("  Select at least one listed number/name, or enter Other: description.")


def set_checkbox_choices(lines, section_name, selected):
    start, end = section_bounds(lines, section_name)
    normal_selected = {
        value.casefold()
        for value in selected
        if not value.casefold().startswith("other:")
    }
    other = next(
        (value.split(":", 1)[1].strip() for value in selected if value.casefold().startswith("other:")),
        None,
    )
    for index in range(start + 1, end):
        match = CHECKBOX_PATTERN.match(lines[index])
        if not match:
            continue
        label = match.group("label").strip()
        if label.casefold().startswith("other"):
            mark = "x" if other else " "
            rendered_label = f"Other: {other}" if other else "Other:"
        else:
            mark = "x" if label.casefold() in normal_selected else " "
            rendered_label = label
        lines[index] = f"{match.group('indent')}- [{mark}] {rendered_label}"


def validate_structure(lines):
    field_index(lines, "Project Information", "Project Name")
    for section_name, label in FIELD_STEPS:
        field_index(lines, section_name, label)
    field_index(lines, "Project Goal", "Secondary Goals")
    field_index(lines, "Target Audience", "Audience Needs")
    list_values(lines, "Required Features", before_marker="Examples:")

    for section_name, expected in (("Website Type", WEBSITE_TYPES), ("Required Pages", PAGE_TYPES)):
        available, _ = checkbox_choices(lines, section_name)
        if tuple(available) != expected:
            raise IntakeError(f"PROJECT-BRIEF.md has an unexpected {section_name} checklist")


def project_stage(status_file):
    try:
        lines = status_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise IntakeError("PROJECT-STATUS.md is unreadable") from error
    try:
        start = lines.index("## Current Stage") + 1
    except ValueError as error:
        raise IntakeError("PROJECT-STATUS.md is missing the Current Stage section") from error
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped:
            return stripped
    raise IntakeError("PROJECT-STATUS.md has an empty Current Stage section")


def run_validator(validator, project_name, brief_file, capture=False):
    return subprocess.run(
        [sys.executable, str(validator), project_name, str(brief_file)],
        capture_output=capture,
        text=True,
        check=False,
    )


def preflight_candidate(validator, project_name, brief_file, text):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=brief_file.parent,
            prefix=".PROJECT-BRIEF.intake-check.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(text)
            temporary_path = Path(temporary_file.name)
        result = run_validator(validator, project_name, temporary_path, capture=True)
    except OSError as error:
        raise IntakeError("the completed answers could not be validated safely; no changes were saved") from error
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        raise IntakeError("the completed answers did not pass brief validation; no changes were saved")


def write_atomic(path, text):
    original_mode = stat.S_IMODE(path.stat().st_mode)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".PROJECT-BRIEF.intake.",
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


def collect_intake(project_name, original_text):
    lines = original_text.splitlines()
    validate_structure(lines)
    set_field_value(lines, "Project Information", "Project Name", project_name)

    print(f"Guided project intake: {project_name}")
    print("Press Enter to keep an existing answer. Type CANCEL at any prompt to exit without saving.")
    print("Use 'None required' for a required field that does not apply.")
    print("Production approval is deliberately excluded and remains a separate workflow gate.")

    current_section = None
    for section_name, label in FIELD_STEPS:
        if section_name != current_section:
            print(f"\n{section_name}")
            current_section = section_name
        current = field_value(lines, section_name, label)
        set_field_value(lines, section_name, label, prompt_field(label, current))

        if label == "Primary Goal":
            current_values = list_values(lines, "Project Goal", "Secondary Goals")
            values = prompt_list("Secondary Goals", current_values)
            replace_bullets(lines, "Project Goal", values, label="Secondary Goals")
        elif label == "Location / Market":
            current_values = list_values(lines, "Target Audience", "Audience Needs")
            values = prompt_list("Audience Needs", current_values)
            replace_bullets(lines, "Target Audience", values, label="Audience Needs")

            _, current_types = checkbox_choices(lines, "Website Type")
            selected_types = prompt_choices("Website Type", WEBSITE_TYPES, current_types)
            set_checkbox_choices(lines, "Website Type", selected_types)

            _, current_pages = checkbox_choices(lines, "Required Pages")
            selected_pages = prompt_choices("Required Pages", PAGE_TYPES, current_pages)
            set_checkbox_choices(lines, "Required Pages", selected_pages)

            current_features = list_values(lines, "Required Features", before_marker="Examples:")
            features = prompt_list("Required Features", current_features)
            replace_bullets(lines, "Required Features", features, before_marker="Examples:")

    return "\n".join(lines).rstrip() + "\n"


def intake(project_name, project_directory):
    projects_root = (FACTORY_ROOT / "projects").resolve()
    if project_directory.is_symlink():
        raise IntakeError("project directory must not be a symbolic link")
    try:
        project_directory.resolve().relative_to(projects_root)
    except ValueError as error:
        raise IntakeError("project directory resolves outside the factory projects directory") from error

    brief_file = project_directory / "PROJECT-BRIEF.md"
    status_file = project_directory / "PROJECT-STATUS.md"
    validator = FACTORY_ROOT / "tools" / "validate-brief.py"
    if brief_file.is_symlink():
        raise IntakeError("PROJECT-BRIEF.md must not be a symbolic link")
    if status_file.is_symlink():
        raise IntakeError("PROJECT-STATUS.md must not be a symbolic link")
    if not brief_file.is_file():
        raise IntakeError("PROJECT-BRIEF.md is missing")
    if not status_file.is_file():
        raise IntakeError("PROJECT-STATUS.md is missing")
    if not validator.is_file():
        raise IntakeError("project brief validator is missing")

    stage = project_stage(status_file)
    if stage != "Intake":
        raise IntakeError(f"project stage is '{stage}', expected Intake; no answers were changed")

    try:
        original_text = brief_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise IntakeError("PROJECT-BRIEF.md is unreadable") from error

    candidate_text = collect_intake(project_name, original_text)
    if candidate_text == original_text:
        print("\nNo changes requested. Running the brief validator.")
        return run_validator(validator, project_name, brief_file).returncode

    preflight_candidate(validator, project_name, brief_file, candidate_text)
    print(f"\nReady to update projects/{project_name}/PROJECT-BRIEF.md.")
    confirmation = read_answer("Save these intake answers? [y/N]: ").casefold()
    if confirmation not in ("y", "yes"):
        raise IntakeCancelled("save was not confirmed")

    if project_stage(status_file) != "Intake":
        raise IntakeError("the project stage changed during intake; no answers were changed")
    try:
        current_text = brief_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise IntakeError("PROJECT-BRIEF.md could not be rechecked before saving") from error
    if current_text != original_text:
        raise IntakeError("PROJECT-BRIEF.md changed during intake; no answers were changed")

    try:
        write_atomic(brief_file, candidate_text)
    except OSError as error:
        raise IntakeError(f"PROJECT-BRIEF.md could not be updated: {error}") from error

    print("\nIntake saved. Running the brief validator.")
    return run_validator(validator, project_name, brief_file).returncode


def main():
    if len(sys.argv) != 3:
        print("Usage: project-intake.py <project-name> <project-directory>", file=sys.stderr)
        return 2
    project_name = sys.argv[1]
    project_directory = Path(sys.argv[2]).absolute()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", project_name):
        print("INTAKE NOT SAVED: invalid project name.", file=sys.stderr)
        return 1
    if not project_directory.is_dir():
        print(f"INTAKE NOT SAVED: project directory does not exist at {project_directory}.", file=sys.stderr)
        return 1

    try:
        return intake(project_name, project_directory)
    except IntakeCancelled as error:
        print(f"\nINTAKE CANCELLED: {error}. No changes were saved.")
        return 0
    except KeyboardInterrupt:
        print("\nINTAKE CANCELLED: interrupted by user. No changes were saved.")
        return 130
    except IntakeError as error:
        print(f"INTAKE NOT SAVED: {error}.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
