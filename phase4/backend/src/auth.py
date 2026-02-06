"""JWT authentication dependency for Phase 3."""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_session

settings = get_settings()

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> uuid.UUID:
    """Extract and validate JWT token, returning user_id.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        UUID of the authenticated user

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id_str: str | None = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        # Convert string to UUID
        user_id = uuid.UUID(user_id_str)

    except JWTError:
        raise credentials_exception
    except ValueError:
        # Invalid UUID format
        raise credentials_exception

    return user_id


async def verify_user_access(
    user_id: Annotated[str, Path(description="User ID from URL path")],
    current_user: Annotated[uuid.UUID, Depends(get_current_user)],
) -> uuid.UUID:
    """Verify that the authenticated user matches the user_id in the path.

    Args:
        user_id: User ID from URL path
        current_user: Authenticated user ID from JWT

    Returns:
        Verified user UUID

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    try:
        path_user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    if path_user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource",
        )

    return current_user


def verify_token_from_header(token: str) -> uuid.UUID:
    """Verify a JWT token directly and return user_id.

    Args:
        token: JWT token string (without Bearer prefix)

    Returns:
        UUID of the authenticated user

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id_str: str | None = payload.get("sub")

        if user_id_str is None:
            raise ValueError("Token missing user ID")

        return uuid.UUID(user_id_str)

    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
    except ValueError as e:
        raise ValueError(f"Invalid user ID format: {e}") from e


# Type aliases for dependency injection
CurrentUser = Annotated[uuid.UUID, Depends(get_current_user)]
VerifiedUser = Annotated[uuid.UUID, Depends(verify_user_access)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
