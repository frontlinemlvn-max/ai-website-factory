# Deployment

Project: yyz-caregivers

## Deployment Platform

Vercel, per `PROJECT-BRIEF.md` ("Hosting / Platform: Local preview; Vercel only after explicit human approval"). No Vercel project has been created or linked yet — this section documents the intended target, not a live link. Once a project is linked, its `orgId`/`projectId` (from `.vercel/project.json`) will be recorded here so the factory's deployment adapter can verify the link matches this document before any deploy.

## Build Process

None required. The site (`src/`) is static HTML, CSS, and JavaScript with no framework, bundler, or dependency manifest. The deployment root is `projects/yyz-caregivers/src`, deployed as-is.

## Environment Variables

None required. The site has no backend, database, or third-party API. If a real inquiry-processing vendor is added later (see `reports/SECURITY-REPORT.md`, SEC-002), any resulting variable names — not values — will be documented here.

## Deployment Procedure

Deployment uses the factory's Vercel adapter (`tools/deployment-adapter.py`), invoked through `./factory deploy` and `./factory rollback`. It refuses to run unless the project stage is `Deployment Ready`, this file names Vercel as the platform, and a real `.vercel/project.json` link exists and matches what's documented here.

Prerequisites, none of which are complete yet:

1. Register the `getcarequick.ca` domain (currently unregistered — see `PROJECT-BRIEF.md`).
2. Replace the temporary placeholder logo with one that has confirmed usage rights.
3. Finalize the Privacy Policy and Terms of Service with legal review (drafts exist at `documentation/PRIVACY-POLICY-DRAFT.md` and `documentation/TERMS-OF-SERVICE-DRAFT.md`).
4. Create and link the Vercel project (`vercel link` from the deployment root), and record its organization/project IDs here.
5. Advance the project stage to `Deployment Ready` and pass `./factory validate-release yyz-caregivers`.

Once prerequisites are met, the procedure is:

1. `./factory deploy yyz-caregivers --dry-run` — verifies the Vercel link, deployment root, and file count without contacting Vercel's deploy API.
2. Review the dry-run output with the owner.
3. `./factory deploy yyz-caregivers --confirm DEPLOY` — performs the live deployment only on this exact confirmation string, per a separate explicit deployment instruction from the owner (see `reports/LAUNCH-READINESS.md`, Deployment Plan). This step is not authorized by the Approved-stage decision alone.

Indexing remains blocked (`noindex, nofollow`, `robots.txt` disallow-all) until the owner separately approves public indexing, per `reports/SEO-REPORT.md` (SEO-001).

## Post-Deployment Verification

After any live deployment, verify before considering it complete:

- The production HTTPS URL loads all 8 routes with no broken links (rerun `./factory check yyz-caregivers`).
- TLS/HTTPS redirects work correctly on the final domain.
- Response security headers are configured per `reports/SECURITY-REPORT.md` (SEC-001).
- Both forms (Contact, Support Needs Assessment) still behave as non-sending previews unless a live inquiry backend has been separately built and security-reviewed (SEC-002) — do not let a hosting change accidentally add a form action.
- `noindex, nofollow` and `robots.txt` disallow rules are intact, unless indexing has been separately, explicitly approved.
- No console errors, and a spot check of the responsive layouts (mobile/desktop).
- Record the resulting deployment ID and production URL here for future rollback reference.

## Rollback

Rollback uses the same adapter: `./factory rollback yyz-caregivers <deployment-id-or-url> --dry-run` to inspect a target deployment read-only, then `./factory rollback yyz-caregivers <deployment-id-or-url> --confirm ROLLBACK` to restore it. The dry run verifies the target belongs to this project's linked Vercel organization/project before any change is made.

No deployment has occurred, so no rollback target exists yet. Once a deployment happens, record its deployment ID and URL in Post-Deployment Verification above so a previous-known-good target is always available.
