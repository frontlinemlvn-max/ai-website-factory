# AI Website Factory

An AI-assisted development system for designing, building, testing, debugging, and deploying modern websites and web applications.

## AI Team

The factory will use specialized AI roles:

1. Website Architect
2. UI/UX Designer
3. Frontend Developer
4. Backend Developer
5. QA Tester
6. Debugger
7. SEO & Performance Agent
8. Deployment Agent

## AI Platforms

Primary AI tools:

- ChatGPT
- Claude
- Gemini

## Factory Structure

AI-WEBSITE-FACTORY/
- projects/ — Active website projects
- agents/ — Instructions for specialized AI agents
- templates/ — Reusable website templates
- documentation/ — Standards, workflows, and specifications
- tools/ — Development scripts and utilities

## Development Workflow

Client Request
↓
Requirements
↓
Website Architect
↓
UI/UX Design
↓
Development
↓
Automated Testing
↓
Debugging
↓
Performance & SEO
↓
Human Approval
↓
Deployment

## Check factory health

Before starting work—or when a command is not behaving as expected—run the read-only factory health check:

```bash
./factory doctor
```

The doctor verifies the local Python, Bash, and Git requirements; confirms that the repository root, required factory files, agent instructions, and executable permissions are intact; checks every project scaffold and status file; and validates any existing Vercel project links without displaying their identifiers. Node.js and the Vercel CLI are reported as optional capabilities because they are needed only for JavaScript checking or explicitly authorized production actions. The command never installs anything, authenticates, contacts a network service, or changes files.

## Create a project

From the factory root, create a new project scaffold with:

```bash
./factory create client-website
```

The command validates the project name, refuses to overwrite an existing project, and creates the standard architecture, design, source, test, report, and documentation structure under `projects/`. After creation, complete the new project's `PROJECT-BRIEF.md` before beginning architecture or implementation.

### Starting from a website type

Optionally apply a website-type starting point:

```bash
./factory create client-website --type restaurant
```

This appends a short, evidence-based starting point (suggested pages, suggested features, common owner inputs still needed, and claims to avoid without verification) to the bottom of the new project's `PROJECT-BRIEF.md`. It never fills in or guesses actual answers — the guided intake or manual completion still does that. Available types live as folders under `templates/website-types/` (currently `restaurant`, `portfolio`, and `contractor`); add a new one by creating `templates/website-types/<name>/STARTER.md` — no code change is required. An unrecognized `--type` value fails clearly and creates nothing, listing the types that do exist.

## Complete guided project intake

While a project is still in the `Intake` stage, complete its brief through the guided questionnaire:

```bash
./factory intake client-website
```

The wizard covers every answer required by the brief validator, including goals, audience, website type, pages, features, branding, content, technical requirements, SEO, and constraints. Pressing Enter keeps an existing substantive answer, and entering `CANCEL` at any prompt exits without saving. The wizard collects answers in memory, validates the completed candidate before offering to save it, requires a final confirmation, writes the brief atomically, and runs the validator again afterward.

Guided intake is intentionally restricted to the `Intake` stage so later work cannot have its requirements silently rewritten. Production approval is never collected by this command; it remains protected by the separate human approval gate.

## List projects and view status

List every factory project and its current stage:

```bash
./factory list
```

Show a project's stage, owner, active work, blockers, known issues, human decisions, and next action:

```bash
./factory status factory-demo
```

Both commands are read-only and use each project's existing `PROJECT-STATUS.md` file.

## Validate a project brief

Before architecture or implementation begins, validate that the project brief contains the required intake information:

```bash
./factory validate-brief client-website
```

The validator checks all required brief sections, 27 core fields, goals, audience needs, website type, required pages, features, and constraints. Placeholder or deferred-decision wording is reported for review. A brief can be ready for architecture while production approval remains pending; deployment still requires separate explicit human approval.

## Validate a workflow stage

Validate the current stage's actual deliverable before attempting to advance:

```bash
./factory validate-stage client-website
```

The validator checks substantive architecture and design content, source and development instructions, QA and specialist audit coverage, launch-readiness evidence, or deployment documentation according to the project's current stage. It rejects empty reports, untouched scaffolds, missing required topics, failed readiness verdicts, and incomplete deployment verification. Structural validation supports specialist review; it does not replace professional judgment or human approval.

