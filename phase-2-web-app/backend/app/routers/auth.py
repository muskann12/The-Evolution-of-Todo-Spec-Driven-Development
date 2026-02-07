"""
Authentication router for signup, login, and session management.

Spec Reference: @specs/features/user-authentication.md
API Reference: @specs/api/auth-endpoints.md
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta

from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, Token, MessageResponse
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import settings


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new user account.

    Spec Reference: @specs/features/user-authentication.md - User Story 1

    Args:
        user_data: User signup data (name, email, password)
        session: Database session

    Returns:
        JWT access token

    Raises:
        400: Email already registered
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.id, "email": new_user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """
    Login with email and password.

    Spec Reference: @specs/features/user-authentication.md - User Story 2

    Args:
        credentials: Login credentials (email, password)
        session: Database session

    Returns:
        JWT access token

    Raises:
        401: Invalid credentials
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/session", response_model=UserResponse)
async def get_session(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user session from JWT token.

    Spec Reference: @specs/features/user-authentication.md

    Args:
        current_user: Current authenticated user

    Returns:
        User data (without password)
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout endpoint (client should discard token).

    Since we use stateless JWT tokens, logout is handled client-side
    by deleting the token from storage.

    Returns:
        Success message
    """
    return MessageResponse(
        message="Logged out successfully",
        detail="Please discard your access token",
    )
