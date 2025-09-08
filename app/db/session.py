from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
