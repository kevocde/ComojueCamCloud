import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{Path(__file__).parent / 'data' / 'comojuecam.db'}"
)

Path(DATABASE_URL.rsplit('/', 1)[0].replace("sqlite+aiosqlite://", "")).mkdir(parents=True, exist_ok=True)

engine = create_async_engine(DATABASE_URL, echo=False)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    from comojuecamcloud.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()
