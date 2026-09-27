#!/bin/bash

set -e

# Repository-root guard: resolve paths relative to this script's location
# rather than the caller's working directory, and confirm we are actually
# inside the AI Website Factory repository before creating anything.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

if [ ! -f "CLAUDE.md" ] || [ ! -d "agents" ] || [ ! -f "templates/PROJECT-BRIEF.md" ]; then
  echo "Error: could not confirm the AI Website Factory repository root at $REPO_ROOT."
  exit 1
fi

if [ -z "$1" ]; then
  echo "Usage: ./tools/init-project.sh project-name [website-type]"
  exit 1
fi

PROJECT_NAME="$1"
WEBSITE_TYPE="${2:-}"

if ! [[ "$PROJECT_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]]; then
  echo "Error: project name must start with a letter or number and contain only letters, numbers, hyphens, and underscores."
  exit 1
fi

STARTER_FILE=""
if [ -n "$WEBSITE_TYPE" ]; then
  if ! [[ "$WEBSITE_TYPE" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]]; then
    echo "Error: website type must start with a letter or number and contain only letters, numbers, hyphens, and underscores."
    exit 1
  fi
  STARTER_FILE="templates/website-types/$WEBSITE_TYPE/STARTER.md"
  if [ ! -f "$STARTER_FILE" ]; then
    AVAILABLE=$(find templates/website-types -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')
    echo "Error: unknown website type '$WEBSITE_TYPE'. Available types: ${AVAILABLE:-none configured}."
    exit 1
  fi
fi

PROJECT_DIR="projects/$PROJECT_NAME"

if [ -d "$PROJECT_DIR" ]; then
  echo "Error: project '$PROJECT_NAME' already exists."
  exit 1
fi

echo "Creating project: $PROJECT_NAME"

mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/architecture"
mkdir -p "$PROJECT_DIR/design/assets"
mkdir -p "$PROJECT_DIR/src"
mkdir -p "$PROJECT_DIR/tests"
mkdir -p "$PROJECT_DIR/reports"
mkdir -p "$PROJECT_DIR/documentation"

# Vercel deploys from src/ (where the project link lives), so headers config must live there too.
if [ -f "templates/security/vercel.json" ]; then
  cp "templates/security/vercel.json" "$PROJECT_DIR/src/vercel.json"
fi

if [ -f ".env.example" ]; then
  cp ".env.example" "$PROJECT_DIR/.env.example"
fi

cat > "$PROJECT_DIR/.gitignore" <<'EOF'
.env
.env.local
.env.*.local
!.env.example
node_modules/
.vercel/
EOF

# Placeholder files so git tracks these otherwise-empty directories.
touch "$PROJECT_DIR/design/assets/.gitkeep"
touch "$PROJECT_DIR/src/.gitkeep"
touch "$PROJECT_DIR/tests/.gitkeep"

if [ -f "templates/PROJECT-BRIEF.md" ]; then
  cp "templates/PROJECT-BRIEF.md" "$PROJECT_DIR/PROJECT-BRIEF.md"
else
  touch "$PROJECT_DIR/PROJECT-BRIEF.md"
fi

if [ -n "$STARTER_FILE" ]; then
  {
    printf '\n---\n\n'
    cat "$STARTER_FILE"
  } >> "$PROJECT_DIR/PROJECT-BRIEF.md"
fi

cat > "$PROJECT_DIR/PROJECT-STATUS.md" <<EOF
# Project Status

## Project

$PROJECT_NAME

## Current Stage

Intake

## Current Owner

Project Orchestrator

## Completed Stages

None

## Active Work

Complete and review PROJECT-BRIEF.md.

## Blockers

None identified.

## Known Issues

None identified.

## Human Decisions Required

Complete project requirements where needed.

## Next Action

Review PROJECT-BRIEF.md and begin architecture.
EOF

cat > "$PROJECT_DIR/architecture/ARCHITECTURE.md" <<EOF
# Architecture

Project: $PROJECT_NAME

Status: Not started

## Sitemap

To be completed by Website Architect.

## User Journeys

To be completed by Website Architect.

## Technology Stack

To be determined.

## Frontend Architecture

To be determined.

## Backend Requirements

To be determined.

## Integrations

To be determined.

## Risks

None documented yet.

## Assumptions

None documented yet.
EOF

cat > "$PROJECT_DIR/design/UI-UX-SPEC.md" <<EOF
# UI/UX Specification

Project: $PROJECT_NAME

Status: Not started

## Design Direction

To be completed by UI/UX Designer.

## Page Layouts

To be completed.

## Responsive Behavior

To be completed.

## Components

To be completed.

## Navigation

To be completed.

## Forms

To be completed.

## Accessibility Considerations

To be completed.
EOF

touch "$PROJECT_DIR/reports/QA-REPORT.md"
touch "$PROJECT_DIR/reports/SECURITY-REPORT.md"
touch "$PROJECT_DIR/reports/PERFORMANCE-REPORT.md"
touch "$PROJECT_DIR/reports/ACCESSIBILITY-REPORT.md"
touch "$PROJECT_DIR/reports/SEO-REPORT.md"

cat > "$PROJECT_DIR/documentation/DEVELOPMENT.md" <<EOF
# Development

Project: $PROJECT_NAME

## Technology Stack

To be documented.

## Prerequisites

To be documented.

## Installation

To be documented.

## Development

To be documented.

## Build

To be documented.

## Testing

To be documented.
EOF

cat > "$PROJECT_DIR/documentation/DEPLOYMENT.md" <<EOF
# Deployment

Project: $PROJECT_NAME

## Deployment Platform

To be determined.

## Build Process

To be documented.

## Environment Variables

Document variable names only. Do not store secret values here.

## Deployment Procedure

To be documented.

## Post-Deployment Verification

To be documented.

## Rollback

To be documented when applicable.
EOF

cat > "$PROJECT_DIR/documentation/CHANGELOG.md" <<EOF
# Changelog

All meaningful changes to $PROJECT_NAME should be documented here.
EOF

cat > "$PROJECT_DIR/README.md" <<EOF
# $PROJECT_NAME

## Purpose

See PROJECT-BRIEF.md.

## Current Status

Intake

## Architecture

See architecture/ARCHITECTURE.md.

## Design

See design/UI-UX-SPEC.md.

## Development

See documentation/DEVELOPMENT.md.

## Deployment

See documentation/DEPLOYMENT.md.
EOF

echo ""
echo "Project created successfully:"
echo "$PROJECT_DIR"
if [ -n "$STARTER_FILE" ]; then
  echo "Website type starting point applied: $WEBSITE_TYPE"
fi
echo ""
echo "Next step:"
echo "Open $PROJECT_DIR/PROJECT-BRIEF.md and complete the project requirements."