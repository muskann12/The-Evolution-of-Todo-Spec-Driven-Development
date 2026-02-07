"""
Migration script to add recurrence fields to tasks table.

Run this script once to update the database schema.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings


async def run_migration():
    """Add recurrence_pattern and recurrence_interval columns to tasks table."""
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # SQL statements
    migrations = [
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(10) DEFAULT NULL;",
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1;",
    ]

    # Execute migrations
    async with engine.begin() as conn:
        for sql in migrations:
            print(f"Executing: {sql}")
            await conn.execute(text(sql))
            print("OK - Success")

    print("\nMigration completed successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
