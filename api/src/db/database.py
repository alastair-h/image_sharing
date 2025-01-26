from os import getenv

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

db_name = getenv("POSTGRES_DB")
user = getenv("POSTGRES_USER")
pw = getenv("POSTGRES_PASSWORD")
DATABASE_URL = f"postgresql+asyncpg://{user}:{pw}@db:5432/{db_name}"


def get_async_engine() -> AsyncEngine:  # TODO: use Singleton pattern with DI
    async_engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        future=True,
    )

    return async_engine


async def get_async_session():
    async_session = sessionmaker(
        bind=get_async_engine(),
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
    async with async_session() as async_sess:
        yield async_sess
