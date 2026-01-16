# JWT Validation Guide

This guide covers JWT token validation patterns and best practices in FastAPI applications.

## JWT Token Structure

### Standard Claims
```python
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

# Standard JWT claims
STANDARD_CLAIMS = [
    'iss',  # Issuer
    'sub',  # Subject (user ID)
    'aud',  # Audience
    'exp',  # Expiration time
    'nbf',  # Not before
    'iat',  # Issued at
    'jti',  # JWT ID
]

def create_token(user_id: str, expires_delta: timedelta = None) -> str:
    """
    Create a JWT token with standard claims
    """
    SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
    ALGORITHM = "HS256"

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode = {
        "sub": user_id,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "scope": ["basic"]
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload
    """
    SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
    ALGORITHM = "HS256"

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise JWTError("Token subject is missing")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

## Token Validation Patterns

### Basic Token Validation
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Basic JWT token validation
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Optionally verify user exists in database
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user
```

### Advanced Token Validation with Multiple Checks
```python
from datetime import datetime

async def get_current_user_advanced(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Advanced JWT token validation with multiple security checks
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"],
            options={
                "verify_exp": True,  # Verify expiration
                "verify_iat": True,  # Verify issued at time
                "verify_nbf": True,  # Verify not before time
            }
        )

        # Check required claims
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Check token expiration manually as well
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.fromtimestamp(exp_timestamp) < datetime.utcnow():
            raise credentials_exception

        # Check audience if present
        audience = payload.get("aud")
        if audience and audience != "your-app-audience":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Verify user exists and is active
    user = await get_user_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user
```

## Token Refresh Patterns

### Token Refresh Endpoint
```python
from fastapi import Form

@app.post("/token/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        refresh_payload = jwt.decode(
            refresh_token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )

        user_id = refresh_payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        # Generate new access token
        new_access_token = create_token(user_id, expires_delta=timedelta(minutes=15))
        new_refresh_token = create_token(
            user_id,
            expires_delta=timedelta(days=7),
            additional_claims={"type": "refresh"}
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )
```

## Security Best Practices

### Secret Key Management
```python
import secrets
import os

def validate_secret_key():
    """
    Validate that the secret key meets security requirements
    """
    secret = os.getenv("BETTER_AUTH_SECRET")

    if not secret:
        raise ValueError("BETTER_AUTH_SECRET environment variable not set")

    # Check minimum length (recommended: at least 32 bytes for HS256)
    if len(secret) < 32:
        raise ValueError("Secret key should be at least 32 characters long")

    # Additional validation could include:
    # - Checking for sufficient entropy
    # - Ensuring it's not a predictable pattern

    return secret

def generate_secure_secret():
    """
    Generate a cryptographically secure secret key
    """
    return secrets.token_urlsafe(32)
```

### Token Blacklisting
```python
from typing import Set
import redis

# Redis connection for token blacklisting
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def blacklist_token(token: str, expires_in: int = 3600):
    """
    Add token to blacklist to handle logout
    """
    try:
        # Decode token to get expiration time
        payload = jwt.decode(token, os.getenv("BETTER_AUTH_SECRET"), algorithms=["HS256"], options={"verify_signature": False})
        exp = payload.get("exp", int(time.time()) + expires_in)

        # Calculate remaining time until expiration
        remaining_time = max(0, exp - int(time.time()))

        # Add to blacklist with TTL matching token expiration
        redis_client.setex(f"blacklisted_{token}", remaining_time, "1")
    except Exception:
        # If we can't decode, still blacklist for a reasonable time
        redis_client.setex(f"blacklisted_{token}", expires_in, "1")

def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted
    """
    return redis_client.exists(f"blacklisted_{token}") == 1

async def get_current_user_with_blacklist(token: str = Depends(oauth2_scheme)) -> dict:
    """
    JWT validation with blacklist check
    """
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await get_current_user(token)
```

## Error Handling

### Comprehensive JWT Error Handling
```python
from jose.constants import ALGORITHMS

def handle_jwt_error(error: JWTError, token: str = None):
    """
    Handle different types of JWT errors with appropriate responses
    """
    if isinstance(error, jwt.ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif isinstance(error, jwt.JWTClaimsError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token claims are invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif isinstance(error, jwt.JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_safe(token: str = Depends(oauth2_scheme)) -> dict:
    """
    JWT validation with comprehensive error handling
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Additional validation checks can be added here
        token_scopes = payload.get("scopes", [])

        user = await get_user_by_id(user_id)
        if user is None:
            raise credentials_exception

        return {
            "user_id": user_id,
            "username": user.username,
            "scopes": token_scopes
        }
    except JWTError as e:
        handle_jwt_error(e, token)
    except Exception:
        raise credentials_exception
```

## Testing JWT Validation

### Unit Tests for JWT Validation
```python
import pytest
from datetime import datetime, timedelta

def test_valid_token():
    """Test that a valid token is accepted"""
    user_id = "test-user"
    token = create_token(user_id)

    # Mock the get_user_by_id function to return a user
    with patch('your_module.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = MagicMock(is_active=True)
        result = get_current_user_safe(token)
        assert result["user_id"] == user_id

def test_expired_token():
    """Test that an expired token raises HTTPException"""
    # Create an expired token
    expired_payload = {
        "sub": "test-user",
        "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp()
    }
    expired_token = jwt.encode(
        expired_payload,
        os.getenv("BETTER_AUTH_SECRET"),
        algorithm="HS256"
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_safe(expired_token)

    assert exc_info.value.status_code == 401

def test_invalid_signature():
    """Test that a token with invalid signature raises HTTPException"""
    # Create a token with a different secret
    invalid_payload = {"sub": "test-user"}
    invalid_token = jwt.encode(invalid_payload, "different-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_safe(invalid_token)

    assert exc_info.value.status_code == 401
```

These patterns ensure secure, reliable JWT validation in your FastAPI applications.