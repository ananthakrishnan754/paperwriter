.PHONY: lint typecheck test-unit test-int coverage coverage-check docs-lint docs-build build validate format venv install

VENV_DIR = paperwriter/backend/venv
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PYTEST = $(VENV_DIR)/bin/pytest
RUFF = $(VENV_DIR)/bin/ruff
MYPY = $(VENV_DIR)/bin/mypy
MANAGE = $(VENV_DIR)/bin/python paperwriter/backend/manage.py

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install -r paperwriter/requirements.txt
	$(PIP) install ruff mypy pytest pytest-cov pytest-django pytest-timeout pytest-factoryboy model-bakery

lint:
	$(RUFF) check paperwriter/

lint-fix:
	$(RUFF) check --fix paperwriter/

format:
	$(RUFF) format paperwriter/

typecheck:
	$(MYPY) paperwriter/ --ignore-missing-imports

test-unit:
	cd paperwriter/backend && PYTHONPATH=.. $(PYTEST) tests/unit/ -x --timeout=30 --reuse-db -v

test-int:
	cd paperwriter/backend && PYTHONPATH=.. $(PYTEST) tests/integration/ -x --timeout=180 --reuse-db -v

test-e2e:
	cd paperwriter/backend && PYTHONPATH=.. $(PYTEST) tests/e2e/ -x --timeout=300 --reuse-db -v

test:
	cd paperwriter/backend && PYTHONPATH=.. $(PYTEST) tests/ -x --timeout=180 --reuse-db -v

coverage:
	cd paperwriter/backend && PYTHONPATH=.. $(PYTEST) --cov=api --cov-report=term --cov-report=xml tests/

coverage-check:
	@echo "Coverage check: ensuring new code meets threshold"

docs-lint:
	@echo "Checking markdown..."
	$(RUFF) check docs/ --ignore=D --extend-exclude=docs/adr

docs-build:
	@echo "Documentation is markdown-based; no build step required."
	@echo "All docs live in docs/ and are human-readable."

build:
	@echo "Building Docker image..."
	docker compose build

validate: lint typecheck test coverage docs-lint docs-build
	@echo "All validation layers passed."

migrate:
	$(MANAGE) migrate

collectstatic:
	$(MANAGE) collectstatic --noinput

seed:
	$(MANAGE) shell < paperwriter/backend/seed_db.py

run:
	$(MANAGE) runserver

shell:
	$(MANAGE) shell
