# YYZ Caregivers — Website Architecture

Status: Architecture revised for a non-sending Support Needs Assessment prototype

> Change-control note — September 10, 2026: The owner approved a safer non-clinical direction. The new page is a browser-only Support Needs Assessment prototype for general consultation preparation. It must not ask for diagnoses, score needs, recommend a care plan, transmit or store entries, create a client relationship, or imply clinical review. “Client” replaces “patient.” A live submission workflow remains a separate future project requiring privacy, security, legal, operational, and professional review.

## 1. Project Summary

- **Project:** YYZ Caregivers
- **Website type:** Informational business website for a private-home personal support worker service
- **Primary objective:** Help people in the Greater Toronto Area understand the proposed service and take a clear, low-pressure step toward a consultation.
- **Target audience:** Older adults, adults who may need help with daily living, and family members or caregivers researching private-home support.
- **Primary conversion:** Contact YYZ Caregivers or complete a non-sending Support Needs Assessment preview that produces only an on-screen summary.
- **Pilot boundary:** This version demonstrates information architecture, content hierarchy, responsive behavior, and interaction design. It does not accept bookings, collect information, perform clinical assessment, diagnose, recommend care, determine eligibility, or make unverified claims about credentials, pricing, services, availability, or outcomes.

## 2. Assumptions

The following assumptions permit the pilot to proceed without presenting unverified business facts as truth:

- YYZ Caregivers initially intends to serve East Toronto and Durham Region, but exact municipalities and travel boundaries remain unconfirmed.
- The business offers non-clinical personal support in private homes. Every specific task shown in future copy must be confirmed as actually offered and within the assigned worker's training and permitted scope.
- The owner supplied public phone and email details, a preferred domain, and candidate images. Domain control, image ownership/model releases, pricing, and launch date remain unconfirmed.
- Deep navy, calming teal, warm white, soft grey, and an accessible system sans serif are pilot design assumptions rather than approved brand standards.
- The pilot will use fictional or clearly labeled placeholder scenarios. It will not fabricate testimonials, reviews, staff biographies, credentials, years in business, response times, or service outcomes.
- The consultation form and Support Needs Assessment are demonstrations only and will not transmit, email, persist, or store entries.
- No user accounts, booking engine, payments, clinical records, diagnosis list, medication details, or personal health information are required.
- Public contact hours are Monday-Friday, 9:00 a.m.-6:00 p.m. Eastern Time, with an expected response within 12 business hours; email is preferred.
- `frontline.mlvn@gmail.com` is the approved public and privacy contact for the pilot; the business address remains private.
- English is the pilot language. Additional language support is an open business decision.
- Production publication requires owner review of all service, employment, privacy, legal, accessibility, and contact information.

## 3. User Types

### Family decision-maker

A spouse, adult child, relative, or friend comparing support options. They need plain-language service information, signs of trust, clarity about next steps, and an easy way to contact the business.

### Prospective care recipient

An older adult or adult seeking help at home. They need respectful language, legible content, predictable navigation, accessible controls, and an experience that preserves dignity and personal agency.

### Referral or community contact

A community professional, neighbour, or organization looking for basic service and contact information to share. The site should make its service area, boundaries, and contact process easy to verify once the business supplies those facts.

### Business owner or content administrator

The person responsible for confirming service claims, contact details, privacy language, and future updates. The pilot has no login or CMS; updates are made directly in reviewed source files.

## 4. Key User Journeys

### Understand the service

Home → Services overview → Individual support categories → Service boundaries and owner-verification notes → Request a consultation.

Success means the visitor can explain what the service may offer, what the pilot does not promise, and how to ask a general question without providing sensitive health details.

### Decide whether the service may fit

Home → About → Services → FAQ → Contact.

Success means the visitor finds clear, non-pressuring information about the intended approach, service area, consultation process, and unanswered business details.

### Reach the business from a mobile device

Any page → Persistent primary “Request a consultation” action → Contact page → Complete the demonstration form or use a verified contact method when one is approved.

Success means the journey works by keyboard and touch, does not require account creation, and never asks for diagnosis, medication, health-card, financial, or emergency information.

### Prepare for a support conversation

Any page → Support Needs Assessment → choose broad daily-living topics and scheduling preferences → review an on-screen summary → contact YYZ Caregivers separately by email or phone.

