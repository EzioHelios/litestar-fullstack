
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "py"))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.domain.carbon.services import EnterpriseInfoService
from app.lib.settings import get_settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def debug_service():
    settings = get_settings()
    engine = create_async_engine(settings.db.URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        service = EnterpriseInfoService(session)
        print("Calling service.get_one_or_none()...")
        try:
            obj = await service.get_one_or_none()
            print(f"Result: {obj}")
            if obj:
                print(f"Has to_dict: {hasattr(obj, 'to_dict')}")
                if hasattr(obj, "to_dict"):
                    print(f"to_dict() output: {obj.to_dict()}")
                else:
                    print("Direct __dict__: ", obj.__dict__)
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")
            if hasattr(e, "__cause__") and e.__cause__:
                print(f"Cause: {type(e.__cause__).__name__}: {e.__cause__}")
            if hasattr(e, "orig"):
                print(f"Original exception: {type(e.orig).__name__}: {e.orig}")

            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_service())
