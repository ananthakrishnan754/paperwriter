# Contributing to PaperWriter

## Workflow

Every task follows the closed-loop development workflow:

```
Issue → Plan → Code → Validate → Fix → Pass → Merge → Close
```

## Getting Started

```bash
make install    # Create venv and install deps
make migrate    # Run database migrations
make seed       # Seed with sample data
make run        # Start dev server at localhost:8000
```

## Development Process

1. **File an issue** using the templates (bug / feature / epic)
2. **Create a branch**: `feat/<issue-number>-<short-name>`
3. **Write code** following existing patterns (see `docs/knowledge/patterns.md`)
4. **Run validation**: `make validate` — MUST pass before commit
5. **Fix issues** until all layers green
6. **Open a PR** with summary, test delta, and docs updated
7. **Request review** from the review agent or a human
8. **Squash-merge** to main — issue closes automatically

## Validation Layers

| Layer | Command | What it checks |
|---|---|---|
| Lint | `make lint` | Code style, imports, anti-patterns (ruff) |
| Typecheck | `make typecheck` | Type annotations (mypy) |
| Unit tests | `make test-unit` | Fast logic tests (<30s) |
| Integration | `make test-int` | API contracts, DB queries (<3m) |
| Coverage | `make coverage` | New code ≥ 90% coverage |
| Docs | `make docs-lint` | Documentation validity |
| Build | `make build` | Docker image compiles |

## PR Review Checklist

- [ ] All CI jobs green
- [ ] Test coverage ≥ 90% for new code
- [ ] No hardcoded secrets or API keys
- [ ] Docs updated (module README, API if relevant)
- [ ] Follows patterns in `docs/knowledge/patterns.md`
- [ ] No deviations from ADRs without a new ADR

## Agent Configuration

See `.opencode/agents.json` for specialized agent definitions and
`.opencode/opencode.json` for custom commands.

## Project Standards

- **Python**: 3.12, ruff for linting/formatting
- **Django**: 6.0+, DRF for API
- **Frontend**: Vanilla JS, no build step
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Tests**: pytest with model-bakery factories
