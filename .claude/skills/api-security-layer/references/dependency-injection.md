# FastAPI Dependency Injection Guide

This guide covers dependency injection patterns for security in FastAPI applications.

## Basic Security Dependencies

### Simple Authentication Dependency
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Basic dependency to get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

# Usage in endpoint
@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user
```

### Dependency with Parameters
```python
async def verify_user_access(user_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that verifies the authenticated user can access a specific resource
    """
    if current_user.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_user

# Usage in endpoint
@app.get("/api/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    current_user: dict = Depends(verify_user_access)
):
    return {"tasks": [], "user_id": user_id}
```

## Advanced Dependency Patterns

### Sub-Dependencies
```python
async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Sub-dependency that extends basic authentication with additional checks
    """
    if current_user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Usage in endpoint
@app.get("/users/me/profile")
async def get_profile(current_user: dict = Depends(get_current_active_user)):
    return {"profile": current_user}
```

### Dependencies with Multiple Parameters
```python
async def verify_resource_access(
    user_id: str,
    resource_owner_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify user has access to a specific resource
    """
    if current_user.get("sub") != user_id or current_user.get("sub") != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_user
```

## Security Dependencies with Scopes

### OAuth2 Scopes
```python
from fastapi import Security, SecurityScopes
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={
    "me": "Read your profile",
    "tasks": "Manage your tasks",
    "admin": "Administrator access"
})

async def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    token: str = Security(oauth2_scheme)
) -> dict:
    """
    Get current user with scope validation
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Get token scopes
        token_scopes = payload.get("scopes", [])

        # Validate required scopes
        for scope in security_scopes.scopes:
            if scope not in token_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing scope: {scope}"
                )

        return payload
    except JWTError:
        raise credentials_exception

# Usage with scopes
@app.get("/users/me", dependencies=[Security(get_current_user_with_scopes, scopes=["me"])])
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/tasks", dependencies=[Security(get_current_user_with_scopes, scopes=["tasks"])])
async def read_tasks():
    return {"tasks": []}
```

## Role-Based Dependencies

### Role Verification Dependencies
```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

def require_role(required_role: UserRole):
    """
    Create a dependency that requires a specific role
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "user")

        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_role.value} role required"
            )

        return current_user

    return role_checker

# Usage
@app.post("/admin/users")
async def create_user(current_user: dict = Depends(require_role(UserRole.ADMIN))):
    return {"message": "User created"}

def require_any_role(*required_roles: UserRole):
    """
    Create a dependency that requires any of the specified roles
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "user")

        if user_role not in [role.value for role in required_roles]:
            role_names = ", ".join([role.value for role in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: One of [{role_names}] role required"
            )

        return current_user

    return role_checker

# Usage
@app.put("/content")
async def update_content(current_user: dict = Depends(require_any_role(UserRole.ADMIN, UserRole.MODERATOR))):
    return {"message": "Content updated"}
```

## Caching and Performance

### Cached Dependencies
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_user_data(user_id: str) -> dict:
    """
    Cached function to get user data
    """
    # Simulate database call
    return {"id": user_id, "permissions": ["read", "write"]}

async def get_current_user_cached(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Dependency with caching for better performance
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get cached user data
        user_data = get_cached_user_data(user_id)
        return {**payload, **user_data}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### Dependency with Session Management
```python
from contextlib import contextmanager
from sqlalchemy.orm import Session

def get_db_session() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user_with_db(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db_session)
) -> dict:
    """
    Dependency that combines authentication with database access
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## Error Handling in Dependencies

### Dependency with Comprehensive Error Handling
```python
from typing import Optional

async def get_current_user_safe(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Dependency that gracefully handles missing or invalid credentials
    """
    if credentials is None:
        # No credentials provided
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"])
        user_id: str = payload.get("sub")

        if user_id is None:
            return None

        # Verify user exists
        user = get_user_by_id_sync(user_id)
        if not user or not user.is_active:
            return None

        return payload
    except JWTError:
        return None

# Usage in endpoint that allows both authenticated and unauthenticated access
@app.get("/public/content")
async def get_content(current_user: Optional[dict] = Depends(get_current_user_safe)):
    if current_user:
        # Show personalized content
        return {"content": "personalized", "user": current_user.get("sub")}
    else:
        # Show generic content
        return {"content": "generic", "user": None}
```

## Testing Dependencies

### Unit Tests for Dependencies
```python
import pytest
from unittest.mock import patch, MagicMock

def test_get_current_user_success():
    """Test that get_current_user works with valid token"""
    valid_token = create_test_token("user123")

    with patch('your_app.jwt.decode') as mock_decode:
        mock_decode.return_value = {"sub": "user123", "role": "user"}

        with patch('your_app.get_user_by_id_sync') as mock_get_user:
            mock_get_user.return_value = MagicMock(is_active=True)

            result = get_current_user_safe(MagicMock(credentials=valid_token))
            assert result["sub"] == "user123"

def test_get_current_user_invalid_token():
    """Test that get_current_user returns None with invalid token"""
    with patch('your_app.jwt.decode') as mock_decode:
        mock_decode.side_effect = JWTError("Invalid token")

        result = get_current_user_safe(MagicMock(credentials="invalid_token"))
        assert result is None

def test_require_role_success():
    """Test that require_role works with correct role"""
    user_data = {"sub": "user123", "role": "admin"}

    # Mock the inner dependency
    with patch('your_app.get_current_user') as mock_get_current_user:
        mock_get_current_user.return_value = user_data

        # This should not raise an exception
        result = require_role(UserRole.ADMIN)(user_data)
        assert result == user_data

def test_require_role_failure():
    """Test that require_role raises 403 with incorrect role"""
    user_data = {"sub": "user123", "role": "user"}

    with patch('your_app.get_current_user') as mock_get_current_user:
        mock_get_current_user.return_value = user_data

        with pytest.raises(HTTPException) as exc_info:
            require_role(UserRole.ADMIN)(user_data)

        assert exc_info.value.status_code == 403
```

## Best Practices

### 1. Use Security() for OAuth2 Scopes
```python
# ✅ Use Security() when you need OAuth2 scopes
from fastapi import Security

@app.get("/items")
async def read_items(current_user: dict = Security(get_current_user, scopes=["items"])):
    return {"items": []}

# ✅ Use Depends() for regular dependencies
@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user
```

### 2. Dependency Composition
```python
# ✅ Build complex dependencies from simpler ones
async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def verify_user_ownership(
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    if current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user
```

### 3. Error Handling
```python
# ✅ Consistent error handling
def create_error_handler(status_code: int, detail: str):
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

async def get_current_user_consistent(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    try:
        # ... validation logic
        pass
    except JWTError:
        raise create_error_handler(401, "Invalid token")
    except Exception:
        raise create_error_handler(500, "Internal server error")
```

These patterns ensure robust, maintainable, and secure dependency injection in your FastAPI applications.