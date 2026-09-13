# AI Website Factory — Standard Project Structure

## Purpose

This template defines the standard directory structure for websites created by the AI Website Factory.

The Project Orchestrator should use this structure when initializing a new project.

The structure may be extended when required by the project's technology stack, but the core organization should remain consistent.

---

# Standard Project Directory

```text
projects/
└── project-name/
    ├── PROJECT-BRIEF.md
    ├── PROJECT-STATUS.md
    ├── HANDOFF.md          # Generated when a workflow gate is ready
    │
    ├── architecture/
    │   └── ARCHITECTURE.md
    │
    ├── design/
    │   ├── UI-UX-SPEC.md
    │   └── assets/
    │
    ├── src/
    │
    ├── tests/
    │
    ├── reports/
    │   ├── QA-REPORT.md
    │   ├── SECURITY-REPORT.md
    │   ├── PERFORMANCE-REPORT.md
    │   ├── ACCESSIBILITY-REPORT.md
    │   └── SEO-REPORT.md
    │
    ├── documentation/
    │   ├── DEVELOPMENT.md
    │   ├── DEPLOYMENT.md
    │   └── CHANGELOG.md
    │
    ├── README.md
    ├── .env.example
    ├── .gitignore
    └── vercel.json
```

New projects also receive a gitignored-secrets template, a project `.gitignore`, and static response-header configuration from `templates/security/`. Next.js API hardening files live under `templates/security/nextjs/` and are copied only when a project adds a Node backend.
