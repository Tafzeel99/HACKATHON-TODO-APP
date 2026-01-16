---
name: cors-configurator
description: |
  Setup secure CORS policies for development and production environments. Use when configuring cross-origin requests between frontend and backend.
---

# CORS Configurator

Setup secure CORS policies for development and production environments.

## When to Use This Skill
- User gets CORS errors in browser console
- User mentions "blocked by CORS policy"
- User needs to configure backend for frontend requests
- User deploying app with separate frontend/backend domains

## Procedure
1. **Identify environment**: Development (localhost) vs production (deployed domains)
2. **Determine origins**: What domains need access to the API
3. **Set allowed methods**: GET, POST, PUT, DELETE, OPTIONS
4. **Configure credentials**: Whether to allow cookies/auth headers
5. **Add preflight handling**: OPTIONS request support

## Output Format
**Backend Configuration Code**:
- Express/FastAPI/Flask CORS middleware
- Allowed origins list (env-based)
- Allowed methods and headers
- Credentials configuration

## Quality Criteria
- Development: Allow localhost with all ports
- Production: Whitelist specific domains only
- Never use `*` with credentials enabled
- Include OPTIONS method for preflight
- Set appropriate max-age for preflight caching

## Example
**Input**: "Fix CORS errors between my React app and FastAPI backend"

**Output**:

**FastAPI (Python)**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
] if os.getenv("ENV") == "development" else [
    "https://myapp.com",
    "https://www.myapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600
)
```

**Express (Node.js)**:
```javascript
const cors = require('cors');

const origins = process.env.NODE_ENV === 'development'
  ? ['http://localhost:3000', 'http://localhost:5173']
  : ['https://myapp.com', 'https://www.myapp.com'];

const corsOptions = {
  origin: origins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
  maxAge: 3600
};

app.use(cors(corsOptions));
```

## Environment-Based Configuration

### Development Configuration
```python
# config/cors.py
import os

def get_cors_config():
    """Get CORS configuration based on environment"""
    if os.getenv("ENVIRONMENT") == "development":
        return {
            "allow_origins": [
                "http://localhost:3000",    # React
                "http://localhost:5173",    # Vite
                "http://localhost:8080",    # Vue
                "http://localhost:4200",    # Angular
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    else:
        return {
            "allow_origins": [
                "https://yourdomain.com",
                "https://www.yourdomain.com",
                "https://app.yourdomain.com",
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        }
```

### Production Configuration
```python
# config/production_cors.py
import os

def get_production_cors_config():
    """Production CORS configuration with strict security"""
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

    return {
        "allow_origins": [origin.strip() for origin in allowed_origins if origin.strip()],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin"
        ],
        "max_age": 86400,  # 24 hours
        "expose_headers": ["Content-Disposition"]  # For file downloads
    }
```

## Framework-Specific Implementations

### FastAPI Implementation
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.cors import get_cors_config

app = FastAPI()

# Apply CORS configuration
cors_config = get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Flask Implementation
```python
# app.py
from flask import Flask
from flask_cors import CORS
from config.cors import get_cors_config

app = Flask(__name__)

cors_config = get_cors_config()
CORS(app, **cors_config)

@app.route('/')
def hello():
    return {'message': 'Hello World'}
```

### Express.js Implementation
```javascript
// server.js
const express = require('express');
const cors = require('cors');
const { getCorsConfig } = require('./config/cors');

const app = express();

const corsConfig = getCorsConfig();
app.use(cors(corsConfig));

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

module.exports = app;
```

## Advanced CORS Configuration

### Dynamic Origin Validation
```python
# utils/cors_validator.py
import re
from typing import Union

def validate_origin(origin: str, allowed_patterns: list) -> bool:
    """Validate origin against allowed patterns"""
    for pattern in allowed_patterns:
        if re.match(pattern, origin):
            return True
    return False

def dynamic_origin_handler():
    """Dynamic origin handler for CORS"""
    allowed_patterns = [
        r'^https://.*\.yourdomain\.com$',  # Subdomains
        r'^http://localhost:\d+$',         # Localhost with any port
        r'^https://yourdomain\.com$'       # Main domain
    ]

    def origin_validator(origin, callback):
        if validate_origin(origin, allowed_patterns):
            callback(None, True)
        else:
            callback(f'Origin {origin} not allowed', False)

    return origin_validator
```

### Environment Variables Setup
```bash
# .env.development
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# .env.production
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com
```

## Security Best Practices

### Secure Configuration
```python
# config/secure_cors.py
def get_secure_cors_config():
    """Security-focused CORS configuration"""
    return {
        "allow_origins": [],  # Will be populated based on environment
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        "max_age": 86400,  # Cache preflight for 24 hours
        "expose_headers": ["Content-Disposition"]  # Only expose necessary headers
    }
```

### Common Security Mistakes to Avoid
```python
# ❌ BAD - Never do this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,  # Dangerous combination!
)

# ❌ BAD - Too permissive
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ GOOD - Specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

## Troubleshooting Common Issues

### Debugging CORS Errors
```python
# middleware/debug_cors.py
from starlette.middleware.base import BaseHTTPMiddleware
import logging

class CORSDbgMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log CORS-related headers
        origin = request.headers.get("origin")
        method = request.headers.get("access-control-request-method")
        headers = request.headers.get("access-control-request-headers")

        logging.info(f"CORS Debug - Origin: {origin}, Method: {method}, Headers: {headers}")

        response = await call_next(request)
        return response
```

### Common Error Solutions
```markdown
## Common CORS Issues & Solutions

### 1. "Credentials flag is 'true', but the 'Access-Control-Allow-Origin' header contains '*'"
**Solution**: Don't use wildcard origin when allow_credentials=True

### 2. Preflight request failed
**Solution**: Ensure OPTIONS method is allowed and proper headers are set

### 3. Request header field X is not allowed
**Solution**: Add the header to allow_headers in CORS configuration

### 4. Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '*'
**Solution**: Use specific origin instead of wildcard when using credentials
```

## Testing CORS Configuration

### Unit Tests
```python
# tests/test_cors.py
import pytest
from fastapi.testclient import TestClient

def test_cors_headers_present(client: TestClient):
    """Test that CORS headers are properly set"""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})

    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

def test_preflight_request(client: TestClient):
    """Test preflight OPTIONS request"""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )

    assert response.status_code == 200
    assert "access-control-allow-methods" in response.headers
```

## Best Practices
1. **Environment-specific**: Different configs for dev/prod
2. **Whitelist origins**: Never use "*" with credentials
3. **Minimize allowed headers**: Only allow necessary headers
4. **Set max-age**: Cache preflight responses for performance
5. **Monitor**: Log CORS violations for security analysis
6. **Regular review**: Periodically audit allowed origins

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Backend framework (FastAPI, Express, Flask), current CORS setup |
| **Conversation** | User's specific domains, authentication requirements, security constraints |
| **Skill References** | CORS security best practices, framework-specific implementations |
| **User Guidelines** | Project-specific environment variables, deployment setup |