Success means the visitor can organize general, non-clinical support needs without entering a diagnosis or other sensitive health details. The summary stays in the current page, is not scored as a care recommendation, and disappears on reset, refresh, or navigation.

### Find policy information

Any page footer → Privacy or Terms → Return to Contact or Home.

Success means visitors can locate policy pages from every route and understand that pilot policy text must be replaced with owner-reviewed production language before launch.

## 5. Sitemap and Information Architecture

```text
Home                         /
├── About                    /about.html
├── Services                 /services.html
├── FAQ                      /faq.html
├── Contact                  /contact.html
├── Support Needs Assessment /intake.html
├── Privacy Policy           /privacy.html
└── Terms                    /terms.html
```

The eight pages form a shallow structure so no important destination is more than one navigation action from the header or footer. “Request a consultation” always routes to the Contact page. “Explore support needs” routes to the assessment. The Services page remains a single pilot page; separate service-detail pages should be added only after the owner confirms a stable service catalogue and sufficient unique content.

### Support Needs Assessment boundary

The new route is an informational self-organization tool, not a patient intake, eligibility check, medical assessment, triage service, or care-plan generator. It must not use diagnosis dropdowns, collect health-card or medication data, ask for a street address, or infer risk. It may show a plain-language summary of the visitor's selections solely in the current browser page. The visitor must contact YYZ Caregivers separately; the summary is not attached or transmitted.

## 6. Page Specifications

### Home — `index.html`

- **Purpose:** Establish the proposed value, intended audience, service area, and safest next step.
- **Primary call to action:** Request a consultation.
- **Required sections:** Accessible header; trust-oriented hero; concise “support at home” introduction; proposed service-category cards; how the consultation process works; why clarity and dignity matter; service-area note; FAQ preview; closing CTA; global footer.
- **Required content:** Plain-language summary, pilot disclaimer, owner-review labels for unverified claims, and no statistics or outcome promises.
- **Components:** Header, mobile navigation, hero, service cards, process steps, reassurance panel, FAQ teaser, CTA band, footer.
- **Functionality:** Responsive navigation, skip link, contact-page links, and no automatic carousel, modal, or form.

### About — `about.html`

- **Purpose:** Explain the proposed business approach without inventing history, team size, credentials, or affiliations.
- **Primary call to action:** Explore services.
- **Required sections:** Mission framing; values such as dignity, respect, consistency, and clear communication; intended support approach; “facts to confirm before launch” panel; next-step CTA.
- **Required content:** Owner-approved organization story is pending. The pilot may describe principles, but it must not imply accreditation, insurance, screening, training, or guaranteed continuity unless verified.
- **Components:** Page header, values grid, approach narrative, verification notice, CTA band.
- **Functionality:** Standard links only.

### Services — `services.html`

- **Purpose:** Explain possible support categories and their limits in scannable language.
- **Primary call to action:** Ask about support needs.
- **Required sections:** Services introduction; proposed categories; what is not included in the pilot; how matching or consultation may work; service-area note; FAQ link; CTA.
- **Required content:** Candidate categories may include personal routine assistance, companionship, meal support, light household help, and mobility-related assistance, but every category and task must be owner-confirmed before publication.
- **Components:** Service cards, scope notice, process steps, service-area panel, CTA band.
- **Functionality:** Optional in-page jump links; no booking, eligibility decision, or clinical assessment.

### Contact — `contact.html`

- **Purpose:** Offer a calm, accessible way to begin a general consultation.
- **Primary call to action:** Review and submit the demonstration request.
- **Required sections:** Contact introduction; non-emergency and privacy notice; demonstration form; verified-contact placeholder; response-expectation placeholder; alternate next steps.
- **Required content:** Explain that the pilot does not send submissions and that visitors should not enter health, medication, financial, identification, or emergency information.
- **Components:** Form, field guidance, consent checkbox, status message, contact-details card, emergency-boundary notice.
- **Functionality:** Client-side demonstration validation only. A successful action displays an on-page message stating that nothing was sent or stored. No data leaves the browser.

### Support Needs Assessment — `intake.html`

