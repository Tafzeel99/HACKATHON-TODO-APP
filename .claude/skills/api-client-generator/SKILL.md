---
name: "api-client-generator"
description: "Generate type-safe API client wrappers with error handling, retries, and interceptors. Use when user needs to make backend API calls."
version: "1.0.0"
---

# API Client Generator Skill

## When to Use This Skill
- User asks to "call an API" or "fetch data from backend"
- User mentions "REST API", "GraphQL", or "HTTP requests"
- User needs error handling, retries, or authentication
- User wants type-safe API calls

## Procedure
1. **Define base client**: Create fetch wrapper with defaults
2. **Add interceptors**: Request/response transformation
3. **Handle errors**: Standardized error responses
4. **Add retry logic**: Exponential backoff for failed requests
5. **Type definitions**: TypeScript interfaces for requests/responses
6. **Auth handling**: Token management and refresh

## Output Format
```typescript
// lib/api-client.ts
export class ApiClient {
  private baseURL: string;
  private headers: Record<string, string>;

  async get<T>(endpoint: string): Promise<T> { }
  async post<T>(endpoint: string, data: any): Promise<T> { }
  async put<T>(endpoint: string, data: any): Promise<T> { }
  async delete<T>(endpoint: string): Promise<T> { }
}
```

## Quality Criteria
- **Type Safety**: Full TypeScript support for requests and responses
- **Error Handling**: Consistent error format with useful messages
- **Retries**: Automatic retry with exponential backoff
- **Interceptors**: Request/response transformation hooks
- **Authentication**: Token management and refresh logic

## Base API Client
```typescript
// lib/api-client.ts

export interface ApiError {
  message: string;
  status: number;
  data?: any;
}

export interface RequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, string>;
  retry?: boolean;
  retryCount?: number;
  retryDelay?: number;
}

export class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;
  private requestInterceptors: Array<(config: RequestInit) => RequestInit> = [];
  private responseInterceptors: Array<(response: Response) => Response | Promise<Response>> = [];

  constructor(baseURL: string, defaultHeaders: Record<string, string> = {}) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...defaultHeaders
    };
  }

  // Add request interceptor
  addRequestInterceptor(interceptor: (config: RequestInit) => RequestInit) {
    this.requestInterceptors.push(interceptor);
  }

  // Add response interceptor
  addResponseInterceptor(interceptor: (response: Response) => Response | Promise<Response>) {
    this.responseInterceptors.push(interceptor);
  }

  // Build URL with query params
  private buildURL(endpoint: string, params?: Record<string, string>): string {
    const url = new URL(endpoint, this.baseURL);
    if (params) {
      Object.keys(params).forEach(key => {
        url.searchParams.append(key, params[key]);
      });
    }
    return url.toString();
  }

  // Apply request interceptors
  private applyRequestInterceptors(config: RequestInit): RequestInit {
    return this.requestInterceptors.reduce((conf, interceptor) => {
      return interceptor(conf);
    }, config);
  }

  // Apply response interceptors
  private async applyResponseInterceptors(response: Response): Promise<Response> {
    let result = response;
    for (const interceptor of this.responseInterceptors) {
      result = await interceptor(result);
    }
    return result;
  }

  // Retry logic with exponential backoff
  private async retry<T>(
    fn: () => Promise<T>,
    retryCount: number = 3,
    delay: number = 1000
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (retryCount <= 0) throw error;

      await new Promise(resolve => setTimeout(resolve, delay));
      return this.retry(fn, retryCount - 1, delay * 2);
    }
  }

  // Main request method
  private async request<T>(
    endpoint: string,
    config: RequestInit = {},
    requestConfig: RequestConfig = {}
  ): Promise<T> {
    const url = this.buildURL(endpoint, requestConfig.params);

    let requestInit: RequestInit = {
      ...config,
      headers: {
        ...this.defaultHeaders,
        ...requestConfig.headers,
        ...config.headers
      }
    };

    // Apply request interceptors
    requestInit = this.applyRequestInterceptors(requestInit);

    const makeRequest = async (): Promise<T> => {
      const response = await fetch(url, requestInit);

      // Apply response interceptors
      const interceptedResponse = await this.applyResponseInterceptors(response);

      if (!interceptedResponse.ok) {
        const errorData = await interceptedResponse.json().catch(() => ({}));
        throw {
          message: errorData.message || 'Request failed',
          status: interceptedResponse.status,
          data: errorData
        } as ApiError;
      }

      // Handle empty responses
      const contentType = interceptedResponse.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        return {} as T;
      }

      return interceptedResponse.json();
    };

    // Use retry if enabled
    if (requestConfig.retry) {
      return this.retry(
        makeRequest,
        requestConfig.retryCount || 3,
        requestConfig.retryDelay || 1000
      );
    }

    return makeRequest();
  }

  // HTTP Methods
  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, config);
  }

  async post<T>(endpoint: string, data: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      config
    );
  }

  async put<T>(endpoint: string, data: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PUT',
        body: JSON.stringify(data)
      },
      config
    );
  }

  async patch<T>(endpoint: string, data: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PATCH',
        body: JSON.stringify(data)
      },
      config
    );
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, config);
  }
}
```

