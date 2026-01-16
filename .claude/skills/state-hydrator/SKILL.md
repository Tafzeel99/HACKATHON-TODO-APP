---
name: state-hydrator
description: |
  Efficiently hydrate client state from server-side data with React Server Components, SSR, or initial data fetching patterns.
---

# State Hydrator

Efficiently hydrate client state from server-side data with React Server Components, SSR, or initial data fetching patterns.

## When to Use This Skill
- User needs initial data loaded before app renders
- User mentions "loading spinner on first load"
- User wants to eliminate loading states for initial data
- User is implementing SSR or React Server Components

## Procedure
1. **Choose hydration strategy**: SSR, RSC, or client-side prefetch
2. **Fetch data on server**: Get initial data before rendering
3. **Serialize and inject**: Pass data to client in HTML
4. **Hydrate client state**: Initialize stores/context with server data
5. **Handle staleness**: Optionally revalidate after hydration

## Output Format
**Hydration System**:
- Server-side data fetching
- Serialization/deserialization
- Client state initialization
- Hydration wrapper components

## Quality Criteria
- No flash of loading state on initial render
- Proper serialization (dates, undefined values)
- XSS-safe data injection
- Type-safe hydration
- Graceful fallback if hydration fails

## Example
**Input**: "Setup state hydration for my Next.js app with React Query"

**Output**:

**Next.js App Router (React Server Components)**:
```typescript
// app/dashboard/page.tsx
import { HydrationBoundary, QueryClient, dehydrate } from '@tanstack/react-query';
import { DashboardClient } from './DashboardClient';
import { getUser, getPosts } from '@/lib/api';

export default async function DashboardPage() {
  const queryClient = new QueryClient();

  // Prefetch data on server
  await Promise.all([
    queryClient.prefetchQuery({
      queryKey: ['user'],
      queryFn: getUser
    }),
    queryClient.prefetchQuery({
      queryKey: ['posts'],
      queryFn: getPosts
    })
  ]);

  // Dehydrate state to pass to client
  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <DashboardClient />
    </HydrationBoundary>
  );
}
```

```typescript
// app/dashboard/DashboardClient.tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export function DashboardClient() {
  // Data is already hydrated, no loading state!
  const { data: user } = useQuery({ queryKey: ['user'] });
  const { data: posts } = useQuery({ queryKey: ['posts'] });

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <PostList posts={posts} />
    </div>
  );
}
```

**Traditional SSR (Next.js Pages Router)**:
```typescript
// pages/dashboard.tsx
import { GetServerSideProps } from 'next';
import { QueryClient, dehydrate, useQuery } from '@tanstack/react-query';

export const getServerSideProps: GetServerSideProps = async (context) => {
  const queryClient = new QueryClient();

  // Fetch on server
  await queryClient.prefetchQuery({
    queryKey: ['user'],
    queryFn: () => fetchUser(context.req.cookies.token)
  });

  return {
    props: {
      dehydratedState: dehydrate(queryClient)
    }
  };
};

export default function Dashboard() {
  const { data: user } = useQuery({ queryKey: ['user'] });

  return <div>Welcome, {user.name}</div>;
}
```

**Client-Side Hydration (SPA)**:
```typescript
// App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect } from 'react';

interface HydratedData {
  user?: User;
  posts?: Post[];
}

function App() {
  const [queryClient] = useState(() => {
    const client = new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 1000 * 60 * 5 // 5 minutes
        }
      }
    });

    // Hydrate from server-injected data
    const hydrationData = getHydrationData();
    if (hydrationData) {
      if (hydrationData.user) {
        client.setQueryData(['user'], hydrationData.user);
      }
      if (hydrationData.posts) {
        client.setQueryData(['posts'], hydrationData.posts);
      }
    }

    return client;
  });

  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

// Extract data from server-injected script
function getHydrationData(): HydratedData | null {
  if (typeof window === 'undefined') return null;

  const script = document.getElementById('__HYDRATION_DATA__');
  if (!script?.textContent) return null;

  try {
    return JSON.parse(script.textContent);
  } catch {
    console.error('Failed to parse hydration data');
    return null;
  }
}
```

