"""
Clear all prepared statements from Neon PostgreSQL server.
This fixes cached statement errors after schema changes.
"""
import asyncio
from app.database import engine
from sqlalchemy import text


async def clear_cache():
    """Issue DISCARD ALL to clear server-side caches."""
    async with engine.connect() as conn:
        await conn.execute(text("DISCARD ALL"))
        print("Cleared all prepared statements from database server")
        await conn.commit()


if __name__ == "__main__":
    asyncio.run(clear_cache())
