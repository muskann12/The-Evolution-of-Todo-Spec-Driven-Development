"""JWT authentication middleware.

This module provides JWT token verification for protected endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from config import settings


# Security scheme for Bearer tokens
security = HTTPBearer()


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token and extract user_id.

    This dependency is used to protect endpoints that require authentication.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        str: User ID from token 'sub' claim

    Raises:
        HTTPException: 401 if token invalid, missing, or expired

    Example:
        @router.get("/tasks")
        async def get_tasks(
            current_user: str = Depends(verify_jwt)
        ):
            # current_user contains the user_id
            ...
    """
    token = credentials.credentials

    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id from 'sub' claim
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
