"""Check tasks table schema."""
import asyncio
from sqlalchemy import text
from db import engine


async def check_schema():
    """Check the tasks table schema."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT column_name, data_type, is_nullable, column_default "
                "FROM information_schema.columns "
                "WHERE table_name='tasks' "
                "ORDER BY ordinal_position"
            )
        )

        print("Tasks table structure:")
        print(f"{'Column':<25} {'Type':<20} {'Nullable':<10} {'Default'}")
        print("-" * 80)

        for row in result:
            print(f"{row[0]:<25} {row[1]:<20} {row[2]:<10} {row[3]}")


if __name__ == "__main__":
    asyncio.run(check_schema())
