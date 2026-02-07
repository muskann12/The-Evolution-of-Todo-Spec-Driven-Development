"""Authentication routes for login and signup.

This module provides endpoints for user authentication:
- POST /api/auth/login - Authenticate existing user
- POST /api/auth/signup - Create new user account
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
import uuid

from db import get_db
from models import User
from schemas import LoginRequest, SignupRequest, AuthResponse, UserResponse
from utils.security import hash_password, verify_password, create_access_token


router = APIRouter()


@router.post("/login", response_model=AuthResponse, status_code=200)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate user and return JWT token.

    Args:
        credentials: Login credentials (email and password)
        session: Database session

    Returns:
        AuthResponse: User info and JWT token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_access_token(user.id)

    # Return user and token
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at
        ),
        token=token
    )


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(
    user_data: SignupRequest,
    session: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Create new user account and return JWT token.

    Args:
        user_data: Signup data (name, email, password)
        session: Database session

    Returns:
        AuthResponse: User info and JWT token

    Raises:
        HTTPException: 400 if email already exists
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Generate JWT token
    token = create_access_token(new_user.id)

    # Return user and token
    return AuthResponse(
        user=UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            created_at=new_user.created_at
        ),
        token=token
    )
