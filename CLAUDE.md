# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Litestar Fullstack reference application — a production-ready fullstack web API built with Litestar (Python ASGI framework) and a React SPA frontend served via Vite. Uses PostgreSQL, SQLAlchemy 2.0, Advanced Alchemy, SAQ (async task queue with Redis), and Granian as the ASGI server.

## Common Commands

### Setup
```bash
make install          # Full install: uv venv, deps, bun install for frontend
cp .env.local.example .env
make start-infra      # Start PostgreSQL via Docker
app database upgrade   # Run Alembic migrations
app run               # Start the dev server (Granian)
```

### Testing
```bash
uv run pytest src/py/tests --quiet                     # Run all tests (uses xdist auto parallelism)
uv run pytest src/py/tests/unit -k "test_name"         # Run a single test by name
uv run pytest src/py/tests -m unit                     # Run only unit tests
uv run pytest src/py/tests -m integration              # Run only integration tests
```
Tests require a PostgreSQL instance (provided by `pytest-databases` Docker fixture). The conftest sets environment variables before any app imports — settings are cached on first import.

### Linting & Type Checking
```bash
make ruff             # Ruff check + format (Python)
make biome            # Biome lint (JS/TS, runs via bun in src/js/web)
make mypy             # mypy via dmypy daemon
make pyright          # pyright
make lint             # All: ruff + mypy + pyright + slotscheck + biome + codespell
make pre-commit       # Run all pre-commit hooks
```

### Build
```bash
make build            # Build emails + frontend assets + Python wheel
make types            # Export OpenAPI schema → generate TypeScript types/client
```

### Database Migrations (Alembic via Advanced Alchemy)
```bash
app database upgrade          # Apply migrations
app database downgrade        # Rollback
app database make-migrations  # Auto-generate a new migration
```

## Architecture

### Source Layout
```
src/
├── py/                       # Python backend (hatch source root)
│   ├── app/                  # Main application package
│   │   ├── server/           # ASGI app factory, core plugin, static files
│   │   ├── domain/           # Business domains (DDD-style)
│   │   ├── db/               # SQLAlchemy models, Alembic migrations, fixtures
│   │   ├── lib/              # Shared utilities: settings, email, crypto, logging, validation
│   │   ├── cli/              # CLI commands (extends Litestar CLI)
│   │   ├── config.py         # Instantiates all config objects from settings
│   │   └── utils/            # General-purpose helpers
│   └── tests/
│       ├── unit/
│       ├── integration/
│       ├── conftest.py       # DB fixtures, env setup (must set env BEFORE app imports)
│       └── factories.py      # Polyfactory model factories
└── js/
    ├── web/                  # React SPA (Vite + TanStack Router + Tailwind CSS)
    │   └── src/routes/       # File-based routing (_app/ = authenticated, _public/ = guest)
    └── templates/            # React Email templates → compiled to static HTML
```

### Key Architectural Patterns

**App factory**: `src/py/app/server/asgi.py:create_app()` creates the Litestar instance with a single `ApplicationCore` plugin (`server/core.py`) that wires all routes, guards, dependencies, and sub-plugins.

**Domain modules**: Each domain (`accounts`, `teams`, `tags`, `carbon`, `system`, `admin`) follows a consistent structure:
- `controllers/` — Litestar route handlers (one file per concern, prefixed with `_`)
- `services/` — Business logic layer using Advanced Alchemy service/repository pattern
- `schemas/` — Pydantic models for request/response DTOs
- `deps.py` — Dependency providers for the domain
- `guards.py` — Route guards for authorization

**Database models**: All SQLAlchemy models live in `src/py/app/db/models/` (prefixed with `_`) and are re-exported from `db/models/__init__.py`. Models use Advanced Alchemy's `UUIDAuditBase`.

**Settings**: `src/py/app/lib/settings.py` — dataclass-based settings loaded from environment variables (via `python-dotenv`). Settings are cached via `@lru_cache` on `get_settings()`. Configuration objects are instantiated in `app/config.py`.

**Authentication**: JWT-based auth with refresh tokens, MFA (TOTP via pyotp), and OAuth support (httpx-oauth). Auth guard is in `domain/accounts/guards.py`.

**Frontend integration**: Litestar-Vite serves the React SPA. `make types` generates TypeScript API client from the OpenAPI schema using `@hey-api`.

## Code Conventions

- Python line length: 120 characters (ruff)
- Ruff selects ALL rules with specific ignores; uses Google-style docstrings
- Relative imports are banned — use absolute imports (`from app.domain.accounts...`)
- Known first-party packages for isort: `tests`, `app`
- Python source root is `src/py` (configured in hatch and ruff)
- Frontend uses bun as package manager, biome for linting
- Test markers: `unit`, `integration`, `slow`, `auth`, `email`, `oauth`, `services`, `models`, `endpoints`, `security`, `teams`
