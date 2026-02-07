"""Generate a test JWT token for authentication testing."""
from jose import jwt
from datetime import datetime, timedelta
from config import settings


def generate_test_token(user_id: str = "test-user-123") -> str:
    """
    Generate a test JWT token for the given user_id.

    Args:
        user_id: User ID to include in token (default: test-user-123)

    Returns:
        str: JWT token
    """
    # Create payload
    payload = {
        "sub": user_id,  # Subject (user_id)
        "exp": datetime.utcnow() + timedelta(days=1),  # Expires in 1 day
        "iat": datetime.utcnow(),  # Issued at
    }

    # Encode token
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm="HS256"
    )

    return token


if __name__ == "__main__":
    user_id = "test-user-123"
    token = generate_test_token(user_id)
    print(f"Test token for user_id: {user_id}")
    print(f"\nToken: {token}")
    print(f"\nTest command:")
    print(f'curl -H "Authorization: Bearer {token}" http://127.0.0.1:8000/api/{user_id}/tasks')
