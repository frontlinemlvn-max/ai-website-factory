#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: ./tools/init-project.sh project-name"
  exit 1
fi

PROJECT_NAME="$1"
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

if [ -f "templates/PROJECT-BRIEF.md" ]; then
  cp "templates/PROJECT-BRIEF.md" "$PROJECT_DIR/PROJECT-BRIEF.md"
else
  touch "$PROJECT_DIR/PROJECT-BRIEF.md"
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
echo ""
echo "Next step:"
echo "Open $PROJECT_DIR/PROJECT-BRIEF.md and complete the project requirements."