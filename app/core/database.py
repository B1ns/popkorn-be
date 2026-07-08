# app/core/database.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        echo=True,
        pool_pre_ping=True,
    )


engine = _build_engine()
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def reset_engine():
    """Celery worker가 포크된 직후 호출 — 부모 프로세스의 엔진을 그대로 물려받지 않고 새로 만든다."""
    global engine, AsyncSessionLocal
    engine = _build_engine()
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()