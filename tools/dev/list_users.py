import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "py"))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.domain.accounts.services import UserService
from app.lib.settings import get_settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def list_users():
    settings = get_settings()
    engine = create_async_engine(settings.db.URL)
    session_factory = async_sessionmaker(engine)
    async with session_factory() as session:
        user_service = UserService(session)
        users = await user_service.list()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"- {u.email} (superuser: {u.is_superuser}, active: {u.is_active})")

if __name__ == "__main__":
    asyncio.run(list_users())
