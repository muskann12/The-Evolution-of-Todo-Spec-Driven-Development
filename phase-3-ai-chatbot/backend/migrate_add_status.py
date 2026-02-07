"""
Migration script to add status column to tasks table.

Run this script once to add the status column to existing tasks.
All existing tasks will default to 'ready' status.
"""

import asyncio
from sqlalchemy import text
from app.database import engine


async def add_status_column():
    """Add status column to tasks table if it doesn't exist."""
    async with engine.begin() as conn:
        # Check if column exists
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='tasks' AND column_name='status'
        """)
        result = await conn.execute(check_query)
        exists = result.fetchone()

        if exists:
            print("[OK] Status column already exists")
            return

        # Add status column with default value 'ready'
        print("Adding status column to tasks table...")
        alter_query = text("""
            ALTER TABLE tasks
            ADD COLUMN status VARCHAR(20) DEFAULT 'ready' NOT NULL
        """)
        await conn.execute(alter_query)

        # Create index on status column
        print("Creating index on status column...")
        index_query = text("""
            CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks(status)
        """)
        await conn.execute(index_query)

        print("[OK] Migration completed successfully!")


if __name__ == "__main__":
    print("Starting migration...")
    asyncio.run(add_status_column())
    print("Done!")
