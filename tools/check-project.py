#!/usr/bin/env python3

"""Run dependency-light integrity checks on a static factory project."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit


REQUIRED_HTML_TAGS = ("html", "head", "title", "body")
REFERENCE_ATTRIBUTES = ("href", "src", "poster")
CSS_URL_PATTERN = re.compile(
    r"url\(\s*(?P<quote>['\"]?)(?P<value>.*?)(?P=quote)\s*\)", re.IGNORECASE
)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.doctype_count = 0
        self.start_tags = Counter()
        self.end_tags = Counter()
        self.ids = {}
        self.duplicate_ids = []
        self.references = []

    def handle_decl(self, declaration):
        if declaration.strip().lower() == "doctype html":
            self.doctype_count += 1

    def handle_starttag(self, tag, attributes):
        self.start_tags[tag] += 1
        line, _ = self.getpos()

        for name, value in attributes:
            if value is None:
                continue
            if name == "id":
                if value in self.ids:
                    self.duplicate_ids.append((value, line))
                else:
                    self.ids[value] = line
            elif name in REFERENCE_ATTRIBUTES:
                self.references.append((value, line))
            elif name == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split(" ", 1)[0]
                    if url:
                        self.references.append((url, line))

    def handle_startendtag(self, tag, attributes):
        self.handle_starttag(tag, attributes)

    def handle_endtag(self, tag):
        self.end_tags[tag] += 1


def display_path(path, site_root):
    try:
        return str(path.relative_to(site_root))
    except ValueError:
        return str(path)


def local_target(raw_reference, source_file, site_root):
    try:
        parsed = urlsplit(raw_reference.strip())
    except ValueError as error:
        return "invalid", None, None, str(error)

    if parsed.scheme or parsed.netloc or raw_reference.startswith("//"):
        return "external", None, None, None

    decoded_path = unquote(parsed.path)
    if not decoded_path:
        target = source_file
    elif decoded_path.startswith("/"):
        target = site_root / decoded_path.lstrip("/")
    else:
        target = source_file.parent / decoded_path

    target = target.resolve()
    try:
        target.relative_to(site_root)
    except ValueError:
        return "invalid", target, parsed.fragment, "reference escapes the project src directory"

    if target.is_dir() or decoded_path.endswith("/"):
        target = target / "index.html"

    return "local", target, unquote(parsed.fragment), None


def delimiter_error(text):
    opening = {"{": "}", "[": "]", "(": ")"}
    closing = {value: key for key, value in opening.items()}
    stack = []
    quote = None
    quote_start = None
    in_comment = False
    comment_start = None
    index = 0

    while index < len(text):
        character = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""

        if in_comment:
            if character == "*" and following == "/":
                in_comment = False
                index += 2
                continue
            index += 1
            continue

        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue

        if character == "/" and following == "*":
            in_comment = True
            comment_start = index
            index += 2
            continue
        if character in ("'", '"'):
            quote = character
            quote_start = index
        elif character in opening:
            stack.append((character, index))
        elif character in closing:
            if not stack or stack[-1][0] != closing[character]:
                return index, f"unexpected '{character}'"
            stack.pop()
        index += 1

    if in_comment:
        return comment_start, "unclosed comment"
    if quote:
        return quote_start, "unclosed string"
    if stack:
        character, position = stack[-1]
        return position, f"unclosed '{character}'"
    return None


def line_number(text, index):
    return text.count("\n", 0, index) + 1


def run_checks(project_name, site_root):
    errors = []
    html_pages = sorted(site_root.rglob("*.html"))
    css_files = sorted(site_root.rglob("*.css"))
    js_files = sorted(site_root.rglob("*.js"))
    parsed_pages = {}
    local_reference_count = 0

    def add_error(path, line, message):
        location = display_path(path, site_root)
        if line:
            location += f":{line}"
        errors.append(f"{location}: {message}")

    if not html_pages:
        errors.append("src: no HTML pages found")

    for page in html_pages:
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            add_error(page, None, f"could not read as UTF-8 ({error})")
            continue

        parser = PageParser()
        try:
            parser.feed(text)
            parser.close()
        except Exception as error:
            add_error(page, None, f"could not parse HTML ({error})")
            continue

        parsed_pages[page.resolve()] = parser
        if parser.doctype_count != 1:
            add_error(page, 1, "expected exactly one <!doctype html> declaration")

        for tag in REQUIRED_HTML_TAGS:
            if parser.start_tags[tag] != 1 or parser.end_tags[tag] != 1:
                add_error(page, None, f"expected exactly one opening and closing <{tag}> tag")

        for duplicate_id, line in parser.duplicate_ids:
            add_error(page, line, f"duplicate id '{duplicate_id}'")

    for page, parser in parsed_pages.items():
        for reference, line in parser.references:
            kind, target, fragment, problem = local_target(reference, page, site_root)
            if kind == "external":
                continue
            if kind == "invalid":
                add_error(page, line, f"invalid reference '{reference}' ({problem})")
                continue

            local_reference_count += 1
            if not target.exists() or not target.is_file():
                add_error(page, line, f"missing local file for '{reference}'")
                continue

            if fragment and target.suffix.lower() in (".html", ".htm"):
                target_page = parsed_pages.get(target.resolve())
                if target_page is not None and fragment not in target_page.ids:
                    add_error(page, line, f"missing fragment '#{fragment}' in {display_path(target, site_root)}")

    for stylesheet in css_files:
        try:
            text = stylesheet.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            add_error(stylesheet, None, f"could not read as UTF-8 ({error})")
            continue

        problem = delimiter_error(text)
        if problem:
            position, message = problem
            add_error(stylesheet, line_number(text, position), message)

        without_comments = re.sub(
            r"/\*.*?\*/",
            lambda match: "\n" * match.group(0).count("\n"),
            text,
            flags=re.DOTALL,
        )
        for match in CSS_URL_PATTERN.finditer(without_comments):
            reference = match.group("value").strip()
            kind, target, _, reference_problem = local_target(reference, stylesheet, site_root)
            if kind == "external":
                continue
            if kind == "invalid":
                add_error(
                    stylesheet,
                    line_number(without_comments, match.start()),
                    f"invalid url('{reference}') ({reference_problem})",
                )
                continue

            local_reference_count += 1
            if not target.exists() or not target.is_file():
                add_error(
                    stylesheet,
                    line_number(without_comments, match.start()),
                    f"missing local file for url('{reference}')",
                )

    node = shutil.which("node")
    if js_files and not node:
        errors.append("JavaScript: Node.js is required to syntax-check .js files")
    elif node:
        for script in js_files:
            result = subprocess.run(
                [node, "--check", str(script)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                detail = next(
                    (line.strip() for line in result.stderr.splitlines() if "SyntaxError" in line),
                    "syntax check failed",
                )
                add_error(script, None, detail)

    print(f"Checking {project_name} ({display_path(site_root, site_root.parent.parent)})")
    print(f"  HTML: {len(html_pages)} page(s)")
    print(f"  Links/assets: {local_reference_count} local reference(s)")
    print(f"  JavaScript: {len(js_files)} file(s)")
    print(f"  CSS: {len(css_files)} file(s)", flush=True)

    if errors:
        print(f"\nFAILED with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("\nPASSED: all project checks succeeded.")
    return 0


def main():
    if len(sys.argv) != 3:
        print("Usage: check-project.py <project-name> <site-directory>", file=sys.stderr)
        return 2

    project_name = sys.argv[1]
    site_root = Path(sys.argv[2]).resolve()
    return run_checks(project_name, site_root)


if __name__ == "__main__":
    raise SystemExit(main())
