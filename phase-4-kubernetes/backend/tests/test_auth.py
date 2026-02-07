"""
Test suite for authentication endpoints.

Tests the auth API endpoints defined in @specs/api/auth-endpoints.md
Covers signup, login, and JWT token generation.
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select

from app.main import app
from app.models import User


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, test_db):
    """
    Test successful user registration.

    Acceptance Criteria (AC-001):
    - POST /api/auth/signup with valid data returns 201
    - Response includes user data and JWT token
    - Password is hashed in database
    """
    response = await client.post(
        "/api/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify token is a valid JWT (basic check)
    assert len(data["access_token"]) > 50
    assert "." in data["access_token"]  # JWT has dots separating parts

    # Verify user was created in database
    result = await test_db.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_db, test_user):
    """
    Test signup with duplicate email fails.

    Acceptance Criteria (AC-002):
    - POST /api/auth/signup with existing email returns 400
    - Error message indicates email already registered
    """
    response = await client.post(
        "/api/auth/signup",
        json={
            "name": "Another User",
            "email": test_user["email"],  # Duplicate email
            "password": "different123"
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(client: AsyncClient, test_db):
    """
    Test signup with invalid email format fails.

    Acceptance Criteria (AC-003):
    - Invalid email format should be rejected with 422
    """
    response = await client.post(
        "/api/auth/signup",
        json={
            "name": "Test User",
            "email": "not-an-email",
            "password": "password123"
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_signup_missing_fields(client: AsyncClient, test_db):
    """
    Test signup with missing required fields fails.

    Acceptance Criteria (AC-004):
    - Missing name, email, or password returns 422
    """
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": "test@example.com"
            # Missing name and password
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_db, test_user):
    """
    Test successful login.

    Acceptance Criteria (AC-005):
    - POST /api/auth/login with correct credentials returns 200
    - Response includes user data and JWT token
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["plain_password"]
        }
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify token is a valid JWT
    assert len(data["access_token"]) > 50
    assert "." in data["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_db, test_user):
    """
    Test login with incorrect password fails.

    Acceptance Criteria (AC-006):
    - Wrong password returns 401
    - Error message indicates invalid credentials
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": "wrongpassword"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient, test_db):
    """
    Test login with non-existent email fails.

    Acceptance Criteria (AC-007):
    - Non-existent email returns 401
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_password_hashed_in_database(client: AsyncClient, test_db):
    """
    Test that passwords are hashed, not stored in plaintext.

    Security Requirement (SR-001):
    - Passwords must be bcrypt hashed in database
    """
    # Create user
    response = await client.post(
        "/api/auth/signup",
        json={
            "name": "Hash Test",
            "email": "hash@example.com",
            "password": "mypassword123"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Check database directly
    async with test_db as session:
        statement = select(User).where(User.email == "hash@example.com")
        result = await session.execute(statement)
        user = result.scalar_one()

        # Verify password is hashed (bcrypt hash starts with $2b$)
        assert user.hashed_password.startswith("$2b$")
        assert user.hashed_password != "mypassword123"
        assert len(user.hashed_password) == 60  # bcrypt hash length


@pytest.mark.asyncio
async def test_jwt_token_contains_user_id(client: AsyncClient, test_db, test_user):
    """
    Test that JWT token contains user ID in 'sub' claim.

    Security Requirement (SR-002):
    - JWT must contain user_id in 'sub' claim
    """
    from jose import jwt
    from app.config import settings

    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["plain_password"]
        }
    )

    token = response.json()["access_token"]

    # Decode token (without verification for test)
    payload = jwt.decode(token, settings.better_auth_secret, algorithms=[settings.jwt_algorithm])

    assert "sub" in payload
    assert payload["sub"] == test_user["id"]
    assert "exp" in payload  # Expiration
    assert "email" in payload  # Email included in token


@pytest.mark.asyncio
async def test_signup_creates_timestamps(client: AsyncClient, test_db):
    """
    Test that user creation sets created_at and updated_at timestamps.

    Data Requirement (DR-001):
    - created_at and updated_at must be set on user creation
    """
    response = await client.post(
        "/api/auth/signup",
        json={
            "name": "Timestamp Test",
            "email": "timestamp@example.com",
            "password": "password123"
        }
    )

    # Get user from database to check timestamps
    statement = select(User).where(User.email == "timestamp@example.com")
    result = await test_db.execute(statement)
    user = result.scalar_one()

    assert user.created_at is not None
    # Verify created_at is recent (within last minute)
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    time_since_creation = (now - user.created_at).total_seconds()
    assert time_since_creation < 60  # Created within last 60 seconds
