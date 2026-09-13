# Changelog

All meaningful changes to yyz-caregivers should be documented here.

## 2026-09-12 — Accessibility follow-up: A11Y-004 fix

- Found and fixed A11Y-004: the Support Needs Assessment's "topics" checkbox group had `required` misapplied to only the "Personal routines" checkbox, mismatching the fieldset's "choose at least one" legend and misleading assistive technology.
- Removed the misplaced `required` attribute from `topic-routines` in `src/intake.html`; group-level validation in `assets/js/assessment.js` and the visible "(required)" legend text already enforced and communicated the actual requirement.
- Verified the two `acknowledgements` checkboxes correctly keep individual `required` attributes, since both statements must be confirmed.
- Reran the frontend smoke suite; all checks, including the accessible required-group check, passed.
- Documented the finding and fix as an addendum to `reports/ACCESSIBILITY-REPORT.md`; no other source file, approval, deployment, commit, or push occurred.

## 2026-09-11 — Eight-page performance review

- Rebuilt the performance report for all eight routes, including the Support Needs Assessment.
- Measured 129,648 bytes of complete uncompressed source and 40,959 bytes of combined CSS and JavaScript.
- Recorded twenty-sample localhost response baselines for Home and Support Needs, plus exact page, image, script, and request inventories.
- Verified deferred scripts, explicit image dimensions, system fonts, no remote resources, the frontend smoke suite, both JavaScript syntax checks, project checks, and all 50 factory regression tests.
- Attempted Lighthouse measurement, documented that the sandbox could not attach to Chrome, and made no unsupported Core Web Vitals or score claim.
- Found no current performance defect and made no source optimization; production measurement, compression, caching, and future media/integration budgets remain release work.
- Left the project in Performance; no stage advance, approval, deployment, commit, or push occurred.

## 2026-09-10 — Eight-page security review

- Rebuilt the security report for all eight routes, including the Contact preview and Support Needs Assessment.
- Verified that both forms remain non-sending and use no network, browser storage, answer-filled links, unsafe HTML rendering, uploads, or external runtimes.
- Found no currently exploitable vulnerability, exposed secret signature, dependency manifest, environment/private-key file, symlink, or project-local executable.
- Passed project checks, frontend smoke tests, both JavaScript syntax checks, and all 50 factory regression tests.
- Recorded production-only requirements for HTTPS response headers, any future live form, dependencies, secrets, and third-party integrations.
- Left the project in Security; no source-code change, stage advance, approval, deployment, commit, or push occurred.

## 2026-09-10 — Eight-page SEO review

- Rebuilt the SEO report for the revised eight-page site, including the Support Needs Assessment.
- Verified unique page metadata, one `h1` per route, logical headings, basic Open Graph metadata, 215 local references, and the frontend smoke suite.
- Confirmed that the assessment is positioned as a private, non-sending organizational tool rather than a diagnosis, medical intake, or care-plan system.
- Recorded production dependencies for domain control, canonical and social URLs, image rights, structured data, verified operating claims, and coordinated indexability changes.
- Flagged the legacy “GTA” footer wording for later alignment with “East Toronto and Durham Region.”
- Left the project in SEO; no source-code change, stage advance, approval, deployment, commit, or push occurred.

## 2026-09-10 — QA-003 and QA-004 corrections

- Fixed QA-003 by directly associating the shared acknowledgement error with both checkboxes and marking only unchecked controls invalid.
- Fixed QA-004 by adding accessible script-level maximum-length validation for Preferred name, City or municipality, and Language preference.
- Added smoke-test coverage for every new error association and validator configuration.
- Independently retested both one-missing acknowledgement cases, all three over-limit fields, live correction, valid review, edit/reset, clearing, console/resources, project checks, JavaScript syntax, and all 50 factory tests.
- Closed both findings and left the project in QA; no approval, deployment, commit, or push occurred.

## 2026-09-10 — Eight-page QA retest