- **Purpose:** Help a prospective client or family decision-maker organize broad, non-clinical support needs before contacting the business.
- **Primary call to action:** Review my support-needs summary.
- **Secondary action:** Contact YYZ Caregivers by email or phone after reviewing the summary.
- **Required sections:** Page introduction; non-emergency and privacy boundaries; who is completing the assessment; general contact preference; broad location; support topics; timing preferences; communication/accessibility preferences; optional general note; acknowledgement; review summary; reset control; separate contact choices.
- **Required content:** Repeatedly explain that this is a non-sending prototype, not medical advice, diagnosis, triage, eligibility determination, booking, or a care plan. Use “client,” “support needs,” “topics to discuss,” and “summary”; avoid “patient,” “clinical intake,” “recommended care plan,” and outcome promises.
- **Components:** Step indicator or clearly titled field groups, progress-independent navigation, native inputs, checkbox groups, radio groups, optional select controls, field guidance, error summary, inline errors, review panel, print guidance if later approved, reset confirmation, privacy notice, and emergency notice.
- **Functionality:** Validate locally, create an on-screen plain-language summary, and let the visitor revise or reset. Do not use a form destination, network request, email composition containing answers, URL query data, cookies, browser storage, analytics, scoring, automated recommendation, downloadable record, or backend.

#### Approved prototype fields

1. **Who is completing this?** Self; family/friend; substitute decision-maker or authorized representative; other/prefer not to say. Include guidance that authority must be confirmed directly before services are arranged.
2. **Preferred name** — optional and used only in the on-screen summary.
3. **Preferred follow-up method** — email, phone, or undecided. This records a preference only; the visitor still contacts the business separately.
4. **City or municipality** — optional; never request a street address. Explain the current general area is East Toronto and Durham Region and that coverage must be confirmed.
5. **General support topics** — multi-select choices labelled “topics to discuss,” not confirmed services: personal routines; mobility and getting around; meal preparation; light household routines; companionship and social connection; caregiver respite; accompaniment to appointments or errands; reminders and routine organization; another general need; unsure.
6. **When support may be useful** — mornings, afternoons, evenings, overnight, weekdays, weekends, flexible/unsure. These are preferences, not availability promises.
7. **Frequency to discuss** — one-time/short-term, a few times per week, daily, respite/occasional, flexible/unsure. Do not calculate price or eligibility.
8. **Communication and accessibility preferences** — large print or written follow-up, slower-paced conversation, language preference, mobility-access consideration for an in-person visit, another preference, none/unsure. Do not infer disability or diagnosis.
9. **General note** — optional, short, and preceded by a persistent warning not to enter diagnoses, medication details, health-card numbers, financial information, a street address, or emergency information.
10. **Acknowledgements** — required confirmations that the visitor understands nothing is sent or stored, the summary is not medical advice or a care plan, and urgent needs require appropriate emergency assistance.

#### Explicitly prohibited fields and behaviour

- Diagnosed conditions or suspected diagnoses
- Symptoms, medication names/doses, treatment history, health-card numbers, government identifiers, payment information, exact home address, or emergency details
- Fall-risk, dementia, wound, medication, or other clinical scoring
- Suitability, eligibility, staffing, price, schedule, or outcome recommendations
- Hidden profiling, preselected sensitive options, forced disclosure, file upload, signature capture, or consent bundled with marketing
- Sending the summary through `mailto:`, placing answers in a URL, or implying YYZ Caregivers received or reviewed it

#### Summary behaviour

The summary restates only the visitor's broad selections under “Topics you may want to discuss.” It must include “This is not a care plan or recommendation” and provide Edit, Start over, Email YYZ Caregivers, and Call YYZ Caregivers actions. Email and phone links must not contain the assessment answers. Reset clears all controls and returns focus predictably. Refreshing or leaving the page discards the summary.

### FAQ — `faq.html`

- **Purpose:** Answer common process and scope questions without making unsupported commitments.
- **Primary call to action:** Ask another question.
- **Required sections:** Service fit; proposed service area; consultation process; scheduling and pricing placeholders; privacy boundary; emergency boundary; owner-review notice.
- **Required content:** Questions must distinguish confirmed information from pilot assumptions. Pricing, minimum hours, worker qualifications, screening, insurance, cancellations, and availability remain “confirm with owner” topics.
- **Components:** Native disclosure elements where appropriate, grouped questions, CTA band.
- **Functionality:** Use semantic `details` and `summary` controls or always-visible content; no custom accordion is required.

### Privacy Policy — `privacy.html`

