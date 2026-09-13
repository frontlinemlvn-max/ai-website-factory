# YYZ Caregivers — SEO & Content Report

- **Project:** `yyz-caregivers`
- **Review date:** September 10, 2026
- **Stage:** SEO and content specialist review
- **Environment:** Eight-page static local pilot
- **Overall status:** **PASSED FOR LOCAL PILOT; PUBLIC INDEXING NOT READY**

## 1. SEO Summary

The revised eight-page pilot has a sound SEO and content foundation. Every route has a unique title, unique meta description, one descriptive `h1`, logical heading order, Canadian English, descriptive internal links, and complete basic Open Graph title/description/type metadata. The project checker resolves all 215 local references. The Support Needs Assessment is accurately presented as a private, non-sending organizational tool—not as a patient intake form, diagnosis tool, medical assessment, or care-plan generator.

The site intentionally remains outside search results. Every page uses `noindex, nofollow`, `robots.txt` blocks crawling, and the sitemap contains no fabricated production URLs. Canonicals, `og:url`, `og:image`, and structured data remain absent because `getcarequick.ca`, image rights, and several operating facts are not yet verified.

These are correct pilot safeguards, not defects. They become release blockers only when the owner requests a public launch.

## 2. Search Intent and Page Roles

| Page | Primary purpose | Intended search intent | Local relevance |
|---|---|---|---|
| Home | Introduce the proposed private-home support service | Understand the offer and choose a next step | East Toronto and Durham Region |
| About | Explain the proposed approach and values | Evaluate fit and trust | Brand-level |
| Services | Explain proposed non-clinical support categories and limits | Compare possible support | East Toronto and Durham Region |
| Support Needs | Organize general support topics before a conversation | Prepare for an inquiry | Service-area context only |
| FAQ | Answer common questions about fit, process, privacy, and pricing | Resolve questions | Service-area explanation |
| Contact | Provide verified contact details and a non-sending inquiry preview | Contact the business | Local contact information |
| Privacy | Explain current pilot data handling | Understand privacy boundaries | No geographic targeting needed |
| Terms | Explain pilot limitations | Understand website boundaries | No geographic targeting needed |

The approved geographic wording is **East Toronto and Durham Region**. Broad “GTA” references are not false, but they are less precise and should be aligned to the approved wording during the production content pass.

## 3. Metadata Review

| Route | Current title | Current meta description | Result |
|---|---|---|---|
| `index.html` | YYZ Caregivers \| Private-home support pilot in East Toronto and Durham | Explore a local pilot for proposed private-home personal support services in East Toronto and Durham Region. | Pass; descriptive and unique |
| `about.html` | About the proposed approach \| YYZ Caregivers | Learn about the intended values and respectful approach behind the YYZ Caregivers local pilot. | Pass |
| `services.html` | Proposed private-home support services \| YYZ Caregivers | Explore proposed non-clinical personal support categories for the YYZ Caregivers East Toronto and Durham pilot. | Pass |
| `intake.html` | Organize support needs \| YYZ Caregivers | Organize general support topics in a private, non-sending browser preview for a future YYZ Caregivers conversation. | Pass; accurately non-clinical |
| `faq.html` | Frequently asked questions \| YYZ Caregivers | Read answers about the YYZ Caregivers pilot, proposed support, consultation, privacy, pricing, and service area. | Pass |
| `contact.html` | Preview a consultation request \| YYZ Caregivers | Preview a private, non-sending consultation request for the local YYZ Caregivers pilot. | Pass; does not imply submission |
| `privacy.html` | Pilot privacy information \| YYZ Caregivers | Understand what the local YYZ Caregivers pilot does and does not collect, send, or store. | Pass |
| `terms.html` | Pilot terms and limitations \| YYZ Caregivers | Read the informational limits and draft terms for the local YYZ Caregivers website pilot. | Pass |

No title or description is duplicated or misleading. The Home title is long but readable; shortening it is optional after final service and domain decisions. Do not add “PSW,” “senior care,” specific municipalities, or live-service claims until the business can substantiate those terms.

## 4. Heading and Content Review

