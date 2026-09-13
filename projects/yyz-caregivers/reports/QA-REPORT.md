# YYZ Caregivers — QA Report

- **Project:** `yyz-caregivers`
- **QA date:** September 10, 2026
- **Stage:** Independent functional QA after Support Needs Assessment implementation
- **Environment:** Factory local preview; Codex in-app Chromium; same-origin responsive harness; Python 3.9.6; Node.js
- **Overall status:** **PASSED**

## 1. QA Summary

The revised eight-page pilot passed route, link, asset, responsive, navigation, contact-form, assessment-review, data-clearing, content-safety, and factory-regression tests. Forty page-and-viewport combinations were measured at 320, 390, 768, 1024, and 1440 CSS pixels with no horizontal overflow, missing images, heading failures, or navigation-breakpoint failures. Both forms remained local. An eight-route browser harness recorded no warnings, errors, unhandled rejections, or failed resource events.

The Support Needs Assessment correctly validates its required groups and text limits, creates a neutral on-screen summary, safely renders visitor text, keeps contact links free of answers, preserves values while editing, and clears local state after confirmed reset. QA found two specification gaps and independently confirmed both corrections: `QA-003` now gives each acknowledgement direct error context, and `QA-004` now blocks over-limit optional text with linked field errors.

Pages tested: Home, About, Services, Contact, Support Needs Assessment, FAQ, Privacy, and Terms.

## 2. Journeys Tested

1. Every route → Support Needs navigation → assessment.
2. Assessment → empty review → linked errors → corrected answers → local summary.
3. Assessment summary → Edit my answers → retained values → review again.
4. Assessment summary → Start over → Keep my answers → Start over → Clear my answers.
5. Assessment summary → separate email/phone links, confirming no answers appear in either link.
6. Contact → empty errors → invalid email → over-limit message → correction → local success → Preview another request.
7. Home mobile header → open navigation → Escape close and focus return.
8. FAQ → native disclosure open and answer visibility.

## 3. Evidence

- Responsive matrix: 8 pages × 5 widths = 40 combinations.
- `./factory check yyz-caregivers`: passed; 8 HTML pages, 215 local references, 2 JavaScript files, and 1 CSS file.
- `python3 projects/yyz-caregivers/tests/frontend_smoke.py`: all assertions passed.
- `node --check` passed for `main.js` and `assessment.js`.
- `./factory test`: all 50 factory regression tests passed; no deployment occurred.
- Combined CSS and JavaScript: 40,959 bytes, below the maintained 100 KB budget.
- Browser console/resource harness: 8 routes tested; 0 issues.
- Server activity contained local `GET`/cached responses only; no form `POST` or remote runtime request was observed.

## 4. Test Results

| Area | Classification | Evidence |
|---|---|---|
| Eight routes | Passed | Every route loaded with a unique title, one `h1`, one main landmark, a description, current-page identification, and Support Needs links. |
| Links and assets | Passed | All 215 local references resolved; no missing image or resource event occurred. |
| Responsive layouts | Passed | No horizontal overflow across 40 combinations; mobile/desktop navigation matched its 960px breakpoint. |
| Assessment mobile sizing | Passed | At 320px and 390px the action filled its container; choice cards measured at least 52px high. |
| Mobile navigation | Passed | At 320px the menu expanded; seven navigation/CTA targets measured at least 48px; Escape collapsed it and returned focus. |
| Assessment empty validation | Passed | Empty review produced assessor, topic, and acknowledgement errors and focused the summary. |
| Correct-after-error behaviour | Passed | Corrections removed errors without clearing valid values. |
| Assessment review | Passed | Form hid, neutral review appeared, boundary text remained visible, and focus moved to its heading. |
| Safe text rendering | Passed | Script-like text stayed plain text; no script element was created or executed. |
| Edit and reset | Passed | Edit preserved answers and focused the heading. Keep retained answers. Confirmed Clear removed all values and summary content, reset the counter, and restored focus. |
| Contact-link safety | Passed | Email and phone links contained no assessment answers or query/body data. |
| No-send/no-storage boundary | Passed | No form destination, network, storage, download, or answer-serialization API exists. |
| Prohibited data | Passed | No diagnosis, medication, health-card, financial, street-address, emergency-detail, scoring, or care-plan field exists. |
| Optional text limits | Passed after retest | Over-limit name, municipality, and language values each produce a linked field error and prevent review. See resolved `QA-004`. |
| Acknowledgement errors | Passed after retest | Both inputs reference the shared error; only the missing control is marked invalid and the summary targets it. See resolved `QA-003`. |
| Contact form | Passed | Empty, invalid-email, 501-character message, correction, success, clearing, and restart-focus states passed. |
| FAQ disclosure | Passed | Native disclosure opened and exposed its answer. |
| No-JavaScript state | Passed by source/automated inspection | Both forms start disabled with explanations; navigation remains available before enhancement. |
| Accessibility basics | Passed | Language, landmarks, headings, native controls, labels, direct error associations, focus, summaries, current-page state, and contrast checks passed. |
| SEO pilot safeguards | Passed | Unique metadata, semantic headings, `noindex`, blocked robots file, and empty pilot sitemap remain present. |
| Obvious performance concerns | Passed | No framework, remote font, tracker, third-party runtime, or oversized raster asset was introduced. |

