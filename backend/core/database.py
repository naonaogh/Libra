from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy-моделей."""

    pass


engine = create_async_engine(
    settings.database_url,
    echo=False,
)


async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Создаёт асинхронную сессию базы данных."""

    async with async_session_maker() as session:
        yield session