- Advanced the revised project from Development to QA and independently retested all eight routes, both non-sending forms, navigation, responsive layouts, console/resource behaviour, and factory regressions.
- Passed 40 responsive route combinations, 215 local references, the frontend smoke suite, both JavaScript syntax checks, and all 50 factory tests.
- Opened QA-003 (Medium) for missing per-checkbox acknowledgement error associations and QA-004 (Low) for optional short-text limits that lack script-level rejection.
- Left the project in QA for fixes; no frontend fix, approval, deployment, commit, or push occurred.

## 2026-09-10 — Support Needs Assessment frontend

- Added `src/intake.html` as the eighth local-pilot route and linked Support Needs from every header and footer.
- Added five accessible assessment field groups, broad support-topic choices, privacy/emergency boundaries, a neutral local review summary, edit state, inline reset confirmation, and verified contact information.
- Added `src/assets/js/assessment.js` for local validation, safe text-node summary rendering, focus management, editing, and complete clearing without network or browser-storage APIs.
- Extended the shared stylesheet with responsive assessment layouts, native choice-card states, review/reset surfaces, forced-colour treatment, and print suppression.
- Expanded the smoke suite to cover eight pages, link consistency, no submission destination, no network/storage or unsafe HTML APIs, required groups, prohibited sensitive fields, contact-link safety, clearing, and the combined asset budget.
- Kept the site local and `noindex`; no backend, integration, diagnosis field, score, recommendation, pricing logic, commit, push, approval, or deployment was added.

## 2026-09-10 — Support Needs Assessment UI/UX design

- Added the complete eighth-page layout, five assessment field groups, mobile/desktop behaviour, choice-card pattern, local review summary, edit state, inline reset confirmation, and no-JavaScript fallback.
- Defined exact field order, optional/required logic, character limits, validation messages, focus management, neutral review styling, and temporary data-clearing behaviour.
- Added confirmed contact, availability, privacy-contact, business-hours, and response wording to the design content system.
- Prohibited diagnosis controls, clinical language, scoring, triage, recommendations, eligibility/pricing logic, implied submission, downloads, answer-filled contact links, analytics, and storage.
- Advanced the revised workflow to Design; all previous implementation and specialist reports remain stale until the eighth page is built and retested.

## 2026-09-10 — Support Needs Assessment architecture

- Replaced the proposed diagnosis/care-plan intake with an approved non-sending Support Needs Assessment prototype.
- Added `intake.html` to the architecture sitemap and defined its purpose, field groups, temporary review summary, accessibility behaviour, prohibited data, and explicit non-clinical boundary.
- Prohibited diagnosis selection, health and medication details, scoring, triage, eligibility decisions, price calculations, care recommendations, submission, storage, analytics, downloads, and third-party integrations.
- Confirmed “client” terminology, Eastern Time contact hours, a 12-business-hour response expectation, `frontline.mlvn@gmail.com` as the public/privacy contact, and “Now accepting new client inquiries” wording.
- Returned the workflow to Architecture because every downstream pilot review predates the new eighth page.

## 2026-09-09 — Owner inputs and intake-form scope change

- Recorded the owner-supplied legal business name, public phone and email, email preference, contact-hour and response-time draft, private-address preference, initial service area, preferred domain, availability request, and candidate brand imagery.
- Added verified public email and phone links to the local pilot while retaining the non-sending demonstration form and pilot safeguards.
- Recorded the owner's NOT APPROVED decision and moved the project to Blocked because the requested diagnosis/care-plan intake workflow materially changes the approved architecture and privacy risk.
- Did not add health-information fields, a backend, storage, email submission, third-party services, production metadata, deployment settings, or external integrations.
- Marked clinical responsibility, privacy status, secure data handling, services, qualifications, screening, insurance, pricing, exact municipalities, response wording, and image rights as unresolved.

## 2026-09-09 — QA defect corrections

- Fixed QA-001 by associating an accessible message-length error with the General message field and adding script-level validation that prevents the preview-success state when browser or programmatic input exceeds 500 characters.
- Fixed QA-002 by moving Preferred contact method below Email address and Phone number so the rendered and assistive-technology order matches the approved UI/UX specification.
- Added automated regression checks for the length guard, accessible error association, and approved form order.
- Preserved the non-sending pilot controls: no form destination, network request, browser storage, or new dependency was added.
- Both corrections are ready for independent QA retesting.
