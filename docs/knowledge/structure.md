# Project Structure

```
paperwriter/
├── .github/
│   ├── workflows/ci.yml       # CI pipeline (lint → test → coverage → docs → build)
│   └── ISSUE_TEMPLATE/        # feature, bug, epic templates
├── .opencode/                 # Agent configuration
│   ├── opencode.json          # Custom commands, hooks, knowledge config
│   ├── agents.json            # Agent definitions (dev, review, test, architect)
│   └── workflows/             # Dynamic workflow scripts
├── docs/
│   ├── adr/                   # Architecture Decision Records
│   ├── knowledge/             # Auto-generated project knowledge
│   ├── contracts/             # Sprint contracts
│   ├── handoffs/              # Agent handoff manifests
│   ├── ARCHITECTURE.md        # System architecture overview
│   └── CONTRIBUTING.md        # Workflow guide
├── scripts/
│   ├── validate.sh            # Local validation script
│   └── generate-docs.sh       # Documentation generation
├── paperwriter/
│   ├── .env.example           # Environment variable template
│   ├── requirements.txt       # Python dependencies
│   ├── backend/               # Django project
│   │   ├── manage.py
│   │   ├── api/               # DRF app (models, views, serializers, urls)
│   │   ├── paperwriter/       # Django project settings
│   │   ├── static/            # Frontend assets (JS, CSS)
│   │   ├── templates/         # Django templates (index.html)
│   │   ├── tests/             # Test suite
│   │   │   ├── unit/          # Fast, isolated tests
│   │   │   ├── integration/   # Cross-module tests
│   │   │   └── e2e/           # Full-stack end-to-end tests
│   │   └── seed_db.py         # Database seeder
│   └── ieee_format/           # IEEE LaTeX template files
├── Dockerfile
├── docker-compose.yml
├── Makefile                   # Dev commands (lint, test, build, validate)
├── codemeta.json              # Project metadata
├── PROGRESS.md                # Feature progress tracking
└── README.md
```
