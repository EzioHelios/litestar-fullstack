from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PY_SRC = REPO_ROOT / "src" / "py"


def ensure_py_src_path() -> None:
    """Make the backend package importable when running tools directly."""
    py_src = str(PY_SRC)
    if py_src not in sys.path:
        sys.path.insert(0, py_src)


def require_env(name: str) -> str:
    """Return a required environment variable with a clear error message."""
    value = os.environ.get(name)
    if not value:
        msg = f"Set {name} before running this tool."
        raise RuntimeError(msg)
    return value


def to_sync_postgres_url(url: str) -> str:
    """Normalize SQLAlchemy async Postgres URLs for psycopg scripts."""
    return url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")
