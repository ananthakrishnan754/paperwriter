{
  "project": "PaperWriter",
  "features": [
    {"id": "doc-crud",     "description": "Create, read, update, delete documents",          "passes": true},
    {"id": "section-crud", "description": "Section management with recursive hierarchy",     "passes": true},
    {"id": "author-mgmt",  "description": "Author management with IEEE ordinal formatting",  "passes": true},
    {"id": "image-upload", "description": "Image upload with LaTeX metadata",                "passes": true},
    {"id": "ref-mgmt",     "description": "BibTeX reference management",                     "passes": true},
    {"id": "ai-command",   "description": "AI text transformation via Gemini",               "passes": true},
    {"id": "latex-export", "description": "LaTeX source generation and preview",             "passes": true},
    {"id": "pdf-export",   "description": "PDF compilation via pdflatex",                    "passes": true},
    {"id": "latex-zip",    "description": "LaTeX project ZIP export",                        "passes": true},
    {"id": "frontend-ui",  "description": "TipTap editor with 3-panel layout",              "passes": true},
    {"id": "user-auth",    "description": "JWT auth (register, login, me, token refresh)",  "passes": true},
    {"id": "ownership",    "description": "Document ownership, per-user isolation",          "passes": true},
    {"id": "permissions",  "description": "Object-level permissions on all resources",       "passes": true},
    {"id": "rate-limiting","description": "Rate limiting on API endpoints",                  "passes": true},
    {"id": "prod-config",  "description": "Env-based settings, whitenoise, logging",         "passes": true},
    {"id": "health-check", "description": "Health check endpoint for monitoring",            "passes": true},
    {"id": "security",     "description": "CORS hardening, CSP, HSTS, secure cookies",       "passes": true},
    {"id": "frontend-auth","description": "Auth UI: login/register screens, token injection",  "passes": true}
  ],
  "current_sprint": "Production Readiness",
  "infrastructure": [
    {"id": "ci-pipeline",      "description": "GitHub Actions CI with layered pipeline",      "passes": true},
    {"id": "makefile",         "description": "Makefile with all targets",                    "passes": true},
    {"id": "docker",           "description": "Dockerfile + docker-compose.yml",              "passes": true},
    {"id": "opencode-config",  "description": "Agent configuration",                          "passes": true},
    {"id": "issue-templates",  "description": "GitHub issue templates",                       "passes": true},
    {"id": "adrs",             "description": "Architecture Decision Records (5 ADRs)",       "passes": true},
    {"id": "knowledge-base",   "description": "Project knowledge",                            "passes": true},
    {"id": "test-suite",       "description": "86 unit/integration/e2e tests",                "passes": true},
    {"id": "lint-clean",       "description": "All lint checks passing",                      "passes": true},
    {"id": "coverage-84",      "description": "84% test coverage",                            "passes": true}
  ],
  "checkpoints": [
    {"id": "ckpt-001", "time": "2026-06-10T00:00Z", "status": "verified", "features": 10, "infrastructure": 0},
    {"id": "ckpt-002", "time": "2026-06-10T10:30Z", "status": "verified", "features": 10, "infrastructure": 10},
    {"id": "ckpt-003", "time": "2026-06-10T12:00Z", "status": "verified", "features": 17, "infrastructure": 10},
    {"id": "ckpt-004", "time": "2026-06-10T14:00Z", "status": "verified", "features": 18, "infrastructure": 10}
  ]
}
