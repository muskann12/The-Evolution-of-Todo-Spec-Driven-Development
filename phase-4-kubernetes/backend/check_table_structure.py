"""Check the actual structure of the users table."""
import asyncio
from app.database import engine
from sqlalchemy import text


async def check_structure():
    """Check users table structure."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """)
            )
            columns = result.fetchall()

            print("[INFO] Users table structure:")
            print("=" * 60)
            for col in columns:
                print(f"  {col[0]:<20} {col[1]:<15} nullable={col[2]}")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_structure())
