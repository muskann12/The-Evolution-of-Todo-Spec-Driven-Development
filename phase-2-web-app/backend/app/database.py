"""
Database connection and session management using SQLModel.

Uses asyncpg driver for async PostgreSQL connections.
"""

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.config import settings


# Convert postgresql:// to postgresql+asyncpg:// for async support
async_database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Remove sslmode from URL if present (asyncpg uses ssl parameter instead)
if "?sslmode=" in async_database_url:
    base_url = async_database_url.split("?")[0]
    async_database_url = base_url

# Create async engine
# Disable prepared statement caching to avoid schema change issues
# Use ssl='require' for Neon PostgreSQL connections
engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    future=True,
    connect_args={
        "prepared_statement_cache_size": 0,
        "ssl": "require"
    },
)

# Create async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """
    Initialize database tables.

    Creates all tables defined in SQLModel models.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.

    Usage in FastAPI:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...

    Yields:
        AsyncSession: Database session that auto-closes after request
    """
    async with async_session_maker() as session:
        yield session
