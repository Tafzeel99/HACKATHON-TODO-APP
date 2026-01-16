# FastAPI Middleware Patterns Guide

This guide covers security middleware patterns for FastAPI applications.

## Basic Middleware Structure

### HTTP Middleware Pattern
```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

class BasicAuthMiddleware(BaseHTTPMiddleware):
    """
    Basic authentication middleware example
    """
    async def dispatch(self, request: Request, call_next):
        # Pre-processing: Check authentication before the request
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header required"}
            )

        # Validate the authorization
        if not self.validate_auth(auth_header):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid credentials"}
            )

        # Continue with the request
        response = await call_next(request)

        # Post-processing: Add security headers to the response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        return response

    def validate_auth(self, auth_header: str) -> bool:
        # Implementation of auth validation
        return True  # Simplified for example
```

## Authentication Middleware

### JWT Token Middleware
```python
import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import os

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT authentication middleware
    """
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []
        self.secret_key = os.getenv("BETTER_AUTH_SECRET")

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths (like login)
        if request.url.path in self.excluded_paths:
            response = await call_next(request)
            return response

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authorization header missing or invalid format"}
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        try:
            # Decode and verify JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Store user info in request state for later use
            request.state.current_user = payload

            # Continue with the request
            response = await call_next(request)
            return response

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token has expired"}
            )
        except jwt.JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"detail": "Authentication error"}
            )

# Usage
app.add_middleware(JWTAuthMiddleware, excluded_paths=["/login", "/register", "/health"])
```

### Session Authentication Middleware
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
import redis
import json

class SessionAuthMiddleware(BaseHTTPMiddleware):
    """
    Session-based authentication middleware
    """
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next):
        # Get session ID from cookie
        session_id = request.cookies.get("session_id")
        if not session_id:
            # For API endpoints, session might be in header
            session_id = request.headers.get("X-Session-ID")

        if session_id:
            # Verify session exists in Redis
            session_data = self.redis.get(session_id)
            if session_data:
                try:
                    user_data = json.loads(session_data)
                    request.state.current_user = user_data
                except json.JSONDecodeError:
                    pass  # Invalid session data

        # Continue with request
        response = await call_next(request)
        return response
```

## Security Middleware

### Rate Limiting Middleware
```python
from collections import defaultdict
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse
    """
    def __init__(self, app, max_requests: int = 100, window: int = 3600, per_user: bool = True):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.per_user = per_user
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Determine the key to track requests (IP or user-based)
        if self.per_user and hasattr(request.state, 'current_user'):
            key = request.state.current_user.get('sub', request.client.host)
        else:
            key = request.client.host

        now = time.time()

        # Clean old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window
        ]

        # Check if rate limit is exceeded
        if len(self.requests[key]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": self.window
                }
            )

        # Add current request to tracking
        self.requests[key].append(now)

        # Continue with request
        response = await call_next(request)
        return response
```

### CORS Security Middleware
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request
from urllib.parse import urlparse

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware with security enhancements
    """
    def __init__(self, app, allowed_origins: list = None, allow_credentials: bool = True):
        super().__init__(app)
        self.allowed_origins = allowed_origins or []
        self.allow_credentials = allow_credentials

    async def dispatch(self, request: Request, call_next):
        # Get origin from request
        origin = request.headers.get("origin")

        response = await call_next(request)

        # Set CORS headers based on origin
        if origin and self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
            response.headers["Access-Control-Allow-Headers"] = "*, Authorization, Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        return response

    def is_origin_allowed(self, origin: str) -> bool:
        if not origin:
            return False

        parsed = urlparse(origin)
        return parsed.netloc in self.allowed_origins
```

### Input Sanitization Middleware
```python
import html
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to sanitize input and prevent common attacks
    """
    def __init__(self, app, max_body_size: int = 1024*1024):  # 1MB
        super().__init__(app)
        self.max_body_size = max_body_size
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS scripts
            r'javascript:',               # JS in URLs
            r'on\w+\s*=',                # Event handlers
            r'<iframe[^>]*>.*?</iframe>', # Iframes
        ]

    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )

        # For GET requests, sanitize query parameters
        if request.method in ["GET", "DELETE"]:
            # Sanitize query parameters
            for key, value in request.query_params.items():
                if self.contains_dangerous_content(value):
                    return JSONResponse(
                        status_code=400,
                        content={"detail": f"Potentially dangerous content in parameter: {key}"}
                    )

        # Process the request
        response = await call_next(request)
        return response

    def contains_dangerous_content(self, content: str) -> bool:
        """
        Check if content contains dangerous patterns
        """
        if not content:
            return False

        content_lower = content.lower()
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content_lower):
                return True

        return False
```

## Request Monitoring Middleware

### Request Logging Middleware
```python
import logging
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.requests import Request

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log requests for security monitoring
    """
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()

        # Log request details (excluding sensitive data)
        request_details = {
            "method": request.method,
            "path": request.url.path,
            "client_host": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": start_time.isoformat()
        }

        # Add user info if available
        if hasattr(request.state, 'current_user'):
            request_details["user_id"] = request.state.current_user.get('sub')

        logger.info(f"Request: {request_details}")

        response = await call_next(request)

        process_time = (datetime.utcnow() - start_time).total_seconds()

        response_details = {
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"Response: {response_details}")

        return response
```

### Security Event Detection Middleware
```python
from collections import defaultdict, deque
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

class SecurityEventDetectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect potential security events
    """
    def __init__(self, app, detection_window: int = 300):  # 5 minutes
        super().__init__(app)
        self.detection_window = detection_window
        self.failed_attempts = defaultdict(lambda: deque())
        self.brute_force_threshold = 10  # attempts
        self.suspicious_patterns = [
            r'\.\./',  # Directory traversal
            r'(union|select|drop|create|delete|update).*sql',
            r'<script',  # Potential XSS
        ]

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        # Check for suspicious patterns in path
        if self.contains_suspicious_pattern(request.url.path):
            # Log suspicious activity
            self.log_security_event(client_ip, "Suspicious pattern detected", request.url.path)

        response = await call_next(request)

        # Track failed authentication attempts
        if response.status_code == 401 or response.status_code == 403:
            self.track_failed_attempt(client_ip)

            # Check if threshold exceeded
            if self.get_failed_attempts_count(client_ip) >= self.brute_force_threshold:
                # Block further requests temporarily
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many failed attempts. Please try again later."}
                )

        return response

    def track_failed_attempt(self, client_ip: str):
        """
        Track failed authentication attempts
        """
        now = time.time()
        self.failed_attempts[client_ip].append(now)

        # Remove attempts older than the detection window
        cutoff = now - self.detection_window
        while self.failed_attempts[client_ip] and self.failed_attempts[client_ip][0] < cutoff:
            self.failed_attempts[client_ip].popleft()

    def get_failed_attempts_count(self, client_ip: str) -> int:
        """
        Get the count of failed attempts in the detection window
        """
        now = time.time()
        cutoff = now - self.detection_window
        return len([attempt for attempt in self.failed_attempts[client_ip] if attempt >= cutoff])

    def contains_suspicious_pattern(self, text: str) -> bool:
        """
        Check if text contains suspicious patterns
        """
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.suspicious_patterns:
            if pattern in text_lower:
                return True

        return False

    def log_security_event(self, client_ip: str, event_type: str, details: str):
        """
        Log security events
        """
        print(f"SECURITY EVENT: {event_type} from {client_ip}: {details}")
```

## Combining Multiple Middlewares

### Middleware Chain Example
```python
from fastapi import FastAPI
from starlette.middleware import Middleware

# Create middlewares
def create_security_middlewares(app: FastAPI):
    """
    Configure security middlewares for the application
    """
    # Add middlewares in the order they should execute
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(InputSanitizationMiddleware)
    app.add_middleware(JWTAuthMiddleware, excluded_paths=["/login", "/register", "/health"])
    app.add_middleware(RateLimitMiddleware, max_requests=100, window=3600)
    app.add_middleware(SecurityEventDetectionMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

# Usage
app = FastAPI()
create_security_middlewares(app)
```

## Testing Middlewares

### Unit Tests for Middleware
```python
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.responses import Response

def test_jwt_auth_middleware_success():
    """
    Test JWT authentication middleware with valid token
    """
    app = FastAPI()

    # Add the middleware
    app.add_middleware(JWTAuthMiddleware, excluded_paths=[])

    @app.get("/test")
    async def test_endpoint(request: Request):
        return {"user": getattr(request.state, 'current_user', None)}

    client = TestClient(app)

    # Create a valid token
    import jwt
    import os
    secret = os.getenv("BETTER_AUTH_SECRET", "test-secret")
    valid_token = jwt.encode({"sub": "test-user"}, secret, algorithm="HS256")

    # Test with valid token
    response = client.get("/test", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200

def test_rate_limiting_middleware():
    """
    Test rate limiting middleware
    """
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, max_requests=2, window=1, per_user=False)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "OK"}

    client = TestClient(app)

    # First two requests should succeed
    response1 = client.get("/test")
    response2 = client.get("/test")
    assert response1.status_code == 200
    assert response2.status_code == 200

    # Third request should be rate limited
    response3 = client.get("/test")
    assert response3.status_code == 429

def test_input_sanitization_middleware():
    """
    Test input sanitization middleware
    """
    app = FastAPI()
    app.add_middleware(InputSanitizationMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "OK"}

    client = TestClient(app)

    # Request with dangerous content should be blocked
    response = client.get("/test?param=<script>alert('xss')</script>")
    assert response.status_code == 400
```

## Performance Considerations

### Efficient Middleware Design
```python
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware

class EfficientSecurityMiddleware(BaseHTTPMiddleware):
    """
    Example of performance-optimized middleware
    """
    def __init__(self, app, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cache = {}

    async def dispatch(self, request: Request, call_next):
        # Use caching to avoid repeated computations
        cache_key = self.get_cache_key(request)

        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                # Use cached result
                request.state.security_check = cached_result
                response = await call_next(request)
                return response

        # Perform security check
        result = await self.perform_security_check(request)

        # Cache the result
        self.cache[cache_key] = (result, time.time())
        request.state.security_check = result

        response = await call_next(request)
        return response

    def get_cache_key(self, request: Request) -> str:
        """
        Generate cache key for the request
        """
        return f"{request.client.host}:{request.method}:{request.url.path}"

    async def perform_security_check(self, request: Request) -> dict:
        """
        Perform security checks asynchronously
        """
        # Asynchronous security checks
        await asyncio.sleep(0.01)  # Simulate async check
        return {"passed": True, "user": "test-user"}
```

These middleware patterns provide comprehensive security for your FastAPI applications while maintaining performance and scalability.