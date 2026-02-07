"""Check database tables."""
import asyncio
from sqlalchemy import text
from db import engine


async def check_tables():
    """List all tables in the database."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]

        print("Tables in database:")
        for table in tables:
            print(f"  - {table}")

        return tables


if __name__ == "__main__":
    tables = asyncio.run(check_tables())
    print(f"\nTotal: {len(tables)} tables created")
