"""
Migration script to add priority and tags columns to tasks table.

Run this script once to update the database schema.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings


async def run_migration():
    """Add priority and tags columns to tasks table."""
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # SQL statements
    migrations = [
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'Medium';",
        "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS tags VARCHAR(500) DEFAULT '';",
        "UPDATE tasks SET priority = 'Medium' WHERE priority IS NULL;",
        "UPDATE tasks SET tags = '' WHERE tags IS NULL;",
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