- **Purpose:** Explain the pilot's no-transmission behavior and reserve space for an owner-reviewed production privacy policy.
- **Primary call to action:** Contact YYZ Caregivers with a privacy question once verified contact details exist.
- **Required sections:** Pilot status; information not collected; local demonstration behavior; cookies and analytics status; third-party services status; production-review requirements; contact placeholder; last-reviewed date.
- **Required content:** Do not claim legal compliance. State accurately that the static pilot does not transmit the demonstration form and uses no analytics or marketing cookies.
- **Components:** Policy content layout, table of contents where useful, callout notice, footer.
- **Functionality:** Static content only.

### Terms — `terms.html`

- **Purpose:** State the pilot's informational limits and reserve space for approved production terms.
- **Primary call to action:** Return to Services or Contact.
- **Required sections:** Pilot-only notice; informational-use boundary; no care relationship created; no emergency use; accuracy and availability limitations; intellectual-property placeholder; external-link policy; owner-review requirement; last-reviewed date.
- **Required content:** All legal wording is draft information architecture, not legal advice or approved production terms.
- **Components:** Policy content layout, callout notice, related links, footer.
- **Functionality:** Static content only.

## 7. Component Architecture

### Global components

- **Skip link:** First focusable element, targeting the page's main content.
- **Site header:** Text-based YYZ Caregivers wordmark, desktop navigation, mobile menu trigger, and consultation CTA.
- **Primary navigation:** Current-page indication, predictable order, keyboard operation, and no hover-only access.
- **Page header:** Consistent eyebrow, `h1`, concise introduction, and optional supporting callout.
- **CTA band:** Reusable heading, supporting text, and one primary plus optional secondary action.
- **Site footer:** Main routes, policy routes, service-area placeholder, contact placeholder, and pilot status.

### Content components

- Hero, service card, values card, process step, reassurance panel, scope or verification notice, service-area panel, FAQ item, policy section, breadcrumb where useful, and empty-state/contact placeholder.
- Cards must remain readable without icons or images; visuals supplement rather than carry meaning.
- Notices use text labels and icons only as redundant cues, never colour alone.

### Form components

- Text input, email or phone preference, select/radio group for a broad inquiry category, textarea for a general message, consent checkbox, field-level error, error summary, and non-sending success status.
- Labels remain visible. Placeholder text is optional guidance and never replaces a label.
- The form must explicitly discourage sensitive health, identity, financial, or emergency details.

## 8. Functional Requirements

### Core pilot features

- Eight linked static HTML pages with a consistent header, footer, navigation, consultation CTA, and Support Needs Assessment route.
- Mobile navigation that works with keyboard, touch, and screen-reader state announcements.
- Demonstration inquiry form with client-side validation and a clear “not sent or stored” result.
- Verified click-to-call and email links using 416-731-5383 and frontline.mlvn@gmail.com, with email identified as preferred.
- Browser-only Support Needs Assessment that validates accessibly and produces a temporary, non-clinical on-screen summary without transmitting or storing answers.
- Accessible FAQ presentation, visible focus, skip navigation, and reduced-motion support.
- Service-area information framed as a GTA pilot assumption, not a guaranteed coverage claim.
- Local assets only; no trackers, third-party widgets, or remote font dependencies.

### Optional future features

- Production form delivery through an approved privacy-conscious provider.
- Consent-aware analytics, CRM routing, scheduling, map/service-area tools, multilingual content, or a CMS.
- Individual service pages after the service catalogue is confirmed.
- None of these options may be added automatically; each requires an explicit business, privacy, security, and maintenance decision.

## 9. Data Requirements

The pilot requires no database and stores no visitor data. Both forms process values only in page memory and must discard them when reset, reloaded, closed, or left. No answers may be placed in URLs, logs, email links, cookies, analytics events, browser storage, downloaded files, or print output by default.

The Support Needs Assessment temporarily holds only the approved broad fields listed in its page specification. Those values exist solely to render the on-screen summary and are not business records. There is no client, diagnosis, condition, risk, care-plan, recommendation, staff, schedule, pricing, consent-record, or submission entity in the pilot.

If a production inquiry form is approved later, its minimum proposed data is:

- Name or preferred form of address
- One chosen contact method
- General inquiry category
- Broad service area or municipality
- General, non-sensitive message
- Consent acknowledgement and submission time