## Authentication Helper
```typescript
// lib/auth-client.ts
import { ApiClient } from './api-client';

export class AuthenticatedApiClient extends ApiClient {
  private tokenKey: string = 'auth_token';
  private refreshTokenKey: string = 'refresh_token';

  constructor(baseURL: string) {
    super(baseURL);

    // Add auth token to all requests
    this.addRequestInterceptor((config) => {
      const token = this.getToken();
      if (token) {
        return {
          ...config,
          headers: {
            ...config.headers,
            Authorization: `Bearer ${token}`
          }
        };
      }
      return config;
    });

    // Handle 401 responses (token expired)
    this.addResponseInterceptor(async (response) => {
      if (response.status === 401) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry the original request
          const token = this.getToken();
          const retryResponse = await fetch(response.url, {
            ...response,
            headers: {
              ...Object.fromEntries(response.headers),
              Authorization: `Bearer ${token}`
            }
          });
          return retryResponse;
        }
      }
      return response;
    });
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.refreshTokenKey);
  }

  setRefreshToken(token: string): void {
    localStorage.setItem(this.refreshTokenKey, token);
  }

  clearTokens(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
  }

  async refreshToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await this.post<{ token: string; refreshToken: string }>(
        '/auth/refresh',
        { refreshToken }
      );

      this.setToken(response.token);
      this.setRefreshToken(response.refreshToken);
      return true;
    } catch {
      this.clearTokens();
      return false;
    }
  }

  async login(email: string, password: string): Promise<{ user: any; token: string }> {
    const response = await this.post<{ user: any; token: string; refreshToken: string }>(
      '/auth/login',
      { email, password }
    );

    this.setToken(response.token);
    this.setRefreshToken(response.refreshToken);
    return response;
  }

  async logout(): Promise<void> {
    try {
      await this.post('/auth/logout', {});
    } finally {
      this.clearTokens();
    }
  }
}
```

## React Hook for API Calls
```typescript
// hooks/use-api.ts
import { useState, useEffect } from 'react';
import { ApiClient, ApiError } from '@/lib/api-client';

interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(options.immediate || false);

  const execute = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      setData(result);
      options.onSuccess?.(result);
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError);
      options.onError?.(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (options.immediate) {
      execute();
    }
  }, []);

  return {
    data,
    error,
    loading,
    execute,
    refetch: execute
  };
}
```

## API Service Example
```typescript
// services/user-service.ts
import { AuthenticatedApiClient } from '@/lib/auth-client';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface CreateUserDto {
  name: string;
  email: string;
  password: string;
}

interface UpdateUserDto {
  name?: string;
  email?: string;
}

class UserService {
  private client: AuthenticatedApiClient;

  constructor() {
    this.client = new AuthenticatedApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api');
  }

  async getUsers(page: number = 1, limit: number = 10): Promise<{ users: User[]; total: number }> {
    return this.client.get<{ users: User[]; total: number }>('/users', {
      params: { page: String(page), limit: String(limit) }
    });
  }

  async getUserById(id: string): Promise<User> {
    return this.client.get<User>(`/users/${id}`);
  }

  async createUser(data: CreateUserDto): Promise<User> {
    return this.client.post<User>('/users', data);
  }

  async updateUser(id: string, data: UpdateUserDto): Promise<User> {
    return this.client.patch<User>(`/users/${id}`, data);
  }

  async deleteUser(id: string): Promise<void> {
    return this.client.delete<void>(`/users/${id}`);
  }

  async searchUsers(query: string): Promise<User[]> {
    return this.client.get<User[]>('/users/search', {
      params: { q: query },
      retry: true,
      retryCount: 2
    });
  }
}

export const userService = new UserService();
```

## Usage Examples

### Basic API Call
```typescript
import { userService } from '@/services/user-service';
import { useApi } from '@/hooks/use-api';

function UserList() {
  const { data, loading, error, refetch } = useApi(
    () => userService.getUsers(1, 10),
    { immediate: true }
  );

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;

  return (
    <div>
      <button onClick={refetch}>Refresh</button>
      <ul>
        {data.users.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Manual API Call
```typescript
import { useState } from 'react';
import { userService } from '@/services/user-service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

function CreateUserForm() {
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await userService.createUser(formData);
      alert('User created successfully!');
      setFormData({ name: '', email: '', password: '' });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />
      <Input
        label="Email"
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
      />
      <Input
        label="Password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
      />
      {error && <p className="text-red-600">{error}</p>}
      <Button type="submit" isLoading={loading}>
        Create User
      </Button>
    </form>
  );
}
```

### With Authentication
```typescript
import { AuthenticatedApiClient } from '@/lib/auth-client';
import { Button } from '@/components/ui/button';

const apiClient = new AuthenticatedApiClient('http://localhost:3000/api');

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { user, token } = await apiClient.login(email, password);
      console.log('Logged in:', user);
      // Redirect to dashboard
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <Button type="submit" isLoading={loading}>
        Log In
      </Button>
    </form>
  );
}
```

## Best Practices
1. **Type Safety**: Define interfaces for all request/response types
2. **Error Handling**: Use consistent error format across the app
3. **Loading States**: Always show loading indicators
4. **Retry Logic**: Implement smart retry for transient failures
5. **Authentication**: Centralize token management
6. **Caching**: Implement response caching when appropriate
7. **Cancellation**: Support request cancellation for long-running requests

## Testing Guidelines
- Mock API responses for unit tests
- Test error scenarios and retry logic
- Verify authentication token handling
- Test concurrent requests and race conditions
- Validate type safety across all API calls

## Output Checklist
- [ ] Base API client with all HTTP methods
- [ ] Type definitions for requests and responses
- [ ] Error handling with consistent format
- [ ] Retry logic with exponential backoff
- [ ] Request/response interceptors
- [ ] Authentication helper with token management
- [ ] React hook for easy integration
- [ ] Example service implementation
- [ ] Usage examples for common scenarios
- [ ] TypeScript interfaces for all types