**Server-Side Data Injection** (Express/FastAPI):
```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>My App</title>
</head>
<body>
  <div id="root"></div>

  <!-- Inject hydration data -->
  <script id="__HYDRATION_DATA__" type="application/json">
    {{{hydrationData}}}
  </script>

  <script src="/bundle.js"></script>
</body>
</html>
```

```python
# FastAPI
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    # Fetch initial data
    user = await get_current_user(request)
    posts = await get_posts()

    # Serialize for hydration
    hydration_data = json.dumps({
        "user": user.dict(),
        "posts": [p.dict() for p in posts]
    })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "hydrationData": hydration_data
    })
```

**Zustand Hydration**:
```typescript
// store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  user: User | null;
  posts: Post[];
  setUser: (user: User) => void;
  setPosts: (posts: Post[]) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      posts: [],
      setUser: (user) => set({ user }),
      setPosts: (posts) => set({ posts })
    }),
    {
      name: 'app-storage'
    }
  )
);

// Hydrate store from server data
export function hydrateStore(data: HydratedData) {
  const { setUser, setPosts } = useAppStore.getState();

  if (data.user) setUser(data.user);
  if (data.posts) setPosts(data.posts);
}
```

**Type-Safe Serialization**:
```typescript
// serialization.ts
export function serialize<T>(data: T): string {
  return JSON.stringify(data, (key, value) => {
    // Handle Date objects
    if (value instanceof Date) {
      return { __type: 'Date', value: value.toISOString() };
    }
    // Handle undefined
    if (value === undefined) {
      return { __type: 'undefined' };
    }
    return value;
  });
}

export function deserialize<T>(json: string): T {
  return JSON.parse(json, (key, value) => {
    if (value?.__type === 'Date') {
      return new Date(value.value);
    }
    if (value?.__type === 'undefined') {
      return undefined;
    }
    return value;
  });
}
```

## Performance Tips
- Only hydrate critical above-the-fold data
- Use streaming SSR for large payloads
- Compress hydration data with gzip
- Consider stale-while-revalidate after hydration
- Lazy load non-critical data after initial render

## Advanced Hydration Strategies

### Streaming SSR with React 18
```typescript
// app/streaming-page.tsx
import { Suspense } from 'react';
import { getUser, getPosts } from '@/lib/data-fetching';

async function UserData() {
  const user = await getUser();
  return <div>Hello, {user.name}!</div>;
}

async function PostsData() {
  const posts = await getPosts();
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}

export default function StreamingPage() {
  return (
    <div>
      <Suspense fallback={<div>Loading user...</div>}>
        <UserData />
      </Suspense>

      <Suspense fallback={<div>Loading posts...</div>}>
        <PostsData />
      </Suspense>
    </div>
  );
}
```

### Context Provider Hydration
```typescript
// contexts/AppContext.tsx
import { createContext, useContext, ReactNode } from 'react';

interface AppContextType {
  user: User | null;
  posts: Post[];
  updateUser: (user: User) => void;
  updatePosts: (posts: Post[]) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
  initialData?: {
    user?: User;
    posts?: Post[];
  };
}

export function AppProvider({ children, initialData }: AppProviderProps) {
  const [state, setState] = useState(() => ({
    user: initialData?.user || null,
    posts: initialData?.posts || []
  }));

  const updateUser = (user: User) => {
    setState(prev => ({ ...prev, user }));
  };

  const updatePosts = (posts: Post[]) => {
    setState(prev => ({ ...prev, posts }));
  };

  return (
    <AppContext.Provider value={{
      user: state.user,
      posts: state.posts,
      updateUser,
      updatePosts
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}
```

