
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "py"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.lib.settings import get_settings


async def query_raw_users():
    settings = get_settings()
    engine = create_async_engine(settings.db.URL)

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT email, is_superuser, is_active FROM user_account"))
        rows = result.fetchall()
        print(f"Total users in user_account: {len(rows)}")
        for row in rows:
            print(f"- {row.email} (superuser: {row.is_superuser}, active: {row.is_active})")

if __name__ == "__main__":
    asyncio.run(query_raw_users())