All eight pages have exactly one `h1`, and no heading-level jumps were found. Headings describe visitor tasks rather than repeating keywords.

Content strengths:

- The assessment avoids diagnosis lists, health histories, medications, clinical scoring, triage, and automated care recommendations.
- Service copy clearly labels the current offer as proposed and non-clinical.
- Emergency, privacy, and no-submission boundaries are visible.
- Verified public contact details are present: `416-731-5383` and `frontline.mlvn@gmail.com`.
- Contact hours are Monday–Friday, 9:00 a.m.–6:00 p.m. Eastern Time, with responses expected within 12 business hours.
- “Now accepting new client inquiries” uses the approved non-medical term “client.”

Before public launch, verify and approve:

- Exact municipalities and travel limits.
- Final services and exclusions.
- Caregiver/PSW qualifications and screening statements.
- Insurance status.
- Pricing or “contact for pricing” wording.
- Legal/privacy review of the live inquiry process.
- Rights to the logo and photographs.
- Ownership and DNS control of `getcarequick.ca`.

Do not add testimonials, ratings, credentials, years in business, partner claims, outcomes, or prices without evidence.

## 5. Internal Links and On-Page Structure

Navigation exposes all eight routes through the header and/or footer, and contextual links guide visitors to Services, FAQ, Contact, Privacy, and Support Needs. Link labels are descriptive. All 215 local references resolve.

No additional service or location pages are recommended yet. Create a service page only after that service is confirmed and supports substantial unique content. Create municipality pages only for genuinely served areas with useful, location-specific information; do not create near-duplicate doorway pages.

Seven legacy page footers use “GTA,” while the Support Needs page uses “East Toronto and Durham Region.” This is a low-priority consistency issue, not a current accuracy failure. Align the wording in the final production content pass.

## 6. Structured Data

No structured data should be added during the local pilot.