### Redux Toolkit Hydration
```typescript
// store/rootReducer.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AppState {
  user: User | null;
  posts: Post[];
}

const initialState: AppState = {
  user: null,
  posts: []
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    hydrateUser(state, action: PayloadAction<User>) {
      state.user = action.payload;
    },
    hydratePosts(state, action: PayloadAction<Post[]>) {
      state.posts = action.payload;
    }
  }
});

export const { hydrateUser, hydratePosts } = appSlice.actions;
export default appSlice.reducer;

// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import appReducer from './rootReducer';

export const initializeStore = (preloadedState?: any) => {
  return configureStore({
    reducer: {
      app: appReducer
    },
    preloadedState
  });
};
```

### Custom Hydration Hook
```typescript
// hooks/useHydration.ts
import { useState, useEffect } from 'react';

interface HydrationOptions {
  key?: string;
  ttl?: number; // Time to live in milliseconds
}

export function useHydration<T>(key: string, defaultValue: T, options: HydrationOptions = {}) {
  const [data, setData] = useState<T>(() => {
    // Check for server-side hydrated data
    if (typeof window !== 'undefined') {
      const script = document.getElementById(`__HYDRATION_${key}__`);
      if (script?.textContent) {
        try {
          return JSON.parse(script.textContent);
        } catch (e) {
          console.error(`Failed to parse hydration data for ${key}:`, e);
        }
      }
    }

    // Fallback to localStorage if available and not expired
    if (options.ttl) {
      const stored = localStorage.getItem(key);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed.timestamp && Date.now() - parsed.timestamp < options.ttl) {
            return parsed.data;
          }
        } catch (e) {
          console.error(`Failed to parse stored data for ${key}:`, e);
        }
      }
    }

    return defaultValue;
  });

  useEffect(() => {
    // Store data with timestamp for TTL
    if (options.ttl) {
      localStorage.setItem(key, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    }
  }, [data, key, options.ttl]);

  return [data, setData] as const;
}
```

## Security Considerations

### XSS Prevention
```typescript
// utils/security.ts
export function sanitizeHydrationData(data: any): any {
  // Remove any potential script tags or dangerous properties
  if (typeof data === 'string') {
    // Basic XSS prevention - use a proper sanitizer in production
    return data.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  }

  if (typeof data === 'object' && data !== null) {
    const sanitized: any = Array.isArray(data) ? [] : {};

    for (const [key, value] of Object.entries(data)) {
      // Sanitize keys too (though less common attack vector)
      const sanitizedKey = key.replace(/[<>'"&]/g, '');
      sanitized[sanitizedKey] = sanitizeHydrationData(value);
    }

    return sanitized;
  }

  return data;
}

// Safe serialization with XSS prevention
export function safeSerialize(data: any): string {
  const sanitized = sanitizeHydrationData(data);
  return JSON.stringify(sanitized);
}
```

## Error Handling and Recovery

### Hydration Error Boundary
```typescript
// components/HydrationErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class HydrationErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Hydration error:', error, errorInfo);

    // Log to error tracking service
    if (typeof window !== 'undefined' && window.Sentry) {
      window.Sentry.captureException(error);
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div>
          <h2>Something went wrong during hydration.</h2>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default HydrationErrorBoundary;
```

## Best Practices
1. **Critical data only**: Hydrate only essential above-the-fold content
2. **Security**: Sanitize all hydration data to prevent XSS
3. **Serialization**: Handle special types (Dates, undefined) properly
4. **Performance**: Use streaming for large datasets
5. **Error handling**: Graceful degradation when hydration fails
6. **Type safety**: Maintain type safety across hydration boundaries
7. **Stale handling**: Implement cache invalidation strategies
8. **Debugging**: Include hydration debugging tools in development

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Current state management, SSR setup, data fetching patterns |
| **Conversation** | User's specific hydration needs, performance requirements, security constraints |
| **Skill References** | SSR best practices, React Server Components patterns, hydration strategies |
| **User Guidelines** | Project-specific performance budgets, security policies, framework versions |