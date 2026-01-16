---
name: api-bridge-builder
description: |
  Generate type-safe TypeScript API client from backend OpenAPI/Swagger specification. Use when connecting frontend to backend APIs with full type safety.
---

# API Bridge Builder

Generate type-safe TypeScript API client from backend OpenAPI/Swagger specification.

## When to Use This Skill
- User needs to connect frontend to backend API
- User mentions "API client" or "type-safe fetch"
- User has OpenAPI/Swagger spec and needs TypeScript client
- User wants to eliminate API type mismatches

## Procedure
1. **Locate OpenAPI spec**: Find backend openapi.json or swagger.json
2. **Parse endpoints**: Extract paths, methods, request/response schemas
3. **Generate TypeScript types**: Convert JSON schemas to TS interfaces
4. **Create client functions**: Build typed fetch wrappers for each endpoint
5. **Add error handling**: Include response validation and error types

## Output Format
**Generated Client Structure**:
- Type definitions (interfaces/types)
- API client object with methods
- Error handling utilities
- Configuration options (base URL, headers)

## Quality Criteria
- Full type safety: No `any` types
- Request and response types match backend exactly
- Proper HTTP method handling (GET, POST, PUT, DELETE)
- Error responses typed and handled
- JSDoc comments from API descriptions

## Example
**Input**: "Generate API client from my FastAPI backend spec"

**Output**:
```typescript
// types.ts
export interface User {
  id: string;
  email: string;
  name: string;
}

export interface CreateUserRequest {
  email: string;
  name: string;
  password: string;
}

// client.ts
export const api = {
  users: {
    get: async (id: string): Promise<User> => {
      const res = await fetch(`/api/users/${id}`);
      if (!res.ok) throw new ApiError(res.status, await res.text());
      return res.json();
    },

    create: async (data: CreateUserRequest): Promise<User> => {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) throw new ApiError(res.status, await res.text());
      return res.json();
    }
  }
};
```

## API Client Generator

### OpenAPI Spec Parser
```typescript
// utils/openapi-parser.ts
export interface OpenApiSpec {
  paths: Record<string, PathItem>;
  components?: {
    schemas?: Record<string, SchemaObject>;
  };
}

export interface PathItem {
  get?: Operation;
  post?: Operation;
  put?: Operation;
  delete?: Operation;
}

export interface Operation {
  summary?: string;
  description?: string;
  parameters?: Parameter[];
  requestBody?: RequestBody;
  responses: Record<string, Response>;
}

export interface SchemaObject {
  type: string;
  properties?: Record<string, SchemaObject>;
  required?: string[];
  items?: SchemaObject;
  enum?: string[];
}

export const parseOpenApiSpec = (spec: OpenApiSpec): ParsedEndpoints => {
  const endpoints: ParsedEndpoint[] = [];

  Object.entries(spec.paths).forEach(([path, pathItem]) => {
    Object.entries(pathItem).forEach(([method, operation]) => {
      if (['get', 'post', 'put', 'delete'].includes(method)) {
        endpoints.push({
          path,
          method: method.toUpperCase() as HttpMethod,
          operation
        });
      }
    });
  });

  return { endpoints, schemas: spec.components?.schemas || {} };
};
```

### TypeScript Type Generator
```typescript
// generators/type-generator.ts
export const generateTypes = (schemas: Record<string, SchemaObject>): string => {
  let types = '';

  Object.entries(schemas).forEach(([name, schema]) => {
    types += generateInterface(name, schema) + '\n\n';
  });

  return types;
};

const generateInterface = (name: string, schema: SchemaObject): string => {
  if (schema.type === 'object') {
    let interfaceDef = `export interface ${name} {\n`;

    Object.entries(schema.properties || {}).forEach(([propName, propSchema]) => {
      const optional = !(schema.required || []).includes(propName);
      const tsType = convertToTsType(propSchema);
      interfaceDef += `  ${propName}${optional ? '?' : ''}: ${tsType};\n`;
    });

    interfaceDef += '}';
    return interfaceDef;
  }

  return `export type ${name} = ${convertToTsType(schema)};`;
};

const convertToTsType = (schema: SchemaObject): string => {
  switch (schema.type) {
    case 'string':
      if (schema.enum) return schema.enum.map(e => `"${e}"`).join(' | ');
      return 'string';
    case 'number':
    case 'integer':
      return 'number';
    case 'boolean':
      return 'boolean';
    case 'array':
      return `${convertToTsType(schema.items!)}[]`;
    case 'object':
      if (schema.additionalProperties) {
        return `{ [key: string]: ${convertToTsType(schema.additionalProperties as SchemaObject)} }`;
      }
      return 'Record<string, any>';
    default:
      return 'any';
  }
};
```

### API Client Generator
```typescript
// generators/client-generator.ts
export const generateApiClient = (endpoints: ParsedEndpoint[]): string => {
  let client = 'export const api = {\n';

  // Group by path segments
  const grouped = groupEndpoints(endpoints);

  Object.entries(grouped).forEach(([groupName, groupEndpoints]) => {
    client += `  ${groupName}: {\n`;

    groupEndpoints.forEach(endpoint => {
      client += generateEndpointFunction(endpoint);
    });

    client += `  },\n`;
  });

  client += '};\n';
  return client;
};

const generateEndpointFunction = (endpoint: ParsedEndpoint): string => {
  const { path, method, operation } = endpoint;
  const functionName = getFunctionName(method, path);
  const responseType = getResponseType(operation.responses);
  const requestType = getRequestBodyType(operation.requestBody);

  let func = `    ${functionName}: async (`;

  // Add path parameters
  const pathParams = getPathParameters(path);
  if (pathParams.length > 0) {
    func += pathParams.map(param => `${param}: string`).join(', ') + ', ';
  }

  // Add request body parameter
  if (requestType && method !== 'GET') {
    func += `data: ${requestType}`;
  }

  func += `): Promise<${responseType}> => {\n`;
  func += `      const url = \`${resolvePathWithParams(path)}\`;\n`;

  if (method === 'GET') {
    func += `      const res = await fetch(url);\n`;
  } else {
    func += `      const res = await fetch(url, {\n`;
    func += `        method: '${method}',\n`;
    func += `        headers: { 'Content-Type': 'application/json' },\n`;
    func += `        body: JSON.stringify(data)\n`;
    func += `      });\n`;
  }

  func += `      if (!res.ok) throw new ApiError(res.status, await res.text());\n`;
  func += `      return res.json();\n`;
  func += `    },\n`;

  return func;
};

const getFunctionName = (method: string, path: string): string => {
  const segments = path.split('/').filter(s => s);
  const lastSegment = segments[segments.length - 1];

  if (lastSegment.startsWith('{')) {
    // Parameterized endpoint, use parent segment
    return `${method.toLowerCase()}${segments[segments.length - 2] || 'resource'}`;
  }

  return `${method.toLowerCase()}${lastSegment}`;
};
```

## Complete Example

### Generated Types
```typescript
// types/api-types.ts
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  is_active: boolean;
}

