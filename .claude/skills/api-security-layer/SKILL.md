---
name: api-security-layer
description: |
  Implements FastAPI dependency injection system for route protection, user authentication verification,
  and authorization checks. Creates reusable security dependencies that validate JWT tokens, extract
  user information, verify ownership, and enforce access control policies. Handles authentication
  failures with proper HTTP status codes.
---

# API Security Layer

Implements FastAPI dependency injection system for route protection, user authentication verification, and authorization checks.

## What This Skill Does
- Creates reusable security dependencies for JWT token validation
- Implements get_current_user() dependency for authentication
- Creates verify_user_access() dependency for authorization
- Handles authentication failures with proper HTTP status codes (401, 403)
- Implements user ownership verification for multi-tenant applications
- Enforces access control policies and role-based permissions
- Provides security middleware for global security concerns

## What This Skill Does NOT Do
- Generate JWT tokens (handled by authentication provider like Better Auth)
- Create user accounts or manage user registration
- Implement password hashing or credential storage
- Handle external authentication providers directly (OAuth, etc.)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing authentication patterns, JWT secret configuration, current security middleware |
| **Conversation** | JWT verification requirements, authorization rules, protected endpoint specifications |
| **Skill References** | Domain patterns from `references/` (JWT validation, dependency injection, middleware patterns) |
| **User Guidelines** | Project-specific security policies, existing auth provider integration |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **JWT Configuration**: "What is your JWT secret key configuration and token structure?"
2. **Authorization Rules**: "What authorization rules and user access policies do you need?"
3. **Security Requirements**: "Do you need role-based access control or custom authorization logic?"

---

## Implementation Workflow

1. **Analyze Security Requirements**
   - Identify JWT token structure and verification needs
   - Determine authorization rules and access policies
   - Identify protected endpoints and access patterns

2. **Design Security Dependencies**
   - Create JWT token validation function
   - Implement get_current_user dependency
   - Create user access verification dependencies

3. **Implement Authorization Logic**
   - Create ownership verification functions
   - Implement role-based access control if needed
   - Add scope validation for advanced authorization

4. **Apply Security Best Practices**
   - Proper error handling with HTTP status codes
   - Security middleware for global concerns
   - Consistent authentication patterns

---

## Security Dependency Patterns

### JWT Token Validation

```python
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
import os

security = HTTPBearer()

def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token and return decoded payload
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
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Extract and verify JWT token from Authorization header.
    Returns authenticated user information.
    """
    token = credentials.credentials
    user_data = verify_jwt_token(token)

    # Verify user exists in database if needed
    # user = get_user_from_db(user_data.get("sub"))
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User not found"
    #     )

    return user_data
```

### User Access Verification

```python
async def verify_user_access(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify user_id in URL matches authenticated user.
    Raises 403 Forbidden if user doesn't have access.
    """
    authenticated_user_id = current_user.get("sub")  # or however user ID is stored in token

    if authenticated_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )

    return current_user

async def verify_user_ownership(
    resource_owner_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verify that the authenticated user owns the resource.
    """
    authenticated_user_id = current_user.get("sub")

    if authenticated_user_id != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this resource"
        )

    return current_user
```

### Role-Based Access Control

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

def require_role(required_role: UserRole):
    """
    Dependency that checks if user has required role.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "user")  # Default to 'user' role

        if user_role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_role.value} role required"
            )

        return current_user

    return role_checker

def require_any_role(*required_roles: UserRole):
    """
    Dependency that checks if user has any of the required roles.
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
```

### Scope-Based Authorization

```python
from fastapi import Security, SecurityScopes
from fastapi.security import HTTPBearer

oauth2_scheme = HTTPBearer(auto_error=False)

async def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)
) -> dict:
    """
    Get current user with scope validation.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided"
        )

    token = credentials.credentials
    user_data = verify_jwt_token(token)

    # Check if user has required scopes
    token_scopes = user_data.get("scopes", [])

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: '{scope}' scope required"
            )

    return user_data
```

---

## Security Middleware

### Authentication Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Global authentication middleware for additional security checks.
    """
    async def dispatch(self, request: Request, call_next):
        # Add additional security headers
        request.state.authenticated_user = None

        # Extract and validate token if present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            try:
                user_data = verify_jwt_token(token)
                request.state.authenticated_user = user_data
            except HTTPException:
                # Token invalid, but don't fail yet - let individual endpoints decide
                pass

        response = await call_next(request)
        return response
```

### Rate Limiting Middleware (Security Enhancement)

```python
from collections import defaultdict
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse.
    """
    def __init__(self, app, max_requests: int = 100, window: int = 3600):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )

        # Add current request
        self.requests[client_ip].append(now)

        response = await call_next(request)
        return response
```

---

## Error Handling

### Consistent Error Responses

```python
def handle_auth_error(status_code: int, detail: str):
    """
    Helper function for consistent authentication error responses.
    """
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

# Standard error codes:
# 401 Unauthorized - Invalid or missing token
# 403 Forbidden - Token valid but insufficient permissions
# 429 Too Many Requests - Rate limit exceeded
```

---

## Usage Examples

### Protected Endpoints

```python
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(verify_user_access),
    # Additional dependencies...
):
    """
    Get tasks for the authenticated user.
    Access is verified by verify_user_access dependency.
    """
    # Implementation here - user access already verified
    pass

@app.post("/api/admin/users")
async def create_user(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Only admin users can create new users.
    """
    # Implementation here - user role already verified
    pass

@app.get("/api/users/me/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's profile.
    """
    # Implementation here - user authenticated
    pass

@app.put("/api/{user_id}/profile")
async def update_profile(
    user_id: str,
    current_user: dict = Depends(verify_user_access)
):
    """
    Update user's own profile.
    """
    # Implementation here - user access verified
    pass
```

### Global Security Dependencies

```python
# Apply security globally to all routes
app = FastAPI(
    dependencies=[Depends(get_current_user)]
)

# Or apply to specific router
from fastapi import APIRouter

secure_router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

@secure_router.get("/protected")
async def protected_endpoint():
    return {"message": "This is protected"}
```

---

## Security Best Practices

### Token Security
- Never log JWT tokens or sensitive user data
- Use HTTPS in production to prevent token interception
- Implement proper token expiration and refresh mechanisms
- Validate token audience and issuer if using them

### Error Handling
- Use consistent HTTP status codes (401, 403, 429)
- Don't leak sensitive information in error messages
- Always include WWW-Authenticate header for 401 errors

### Performance
- Cache JWT verification results when appropriate
- Use efficient data structures for rate limiting
- Consider async validation for high-throughput applications

### Multi-Tenancy
- Always verify user ownership of resources
- Use user_id in URL path for clear separation
- Implement proper isolation between tenants

---

## Output Checklist

Before delivering security implementation, verify:
- [ ] JWT token validation function handles all error cases
- [ ] get_current_user dependency properly extracts user info
- [ ] User access verification dependencies prevent unauthorized access
- [ ] Proper HTTP status codes (401, 403) are used consistently
- [ ] Error messages don't leak sensitive information
- [ ] Security middleware is properly implemented if needed
- [ ] Role-based access control is implemented if required
- [ ] Rate limiting is applied if needed for security
- [ ] All protected endpoints use appropriate security dependencies

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/jwt-validation.md` | When implementing JWT token verification logic |
| `references/dependency-injection.md` | When creating custom security dependencies |
| `references/middleware-patterns.md` | When implementing global security middleware |
| `references/access-control.md` | When implementing role-based or scope-based authorization |