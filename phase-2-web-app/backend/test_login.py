"""Script to test login credentials."""
import asyncio
from app.database import engine
from app.auth import verify_password
from sqlalchemy import text


async def test_login(email: str, password: str):
    """Test if login credentials are valid."""
    try:
        async with engine.begin() as conn:
            # Get user by email
            result = await conn.execute(
                text("SELECT id, name, email, hashed_password FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()

            if not user:
                print(f"[ERROR] User with email '{email}' not found in database")
                print("\nAvailable users:")
                users_result = await conn.execute(
                    text("SELECT email FROM users ORDER BY created_at DESC")
                )
                for user_email in users_result.fetchall():
                    print(f"  - {user_email[0]}")
                return

            print(f"[OK] User found: {user[1]} ({user[2]})")

            # Verify password
            is_valid = verify_password(password, user[3])

            if is_valid:
                print(f"[SUCCESS] Password is correct!")
                print(f"User ID: {user[0]}")
            else:
                print(f"[ERROR] Password is incorrect")
                print(f"Provided password: {password}")

    except Exception as e:
        print(f"[ERROR] Error testing login: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python test_login.py <email> <password>")
        print("\nExample:")
        print("  python test_login.py test@example.com password123")
        print("\nAvailable test users:")
        print("  - test@example.com")
        print("  - kannethchamp@gmail.com")
        print("  - johndoe@example.com")
        print("  - roofanjluv@hotmail.com")
        print("  - crk.solutions.giaic@gmail.com")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    print(f"Testing login for: {email}")
    print("=" * 50)
    asyncio.run(test_login(email, password))