## Control project workflow

Show the current stage, next stage, responsible agent, required output, and whether the transition gate is ready:

```bash
./factory next client-website
```

When the gate is ready, create a focused work package for the next specialist agent:

```bash
./factory handoff client-website
```

The command writes `projects/client-website/HANDOFF.md` with the source and destination stages, responsible agents, relevant files, requirements, assumptions, known issues, blockers, required output, and definition of done. It runs the existing transition gate first, does not advance the project, and refuses blocked or completed workflows. Generated handoffs can be refreshed safely; a manually created `HANDOFF.md` will not be overwritten.

After completing the required output, advance exactly one stage:

```bash
./factory advance client-website
```

`next` is read-only. `advance` runs the stage validator and updates only `PROJECT-STATUS.md` after the current deliverable passes; it cannot skip stages. Generic advancement cannot grant human approval or deploy a production project. Conditional Backend, Debugging, and Blocked states remain under the Project Orchestrator's routing rules in `workflows/WEBSITE-BUILD.md`.

## Record human approval

After Final Review passes and the project has advanced to `Ready for Human Approval`, review the launch-readiness evidence and record an explicit approval with:

```bash
./factory approve client-website APPROVED
```

The final `APPROVED` confirmation is case-sensitive and intentional. The command revalidates launch readiness, refuses projects in any other stage or with active blockers, and records the UTC decision time and evidence in `PROJECT-STATUS.md`. Approval moves the project to `Approved` for release preparation; it does not deploy the project. Production deployment always requires a separate explicit instruction.

## Validate release readiness

After approval, verify the release package before entering `Deployment Ready`:

```bash
./factory validate-release client-website
```

The release validator confirms the recorded human approval, checks for active blockers, validates the deployment and rollback documentation, reruns the static project checks, and scans project files for sensitive filenames and high-confidence secret patterns without displaying secret values. `./factory next` and `./factory advance` run this gate automatically for an `Approved` project. Passing the gate allows the workflow to enter `Deployment Ready`; it never deploys the project.

## Deploy safely to Vercel

At `Deployment Ready`, preview the exact local deployment target without contacting Vercel:

```bash
./factory deploy client-website --dry-run
```

The dry run rechecks release readiness, requires an existing `.vercel/project.json` link, confirms Vercel is the documented platform, identifies the linked organization and project, checks any documented Vercel IDs for a match, counts deployable files, and reports whether Vercel CLI is installed. Vercel organization and project IDs are identifiers, not authentication credentials. The command never installs tools, authenticates, links a project, deploys, or changes project files.

After reviewing the dry run, explicitly authorize a production deployment with:

```bash
./factory deploy client-website --confirm DEPLOY
```

The live path requires the exact `DEPLOY` confirmation, an existing authenticated Vercel CLI, and the existing linked project. It runs a noninteractive production deployment, reads the deployment URL from Vercel, verifies that the HTTPS URL returns HTML successfully, records the result in `documentation/DEPLOYMENT.md`, and only then moves the workflow to `Deployed`. Authentication tokens are never accepted as command arguments or printed.

## Roll back a Vercel deployment safely

For a project already in the `Deployed` stage, inspect the exact previous production deployment before restoring it:

```bash
./factory rollback client-website dpl_previousDeployment --dry-run
```

The rollback dry run performs authenticated, read-only Vercel checks. It confirms the existing local project link, verifies that the requested deployment belongs to the same Vercel organization and project, and requires the target to be a `READY` production deployment. It reports the target and the documented production URLs that will be checked afterward, but it does not request a rollback or change local project files.

After reviewing that output, explicitly authorize the rollback with:

```bash
./factory rollback client-website dpl_previousDeployment --confirm ROLLBACK
```

The target may be a Vercel deployment ID or a plain HTTPS deployment URL. The live path requires the exact `ROLLBACK` confirmation, repeats every check, uses Vercel's noninteractive Instant Rollback command, confirms completion, verifies the documented production URLs return HTML over HTTPS, and records the result while keeping the workflow in `Deployed`. If Vercel accepts the request but completion or verification is uncertain, the command stops with `ROLLBACK REQUIRES ATTENTION` and does not rewrite local records.

