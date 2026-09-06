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
