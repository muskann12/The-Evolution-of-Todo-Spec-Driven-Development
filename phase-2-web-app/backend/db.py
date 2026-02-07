"""Database connection and session management.

This module provides async database connection using SQLModel and asyncpg.
"""
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from models import User, Task  # Import models to register with SQLModel metadata


# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,      # Test connections before using
    pool_size=10,            # Base pool size
    max_overflow=20,         # Additional connections allowed
    pool_timeout=30          # Timeout for getting connection (seconds)
)

# Create async session maker
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """
    Dependency that provides database sessions.

    Yields:
        AsyncSession: Database session with automatic commit/rollback

    Example:
        @router.get("/tasks")
        async def get_tasks(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """
    Initialize database by creating all tables.

    This is typically called on application startup.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
