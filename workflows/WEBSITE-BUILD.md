# AI Website Factory — Website Build Workflow

## Purpose

This workflow defines how the AI Website Factory takes a website from an initial project brief to a tested, reviewed, and deployment-ready product.

The Project Orchestrator controls this workflow.

Specialist agents perform the work assigned to them.

No specialist agent should independently change the overall project workflow unless the Project Orchestrator approves the change.

---

# 1. Workflow Overview

Default production pipeline:

Project Brief
→ Project Orchestrator
→ Website Architect
→ UI/UX Designer
→ Frontend Developer
→ Backend Developer when required
→ QA Tester
→ Debug Fixer when required
→ QA Retest
→ SEO & Content
→ Security Auditor
→ Performance Optimizer
→ Accessibility Specialist
→ Final QA
→ Human Approval
→ Deployment

Not every project requires every agent.

The Project Orchestrator determines which agents are applicable.

---

# 2. Project Intake

Every project begins with:

`templates/PROJECT-BRIEF.md`

A project-specific copy should be created inside the project's directory.

Example:

`projects/example-project/PROJECT-BRIEF.md`

The brief should define, when applicable:

- Project name
- Business or organization
- Website purpose
- Target audience
- Primary conversion goal
- Required pages
- Required functionality
- Brand requirements
- Content requirements
- Technical requirements
- Integrations
- SEO requirements
- Accessibility requirements
- Security requirements
- Performance requirements
- Deployment target
- Known constraints

The Orchestrator must review the brief before assigning development work.

---

# 3. Project Initialization

The Orchestrator creates or verifies the project workspace.

Recommended structure:

projects/
└── project-name/
    ├── PROJECT-BRIEF.md
    ├── architecture/
    ├── design/
    ├── src/
    ├── tests/
    ├── reports/
    └── documentation/

Additional directories may be created when required by the technology stack.

---

# 4. Architecture Stage

Owner:

Website Architect

Input:

- PROJECT-BRIEF.md

Responsibilities:

- Analyze requirements
- Define sitemap
- Define information architecture
- Define major user journeys
- Recommend technology stack
- Define frontend architecture
- Define backend requirements
- Define integrations
- Identify technical risks
- Identify assumptions
- Identify unresolved decisions

Output should be stored in the project workspace.

Example:

`projects/project-name/architecture/ARCHITECTURE.md`

The project must not proceed to implementation when critical architecture decisions remain unresolved.

---

# 5. UI/UX Stage

Owner:

UI/UX Designer

Input:

- Project brief
- Approved architecture
- Brand assets
- Existing design requirements

Responsibilities:

- Define page layouts
- Define responsive behavior
- Define navigation behavior
- Define component states
- Define forms and interactions
- Define design system
- Define typography
- Define spacing
- Define accessibility-conscious interactions
- Document mobile behavior

Output example:

`projects/project-name/design/UI-UX-SPEC.md`

Development begins only when the design specification is sufficiently complete.

---

# 6. Frontend Development Stage

Owner:

Frontend Developer

Input:

- Project brief
- Architecture
- UI/UX specification
- Approved assets

Responsibilities:

- Implement pages
- Implement components
- Implement responsive layouts
- Implement navigation
- Implement forms
- Implement client-side interactions
- Preserve semantic HTML
- Follow accessibility requirements
- Follow approved architecture
- Avoid unnecessary dependencies

The Frontend Developer must document:

- Implemented functionality
- Remaining work
- Known limitations
- Assumptions
- Build instructions

---

# 7. Backend Development Stage

Owner:

Backend Developer

This stage is conditional.

Use it when the project requires:

- Authentication
- Authorization
- Database
- APIs
- Server-side logic
- Payments
- Webhooks
- Persistent data
- Secure third-party integrations

Responsibilities:

- Implement server-side architecture
- Implement APIs
- Implement authentication
- Implement authorization
- Validate input
- Protect sensitive operations
- Implement database access
- Handle errors safely
- Document environment requirements

Backend implementation must not expose production credentials or secrets.

---

# 8. Initial QA Stage

Owner:

QA Tester

QA independently tests the implementation.

Test:

- Required pages
- Navigation
- Forms
- User journeys
- Responsive layouts
- Error handling
- Functional requirements
- Browser behavior
- Mobile behavior
- Basic accessibility
- Regression risks

Every defect must include:

- Severity
- Location
- Reproduction steps
- Expected behavior
- Actual behavior
- Evidence when available

QA does not fix defects.

QA reports them.

---

# 9. Debug Loop

When QA discovers defects:

QA Tester
→ Debug Fixer
→ QA Tester

The Debug Fixer must:

1. Reproduce the defect.
2. Identify the root cause.
3. Apply the smallest safe fix.
4. Document the change.
5. Return the issue to QA.

QA must independently retest the fix.

A developer claiming that a defect is fixed does not count as QA verification.

Repeat the loop until launch-blocking defects are resolved.

---

# 10. SEO & Content Stage

Owner:

SEO & Content Agent

