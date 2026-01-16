---
name: api-test-collection
description: |
  Generate Postman collections and curl commands for API testing. Use when users need manual API testing tools,
  Postman collections, or curl commands for testing REST endpoints.
---

# API Test Collection

Generate Postman collections and curl commands for API testing.

## When to Use
- User asks for "API tests", "Postman collection", or "curl commands"
- User needs to test REST endpoints manually
- User wants API documentation with examples

## Procedure
1. **List endpoints**: Identify GET, POST, PUT, DELETE operations
2. **Add authentication**: Include headers, tokens, API keys as needed
3. **Provide examples**: Create request/response samples
4. **Create curl commands**: Generate copy-paste ready commands
5. **Generate Postman**: Format JSON collection for import

## Curl Command Templates

### Basic Requests
```bash
# GET request
curl -X GET {{base_url}}/api/users \
  -H "Content-Type: application/json"

# POST request with data
curl -X POST {{base_url}}/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "name": "Test User"
  }'

# PUT request
curl -X PUT {{base_url}}/api/users/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {{auth_token}}" \
  -d '{
    "name": "Updated Name"
  }'

# DELETE request
curl -X DELETE {{base_url}}/api/users/1 \
  -H "Authorization: Bearer {{auth_token}}"
```

### Authentication Examples
```bash
# Bearer Token
curl -X GET {{base_url}}/api/protected \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# API Key
curl -X GET {{base_url}}/api/data \
  -H "X-API-Key: your-api-key-here"

# Login and extract token
TOKEN=$(curl -X POST {{base_url}}/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' \
  | jq -r '.token')
```

## Postman Collection Template
```json
{
  "info": {
    "name": "API Test Collection",
    "description": "Complete API testing suite",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{auth_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "auth_token",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "pm.environment.set('auth_token', response.token);",
                  "pm.test('Status is 200', () => {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "pm.test('Token exists', () => {",
                  "    pm.expect(response.token).to.exist;",
                  "});"
                ]
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"user@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/login",
              "host": ["{{base_url}}"],
              "path": ["api", "login"]
            }
          }
        }
      ]
    },
    {
      "name": "Users",
      "item": [
        {
          "name": "Get All Users",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/api/users?page=1&limit=10",
              "host": ["{{base_url}}"],
              "path": ["api", "users"],
              "query": [
                {
                  "key": "page",
                  "value": "1"
                },
                {
                  "key": "limit",
                  "value": "10"
                }
              ]
            }
          }
        }
      ]
    }
  ]
}
```

## Best Practices
1. **Use proper authentication** - Always include required headers
2. **Handle errors** - Check response codes and error messages
3. **Validate responses** - Verify expected data structure
4. **Environment variables** - Don't hardcode sensitive data
5. **Test edge cases** - Invalid inputs, missing fields, rate limits

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing API endpoints, authentication methods, request/response structures |
| **Conversation** | User's specific API endpoints, authentication requirements, testing needs |
| **Skill References** | Standard API testing patterns, common authentication schemes, Postman best practices |
| **User Guidelines** | Project-specific conventions, security requirements |