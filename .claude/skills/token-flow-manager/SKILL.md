---
name: token-flow-manager
description: |
  Manage JWT token storage, refresh logic, and automatic injection into API requests. Use when implementing authentication flows.
---

# Token Flow Manager

Manage JWT token storage, refresh logic, and automatic injection into API requests.

## When to Use This Skill
- User needs JWT authentication setup
- User mentions "token expired" or "unauthorized errors"
- User wants automatic token refresh
- User needs secure token storage

## Procedure
1. **Choose storage**: localStorage (web), secure storage (mobile), httpOnly cookies
2. **Implement token service**: Store, retrieve, refresh tokens
3. **Add interceptor**: Inject token into all requests
4. **Handle refresh**: Detect 401, refresh token, retry request
5. **Clear on logout**: Remove tokens and redirect

## Output Format
**Token Service**:
- Store/retrieve access and refresh tokens
- Automatic token injection
- Refresh logic with retry
- Logout cleanup

## Quality Criteria
- Access token in memory or short-lived storage
- Refresh token in httpOnly cookie (preferred) or secure storage
- Never log tokens
- Handle concurrent requests during refresh
- Clear tokens on 401 from refresh endpoint

## Example
**Input**: "Setup JWT token management for my React app"

**Output**:

```typescript
// tokenService.ts
class TokenService {
  private accessToken: string | null = null;
  private refreshPromise: Promise<string> | null = null;

  setAccessToken(token: string) {
    this.accessToken = token;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  async refreshAccessToken(): Promise<string> {
    // Prevent multiple simultaneous refresh calls
    if (this.refreshPromise) return this.refreshPromise;

    this.refreshPromise = fetch('/api/auth/refresh', {
      method: 'POST',
      credentials: 'include' // Send httpOnly refresh cookie
    })
      .then(res => {
        if (!res.ok) throw new Error('Refresh failed');
        return res.json();
      })
      .then(data => {
        this.setAccessToken(data.access_token);
        return data.access_token;
      })
      .finally(() => {
        this.refreshPromise = null;
      });

    return this.refreshPromise;
  }

  clearTokens() {
    this.accessToken = null;
    // Clear refresh cookie by calling logout endpoint
    fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
  }
}

export const tokenService = new TokenService();

// apiClient.ts
export async function apiRequest(url: string, options: RequestInit = {}) {
  let token = tokenService.getAccessToken();

  const makeRequest = async (authToken: string | null) => {
    const headers = new Headers(options.headers);
    if (authToken) {
      headers.set('Authorization', `Bearer ${authToken}`);
    }

    return fetch(url, { ...options, headers });
  };

  let response = await makeRequest(token);

  // If 401, try to refresh token and retry
  if (response.status === 401 && token) {
    try {
      token = await tokenService.refreshAccessToken();
      response = await makeRequest(token);
    } catch {
      tokenService.clearTokens();
      window.location.href = '/login';
      throw new Error('Session expired');
    }
  }

  return response;
}
```

**Backend (FastAPI)**:
```python
from fastapi import Response, Cookie

@app.post("/auth/login")
async def login(credentials: LoginRequest, response: Response):
    user = authenticate(credentials)
    access_token = create_access_token(user.id, expires_minutes=15)
    refresh_token = create_refresh_token(user.id, expires_days=7)

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7*24*60*60
    )

    return {"access_token": access_token}

@app.post("/auth/refresh")
async def refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(401, "No refresh token")

    user_id = verify_refresh_token(refresh_token)
    new_access = create_access_token(user_id, expires_minutes=15)

    return {"access_token": new_access}
```

## Frontend Token Management

### React Hook Implementation
```typescript
// hooks/useAuth.ts
import { useState, useEffect, useContext, createContext } from 'react';
import { tokenService } from '../services/tokenService';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if token exists and is valid
    const token = tokenService.getAccessToken();
    if (token) {
      // Validate token and get user info
      validateTokenAndSetUser(token);
    } else {
      setIsLoading(false);
    }
  }, []);

  const validateTokenAndSetUser = async (token: string) => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
      } else {
        // Token invalid, clear it
        tokenService.clearTokens();
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      tokenService.clearTokens();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });

    if (response.ok) {
      const data = await response.json();
      tokenService.setAccessToken(data.access_token);
      setIsAuthenticated(true);
      // Optionally fetch user data here
    } else {
      throw new Error('Login failed');
    }
  };

  const logout = () => {
    tokenService.clearTokens();
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### Axios Interceptor Implementation
```typescript
// api/axiosInstance.ts
import axios from 'axios';
import { tokenService } from '../services/tokenService';

const axiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

// Request interceptor to add token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = tokenService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newToken = await tokenService.refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        tokenService.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
```

## Advanced Token Handling

### Token Expiration Monitoring
```typescript
// services/tokenExpirationMonitor.ts
class TokenExpirationMonitor {
  private timer: NodeJS.Timeout | null = null;
  private readonly checkInterval = 30000; // 30 seconds

  startMonitoring() {
    if (this.timer) return;

    this.timer = setInterval(() => {
      const token = tokenService.getAccessToken();
      if (token) {
        const decoded = this.decodeToken(token);
        const currentTime = Date.now() / 1000;
        const timeUntilExpiry = decoded.exp - currentTime;

        // If token expires in less than 1 minute, refresh it
        if (timeUntilExpiry < 60) {
          tokenService.refreshAccessToken();
        }
      }
    }, this.checkInterval);
  }

  stopMonitoring() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  private decodeToken(token: string) {
    const parts = token.split('.');
    const payload = JSON.parse(atob(parts[1]));
    return payload;
  }
}

export const tokenExpirationMonitor = new TokenExpirationMonitor();
```

### Secure Token Storage
```typescript
// utils/secureStorage.ts
class SecureStorage {
  private storageKey = 'app_tokens';

  saveTokens(accessToken: string, refreshToken: string) {
    const tokens = {
      access: this.encrypt(accessToken),
      refresh: this.encrypt(refreshToken),
      timestamp: Date.now()
    };

    sessionStorage.setItem(this.storageKey, JSON.stringify(tokens));
  }

  getTokens() {
    const stored = sessionStorage.getItem(this.storageKey);
    if (!stored) return null;

    try {
      const tokens = JSON.parse(stored);
      return {
        access: this.decrypt(tokens.access),
        refresh: this.decrypt(tokens.refresh),
        timestamp: tokens.timestamp
      };
    } catch {
      return null;
    }
  }

  clearTokens() {
    sessionStorage.removeItem(this.storageKey);
  }

  private encrypt(value: string): string {
    // In a real app, use a proper encryption library
    // This is just a placeholder
    return btoa(encodeURIComponent(value));
  }

  private decrypt(value: string): string {
    // In a real app, use a proper decryption library
    // This is just a placeholder
    return decodeURIComponent(atob(value));
  }
}

export const secureStorage = new SecureStorage();
```

## Backend Token Management

### FastAPI Security Dependencies
```python
# auth/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(user_id: str, expires_minutes: int = 15):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str, expires_days: int = 7):
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id
```

## Mobile Token Management

### React Native Secure Storage
```typescript
// services/mobileTokenService.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Keychain from 'react-native-keychain';

class MobileTokenService {
  private static ACCESS_TOKEN_KEY = 'access_token';
  private static REFRESH_TOKEN_KEY = 'refresh_token';

  async saveTokens(accessToken: string, refreshToken: string) {
    // Store access token in async storage (short lived)
    await AsyncStorage.setItem(MobileTokenService.ACCESS_TOKEN_KEY, accessToken);

    // Store refresh token in secure keychain
    await Keychain.setGenericPassword('refresh_token', refreshToken, {
      service: 'refresh_token',
      accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED
    });
  }

  async getAccessToken(): Promise<string | null> {
    return await AsyncStorage.getItem(MobileTokenService.ACCESS_TOKEN_KEY);
  }

  async getRefreshToken(): Promise<string | null> {
    const credentials = await Keychain.getGenericPassword({
      service: 'refresh_token'
    });
    return credentials ? credentials.password : null;
  }

  async clearTokens() {
    await AsyncStorage.removeItem(MobileTokenService.ACCESS_TOKEN_KEY);
    await Keychain.resetGenericPassword({
      service: 'refresh_token'
    });
  }
}

export const mobileTokenService = new MobileTokenService();
```

## Best Practices
1. **Secure storage**: Use httpOnly cookies for refresh tokens
2. **Token rotation**: Refresh tokens regularly
3. **Concurrent requests**: Handle multiple requests during refresh
4. **Error handling**: Graceful handling of authentication failures
5. **Monitoring**: Track token usage and refresh patterns
6. **Cleanup**: Clear tokens on logout and session expiry

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing authentication system, frontend framework, backend architecture |
| **Conversation** | User's specific token storage needs, security requirements, platform constraints |
| **Skill References** | JWT best practices, secure storage patterns, framework-specific implementations |
| **User Guidelines** | Project-specific security policies, token expiration requirements |