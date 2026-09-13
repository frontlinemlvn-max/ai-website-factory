# YYZ Caregivers — Security Review

- **Project:** `yyz-caregivers`
- **Review date:** September 10, 2026
- **Stage:** Independent security review
- **Scope:** Eight-page static local pilot, Contact preview, Support Needs Assessment, and project configuration
- **Overall status:** **READY FOR THE NEXT SPECIALIST STAGE; NOT READY FOR PRODUCTION**

## 1. Security Summary

The revised pilot retains a deliberately small attack surface. It contains eight static HTML pages, one local stylesheet, two local JavaScript files, and two local SVG assets. It has no backend, API, database, authentication, accounts, cookies, analytics, third-party runtime, package dependency, upload, payment, CMS, admin interface, or production hosting configuration.

Both forms are non-sending browser previews. Neither form has an `action`; both prevent native submission; neither script uses network or browser-storage APIs. Assessment answers are rendered with DOM text nodes and `textContent`, never as HTML, then discarded on reset, refresh, navigation, or closure. No answer is placed in a URL, email link, log, download, cookie, or external service.

No currently exploitable vulnerability was identified.

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational / future control | 3 |

The highest future risk is turning either form into a live submission workflow without first designing secure data minimization, server-side validation, access controls, retention, logging, abuse protection, provider governance, and incident handling. That workflow does not exist today.

Deployment recommendation: continue to the Performance stage after the workflow is explicitly advanced, but do not publish this as a live service. Production still requires verified hosting, response headers, HTTPS, final data-flow and privacy review, remaining factory gates, and explicit human approval.

## 2. Threat Model and Trust Boundaries

### Assets that would require protection

- Future visitor names, contact details, municipalities, messages, and support-needs information.
- Future business records, staff access, accounts, credentials, and administrative systems.
- The integrity of public service, availability, privacy, and emergency information.
- Future hosting, email, CRM, scheduling, analytics, or domain credentials.

### Current trust boundary

The current boundary ends inside the visitor’s browser. Static files load locally, form values exist temporarily in page memory, and no project code transmits or persists them. Public `mailto:` and `tel:` links open visitor-controlled applications, but assessment answers are not attached to those links.

### Future threat actors

If the project becomes live, realistic threats include automated spam, injection payloads, sensitive oversharing, unauthorized staff access, account compromise, malicious dependencies, misconfigured hosting, and accidental publication of secrets or unverified claims.

Any backend, form provider, CMS, CRM, analytics tool, scheduler, map, chat widget, upload, or payment feature changes the trust boundary and requires another security review.

## 3. Findings

### SEC-001 — Production response security headers are not configured

