"""API dependencies for authentication and database sessions."""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_session

settings = get_settings()

# HTTP Bearer security scheme - auto_error=False to return 401 instead of 403
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> uuid.UUID:
    """Dependency to extract and validate JWT token, returning user_id.

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


# Type alias for dependency injection
CurrentUser = Annotated[uuid.UUID, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
