"""
Migration script to add due_date field to tasks table.

Run this script once to update the database schema.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings


async def run_migration():
    """Add due_date column to tasks table."""
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # SQL statements
    migrations = [
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP DEFAULT NULL;",
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
