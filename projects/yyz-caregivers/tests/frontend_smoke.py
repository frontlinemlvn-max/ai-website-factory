#!/usr/bin/env python3

"""Dependency-free structural checks for the YYZ Caregivers static pilot."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys


PROJECT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT / "src"
PAGES = (
    "index.html",
    "about.html",
    "services.html",
    "contact.html",
    "intake.html",
    "faq.html",
    "privacy.html",
    "terms.html",
)


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attributes = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attributes.append((tag, dict(attrs)))


def check(condition, message, errors):
    if condition:
        print(f"  [PASS] {message}")
    else:
        print(f"  [FAIL] {message}")
        errors.append(message)


def luminance(hex_color):
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def main():
    errors = []
    print("YYZ Caregivers frontend smoke tests")

    check(all((SOURCE / page).is_file() for page in PAGES), "all eight approved HTML pages exist", errors)

    for page_name in PAGES:
        page = SOURCE / page_name
        if not page.is_file():
            continue
        text = page.read_text(encoding="utf-8")
        parser = Inspector()
        parser.feed(text)

        html_attrs = next((attrs for tag, attrs in parser.attributes if tag == "html"), {})
        metas = [attrs for tag, attrs in parser.attributes if tag == "meta"]
        links = [attrs for tag, attrs in parser.attributes if tag == "link"]

        check(html_attrs.get("lang") == "en-CA", f"{page_name} declares Canadian English", errors)
        check(parser.tags.count("h1") == 1, f"{page_name} has exactly one h1", errors)
        check(parser.tags.count("main") == 1, f"{page_name} has one main landmark", errors)
        check(any(meta.get("name") == "viewport" for meta in metas), f"{page_name} includes responsive viewport metadata", errors)
        check(any(meta.get("name") == "description" and meta.get("content") for meta in metas), f"{page_name} includes a description", errors)
        check(any(meta.get("name") == "robots" and meta.get("content") == "noindex, nofollow" for meta in metas), f"{page_name} remains excluded from indexing", errors)
        check(any(link.get("rel") == "stylesheet" and link.get("href") == "assets/css/styles.css" for link in links), f"{page_name} uses the shared stylesheet", errors)
        check("http://" not in text and "https://" not in text, f"{page_name} makes no external runtime reference", errors)
        check("style=" not in text, f"{page_name} contains no one-off inline style", errors)

    contact = (SOURCE / "contact.html").read_text(encoding="utf-8")
    intake = (SOURCE / "intake.html").read_text(encoding="utf-8")
    script = (SOURCE / "assets/js/main.js").read_text(encoding="utf-8")
    assessment_script = (SOURCE / "assets/js/assessment.js").read_text(encoding="utf-8")
    check("data-consultation-form" in contact and not re.search(r"<form[^>]+action=", contact), "contact form has no submission destination", errors)
    check("data-preview-submit disabled" in contact, "form preview is safely disabled without JavaScript", errors)
    check("event.preventDefault()" in script, "enhanced form prevents native submission", errors)
    check(not re.search(r"\b(fetch|XMLHttpRequest|localStorage|sessionStorage|sendBeacon)\b", script), "script contains no network or storage API", errors)
    check("form.reset()" in script, "successful preview clears entered values", errors)
    check('id="message-error"' in contact and "message-error" in contact.split('id="message"', 1)[1].split(">", 1)[0], "message length error is associated with the textarea", errors)
    check("fields.message.value.length > 500" in script, "script rejects messages longer than 500 characters", errors)
    approved_order = tuple(contact.index(marker) for marker in ('id="preferred-name"', 'id="email"', 'id="phone"', 'name="contact-method"'))
    check(approved_order == tuple(sorted(approved_order)), "contact controls follow the approved name, email, phone, method order", errors)

    check("data-support-assessment" in intake and not re.search(r"<form[^>]+action=", intake), "support assessment has no submission destination", errors)
    check("data-assessment-review disabled" in intake, "support assessment is safely disabled without JavaScript", errors)
    check("event.preventDefault()" in assessment_script, "support assessment prevents native submission", errors)
    check(not re.search(r"\b(fetch|XMLHttpRequest|localStorage|sessionStorage|sendBeacon|indexedDB)\b", assessment_script), "support assessment uses no network or browser storage API", errors)
    check("innerHTML" not in assessment_script and "insertAdjacentHTML" not in assessment_script, "support assessment renders visitor text without unsafe HTML insertion", errors)
    check("form.reset()" in assessment_script and "reviewContent.replaceChildren()" in assessment_script, "support assessment clears local answers and summary", errors)
    check('name="topics"' in intake and 'id="topics-error"' in intake, "support topics use an accessible required group", errors)
    check('name="acknowledgements"' in intake and 'id="acknowledgements-error"' in intake, "assessment acknowledgements use an accessible required group", errors)
    ack_local_tag = intake.split('id="ack-local"', 1)[1].split(">", 1)[0]
    ack_boundary_tag = intake.split('id="ack-boundary"', 1)[1].split(">", 1)[0]
    check("acknowledgements-error" in ack_local_tag and "acknowledgements-error" in ack_boundary_tag, "each assessment acknowledgement references its validation error", errors)
    limited_field_requirements = (
        ("assessment-name", "assessment-name-error", 'maximum: 80', "Reduce your preferred name"),
        ("assessment-municipality", "assessment-municipality-error", 'maximum: 80', "Reduce your city or municipality"),
        ("assessment-language", "assessment-language-error", 'maximum: 60', "Reduce your language preference"),
    )
    for field_id, error_id, maximum, message in limited_field_requirements:
        field_tag = intake.split(f'id="{field_id}"', 1)[1].split(">", 1)[0]
        check(error_id in field_tag and f'id="{error_id}"' in intake, f"{field_id} has an associated length error", errors)
        check(f'field: form.querySelector("#{field_id}")' in assessment_script and maximum in assessment_script and message in assessment_script, f"{field_id} has script-level length validation", errors)
    check("Nothing was sent or stored. This is not a care plan or recommendation." in intake, "review state states the non-sending and non-clinical boundary", errors)
    prohibited_fields = ("diagnosis", "medication-name", "health-card", "street-address", "care-plan-score")
    check(not any('name="' + field + '"' in intake for field in prohibited_fields), "support assessment contains no prohibited sensitive field", errors)
    check("mailto:frontline.mlvn@gmail.com?" not in intake and "tel:+14167315383?" not in intake, "assessment answers cannot be placed in contact links", errors)
    for page_name in PAGES:
        page_text = (SOURCE / page_name).read_text(encoding="utf-8")
        check('href="intake.html"' in page_text, f"{page_name} links to Support Needs", errors)

    robots = (SOURCE / "robots.txt").read_text(encoding="utf-8")
    sitemap = (SOURCE / "sitemap.xml").read_text(encoding="utf-8")
    check("Disallow: /" in robots, "pilot robots file blocks crawling", errors)
    check("<url>" not in sitemap and "https://" not in sitemap, "pilot sitemap contains no fabricated production URL", errors)

    asset_bytes = sum((SOURCE / relative).stat().st_size for relative in ("assets/css/styles.css", "assets/js/main.js", "assets/js/assessment.js"))
    check(asset_bytes < 100_000, f"combined CSS and JavaScript stay below 100 KB ({asset_bytes} bytes)", errors)

    css = (SOURCE / "assets/css/styles.css").read_text(encoding="utf-8")
    tokens = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", css))
    text_pairs = (
        ("white", "teal-700"),
        ("navy-900", "warm-white"),
        ("body", "warm-white"),
        ("muted", "warm-white"),
        ("success", "success-bg"),
        ("warning", "warning-bg"),
        ("error", "error-bg"),
        ("disabled", "disabled-bg"),
    )
    for foreground, background in text_pairs:
        ratio = contrast(tokens[foreground], tokens[background])
        check(ratio >= 4.5, f"{foreground} on {background} meets AA text contrast ({ratio:.2f}:1)", errors)

    control_ratio = contrast(tokens["control-border"], tokens["white"])
    check(control_ratio >= 3, f"form control border meets non-text contrast ({control_ratio:.2f}:1)", errors)

    if errors:
        print(f"\nFAILED: {len(errors)} check(s) need attention.")
        return 1

    print("\nPASSED: all YYZ Caregivers frontend smoke tests succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
