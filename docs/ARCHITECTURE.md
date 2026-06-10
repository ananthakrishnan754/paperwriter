# PaperWriter Architecture

## Overview

PaperWriter is a Django REST Framework backend with a vanilla JavaScript SPA frontend. It uses SQLite for development, JWT authentication, and Gemini AI for text processing.

## Key Architecture Decisions

See [ADRs](./adr/) for detailed records:

| ADR | Decision |
|-----|----------|
| ADR-0001 | Django REST Framework for API |
| ADR-0002 | Vanilla JS SPA (no frontend framework) |
| ADR-0003 | SQLite for development |
| ADR-0004 | Google Gemini for AI text |
| ADR-0005 | Recursive section hierarchy |
| ADR-0006 | JWT authentication |
| ADR-0007 | Object-level permissions |
| ADR-0008 | Production configuration |

## Data Flow

```
Browser → nginx/WhiteNoise → Django → SQLite
   ↑              ↓
   └─────── JSON API (DRF)
```

## Directory Structure

- `paperwriter/backend/api/` — Django app (models, views, serializers, auth)
- `paperwriter/backend/static/` — Frontend JS/CSS
- `paperwriter/backend/templates/` — HTML templates
- `paperwriter/backend/tests/` — Unit, integration, e2e tests
- `docs/` — ADRs, knowledge base, contributing guide

See [docs/knowledge/structure.md](./knowledge/structure.md) for the full layout.