- **Severity:** Informational now; production requirement
- **Affected component:** Future hosting configuration
- **Status:** Open for production; not a local-pilot defect
- **Evidence:** No project-specific production-host configuration or deployed HTTPS response exists to define or verify security headers.
- **Risk:** A public site without suitable headers would lose browser-level defence in depth against content injection, framing, MIME confusion, excessive permissions, and referrer leakage.
- **Reproduction:** Inspect the project tree; no production configuration is present. No deployed response was available for header inspection.
- **Recommended fix:** At the approved host, test a restrictive policy compatible with the final site. For the present no-send design, evaluate `default-src 'self'`, explicit self-hosted script/style/image rules, `connect-src 'none'`, `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`, and `form-action 'none'`. Also evaluate `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, and HTTPS-only HSTS after the final domain is stable. OWASP recommends deploying CSP through response headers and tailoring directives such as `frame-ancestors` and `form-action` to the real application ([OWASP CSP guidance](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)).
- **Verification:** Inspect every real HTTPS route, review CSP violation reports during testing, and regress all navigation and form interactions under the final policy.

### SEC-002 — Any live inquiry or assessment flow requires a separate secure architecture

- **Severity:** Informational now; production blocker if transmission is added
- **Affected files:** `src/contact.html`, `src/intake.html`, `src/assets/js/main.js`, `src/assets/js/assessment.js`, and any future endpoint/provider configuration
- **Status:** No live workflow exists
- **Evidence:** Both forms have no destination. JavaScript prevents native submission, uses no network/storage API, and does not put answers into contact links. The assessment blocks diagnosis, medication, health-card, financial, street-address, and emergency fields.
- **Current risk:** No server-side injection, authorization, CSRF, retention, or provider-exposure surface exists because no submission leaves the browser.
- **Future risk:** A live workflow could receive personal or care-related information, attract automated abuse and injection attempts, disclose data to unauthorized people or providers, retain data excessively, or leak values through logs and notifications.
- **Reproduction:** Inspect both form elements and both JavaScript files; there is no `action`, `fetch`, XHR, beacon, WebSocket, browser storage, or answer-filled URL.
- **Recommended fix:** Treat a live workflow as new architecture. Approve the minimum fields and purpose; validate and normalize on the server; safely encode all output; rate-limit abuse; define staff roles and least-privilege access; redact logs; define retention, deletion, backup, provider, breach, and incident processes; and update Privacy/Terms to match reality. Client-side validation may support usability but cannot provide security because it can be bypassed; OWASP recommends server-side validation before processing ([OWASP Input Validation guidance](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)).
- **Verification:** Test the endpoint directly without the browser, including validation bypass, injection, rate limits, access controls, CSRF where applicable, log redaction, retention/deletion, provider settings, failure handling, and accessible recovery.

### SEC-003 — Dependency and secret controls become necessary if the stack expands

- **Severity:** Informational
- **Affected component:** Future packages, integrations, deployment variables, CMS, CRM, analytics, and scheduling
- **Status:** No current dependency or secret exposure found
- **Evidence:** No dependency manifest, lockfile, environment file, private-key file, remote runtime, or secret-signature match was found. No package vulnerability scan was applicable because there is no dependency graph.
- **Risk:** Future dependencies can introduce vulnerable or compromised code. Credentials can leak through frontend bundles, source control, logs, documentation, preview URLs, or overly broad hosting variables. Third-party JavaScript also executes within the site’s browser trust boundary; OWASP documents controls and governance for this increased exposure ([OWASP Third-Party JavaScript guidance](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html)).
- **Reproduction:** Inventory the project for package/lock files, environment/credential files, external runtime URLs, and common high-confidence secret signatures; all counts are zero.
- **Recommended fix:** Preserve the dependency-free approach where practical. Before adding packages, commit a lockfile, review transitive dependencies, scan them, pin/update deliberately, and remove unused code. Store privileged credentials only in approved server-side secret storage with least privilege and rotation ownership; never expose them in frontend variables or bundles.
- **Verification:** Scan the final dependency graph, lockfile, build output, deployment-variable visibility, current source, and committed history without printing secret values. Exercise credential rotation and provider removal.

## 4. Authentication and Session Review

Authentication is not applicable. There is no registration, login, logout, password, password reset, token, cookie, session, protected route, or administrative interface.

If a CMS, CRM, scheduling tool, inbox, or staff dashboard is introduced, require provider-supported multi-factor authentication where available, secure account recovery, appropriate session expiry and invalidation, least privilege, auditable access, and prompt staff offboarding. Do not store privileged tokens in browser storage.

## 5. Authorization Review

Authorization is not applicable because the pilot has no users, roles, records, protected endpoints, ownership identifiers, or privileged actions.

Any future backend must enforce authorization on the server for every record and action. Hidden buttons, form fields, or frontend route guards must never be treated as access control.

## 6. Input and Browser-Side Review

The two forms use client-side validation only for a local preview. This is suitable for the current no-send behavior but must not be reused as production security validation.

Security-positive observations:

- No `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, or dynamic `Function` use.
- User-entered assessment values are rendered using created elements and `textContent`.
- No URL-parameter reader, user-controlled redirect, dynamic script loader, inline event handler, iframe, object, embed, or remote SVG reference.
- No file input, executable upload path, query/database operation, shell call, filesystem path construction, Markdown renderer, or rich-text editor.
- Input lengths are bounded in markup and script for local usability.
- Fixed browser errors expose no stack, internal path, environment detail, or credential.

SQL/NoSQL injection, command injection, path traversal, server-side request forgery, insecure direct-object references, upload abuse, server-side XSS, and header injection are outside the implemented system because the corresponding server components do not exist.

## 7. Data, Privacy, Secrets, Storage, and Logging

- No database, backend, cookie, application storage, analytics, tracker, or application session exists.
- No `localStorage`, `sessionStorage`, IndexedDB, network request, or beacon is used.
- Values exist only in page memory and are cleared by reset or discarded when the page is left or refreshed.
- The assessment repeatedly discourages diagnoses, medications, identifiers, finances, street addresses, and emergency information.
- Assessment answers are excluded from `mailto:` and `tel:` links.
- The application creates no log containing visitor values. A development preview server may log requested paths only.
- Browser autocomplete for ordinary contact fields is browser-managed and is not project-controlled storage.
- The focused scan found no API key, token, password, private key, environment file, credential-bearing configuration, symlink, or project-local executable.

