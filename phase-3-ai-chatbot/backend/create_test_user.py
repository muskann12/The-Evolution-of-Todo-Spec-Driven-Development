"""Script to create a test user with known credentials."""
import asyncio
import uuid
from datetime import datetime, UTC
from app.database import engine
from app.auth import hash_password
from sqlalchemy import text


async def create_test_user():
    """Create a test user with known credentials."""
    # Test user credentials
    email = "admin@test.com"
    password = "admin123"
    name = "Admin User"

    try:
        async with engine.begin() as conn:
            # Check if user already exists
            result = await conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            existing = result.fetchone()

            if existing:
                print(f"[INFO] User already exists: {email}")
                print(f"[INFO] You can login with:")
                print(f"       Email: {email}")
                print(f"       Password: {password}")
                return

            # Create new user
            user_id = str(uuid.uuid4())
            hashed_pwd = hash_password(password)
            created_at = datetime.now(UTC).replace(tzinfo=None)

            await conn.execute(
                text("""
                    INSERT INTO users (id, name, email, hashed_password, created_at)
                    VALUES (:id, :name, :email, :hashed_password, :created_at)
                """),
                {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "hashed_password": hashed_pwd,
                    "created_at": created_at
                }
            )

            print(f"[SUCCESS] Test user created!")
            print(f"")
            print(f"===========================================")
            print(f"  LOGIN CREDENTIALS")
            print(f"===========================================")
            print(f"  Email:    {email}")
            print(f"  Password: {password}")
            print(f"===========================================")
            print(f"")
            print(f"User ID: {user_id}")

    except Exception as e:
        print(f"[ERROR] Failed to create test user: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(create_test_user())
