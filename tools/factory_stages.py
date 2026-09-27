#!/usr/bin/env python3

"""
Single source of truth for the AI Website Factory's project-stage state machine.

STAGES, NEXT_STAGE, and ALIASES previously existed as independent copies in
tools/workflow-controller.py and tools/validate-stage.py, with nothing
enforcing that they stayed in sync. Both modules now import this file
instead, so a stage can only be added, renamed, or reordered in one place.
"""

STAGES = {
    "Intake": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Complete and validate the project brief.",
        "output": "PROJECT-BRIEF.md",
    },
    "Architecture": {
        "owner": "Website Architect",
        "agent": "agents/website-architect/AGENT.md",
        "action": "Define the sitemap, user journeys, technical architecture, integrations, risks, and assumptions.",
        "output": "architecture/ARCHITECTURE.md",
    },
    "Design": {
        "owner": "UI/UX Designer",
        "agent": "agents/ui-ux-designer/AGENT.md",
        "action": "Complete the responsive UI/UX specification and component behavior.",
        "output": "design/UI-UX-SPEC.md",
    },
    "Development": {
        "owner": "Frontend Developer",
        "agent": "agents/frontend-developer/AGENT.md",
        "action": "Implement the approved architecture and design in the project source directory.",
        "output": "src/index.html and supporting source files",
    },
    "Backend": {
        "owner": "Backend Developer",
        "agent": "agents/backend-developer/AGENT.md",
        "action": "Implement only the server-side functionality required by the approved architecture.",
        "output": "backend implementation and documentation",
    },
    "QA": {
        "owner": "QA Tester",
        "agent": "agents/qa-tester/AGENT.md",
        "action": "Independently test requirements, journeys, responsive behavior, forms, and regressions.",
        "output": "reports/QA-REPORT.md",
    },
    "Debugging": {
        "owner": "Debug Fixer",
        "agent": "agents/debug-fixer/AGENT.md",
        "action": "Fix verified defects and return the project to QA for independent retesting.",
        "output": "documented fixes and updated source",
    },
    "SEO": {
        "owner": "SEO & Content Agent",
        "agent": "agents/seo-content/AGENT.md",
        "action": "Review content, metadata, structure, indexing, internal links, and search intent.",
        "output": "reports/SEO-REPORT.md",
    },
    "Security": {
        "owner": "Security Auditor",
        "agent": "agents/security-auditor/AGENT.md",
        "action": "Review applicable security risks and document findings with evidence and severity.",
        "output": "reports/SECURITY-REPORT.md",
    },
    "Performance": {
        "owner": "Performance Optimizer",
        "agent": "agents/performance-optimizer/AGENT.md",
        "action": "Measure and improve performance without breaking functionality or accessibility.",
        "output": "reports/PERFORMANCE-REPORT.md",
    },
    "Accessibility": {
        "owner": "Accessibility Specialist",
        "agent": "agents/accessibility-specialist/AGENT.md",
        "action": "Review the project against its accessibility target and document verified findings.",
        "output": "reports/ACCESSIBILITY-REPORT.md",
    },
    "Final Review": {
        "owner": "QA Tester",
        "agent": "agents/qa-tester/AGENT.md",
        "action": "Run final regression testing and produce the launch-readiness decision.",
        "output": "reports/LAUNCH-READINESS.md",
    },
    "Ready for Human Approval": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Present final evidence, risks, known issues, and the deployment plan for an explicit human decision.",
        "output": "explicit APPROVED or NOT APPROVED human decision",
    },
    "Approved": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Prepare the approved release for the deployment-readiness gate.",
        "output": "verified deployment plan and rollback procedure",
    },
    "Deployment Ready": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Await an explicit deployment instruction and use the configured deployment adapter.",
        "output": "verified production deployment",
    },
    "Deployed": {
        "owner": "None",
        "agent": None,
        "action": "Project is deployed; perform post-deployment verification when changes are released.",
        "output": "production verification record",
    },
    "Blocked": {
        "owner": "Project Orchestrator",
        "agent": "agents/project-orchestrator/AGENT.md",
        "action": "Resolve and document the blocking issue before resuming downstream work.",
        "output": "resolved blocker and an explicit next state",
    },
}

NEXT_STAGE = {
    "Intake": "Architecture",
    "Architecture": "Design",
    "Design": "Development",
    "Development": "QA",
    "Backend": "QA",
    "QA": "SEO",
    "Debugging": "QA",
    "SEO": "Security",
    "Security": "Performance",
    "Performance": "Accessibility",
    "Accessibility": "Final Review",
    "Final Review": "Ready for Human Approval",
    "Ready for Human Approval": "Approved",
    "Approved": "Deployment Ready",
    "Deployment Ready": "Deployed",
}

ALIASES = {
    "SEO & Content": "SEO",
    "Final QA": "Final Review",
    "Human Approval": "Ready for Human Approval",
    "Complete": "Deployed",
}

# Derived rather than hand-maintained, so it can never drift from STAGES.
SUPPORTED_STAGES = set(STAGES.keys())
