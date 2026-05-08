
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
        print("Checking yj_year_sum_view data:")
        res = await conn.execute(text("SELECT * FROM yj_year_sum_view"))
        rows = res.fetchall()
        print(f"Rows: {rows}")

        print("\nChecking yj_year_sum_view definition:")
        res = await conn.execute(text("SELECT definition FROM pg_catalog.pg_views WHERE viewname = 'yj_year_sum_view'"))
        defn = res.scalar()
        print(f"Definition: {defn}")

if __name__ == "__main__":
    asyncio.run(check())
