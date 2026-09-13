# Development

Project: yyz-caregivers

## Technology Stack

Semantic HTML5, mobile-first CSS, and small vanilla JavaScript enhancements. The site has no framework, package manager, build dependency, backend, database, analytics, remote font, or third-party runtime request. All eight routes share `src/assets/css/styles.css` and `src/assets/js/main.js`; `intake.html` adds the isolated `src/assets/js/assessment.js` interaction.

## Prerequisites

Python 3 is recommended for the factory preview and project test script. Node.js is used by the factory checker to confirm JavaScript syntax. No packages need to be installed.

## Installation

No installation is required. The files in `src/` are the complete pilot website.

## Development

From the factory root, run:

```text
./factory preview yyz-caregivers
```

The preview command serves `projects/yyz-caregivers/src/` and prints the local address. Edit the HTML, shared stylesheet, script, or local SVG assets and refresh the browser.

Important implementation decisions:

- Navigation remains visible and usable without JavaScript. JavaScript progressively enhances it into a mobile disclosure below 960px.
- The Contact form is disabled when JavaScript is unavailable. With JavaScript, it validates and clears values entirely in the browser; it has no action URL, network request, storage call, or production destination.
- The Support Needs Assessment is also disabled without JavaScript. It validates only the minimum required choices, renders visitor text with DOM text nodes, shows a temporary local summary, supports editing and confirmed reset, and never sends, stores, scores, recommends, downloads, or adds answers to email/phone links.
- All pages retain a visible local-pilot warning and `noindex, nofollow` metadata.
- `robots.txt` blocks crawling and `sitemap.xml` is intentionally empty until a production domain and public routes are approved.
- The text wordmark and two SVG files are local pilot assets. Supplied candidate imagery has not been added because usage rights and representation remain unconfirmed.
- The approved light border remains on decorative surfaces. Form controls use a darker `--control-border` token so their white boundaries meet the 3:1 non-text contrast target.

## Build

There is no build step. Serve or deploy the contents of `src/` directly only after the factory release and human approval gates are satisfied.

## Testing

Run the maintained checks from the factory root:

```text
./factory check yyz-caregivers
python3 projects/yyz-caregivers/tests/frontend_smoke.py
./factory validate-stage yyz-caregivers
```

The checks cover HTML structure, internal links and fragments, local assets, CSS/JavaScript syntax, the eight-page route set, page metadata, pilot indexing controls, both non-sending form safeguards, safe text rendering, data clearing, required groups, contact-link safety, and the static asset budget. Live browser review should additionally cover the menu, Escape-key close behaviour, keyboard focus, both form journeys, 320px reflow, 200% zoom, reduced motion, forced colours, and browser console output.

### Development-stage results

- `./factory check yyz-caregivers`: passed with eight HTML pages, 215 local references, two JavaScript files, and one CSS file.
- `python3 projects/yyz-caregivers/tests/frontend_smoke.py`: passed every structural, metadata, privacy-safety, indexing, contrast, and asset-budget check.
- `./factory validate-stage yyz-caregivers`: passed every Development-stage gate.
- Assessment browser review: empty review exposed the linked assessor, topic, and acknowledgement errors; a valid review rendered the selected answers and boundary language without interpreting visitor text as HTML.
- Assessment state review: Edit preserved the answers; Keep returned from reset confirmation without clearing; Clear removed the name, choices, note, review summary, and character count.
- Responsive assessment review: no horizontal overflow at 320px or 960px; the small-screen action filled its container after correction, and the desktop navigation stayed within the header.
- Browser console review: no warnings or errors were recorded during the assessment journeys.

Independent QA must still complete the full eight-route browser sweep plus screen-reader, 200% browser zoom, forced-colour, reduced-motion, touch, and cross-browser review before release consideration.

## Implemented Pages and Components

- Home, About, Services, Contact, Support Needs Assessment, FAQ, Privacy, and Terms
- Pilot-status bar, responsive site header and navigation, text wordmark, page headers, content cards, service cards, process steps, notices, service-area panel, native FAQ disclosures, consultation form, CTA bands, policy layouts, and footer
- Accessible field labels, conditional email/phone validation, linked error summary, character count, local success state, skip link, current-page indicators, visible focus styles, and reduced-motion support
- Native assessment choice cards, required-group validation, neutral local review summary, safe text rendering, edit/reset focus management, no-JavaScript boundary, and data-clearing controls

## Known Limitations

- Exact services and municipalities, qualifications, screening, insurance, pricing, actual capacity, policies, domain control, candidate-image rights, and launch date remain unverified.
- The consultation form is deliberately a non-sending demonstration. Production delivery requires a separately approved backend or provider plus privacy, security, retention, accessibility, and incident-response decisions.
- The Support Needs Assessment is deliberately not a patient intake, diagnosis tool, clinical assessment, triage flow, eligibility decision, pricing calculator, booking, or care-plan generator.
- Privacy and Terms are pilot explanations, not approved legal documents.
- The implementation is ready for independent QA, not public launch.
