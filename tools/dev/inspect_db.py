
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "py"))

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from app.lib.settings import get_settings

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def inspect_table():
    settings = get_settings()
    engine = create_async_engine(settings.db.URL)
    def inspect_sync(connection):
        ins = inspect(connection)
        columns = ins.get_columns("user_account")
        for col in columns:
            print(f"Column: {col['name']}, Nullable: {col['nullable']}, Type: {col['type']}")

    async with engine.connect() as conn:
        await conn.run_sync(inspect_sync)

if __name__ == "__main__":
    asyncio.run(inspect_table())