### Not tested

- Safari and Firefox execution
- A physical screen-reader or touch-device session
- Operating-system forced-colour and reduced-motion simulation
- Browser zoom controls beyond equivalent 320 CSS-pixel reflow
- Lighthouse or field Core Web Vitals measurement
- Production submission, storage, delivery, booking, or integrations because none are implemented

## 5. Resolved Defects

### QA-003 — Acknowledgement errors are not associated with each checkbox

- **Severity:** Medium
- **Status:** Resolved and independently retested
- **Feature:** Support Needs Assessment → Review your understanding
- **Steps:** Complete assessor and topic requirements, leave either acknowledgement unchecked, activate “Review my topics,” and inspect that checkbox's accessible description.
- **Expected:** Each invalid checkbox directly references an error message; the summary links to the first missing checkbox.
- **Actual after fix:** Both inputs reference the shared hint and error. When either box alone is missing, only that control receives `aria-invalid="true"`, the summary targets its ID, and the completed box remains valid.
- **Root cause:** The error was connected only to the containing fieldset, and group validation marked every acknowledgement invalid.
- **Resolution:** Added direct `aria-describedby` associations and limited invalid state to unchecked controls. Both one-missing combinations passed browser retesting.

### QA-004 — Optional text limits lack script-level validation

- **Severity:** Low
- **Status:** Resolved and independently retested
- **Feature:** Preferred name, City or municipality, Language preference
- **Steps:** Complete required groups, insert 81/81/61 characters through a path that bypasses native `maxlength`, then review.
- **Expected:** An associated length error prevents review.
- **Actual after fix:** Each over-limit field displays its specific linked error, receives `aria-invalid="true"`, and prevents review. Correcting all three clears the summary and inline errors without losing required selections; valid review then succeeds.
- **Root cause:** The JavaScript validator included the General note but omitted Preferred name, City or municipality, and Language preference.
- **Resolution:** Added a shared limited-field configuration, three associated inline errors, and regression checks. The original 81/81/61-character reproduction passed browser retesting.

## 6. Regression Status

All four QA defects are closed. After `QA-003` and `QA-004`, QA reran both one-missing acknowledgement combinations, all three over-limit fields together, live correction, answer preservation, valid review, edit focus, complete reset, the eight-route console/resource check, JavaScript syntax, project checks, the expanded smoke suite, and all 50 factory regression tests. No regression was found.

## 7. Launch Readiness

**READY FOR FINAL REVIEW**

No unresolved QA defect prevents the project from proceeding to the revised SEO stage. Production release remains prohibited and still requires updated SEO, Security, Performance, Accessibility, Final Review, explicit human approval, and release gates.

## 8. Handoff

Recommended owner: SEO and Content Specialist.

1. Validate the completed QA deliverable and advance the workflow to SEO.
2. Reassess the eighth page and confirmed contact/service-area content while preserving `noindex` and all non-sending safeguards.

No approval, deployment, Git commit, or push occurred during QA.