Review:

- Page titles
- Meta descriptions
- Heading structure
- Content hierarchy
- Internal linking
- Indexability
- Canonical strategy
- Structured data
- Image alternative text where relevant
- Search intent
- Local SEO when applicable

Do not invent business claims, locations, credentials, reviews, or services.

SEO recommendations must remain consistent with the actual business.

---

# 11. Security Review

Owner:

Security Auditor

Review applicable areas including:

- Authentication
- Authorization
- Input validation
- API protection
- Secret handling
- Dependency risks
- Security headers
- Data exposure
- Session handling
- Privilege boundaries
- File uploads
- Third-party integrations

Critical and High security findings must be resolved or explicitly accepted by an authorized human before deployment.

Security fixes must be retested.

---

# 12. Performance Review

Owner:

Performance Optimizer

Review:

- Images
- Fonts
- JavaScript
- CSS
- Rendering
- Network requests
- Caching
- Lazy loading
- Code splitting
- Core Web Vitals
- Production build behavior

Performance optimization must not break:

- Functionality
- Accessibility
- Security
- SEO
- Design requirements

Meaningful implementation changes must return to QA for regression testing.

---

# 13. Accessibility Review

Owner:

Accessibility Specialist

Target:

WCAG 2.2 AA where applicable unless the project specifies another standard.

Review:

- Semantic HTML
- Keyboard navigation
- Focus behavior
- Forms
- Labels
- Errors
- Contrast
- Alternative text
- ARIA
- Responsive accessibility
- Touch accessibility
- Reduced motion
- Interactive components
- Screen-reader considerations

Automated accessibility testing alone is insufficient to claim compliance.

Accessibility defects must return to the appropriate development or debugging agent.

---

# 14. Final QA

After specialist reviews and remediation, QA performs final regression testing.

Verify:

- Critical user journeys
- Navigation
- Forms
- Responsive behavior
- Fixed defects
- Major integrations
- No regressions from optimization
- No regressions from accessibility fixes
- No regressions from security fixes

Final QA produces a launch status.

---

# 15. Launch Gate

Before deployment, the Orchestrator produces a readiness report.

Report:

## Architecture

Status:
- Passed
- Needs attention
- Blocked

## UI/UX

Status:
- Passed
- Needs attention
- Blocked

## Frontend

Status:
- Passed
- Needs attention
- Blocked

## Backend

Status:
- Passed
- Needs attention
- Blocked
- Not applicable

## QA

Status:
- Passed
- Needs attention
- Blocked

## SEO

Status:
- Passed
- Needs attention
- Blocked
- Not applicable

## Security

Status:
- Passed
- Needs attention
- Blocked

## Performance

Status:
- Passed
- Needs attention
- Blocked

## Accessibility

Status:
- Passed
- Needs attention
- Blocked

The Orchestrator then chooses:

- NOT READY
- READY AFTER FIXES
- READY FOR HUMAN APPROVAL

---

# 16. Human Approval

Production deployment requires explicit human approval.

The Orchestrator must present:

- Final project status
- Known issues
- Remaining risks
- QA status
- Security status
- Accessibility status
- Performance status
- SEO status
- Deployment plan

The human decision must be:

APPROVED

or

NOT APPROVED

Silence does not count as approval.

---

# 17. Deployment

Deployment occurs only after approval.

Deployment responsibilities will be handled by the deployment workflow and deployment tooling configured for the project.

Potential targets include:

- Vercel
- Netlify
- Cloudflare
- GitHub Pages
- Traditional hosting
- Custom servers
- Other approved platforms

Deployment credentials must never be stored directly in project source files.

---

# 18. Post-Deployment Verification

After deployment verify:

- Production URL loads
- HTTPS works
- Navigation works
- Forms work
- Critical user journeys work
- Assets load
- Mobile layout works
- No obvious production console errors
- Metadata is present
- Robots/indexing configuration is correct
- Analytics works when configured

Production defects must enter the QA → Debug → QA workflow.

---

# 19. Workflow Failure Rules

If a stage fails:

Do not silently continue.

Record:

- Failed stage
- Failure reason
- Severity
- Responsible agent
- Required remediation
- Next action

Critical failures block downstream deployment.

---

# 20. Source of Truth

Priority order:

1. Explicit human-approved requirements
2. Current PROJECT-BRIEF.md
3. Approved architecture
4. Approved UI/UX specification
5. Current implementation
6. Agent recommendations

When sources conflict, the Orchestrator must identify the conflict rather than silently choosing one.

---

# 21. Project Status

The Orchestrator must always be able to answer:

- What project are we building?
- What stage are we in?
- What has been completed?
- What is currently being worked on?
- What is blocked?
- Which agent owns the next action?
- What requires human approval?

---

# 22. Completion Rule

A website project is not complete merely because the website renders.

Completion requires all applicable quality gates to pass and explicit human approval before production deployment.

The final objective is:

Brief
→ Build
→ Test
→ Audit
→ Fix
→ Verify
→ Approve
→ Deploy