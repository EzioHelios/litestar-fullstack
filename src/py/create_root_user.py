
import asyncio
import uuid
import traceback
import sys
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError as SQIntegrityError
from advanced_alchemy.exceptions import IntegrityError as AAIntegrityError
from app.lib.settings import get_settings
from app.lib import crypt
from app.db.models import User

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def create_root_user():
    settings = get_settings()
    engine = create_async_engine(settings.db.URL)
    session_factory = async_sessionmaker(engine)
    async with session_factory() as session:
        try:
            password = "12345678"
            hashed_password = await crypt.get_password_hash(password)
            
            now = datetime.now(UTC)
            user = User(
                id=uuid.uuid4(),
                email="root@example.com",
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=True,
                is_verified=True,
                name="Root User",
                joined_at=now.date(),
                login_count=0,
                failed_reset_attempts=0,
                is_two_factor_enabled=False,
                created_at=now,
                updated_at=now
            )
            session.add(user)
            await session.commit()
            print("User root@example.com created successfully.")
        except (SQIntegrityError, AAIntegrityError) as e:
            print(f"IntegrityError: {e}")
            if hasattr(e, 'orig'):
                print(f"Orig: {e.orig}")
            if hasattr(e, 'statement'):
                print(f"Statement: {e.statement}")
            if hasattr(e, 'params'):
                print(f"Params: {e.params}")
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_root_user())