export interface CreateUserRequest {
  email: string;
  name: string;
  password: string;
}

export interface UpdateUserRequest {
  name?: string;
  email?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
}
```

### Generated Client
```typescript
// api/client.ts
import { User, CreateUserRequest, UpdateUserRequest, PaginatedResponse } from './types/api-types';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

export interface ApiConfig {
  baseUrl: string;
  headers?: Record<string, string>;
}

export class ApiClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: ApiConfig) {
    this.baseUrl = config.baseUrl;
    this.headers = {
      'Content-Type': 'application/json',
      ...config.headers
    };
  }

  async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: { ...this.headers, ...options.headers }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ApiError(response.status, errorText);
    }

    return response.json();
  }

  users = {
    /**
     * Get all users with pagination
     */
    getAll: async (params?: { page?: number; limit?: number }): Promise<PaginatedResponse<User>> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.append('page', params.page.toString());
      if (params?.limit) searchParams.append('limit', params.limit.toString());

      const queryString = searchParams.toString();
      const path = `/users${queryString ? `?${queryString}` : ''}`;

      return this.request<User[]>(path);
    },

    /**
     * Get user by ID
     */
    getById: async (id: string): Promise<User> => {
      return this.request<User>(`/users/${id}`);
    },

    /**
     * Create new user
     */
    create: async (data: CreateUserRequest): Promise<User> => {
      return this.request<User>('/users', {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },

    /**
     * Update user
     */
    update: async (id: string, data: UpdateUserRequest): Promise<User> => {
      return this.request<User>(`/users/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      });
    },

    /**
     * Delete user
     */
    delete: async (id: string): Promise<void> => {
      await this.request(`/users/${id}`, {
        method: 'DELETE'
      });
    }
  };

  auth = {
    /**
     * Login and get token
     */
    login: async (credentials: { email: string; password: string }): Promise<{ token: string }> => {
      return this.request('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials)
      });
    },

    /**
     * Refresh token
     */
    refreshToken: async (refreshToken: string): Promise<{ token: string }> => {
      return this.request('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken })
      });
    }
  };
}

// Default instance
export const api = new ApiClient({
  baseUrl: process.env.API_BASE_URL || 'http://localhost:8000'
});
```

## Usage Examples

### In Components
```typescript
// components/UserList.tsx
import { useState, useEffect } from 'react';
import { api, User } from '../api/client';

export const UserList = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await api.users.getAll({ page: 1, limit: 10 });
        setUsers(response.items);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
};
```

### With Error Handling
```typescript
// services/user-service.ts
import { api, User, CreateUserRequest } from '../api/client';

export const userService = {
  async createUser(userData: CreateUserRequest): Promise<User> {
    try {
      return await api.users.create(userData);
    } catch (error) {
      if (error instanceof api.ApiError) {
        // Handle specific API errors
        if (error.status === 409) {
          throw new Error('User with this email already exists');
        }
        throw new Error(`Failed to create user: ${error.message}`);
      }
      throw error;
    }
  }
};
```

## Best Practices
1. **Type Safety**: All request/response bodies are fully typed
2. **Error Handling**: Proper error types and handling mechanisms
3. **Configuration**: Flexible base URL and header configuration
4. **Documentation**: JSDoc comments from OpenAPI spec
5. **Modularity**: Separate types, client, and error handling
6. **Consistency**: Standardized naming and structure

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing API endpoints, OpenAPI spec location, frontend architecture |
| **Conversation** | User's specific API requirements, authentication needs, custom headers |
| **Skill References** | OpenAPI specification standards, TypeScript best practices |
| **User Guidelines** | Project-specific naming conventions, error handling patterns |