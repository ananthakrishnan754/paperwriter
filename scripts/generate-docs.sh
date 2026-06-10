#!/usr/bin/env bash
set -euo pipefail

echo "Generating documentation for PaperWriter..."

# Build the main ARCHITECTURE.md from ADRs
cat > docs/ARCHITECTURE.md << 'EOF'
# PaperWriter Architecture

> Auto-generated from ADRs and codebase analysis.

## Overview

PaperWriter is a full-stack, single-page web application for authoring,
formatting, and exporting IEEE-style research papers.

## Architecture Diagram

```
Frontend (Vanilla SPA + TipTap)
       |
   REST API (DRF)
       |
   Django ORM
       |
   SQLite / PostgreSQL
       |
   AI (Gemini)    LaTeX Engine (pdflatex)
```

## Components

### Backend (Django REST Framework)
EOF

echo "  - Reading ADRs..."
for adr in docs/adr/*.md; do
  title=$(head -1 "$adr" | sed 's/^# //')
  echo "- [$title]($adr)" >> docs/ARCHITECTURE.md
done

echo "" >> docs/ARCHITECTURE.md
echo "## Data Model" >> docs/ARCHITECTURE.md
echo "" >> docs/ARCHITECTURE.md
echo '```' >> docs/ARCHITECTURE.md
echo "Document ──┬── Section (recursive FK, max 3 levels)" >> docs/ARCHITECTURE.md
echo "            ├── Author (ordered, IEEE ordinal)" >> docs/ARCHITECTURE.md
echo "            ├── PaperImage (figures with LaTeX metadata)" >> docs/ARCHITECTURE.md
echo "            └── Reference (BibTeX entries)" >> docs/ARCHITECTURE.md
echo '```' >> docs/ARCHITECTURE.md

echo ""
echo "Documentation generated at docs/ARCHITECTURE.md"