Do not request diagnosis, medication, treatment, health-card number, government identification, payment information, detailed care history, or emergency information. Before production, the owner must approve the exact fields, purpose, retention period, access rules, deletion process, vendor, privacy notice, and incident response plan.

## 10. Authentication and Authorization

No authentication, registration, password reset, user role, dashboard, or protected page is required. The pilot has no administrative interface. If a CMS or CRM is approved later, its access model must be designed separately with least-privilege roles, multi-factor authentication where supported, auditability, and documented offboarding.

## 11. Integrations

### Pilot integrations

None. The pilot must not load analytics, maps, chat widgets, remote fonts, social embeds, form processors, calendars, payment services, or CRM scripts.

### Production integrations requiring approval

- Form delivery or email provider
- Spam protection that does not create an unnecessary accessibility or privacy barrier
- Consent-aware analytics
- CRM or scheduling platform
- Map or service-area visualization

Each proposed integration requires a documented purpose, data-flow review, accessibility check, security review, cost/ownership decision, failure fallback, and removal plan before implementation.

## 12. Recommended Technology Stack

- **Frontend:** Semantic HTML5, modern CSS, and minimal vanilla JavaScript.
- **Frontend architecture:** One HTML file per route; shared styles in `src/assets/css/styles.css`; progressive enhancement in `src/assets/js/main.js`; local optimized images in `src/assets/images/`; no runtime framework.
- **Backend requirements:** None for the pilot. A production form backend or provider is a separate approved scope item.
- **Database:** None.
- **Authentication:** None.
- **Build process:** None required; files should run directly through the factory preview command.
- **Hosting:** Local factory preview during the pilot.
- **Deployment:** Vercel may be considered only after the release-readiness and explicit human approval gates; no project link should be created during architecture or design.
- **Analytics:** None in the pilot.
- **CMS:** None in the pilot; source-controlled content is sufficient at this scale.

Proposed source structure:

```text
src/
├── index.html
├── about.html
├── services.html
├── contact.html
├── intake.html
├── faq.html
├── privacy.html
├── terms.html
├── assets/
│   ├── css/styles.css
│   ├── js/main.js
│   └── images/
├── robots.txt
└── sitemap.xml
```

## 13. Responsive Design Requirements

- **Mobile first (below 768px):** Single-column content, full-width primary actions where useful, compact header, explicit menu control, no horizontal scrolling at 320 CSS pixels, and touch targets designed to be comfortably operable.
- **Tablet (768–1023px):** Two-column cards where content length permits, increased page padding, and navigation that may remain collapsed if labels do not fit comfortably.
- **Desktop (1024px and above):** Constrained reading widths, two- or three-column supporting grids, visible primary navigation, and balanced whitespace. Do not stretch paragraphs across the full viewport.
- Navigation, form order, headings, and content meaning remain identical across breakpoints.
- Essential actions must not depend on hover, fine pointer control, device orientation, or animation.
- Test at content-driven widths rather than targeting specific devices only.

## 14. Accessibility Requirements

The pilot targets WCAG 2.2 AA as a design and implementation goal, subject to specialist verification.

- Use one descriptive `h1` per page and a logical heading hierarchy.
- Use semantic landmarks, lists, buttons, links, labels, fieldsets, legends, and native disclosure controls.
- Provide a visible skip link and strong focus indicators that remain visible against every background.
- Meet AA text and interface contrast targets; brand colours must be tested before approval.
- Keep body text comfortably readable, allow browser zoom, and avoid fixed-height text containers.
- Ensure the menu, FAQ, and form work fully by keyboard and expose accurate names, roles, values, and expanded states.
- Provide text alternatives for meaningful imagery; decorative images use empty alternative text.
- Do not use ageist, infantilizing, fear-based, or autonomy-reducing language or imagery.
- Respect `prefers-reduced-motion` and avoid auto-playing, flashing, parallax, or essential animation.
- Form errors must be identified in text, associated with fields, summarized when multiple, and announced without moving focus unexpectedly.
- Complete keyboard, screen-reader, zoom/reflow, contrast, and reduced-motion testing before release approval.

## 15. SEO Requirements