The public email and phone number are intentional business contact data, not credentials. This review does not claim legal compliance; professional privacy/legal review remains required before any live collection.

## 8. Dependency and Integration Review

No package manager, dependency manifest, lockfile, framework, remote font, third-party script, widget, analytics tag, map, chat, CRM, scheduler, mail processor, payment service, or API integration exists.

**Dependency vulnerability scan:** Not performed because there is no application dependency graph to scan. Static source and integration inventories were performed instead. The local browser, Python, Node syntax checker, and factory tooling are development infrastructure, not shipped YYZ Caregivers dependencies.

## 9. APIs, CORS, CSRF, Uploads, Payments, and Abuse

- **APIs/CORS:** None.
- **State-changing requests/CSRF:** None.
- **Files/uploads:** None.
- **Payments/webhooks:** None.
- **Rate limiting:** Not applicable to the local pilot; required for a future public endpoint according to its abuse risk.
- **Accounts/sessions:** None.
- **Server error handling:** None.

These conclusions apply only to the current implementation and must be reassessed when a corresponding feature is introduced.

## 10. Production Configuration Requirements

Before any public deployment:

1. Complete Performance, Accessibility, Final Review, human approval, and release-readiness gates.
2. Use HTTPS on the verified canonical domain and confirm scheme/hostname redirects.
3. Configure and test SEC-001 response headers at the actual hosting layer.
4. If either form becomes live, complete SEC-002 before collecting anything.
5. Confirm there are no debug tools, directory listings, source-only documents, sensitive source maps, default credentials, preview tokens, backups, environment files, logs, or admin interfaces in the deployed output.
6. Keep privileged credentials in least-privilege server-side secret storage and verify they are absent from client bundles.
7. Review every third-party domain and narrowly scope browser permissions, CSP, CORS, and connections.
8. Ensure Privacy and Terms accurately describe the final data flow; do not claim legal compliance without qualified review.
9. Verify error pages and provider notifications expose no unnecessary personal or internal information.
10. Run source/history secret checks and dependency scans appropriate to the final stack.

## 11. Remediation Handoff

No correction to the present static source is required for Security-stage progression.

| Finding | Priority | Owner | Required before | Verification |
|---|---|---|---|---|
| SEC-001 | Production hardening | Deployment/Frontend with Security review | Public hosting | Inspect HTTPS headers and regress the site under final CSP |
| SEC-002 | Production blocker if transmission is added | Architect, Backend, Privacy owner, Security | Any real submission | Direct endpoint, abuse, authorization, logging, retention, and privacy tests |
| SEC-003 | Change-triggered control | Developer/Deployment/Security | Dependencies, secrets, or integrations | Dependency, source, history, build-output, and environment scans |

Return to Security review if the architecture adds a backend, API, authentication, database, CMS, CRM, analytics, upload, payment, scheduling, tracking, or third-party runtime.

## 12. Verification Evidence

- Factory project check: **Passed** — 8 HTML pages, 215 local references, 2 JavaScript files, 1 CSS file.
- Frontend smoke suite: **Passed**.
- JavaScript syntax checks: **Passed** for both scripts.
- Factory regression suite: **Passed** — all 50 tests; no production deployment.
- Forms found: 2; forms with submission destinations: 0.
- Network/storage API files: 0.
- Unsafe DOM sink files: 0.
- External runtime URL files: 0.
- Upload controls: 0.
- Inline event-handler files: 0.
- Embedded iframe/object/embed files: 0.
- Dependency/lock/config manifests: 0.
- Environment/private-key files: 0.
- High-confidence secret-signature file matches: 0.
- Symlinks: 0; project-local executables: 0.

## 13. Security Readiness

**Ready for the next specialist stage.** The eight-page local pilot has no identified exploitable vulnerability and preserves its no-send, no-store, no-secret, no-dependency, and no-integration boundaries.

**Not ready for production.** SEC-001 must be completed at the approved host. SEC-002 and SEC-003 apply whenever their triggering capabilities are introduced. Verified hosting, professional privacy/legal review, remaining factory gates, and explicit human approval are still required.

No external system was changed, no credential was accessed, and no deployment, Git commit, push, approval, or workflow advancement occurred during this review.
