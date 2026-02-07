"""
Drop and recreate the tasks table with the correct schema for Phase 2.
This fixes the issue where the old Phase 1 schema had INTEGER ids but Phase 2 uses VARCHAR UUIDs.
"""
import asyncio
from app.database import engine
from sqlalchemy import text


async def recreate_tasks_table():
    """Drop and recreate the tasks table with correct schema."""
    async with engine.begin() as conn:
        # Drop the old tasks table
        await conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
        print("Dropped old tasks table")

        # Create new tasks table with VARCHAR id
        await conn.execute(text("""
            CREATE TABLE tasks (
                id VARCHAR PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description VARCHAR(1000),
                completed BOOLEAN DEFAULT FALSE,
                priority VARCHAR(10) DEFAULT 'Medium',
                tags TEXT DEFAULT '',
                recurrence_pattern VARCHAR(10),
                recurrence_interval INTEGER DEFAULT 1,
                due_date TIMESTAMP,
                user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("Created new tasks table with VARCHAR id")

        # Create indexes
        await conn.execute(text("CREATE INDEX idx_tasks_user_id ON tasks(user_id)"))
        await conn.execute(text("CREATE INDEX idx_tasks_completed ON tasks(completed)"))
        await conn.execute(text("CREATE INDEX idx_tasks_priority ON tasks(priority)"))
        await conn.execute(text("CREATE INDEX idx_tasks_due_date ON tasks(due_date)"))
        print("Created indexes")

        print("Tasks table is now ready for Phase 2!")


if __name__ == "__main__":
    asyncio.run(recreate_tasks_table())
