#!/usr/bin/env python3

"""Validate whether a factory project brief is ready for architecture."""

from pathlib import Path
import re
import sys


REQUIRED_SECTIONS = (
    "Project Information",
    "Project Goal",
    "Target Audience",
    "Website Type",
    "Required Pages",
    "Required Features",
    "Branding",
    "Design Direction",
    "Content",
    "Technical Requirements",
    "SEO Requirements",
    "Accessibility",
    "Performance",
    "Deliverables",
    "Constraints",
    "Human Approval",
)

REQUIRED_FIELDS = {
    "Project Information": (
        "Project Name",
        "Client / Brand",
        "Project Type",
        "Target Launch Date",
    ),
    "Project Goal": ("Primary Goal",),
    "Target Audience": ("Primary Audience", "Location / Market"),
    "Branding": (
        "Brand Name",
        "Logo Available",
        "Primary Colors",
        "Secondary Colors",
        "Typography",
        "Brand Personality",
    ),
    "Design Direction": ("Desired Style",),
    "Content": ("Content Provided By",),
    "Technical Requirements": (
        "Domain",
        "Hosting / Platform",
        "Frontend",
        "Backend",
        "Database",
        "Third-Party Integrations",
    ),
    "SEO Requirements": ("Primary Keywords", "Target Location"),
    "Constraints": (
        "Budget",
        "Deadline",
        "Platform Restrictions",
        "Other Constraints",
    ),
}

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

REVIEW_PATTERNS = (
    re.compile(r"\bplaceholder\b", re.IGNORECASE),
    re.compile(r"\b(?:tbd|todo|lorem ipsum)\b", re.IGNORECASE),
    re.compile(r"\bto be (?:determined|selected|confirmed|provided|decided)\b", re.IGNORECASE),
    re.compile(r"\bpending (?:confirmation|decision|review)\b", re.IGNORECASE),
    re.compile(r"\bnot (?:specified|decided|confirmed)\b", re.IGNORECASE),
)

FIELD_PATTERN = re.compile(r"^\*\*(?P<label>.+?):\*\*\s*(?P<value>.*)$")
CHECKBOX_PATTERN = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s*(?P<label>.+?)\s*$")
BULLET_PATTERN = re.compile(r"^\s*-\s+(?P<value>.+?)\s*$")


def normalized_section_name(heading):
    return re.sub(r"^\d+\.\s*", "", heading).strip()


def parse_brief(text):
    sections = {}
    current_section = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            current_section = normalized_section_name(line[3:])
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append((line_number, line))

    return sections


def fields_in(section_lines):
    fields = {}
    for line_number, line in section_lines:
        match = FIELD_PATTERN.match(line.strip())
        if match:
            fields[match.group("label").strip()] = (
                match.group("value").strip(),
                line_number,
            )
    return fields


def is_unanswered(value):
    normalized = re.sub(r"\s+", " ", value.strip()).lower()
    if normalized in UNANSWERED_VALUES:
        return True
    return bool(re.fullmatch(r"[_\.\s]+", normalized))


def checked_choices(section_lines):
    choices = []
    for _, line in section_lines:
        match = CHECKBOX_PATTERN.match(line)
        if match and match.group("mark").lower() == "x":
            label = match.group("label").strip()
            if label.lower().rstrip(":") != "other" or ":" in label and label.split(":", 1)[1].strip():
                choices.append(label)
    return choices


def bullets_after_label(section_lines, label, stop_at_examples=False):
    values = []
    collecting = False

    for _, line in section_lines:
        field_match = FIELD_PATTERN.match(line.strip())
        if field_match:
            collecting = field_match.group("label").strip() == label
            continue
        if not collecting:
            continue
        if line.strip() == "---" or (stop_at_examples and line.strip().lower() == "examples:"):
            break

        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match:
            value = bullet_match.group("value").strip()
            if value and not value.startswith("["):
                values.append(value)

    return values


def feature_answers(section_lines):
    features = []
    for _, line in section_lines:
        if line.strip().lower() == "examples:":
            break
        match = BULLET_PATTERN.match(line)
        if match:
            value = match.group("value").strip()
            if value and not value.startswith("["):
                features.append(value)
    return features


def review_warnings(sections):
    warnings = []
    for section_name, lines in sections.items():
        if section_name == "Human Approval":
            continue
        for line_number, line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("Examples:"):
                continue
            if any(pattern.search(stripped) for pattern in REVIEW_PATTERNS):
                excerpt = stripped if len(stripped) <= 120 else stripped[:117] + "..."
                warnings.append(f"line {line_number} ({section_name}): {excerpt}")
    return warnings


def validate(project_name, brief_file):
    try:
        text = brief_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"Error: could not read {brief_file} ({error}).", file=sys.stderr)
        return 1

    sections = parse_brief(text)
    errors = []

    for section_name in REQUIRED_SECTIONS:
        if section_name not in sections:
            errors.append(f"missing required section: {section_name}")

    answered_fields = 0
    required_field_count = sum(len(fields) for fields in REQUIRED_FIELDS.values())

    for section_name, required_fields in REQUIRED_FIELDS.items():
        if section_name not in sections:
            continue
        available_fields = fields_in(sections[section_name])
        for field_name in required_fields:
            if field_name not in available_fields:
                errors.append(f"{section_name}: missing field '{field_name}'")
                continue
            value, line_number = available_fields[field_name]
            if is_unanswered(value):
                errors.append(f"line {line_number}: '{field_name}' is unanswered")
            else:
                answered_fields += 1

    project_fields = fields_in(sections.get("Project Information", []))
    brief_project_name = project_fields.get("Project Name", ("", None))[0]
    if brief_project_name and not is_unanswered(brief_project_name) and brief_project_name != project_name:
        errors.append(
            f"Project Name is '{brief_project_name}', but the project directory is '{project_name}'"
        )

    secondary_goals = bullets_after_label(sections.get("Project Goal", []), "Secondary Goals")
    if not secondary_goals:
        errors.append("Project Goal: provide at least one secondary goal")

    audience_needs = bullets_after_label(sections.get("Target Audience", []), "Audience Needs")
    if not audience_needs:
        errors.append("Target Audience: provide at least one audience need")

    website_types = checked_choices(sections.get("Website Type", []))
    if not website_types:
        errors.append("Website Type: select at least one option with [x]")

    required_pages = checked_choices(sections.get("Required Pages", []))
    if not required_pages:
        errors.append("Required Pages: select at least one page with [x]")

    features = feature_answers(sections.get("Required Features", []))
    if not features:
        errors.append("Required Features: list at least one required feature")

    warnings = review_warnings(sections)

    print(f"Validating project brief: {project_name}")
    print(f"  Sections: {len(set(REQUIRED_SECTIONS) & set(sections))}/{len(REQUIRED_SECTIONS)}")
    print(f"  Required fields answered: {answered_fields}/{required_field_count}")
    print(f"  Website type: {', '.join(website_types) if website_types else 'Not selected'}")
    print(f"  Required pages selected: {len(required_pages)}")
    print(f"  Required features listed: {len(features)}", flush=True)

    if warnings:
        print(f"\nReview warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print(f"\nNOT READY: {len(errors)} blocking issue(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("\nREADY: the brief contains the required intake information.")
    if warnings:
        print("Review the warnings before architecture; they do not currently block readiness.")
    print("Production deployment still requires separate human approval.")
    return 0


def main():
    if len(sys.argv) != 3:
        print("Usage: validate-brief.py <project-name> <brief-file>", file=sys.stderr)
        return 2

    return validate(sys.argv[1], Path(sys.argv[2]).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
