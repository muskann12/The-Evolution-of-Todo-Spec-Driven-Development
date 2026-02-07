"""
Clear old tasks with integer IDs from the database.
This removes tasks created by the Phase 1 console app.
"""
import asyncio
from app.database import engine
from sqlalchemy import text


async def clear_old_tasks():
    """Delete all tasks from the database."""
    async with engine.begin() as conn:
        # Delete all tasks (old and new)
        result = await conn.execute(text("DELETE FROM tasks"))
        print(f"Cleared {result.rowcount} tasks from database")
        print("Database is now ready for Phase 2 web app")


if __name__ == "__main__":
    asyncio.run(clear_old_tasks())