- Give every page a unique, accurate title and concise meta description without keyword stuffing or unsupported claims.
- Use one `h1`, logical subheadings, descriptive link text, and natural GTA-focused language where relevant.
- Add canonical URLs only after a production domain is approved.
- Generate `sitemap.xml` and `robots.txt` from the final public URLs; pilot files must not point to a fabricated domain.
- Include Open Graph metadata with a local approved image before production.
- Organization or LocalBusiness structured data may be considered only after the legal name, public contact information, service area, and business details are verified. Do not use ratings, reviews, medical categories, prices, or credentials in structured data without evidence.
- Keep Privacy and Terms indexable only when their content is production-approved.
- Use clear local service wording, but do not create location pages without genuine, distinct service information.

## 16. Performance Requirements

Project performance targets for the pilot are:

- No framework, third-party runtime, remote font, tracker, or unused library.
- Combined production CSS and JavaScript target below 100 KB uncompressed, excluding images.
- Prefer SVG for simple graphics and AVIF/WebP with width and height attributes for photographs.
- Keep initial above-the-fold imagery appropriately sized; lazy-load below-the-fold images.
- Target Largest Contentful Paint at or below 2.5 seconds, Interaction to Next Paint at or below 200 milliseconds, and Cumulative Layout Shift at or below 0.1 during representative testing.
- Cache versioned static assets in production and keep HTML updates straightforward to invalidate.
- The experience must remain usable if JavaScript fails, except for the explicitly labeled demonstration form enhancement and mobile menu; navigation still requires a functional fallback.

These are internal acceptance targets, not claims about current field performance. Measurements must be recorded during Performance review.

## 17. Security Requirements

- Keep the pilot static and dependency-light; do not place secrets, API keys, tokens, personal records, or production identifiers in source files.
- Treat every future form value as untrusted. Production submission requires server-side validation, length limits, allow-listing where appropriate, safe output handling, rate limiting, and accessible spam controls.
- The assessment must use no network or storage API and must never serialize answers into a URL, `mailto:` link, analytics event, console output, or downloadable file.
- Broad support-topic choices must not be mapped to diagnoses, risk levels, worker matches, prices, schedules, or care recommendations.
- Do not collect personal health information in the general inquiry path. If future operations require sensitive information, stop and design a separately reviewed system rather than extending this form casually.
- Use HTTPS in production and define appropriate security headers during release preparation, including a content security policy compatible with approved assets and integrations.
- External links must be explicit and use safe new-window behavior only when truly necessary.
- Avoid exposing private staff data, schedules, client information, internal documents, or unpublished contact details.
- Review dependencies and deployment configuration before release, even though the pilot intends to use no runtime dependencies.
- The static site must not imply emergency monitoring, medical advice, guaranteed response, or an established care relationship.

## 18. Development Phases

1. **Architecture:** Confirm this revised document, assessment fields, prohibited behaviour, open decisions, and pilot boundaries.
2. **UI/UX revision:** Add the eighth-page layout, multi-step or grouped-form behaviour, review summary, error/reset states, privacy language, and mobile interaction details.
3. **Content verification:** Obtain owner-approved service scope, contact information, service area, organization story, claims, and policy direction. Until then, keep pilot labels visible.
4. **Frontend development:** Build the eight static pages and shared local assets with progressive enhancement; keep both forms non-sending.
5. **Functional QA:** Test navigation, links, form behavior, content consistency, and responsive layouts.
6. **Specialist review:** Complete SEO/content, security, performance, and accessibility audits with recorded evidence.
7. **Final review:** Re-test the complete pilot and document every unresolved production item.
8. **Human approval and release preparation:** Approve verified content, privacy/legal text, real contact details, domain, hosting link, and deployment plan separately.
9. **Deployment:** Run the factory release and deployment gates only after explicit authorization.

## 19. Acceptance Criteria

Architecture is ready for Design when:

- The eight-page sitemap, page purposes, primary actions, and reusable components are documented.
- The pilot/non-production boundary and owner-verification requirements are visible to downstream agents.
- No backend, database, authentication, payment, booking, health-record, or third-party integration is assumed.
- The non-sending behaviour, temporary summary, approved support-topic fields, and prohibited sensitive fields are unambiguous.
- Responsive, accessibility, SEO, performance, and security requirements are actionable.

The website is ready for final human approval only when:

- All eight pages are implemented with consistent navigation and no broken local links.
- Required content is complete, readable, responsive, keyboard-accessible, and free of placeholder domains or fake contact actions.
- The demonstration form validates accessibly, clearly states that nothing is sent, and stores or transmits no data.
- The Support Needs Assessment produces no diagnosis, score, care recommendation, price, match, or implied submission; its answers disappear on reset, refresh, or navigation.
- Every public service, area, credential, screening, insurance, price, availability, response-time, testimonial, and business-history claim has owner-supplied evidence or is removed.
- Privacy and Terms content has received appropriate owner and professional review for the real operating model.
- Automated factory checks and specialist QA, SEO, security, performance, and accessibility reviews pass with no unresolved launch blocker.
- Production hosting, domain, form processing, analytics, and contact details are separately approved.
- The human approval and release-readiness gates pass before deployment.

## 20. Risks and Open Decisions

### Launch-blocking decisions for any production version

- Legal ownership/registration details and exact East Toronto and Durham Region service boundaries; the public phone/email and private-address choice are owner supplied
- Confirmed service catalogue, exclusions, operating hours, consultation process, scheduling model, prices, minimum visits, cancellations, and availability language
- Evidence and approved wording for worker qualifications, training, screening, insurance, supervision, languages, and any professional or organizational affiliations
- Approved organization story, staff information, photography rights, testimonials, consent records, and brand identity
- Production form fields, recipient, vendor, retention, access, deletion, consent, privacy notice, spam control, and incident handling
- Owner-reviewed Privacy Policy, Terms, disclaimers, accessibility process, and emergency/non-clinical boundaries
- Production domain, hosting ownership, analytics decision, maintenance owner, and content update process

### Delivery risks

- Generic caregiving language can accidentally imply medical services, guaranteed outcomes, or verified credentials. Content and structured data need claim-by-claim review.
- Visitors may disclose sensitive information even when not asked. Form design must minimize fields, repeat clear warnings, and provide a safer follow-up process before production.
- Visitors may mistake the assessment summary for professional advice or believe it was submitted. Page title, introduction, review state, contact actions, and confirmation text must repeat the non-clinical and non-sending boundary.
- Older visitors and stressed family members may have accessibility, literacy, language, or device constraints. Design must prioritize readability and predictable interactions over decorative novelty.
- Placeholder contact details or a form that appears live can mislead visitors. The pilot must label all non-functional actions conspicuously.
- A GTA-wide claim may overstate the real service area. Location language stays provisional until confirmed.

No unresolved item above blocks pilot design, because the pilot will label assumptions and remain local. These items block removal of pilot labels and any production release.

## 21. Handoff to the UI/UX Designer

Revise the warm, calm, highly legible design into an eight-page business website using this information architecture: Home, About, Services, Contact, Support Needs Assessment, FAQ, Privacy, and Terms. Use the pilot navy/teal/warm-neutral direction as provisional, not final branding.

The design must include:

- A text wordmark, responsive header, keyboard-accessible mobile menu, strong focus states, skip link, and consistent footer
- Reusable hero, service-card, process-step, values-card, verification-notice, service-area, FAQ, policy-content, form, and CTA patterns
- A primary “Request a consultation” journey that always leads to Contact
- A demonstration form that discourages sensitive information and unmistakably confirms that nothing was sent or stored
- A separate Support Needs Assessment using the approved broad field groups, strong non-emergency/privacy boundaries, accessible validation, a temporary “Topics you may want to discuss” summary, Edit and Start over controls, and contact links that never include answers
- No diagnosis selector, clinical language, scoring, triage, care-plan recommendation, price calculation, suitability decision, storage, submission, print-by-default, or download
- Mobile-first layouts that work from 320 CSS pixels upward without horizontal scrolling
- Respectful imagery direction that avoids stereotypes, fear, medical theatre, fabricated staff, and unsupported trust signals
- Visible pilot/verification treatment for all unconfirmed service, contact, policy, and business information

Carry forward these unconfirmed assumptions: exact municipalities, service catalogue, logo/photo usage rights, credentials, screening, insurance, pricing, availability, business story, live form processing, production policies, domain control, and launch date. Confirmed defaults are public phone 416-731-5383, public/privacy email frontline.mlvn@gmail.com, email preferred, Monday-Friday 9:00 a.m.-6:00 p.m. Eastern Time, response within 12 business hours, and no public address. Do not resolve remaining facts through invented copy or visual badges. The next required output is a revised `design/UI-UX-SPEC.md`.
