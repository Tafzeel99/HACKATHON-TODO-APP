# FastAPI Dependencies Guide

This guide covers dependency injection patterns for FastAPI applications with SQLModel.

## Database Session Dependencies

### Basic Session Dependency
```python
from sqlmodel import Session, create_engine
from fastapi import Depends

engine = create_engine("sqlite:///database.db")

def get_session():
    with Session(engine) as session:
        yield session

# Usage in endpoints
@app.get("/items/")
def read_items(session: Session = Depends(get_session)):
    # Use session here
    pass
```

### Session with Context Manager
```python
from contextlib import contextmanager
from sqlmodel import Session, create_engine
from fastapi import Depends

engine = create_engine("sqlite:///database.db")

@contextmanager
def get_db_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

## Authentication Dependencies

### Current User Dependency
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token and return user
    pass
```

### Current Active User Dependency
```python
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

## Parameter Dependencies

### Query Parameter Validation
```python
from fastapi import Query

def pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=0, le=1000, description="Max number of records to return")
):
    return {"skip": skip, "limit": limit}

@app.get("/items/")
def read_items(params: dict = Depends(pagination_params)):
    skip = params["skip"]
    limit = params["limit"]
    # Use skip and limit
```

### Path Parameter Validation
```python
from fastapi import Path

def validate_id(item_id: int = Path(..., ge=1, description="Item ID")):
    return item_id
```

## Complex Dependencies

### Combined Dependencies
```python
from typing import Tuple

def get_current_user_and_session(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> Tuple[dict, Session]:
    user = get_current_user(token)
    return user, session

@app.get("/items/")
def read_items(dependencies: Tuple[dict, Session] = Depends(get_current_user_and_session)):
    user, session = dependencies
    # Use both user and session
```

### Dependency with Sub-dependencies
```python
def get_current_user_from_token(
    token: str = Depends(oauth2_scheme)
) -> User:
    # Verify token and return user
    pass

def get_user_with_session(
    current_user: User = Depends(get_current_user_from_token),
    session: Session = Depends(get_session)
) -> Tuple[User, Session]:
    return current_user, session
```

## Security Dependencies

### Role-Based Access Control
```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

def require_role(required_role: Role):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

@app.get("/admin-data", dependencies=[Depends(require_role(Role.ADMIN))])
def get_admin_data():
    # Only accessible to admins
    pass
```

### Permission-Based Access
```python
def check_permission(permission: str):
    def permission_checker(current_user: User = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_checker
```

## Dependency Error Handling

### Custom Exception Handlers for Dependencies
```python
def get_valid_session():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

# Global exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )
```

## Testing Dependencies

### Mock Dependencies for Testing
```python
# For testing purposes
def override_get_session():
    # Create an in-memory database session for testing
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

# In test file
app.dependency_overrides[get_session] = override_get_session
```

## Performance Considerations

### Dependency Caching
Dependencies are created once per request, so expensive operations should be minimized.

### Async Dependencies
```python
import asyncio
from typing import AsyncGenerator

async def get_async_session() -> AsyncGenerator[Session, None]:
    async with AsyncSession(engine) as session:
        yield session
```