Instant Rollback restores the selected deployment's earlier build and configuration state, including its environment and cron configuration. Vercel also disables automatic assignment of production domains after a rollback until the rollback is explicitly undone by promoting a deployment. Review those effects in the dry run before confirming.

## Local project previews

From the factory root, start a safe local preview with:

```bash
./factory preview factory-demo
```

The command serves `projects/factory-demo/src` at `http://127.0.0.1:8743/` with XSS/CSP headers, path checks, and loopback-only binding. It keeps running until you press `Ctrl-C`. To use another port, add it as the final argument (for example, `./factory preview factory-demo 9000`).

## Customer frontend prototype

The Claude Design customer-facing prototype is isolated in `frontend/`; it does not
replace the factory CLI. Two ways to run it:

**Static only** (no project creation, everything simulated):

```bash
cd /Users/brandingbadge/Documents/ai-website-factory/frontend
python3 -m http.server 5173 --bind 127.0.0.1
```

**With the local backend** (creates and reads real factory projects):

```bash
./factory frontend
```

Serves `frontend/` and a small JSON API from the same origin and port
(default 5173; pass a port to use another one, e.g. `./factory frontend 9000`):

- `GET /api/health`
- `POST /api/projects` — validates the submitted name, derives a project slug, and
  calls the existing `tools/init-project.sh` to create it (no scaffolding logic is
  duplicated), then appends the submitted intake fields to the new
  `PROJECT-BRIEF.md` as an unverified summary for human review.
- `GET /api/projects/<slug>/status` — reads the project's `PROJECT-STATUS.md`.
- `POST /api/generate` — calls the real Anthropic API server-side to write home-page
  copy from the submitted brief. Requires `ANTHROPIC_API_KEY` (environment or a
  `.env` file at the factory root; see `.env.example`) — fails closed with a clear
  503 rather than fabricating output when it's not set. Limited to 5 requests/minute
  per IP, since each call costs real money.

When run this way, finishing the frontend's onboarding wizard creates a real
project under `projects/` and shows its live stage in a small "Factory record"
readout, and copy generation uses the real API when configured. If the backend
isn't running (the static-only option above) or `/api/generate` isn't configured,
the page fails silently and keeps its fully simulated/local-draft behavior — no
functionality is lost either way. **Payments, domain purchase, publishing,
deployment, and downloads remain explicitly simulated** in both modes. See
`frontend/README.md` for the full boundary and the export technology.

## Scan for secrets

Before committing or during validation, scan the factory or a project for committed `.env` files and high-confidence secret patterns. The scanner reports file paths and pattern classes only; it never prints secret values.

```bash
./factory scan-secrets
./factory scan-secrets factory-demo
```

Keep real credentials in a gitignored `.env`. Use `.env.example` for required variable names.

## Project checks

Before committing or deploying a static project, run:

```bash
./factory check factory-demo
```

The command checks every HTML page for its basic document structure and duplicate IDs, verifies local links, fragments, and assets, checks CSS delimiter balance and referenced files, and runs a syntax check on every JavaScript file. It uses Python's standard library and, when JavaScript files are present, the installed `node` command.

## Test the factory

Before committing changes to the factory itself, run its isolated regression suite:

```bash
./factory test
```

The suite copies the factory into a temporary directory, creates a disposable project, and exercises every public command. It verifies factory health diagnostics, project creation, guided intake, status reporting, brief and stage validation, workflow handoffs and transitions, human approval, release readiness, deployment and rollback safeguards, static checks, and local previews. Vercel behavior is represented by a local fake executable: the suite never authenticates with or contacts Vercel, changes production, or modifies anything under the real `projects/` directory.

## Continuous integration

`.github/workflows/factory-ci.yml` runs `./factory doctor`, `./factory scan-secrets`, and `./factory test` on every push and pull request to `main`. It requires no secrets or external service access: Vercel behavior in the regression suite is represented by a local fake executable, and the doctor and scanner commands are read-only.

## Goal

Create a repeatable AI-assisted workflow capable of producing professional websites efficiently while maintaining human oversight, version control, testing, and quality standards.
