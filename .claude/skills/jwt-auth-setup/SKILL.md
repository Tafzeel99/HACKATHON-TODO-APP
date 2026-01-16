---
name: jwt-auth-setup
description: |
  Configures Better Auth JWT token verification in FastAPI backend. Sets up shared secret key,
  implements token decoding middleware, extracts user information from JWT payload, and validates
  token signatures. Handles token expiration, refresh logic, and integrates with dependency
  injection for protected routes.
---

# JWT Authentication Setup

Configures Better Auth JWT token verification in FastAPI backend.

## What This Skill Does
- Sets up shared secret key for JWT signing/verification between Better Auth and FastAPI
- Implements token decoding middleware for verifying JWT signatures
- Creates get_current_user() dependency function for protected routes
- Adds token validation utilities with proper error handling
- Implements error handlers for invalid/expired tokens

## What This Skill Does NOT Do
- Create user registration/login forms (handled by Better Auth frontend)
- Manage user database tables (handled by existing user models)
- Handle password hashing (handled by Better Auth)
- Deploy authentication system to production

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing FastAPI structure, user models, current auth patterns to integrate with |
| **Conversation** | BETTER_AUTH_SECRET configuration, token refresh requirements, specific endpoint protection needs |
| **Skill References** | Domain patterns from `references/` (JWT best practices, FastAPI security patterns, Better Auth integration) |
| **User Guidelines** | Project-specific conventions, existing auth requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **Environment**: "Where is BETTER_AUTH_SECRET stored in your environment?"
2. **Token requirements**: "Do you need custom claims in the JWT tokens?"
3. **Endpoint protection**: "Which specific endpoints need authentication?"

---

## Implementation Workflow

1. **Configure Environment Variables**
   - Set BETTER_AUTH_SECRET in both frontend and backend environments
   - Ensure consistent secret key across services

2. **Create JWT Utilities Module**
   - Import PyJWT for token decoding/verification
   - Implement token verification function with proper error handling
   - Create TokenData Pydantic model for payload validation

3. **Implement Authentication Dependency**
   - Create get_current_user() dependency with OAuth2PasswordBearer
   - Add proper exception handling for invalid/expired tokens
   - Integrate with existing user lookup mechanisms

4. **Protect Endpoints**
   - Apply Depends(get_current_user) to protected routes
   - Ensure user ID in URL matches authenticated user

---

## JWT Token Verification Implementation

### Core Components

```python
import jwt
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Token data model for validation
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    exp: Optional[int] = None

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# JWT verification function
def verify_jwt_token(token: str) -> TokenData:
    """
    Verifies JWT token signature and returns decoded payload
    """
    SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret key not configured"
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            audience="your-app-audience"  # if using audience validation
        )

        # Validate token structure with Pydantic
        token_data = TokenData(**payload)

        # Check if token is expired
        if token_data.exp and datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token_data

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to get current user from JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency that extracts user information from JWT token
    """
    token_data = verify_jwt_token(token)

    # Here you would typically look up the user in your database
    # This is where you'd integrate with your existing user models
    user = {
        "id": token_data.user_id,
        "email": token_data.email
    }

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

# Alternative dependency for getting current active user
async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Extends get_current_user with active status check
    """
    if current_user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

### Protected Endpoint Example

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Verify that the user_id in the URL matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's data"
        )

    # Return only tasks belonging to the authenticated user
    # ... implementation logic here
    return {"tasks": [], "user_id": user_id}
```

---

## Security Best Practices

### Token Validation
- Always verify JWT signature using the shared secret
- Check token expiration (exp claim)
- Validate audience if using audience validation
- Never trust unverified tokens

### Error Handling
- Use consistent 401 Unauthorized for invalid tokens
- Include WWW-Authenticate header in 401 responses
- Don't leak sensitive information in error messages

### Secret Management
- Store BETTER_AUTH_SECRET in environment variables
- Never hardcode secret keys in source code
- Use different secrets for development and production

---

## Output Checklist

Before delivering implementation, verify:
- [ ] BETTER_AUTH_SECRET properly configured in environment
- [ ] JWT token verification function handles all error cases
- [ ] get_current_user dependency integrated with existing user models
- [ ] Protected endpoints properly validate user identity
- [ ] Error responses follow HTTP authentication standards
- [ ] No hardcoded secrets in the implementation

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/better-auth-integration.md` | When integrating with Better Auth frontend |
| `references/fastapi-security.md` | When implementing additional security measures |
| `references/jwt-best-practices.md` | When customizing token validation logic |