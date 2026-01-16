---
name: request-interceptor
description: |
  Global API request/response handling with authentication, logging, retry logic, and error handling.
---

# Request Interceptor

Global API request/response handling with authentication, logging, retry logic, and error handling.

## When to Use This Skill
- User needs centralized API call handling
- User mentions "retry failed requests" or "global auth"
- User wants request/response logging
- User needs to add headers to all API calls

## Procedure
1. **Create interceptor wrapper**: Wrap fetch or axios
2. **Add auth injection**: Automatically include tokens
3. **Implement retry logic**: Retry failed requests with backoff
4. **Add logging**: Track requests in dev mode
5. **Handle errors globally**: Catch and transform errors

## Output Format
**Interceptor System**:
- Request interceptor (outgoing)
- Response interceptor (incoming)
- Retry mechanism with exponential backoff
- Request/response logging
- Error transformation

## Quality Criteria
- Auth tokens injected automatically
- Retry only on network errors or 5xx (not 4xx)
- Exponential backoff for retries (1s, 2s, 4s)
- Max 3 retry attempts
- Request deduplication for simultaneous identical requests
- Proper cleanup on component unmount

## Example
**Input**: "Create global API interceptor with auth, retry, and logging"

**Output**:

```typescript
// apiInterceptor.ts
import { tokenService } from './tokenService';

interface RequestConfig extends RequestInit {
  retry?: number;
  maxRetries?: number;
  retryDelay?: number;
  skipAuth?: boolean;
  skipRetry?: boolean;
}

interface ApiResponse<T = any> {
  data: T;
  status: number;
  headers: Headers;
}

class ApiInterceptor {
  private baseURL: string;
  private requestLog: Map<string, Promise<any>> = new Map();

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  // Request Interceptor
  private async interceptRequest(
    url: string,
    config: RequestConfig = {}
  ): Promise<[string, RequestInit]> {
    const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`;

    // Clone config to avoid mutation
    const interceptedConfig: RequestInit = { ...config };
    const headers = new Headers(config.headers);

    // 1. Inject Authentication
    if (!config.skipAuth) {
      const token = tokenService.getAccessToken();
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    }

    // 2. Add Default Headers
    if (!headers.has('Content-Type') && config.body) {
      headers.set('Content-Type', 'application/json');
    }

    // 3. Add Request ID for tracking
    const requestId = `${Date.now()}-${Math.random()}`;
    headers.set('X-Request-ID', requestId);

    // 4. Log in Development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 ${config.method || 'GET'} ${fullUrl}`, {
        headers: Object.fromEntries(headers.entries()),
        body: config.body
      });
    }

    interceptedConfig.headers = headers;
    return [fullUrl, interceptedConfig];
  }

  // Response Interceptor
  private async interceptResponse<T>(
    response: Response,
    url: string,
    config: RequestConfig
  ): Promise<ApiResponse<T>> {
    // Log Response
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ ${response.status} ${url}`, {
        status: response.status,
        headers: Object.fromEntries(response.headers.entries())
      });
    }

    // Handle 401 - Token Refresh
    if (response.status === 401 && !config.skipAuth) {
      try {
        await tokenService.refreshAccessToken();
        // Retry original request with new token
        return this.request<T>(url, config);
      } catch {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        throw new Error('Authentication failed');
      }
    }

    // Parse Response
    const contentType = response.headers.get('content-type');
    let data: any;

    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Handle Error Responses
    if (!response.ok) {
      throw {
        response: {
          status: response.status,
          data,
          headers: response.headers
        }
      };
    }

    return {
      data,
      status: response.status,
      headers: response.headers
    };
  }

  // Retry Logic with Exponential Backoff
  private async retryRequest<T>(
    url: string,
    config: RequestConfig,
    attempt: number = 0
  ): Promise<ApiResponse<T>> {
    const maxRetries = config.maxRetries ?? 3;
    const retryDelay = config.retryDelay ?? 1000;

    try {
      const [fullUrl, interceptedConfig] = await this.interceptRequest(url, config);
      const response = await fetch(fullUrl, interceptedConfig);
      return await this.interceptResponse<T>(response, url, config);
    } catch (error: any) {
      // Don't retry on 4xx errors (client errors)
      const status = error.response?.status;
      if (status && status >= 400 && status < 500) {
        throw error;
      }

      // Retry on network errors or 5xx
      if (attempt < maxRetries && !config.skipRetry) {
        const delay = retryDelay * Math.pow(2, attempt); // Exponential backoff

        console.warn(
          `⚠️  Request failed, retrying in ${delay}ms (${attempt + 1}/${maxRetries})`,
          url
        );

        await new Promise(resolve => setTimeout(resolve, delay));
        return this.retryRequest<T>(url, config, attempt + 1);
      }

      throw error;
    }
  }

  // Request Deduplication
  private async deduplicatedRequest<T>(
    url: string,
    config: RequestConfig
  ): Promise<ApiResponse<T>> {
    const key = `${config.method || 'GET'}:${url}`;

    // If same request is in flight, return existing promise
    if (this.requestLog.has(key)) {
      return this.requestLog.get(key)!;
    }

    const promise = this.retryRequest<T>(url, config).finally(() => {
      this.requestLog.delete(key);
    });

    this.requestLog.set(key, promise);
    return promise;
  }

  // Main Request Method
  async request<T = any>(
    url: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    return this.deduplicatedRequest<T>(url, config);
  }

  // Convenience Methods
  async get<T = any>(url: string, config?: RequestConfig) {
    return this.request<T>(url, { ...config, method: 'GET' });
  }

  async post<T = any>(url: string, data?: any, config?: RequestConfig) {
    return this.request<T>(url, {
      ...config,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put<T = any>(url: string, data?: any, config?: RequestConfig) {
    return this.request<T>(url, {
      ...config,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete<T = any>(url: string, config?: RequestConfig) {
    return this.request<T>(url, { ...config, method: 'DELETE' });
  }
}

// Export singleton instance
export const api = new ApiInterceptor(
  import.meta.env.VITE_API_URL || 'http://localhost:8000'
);

// Usage Examples
/*
// Simple GET
const { data } = await api.get('/users');

// POST with data
const { data } = await api.post('/users', { name: 'John', email: 'john@example.com' });

// Skip retry for specific request
const { data } = await api.get('/health', { skipRetry: true });

// Custom retry config
const { data } = await api.get('/important-data', {
  maxRetries: 5,
  retryDelay: 2000
});

// Skip auth for public endpoints
const { data } = await api.get('/public/posts', { skipAuth: true });
*/
```

**React Hook Integration**:
```typescript
// useApi.ts
import { useState, useCallback } from 'react';
import { api } from './apiInterceptor';
import { mapError } from './errorMapper';

export function useApi<T>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (
    callback: () => Promise<T>
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const result = await callback();
      return result;
    } catch (err) {
      const userError = mapError(err);
      setError(userError.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { execute, loading, error };
}

// Usage in component
/*
function UserList() {
  const { execute, loading, error } = useApi<User[]>();
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const fetchUsers = async () => {
      const result = await execute(() => api.get('/users'));
      if (result) {
        setUsers(result.data);
      }
    };

    fetchUsers();
  }, [execute]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
*/
```

## Advanced Interceptor Features

### Axios Interceptor Alternative
```typescript
// axiosInterceptor.ts
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { tokenService } from './tokenService';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000
});

// Request Interceptor
apiClient.interceptors.request.use(
  async (config: AxiosRequestConfig) => {
    // Add auth token
    const token = tokenService.getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request ID
    config.headers = {
      ...config.headers,
      'X-Request-ID': `${Date.now()}-${Math.random()}`
    };

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config);
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ ${response.status} ${response.config.url}`, response);
    }
    return response;
  },
  async (error: AxiosError) => {
    // Handle 401 - token refresh
    if (error.response?.status === 401) {
      try {
        await tokenService.refreshAccessToken();
        // Retry original request
        return apiClient.request(error.config!);
      } catch {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### WebSocket Interceptor
```typescript
// websocketInterceptor.ts
class WebSocketInterceptor {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(private url: string) {}

  connect(): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0; // Reset on successful connection
        console.log('✅ WebSocket connected');
        resolve(this.ws);
      };

      this.ws.onclose = (event) => {
        console.log(`❌ WebSocket disconnected: ${event.code} ${event.reason}`);

        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

          console.log(`🔄 Attempting to reconnect in ${delay}ms (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

          setTimeout(() => {
            this.connect().then(resolve).catch(reject);
          }, delay);
        } else {
          reject(new Error('Max reconnection attempts reached'));
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };
    });
  }

  send(data: string | ArrayBuffer | Blob | ArrayBufferView) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    } else {
      throw new Error('WebSocket not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
```

## Middleware Pattern

### Composable Middleware
```typescript
// middleware.ts
interface MiddlewareContext {
  url: string;
  config: RequestConfig;
  response?: Response;
  error?: any;
}

type Middleware = (context: MiddlewareContext, next: () => Promise<void>) => Promise<void>;

class MiddlewarePipeline {
  private middlewares: Middleware[] = [];

  use(middleware: Middleware) {
    this.middlewares.push(middleware);
  }

  async execute(context: MiddlewareContext) {
    let index = -1;

    const dispatch = async (i: number): Promise<void> => {
      if (i <= index) {
        throw new Error('next() called multiple times');
      }
      index = i;

      const fn = this.middlewares[i];
      if (i === this.middlewares.length) {
        return Promise.resolve();
      }

      if (!fn) {
        return Promise.resolve();
      }

      return fn(context, () => dispatch(i + 1));
    };

    await dispatch(0);
  }
}

// Usage
const pipeline = new MiddlewarePipeline();

pipeline.use(async (ctx, next) => {
  console.log(`Processing request to ${ctx.url}`);
  await next();
  console.log(`Response status: ${ctx.response?.status}`);
});

pipeline.use(async (ctx, next) => {
  // Add auth header
  const token = tokenService.getAccessToken();
  if (token) {
    ctx.config.headers = {
      ...ctx.config.headers,
      Authorization: `Bearer ${token}`
    };
  }
  await next();
});
```

## Error Handling Integration

### Error Boundary with Interceptor
```typescript
// components/ApiErrorBoundary.tsx
import React, { Component, ReactNode } from 'react';
import { api } from '../apiInterceptor';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: any;
}

class ApiErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: any): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('API Error Boundary caught error:', error, errorInfo);

    // Log to error tracking service
    if (window.Sentry) {
      window.Sentry.captureException(error);
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div>
          <h2>Something went wrong with the API.</h2>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ApiErrorBoundary;
```

## Performance Monitoring

### Request Timing
```typescript
// timingInterceptor.ts
interface RequestTiming {
  startTime: number;
  endTime?: number;
  duration?: number;
  url: string;
  method: string;
}

class TimingInterceptor {
  private timings: RequestTiming[] = [];
  private maxTimings = 100;

  async interceptRequest(url: string, config: RequestConfig) {
    const timing: RequestTiming = {
      startTime: performance.now(),
      url,
      method: config.method || 'GET'
    };

    // Store timing info
    this.timings.push(timing);

    // Keep only recent timings
    if (this.timings.length > this.maxTimings) {
      this.timings.shift();
    }

    return { ...config, _timing: timing };
  }

  async interceptResponse(response: Response, config: RequestConfig) {
    const timing = (config as any)._timing as RequestTiming;
    if (timing) {
      timing.endTime = performance.now();
      timing.duration = timing.endTime - timing.startTime;

      // Log slow requests (> 1s)
      if (timing.duration > 1000) {
        console.warn(`⚠️ Slow request: ${timing.method} ${timing.url} took ${timing.duration}ms`);
      }
    }

    return response;
  }

  getAverageDuration(): number {
    const durations = this.timings.filter(t => t.duration !== undefined).map(t => t.duration!);
    if (durations.length === 0) return 0;
    return durations.reduce((sum, dur) => sum + dur, 0) / durations.length;
  }
}
```

## Best Practices
1. **Centralized error handling**: Handle common error patterns globally
2. **Automatic retries**: Implement exponential backoff for transient failures
3. **Request deduplication**: Avoid duplicate requests for same resource
4. **Performance monitoring**: Track request timing and success rates
5. **Security**: Sanitize sensitive data in logs
6. **Type safety**: Maintain type safety across interceptors
7. **Modularity**: Keep interceptors composable and testable

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing API patterns, authentication system, error handling approach |
| **Conversation** | User's specific interception needs, preferred HTTP client, security requirements |
| **Skill References** | HTTP interceptor patterns, retry strategies, authentication flows |
| **User Guidelines** | Project-specific naming conventions, logging requirements, error handling policies |