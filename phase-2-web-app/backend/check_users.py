"""Script to check users in the database."""
import asyncio
from app.database import engine
from app.models import User
from sqlmodel import select
from sqlalchemy import text


async def check_users():
    """Check if there are any users in the database."""
    try:
        async with engine.begin() as conn:
            # First check if the users table exists
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            table_exists = result.scalar()

            if not table_exists:
                print("[ERROR] Users table does not exist. Please run database migrations.")
                return

            print("[OK] Users table exists")

            # Count users
            count_result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = count_result.scalar()

            print(f"[INFO] Total users in database: {user_count}")

            # List all users (email only, not passwords)
            if user_count > 0:
                users_result = await conn.execute(
                    text("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
                )
                users = users_result.fetchall()

                print("\n[USERS]")
                for user in users:
                    print(f"  - ID: {user[0]}")
                    print(f"    Name: {user[1]}")
                    print(f"    Email: {user[2]}")
                    print(f"    Created: {user[3]}")
                    print()
            else:
                print("\n[WARNING] No users found in database. Please sign up to create an account.")

    except Exception as e:
        print(f"[ERROR] Error checking users: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_users())
