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

## Create a project

From the factory root, create a new project scaffold with:

```bash
./factory create client-website
```

The command validates the project name, refuses to overwrite an existing project, and creates the standard architecture, design, source, test, report, and documentation structure under `projects/`. After creation, complete the new project's `PROJECT-BRIEF.md` before beginning architecture or implementation.

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

## Local project previews

From the factory root, start a safe local preview with:

```bash
./factory preview factory-demo
```

The command serves `projects/factory-demo/src` at `http://127.0.0.1:8743/` and keeps running until you press `Ctrl-C`. To use another port, add it as the final argument (for example, `./factory preview factory-demo 9000`).

## Project checks

Before committing or deploying a static project, run:

```bash
./factory check factory-demo
```

The command checks every HTML page for its basic document structure and duplicate IDs, verifies local links, fragments, and assets, checks CSS delimiter balance and referenced files, and runs a syntax check on every JavaScript file. It uses Python's standard library and, when JavaScript files are present, the installed `node` command.

## Goal

Create a repeatable AI-assisted workflow capable of producing professional websites efficiently while maintaining human oversight, version control, testing, and quality standards.