For production, consider `Organization` only after the public identity, canonical URL, approved logo, and contact facts are finalized. Google’s Organization guidance supports administrative details such as name, URL, logo, and contact information when they are accurate and visible ([Google Organization structured data](https://developers.google.com/search/docs/appearance/structured-data/organization)).

Do not invent a public address to qualify for LocalBusiness markup. Google’s supported LocalBusiness rich-result documentation identifies the business name and physical address as required properties; the owner has chosen to keep the address private ([Google LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business)). Organization markup is therefore the safer initial candidate unless later verified circumstances support something more specific.

Additional guidance:

- Add `Service` data only when each visible service, provider, and area is verified.
- Do not add `MedicalBusiness`, medical-condition, diagnosis, or clinical-care schema.
- Do not add `Review`, `AggregateRating`, price, credential, or availability data without matching visible evidence.
- FAQ content is useful to visitors, but FAQ rich results are now generally limited to well-known authoritative government and health websites, so FAQPage markup is not a practical visibility target for this site ([Google FAQ rich-result change](https://developers.google.com/search/blog/2023/08/howto-faq-changes?hl=en)).

## 7. Technical SEO

| Check | Result | Production action |
|---|---|---|
| Titles/descriptions | Pass: eight unique pairs | Reapprove after final copy |
| Language/headings | Pass: `en-CA`, one `h1` per page | Preserve during revisions |
| Local links/assets | Pass: 215 references resolve | Recheck after routing changes |
| Indexability | Intentionally blocked on all pages | Remove only during approved release |
| Robots | `Disallow: /` | Replace with production rules at release |
| Sitemap | Intentionally empty | Populate with approved canonical HTTPS URLs |
| Canonicals | Correctly absent while domain is unverified | Add self-canonicals after domain approval |
| Open Graph | Title, description, and type present | Add verified `og:url` and rights-cleared `og:image` |
| Structured data | Correctly absent | Add evidence-backed Organization data if approved |
| Images | Decorative SVGs use empty alternative text | Review future photographs individually |
| Mobile structure | Passed during QA at tested widths | Retest after final content changes |
| Asset budget | Combined CSS and JavaScript: 40,959 bytes | Preserve lightweight delivery |

Important preview-hosting note: Google states that a crawler must be able to access a page to see its `noindex` rule. If `robots.txt` blocks the page, that rule may not be observed; Google also says robots rules are not a reliable way to keep a URL out of search results ([Google noindex guidance](https://developers.google.com/search/docs/crawling-indexing/block-indexing?authuser=531&hl=en)). If this pilot is placed on a public URL before release, protect it with authentication or another access control rather than relying only on `robots.txt` and `noindex`.

No live crawl, redirect audit, Search Console review, ranking analysis, backlink analysis, or Core Web Vitals field review was appropriate because the project has no approved public domain and is intentionally offline.

## 8. Local SEO

The public service area should remain **East Toronto and Durham Region** until exact municipalities are confirmed. Do not claim all of Toronto or the entire GTA by implication.

Before creating or updating public directory profiles, verify:

- The exact public business name and category.
- Whether YYZ Caregivers operates strictly as a service-area business.
- Exact municipalities, postal-code boundaries, and travel exceptions.
- Service, qualification, screening, insurance, and pricing statements.
- Ownership of the public phone, email, website domain, and any business profile.

Keep the private address off the public website and do not fabricate a storefront for local SEO. Public name, phone, email, hours, and area information should remain consistent across the future website and any owner-controlled profiles.

## 9. Findings and Risk Register

### SEO-001 — Production indexing remains disabled

- **Severity:** Production blocker; expected local safeguard
- **Status:** Open until approved release
- **Action:** Keep current controls for local work. At release, coordinate index directives, robots rules, sitemap, canonical URLs, and the deployed route audit.

### SEO-002 — Domain-dependent metadata is pending

- **Severity:** Production blocker; not a pilot defect
- **Status:** Awaiting proof of domain control and approved image rights
- **Action:** Add self-canonicals, `og:url`, and an approved social image only after verification.

### SEO-003 — Structured data lacks enough verified operating facts

- **Severity:** Production blocker; not a pilot defect
- **Status:** Awaiting owner inputs
- **Action:** Start with accurate Organization data only if approved. Do not invent an address or medical/service claims.

### SEO-004 — Operating and service claims remain provisional

- **Severity:** Production blocker; not a pilot defect
- **Status:** Awaiting verification
- **Action:** Confirm services, exclusions, qualifications, screening, insurance, pricing, exact areas, and policy wording before replacing pilot language.

### SEO-005 — Footer geography is inconsistent

- **Severity:** Low
- **Status:** Open; non-blocking for local pilot
- **Evidence:** Seven pages say “GTA”; Support Needs says “East Toronto and Durham Region.”
- **Action:** Standardize on the approved precise service-area wording during the final production content pass.

## 10. Implementation Handoff

No website-code correction is required to pass the local-pilot SEO stage. Preserve the current indexing and privacy safeguards.

At an approved production-release step:

1. Verify the domain, public business facts, service scope, geography, policies, and image rights.
2. Finalize provisional copy and standardize the footer service area.
3. Add self-canonical and matching `og:url` values for every public route.
4. Add a rights-cleared local social-sharing image and complete Open Graph image metadata.
5. Populate the sitemap and replace the pilot robots/indexing rules in one coordinated change.
6. Add only evidence-backed structured data.
7. Re-run content, link, accessibility, security, and performance checks.
8. Crawl the deployed preview for status codes, redirects, indexability conflicts, canonicals, and missing assets before requesting indexing.

## 11. Verification

- Factory project check: **Passed** — 8 HTML files, 215 local references, 2 JavaScript files, 1 CSS file.
- Frontend smoke suite: **Passed**.
- Metadata audit: **Passed** — 8 unique titles, 8 unique descriptions, complete basic Open Graph metadata.
- Heading audit: **Passed** — one `h1` per page and no heading-level jumps.

## 12. Readiness

**SEO STAGE PASSED FOR THE LOCAL PILOT.** The revised eight-page site may proceed to Security review after the workflow stage is explicitly advanced. It is not ready for public indexing or production launch until SEO-001 through SEO-004 are resolved; SEO-005 should be completed in the final production content pass.

No website source, deployment setting, external profile, Git history, or production system was changed during this review.
