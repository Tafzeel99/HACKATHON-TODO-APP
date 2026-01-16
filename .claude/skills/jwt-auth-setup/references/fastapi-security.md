# FastAPI Security Best Practices

Best practices for implementing secure authentication in FastAPI applications.

## Authentication Patterns

### OAuth2 with Password Flow

Use OAuth2PasswordBearer for token-based authentication:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

### Dependency Injection for Auth

Use dependency injection to enforce authentication:

```python
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token and return user
    pass

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user": user}
```

## Security Headers

Always include proper security headers in responses:

- WWW-Authenticate for 401 responses
- Content Security Policy headers
- Strict Transport Security (HSTS)
- X-Content-Type-Options

## Error Handling

### Consistent Error Responses

Use consistent status codes for authentication errors:

- 401 Unauthorized: Invalid or missing token
- 403 Forbidden: Insufficient permissions
- 400 Bad Request: Invalid request format

### Secure Error Messages

Never expose sensitive information in error messages:

```python
# ❌ Don't reveal specific reasons
detail="Invalid password"

# ✅ Generic messages
detail="Invalid credentials"
```

## Token Management

### JWT Best Practices

- Use strong secret keys (at least 256 bits)
- Set reasonable expiration times
- Validate all token claims
- Use HTTPS in production
- Implement proper token refresh mechanisms

### Session Security

- Regenerate tokens after login
- Implement token blacklisting for logout
- Use secure, HttpOnly cookies for tokens when possible
- Set appropriate SameSite attributes

## Input Validation

Always validate user inputs and token claims:

```python
from pydantic import BaseModel, validator

class TokenData(BaseModel):
    user_id: str

    @validator("user_id")
    def validate_user_id(cls, v):
        if not v.isalnum():
            raise ValueError("Invalid user ID format")
        return v
```