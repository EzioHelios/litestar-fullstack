
import asyncio
import sys
from pathlib import Path

# Set policy for Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def check():
    project_root = Path(__file__).resolve().parents[3]
    sys.path.append(str(project_root / "src" / "py"))

    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.lib.settings import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.db.URL)

    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT current_database()"))
        db_name = res.scalar()
        print(f"Current DB: {db_name}")

        res = await conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [r[0] for r in res.fetchall()]
        print(f"Tables: {sorted(tables)}")

if __name__ == "__main__":
    asyncio.run(check())
