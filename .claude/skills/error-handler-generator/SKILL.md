---
name: error-handler-generator
description: |
  Generate comprehensive error handling utilities with user-friendly messages. Use when users need robust error handling and user-friendly error displays.
---

# Error Handler Generator

Generate comprehensive error handling utilities with user-friendly messages.

## When to Use This Skill
- User needs better error handling in their application
- User wants to display user-friendly error messages
- User has raw API errors that need mapping to user messages
- User needs centralized error management

## Procedure
1. **Identify error types**: Authentication, validation, server, network, etc.
2. **Map error codes**: Create mapping from backend codes to user messages
3. **Generate error utilities**: Create error mapping functions
4. **Create user components**: Build error display components
5. **Add logging**: Include error tracking and reporting

## Output Format
**Generated Error Utilities**:
- Error mapping functions
- User-friendly message translations
- Error categorization utilities
- Error display components

## Quality Criteria
- Clear, actionable user messages
- Proper error categorization
- Consistent error handling across the app
- Logging for debugging
- Accessibility for screen readers

## Example
**Input**: "Create error handler for my API responses"

**Output**:

```typescript
// errorMapper.ts
interface ErrorMapping {
  message: string;
  action?: string;
}

const ERROR_MAP: Record<string, ErrorMapping> = {
  // Authentication
  'AUTH_INVALID_CREDENTIALS': {
    message: 'Email or password is incorrect',
    action: 'Double-check your credentials or reset your password'
  },
  'AUTH_TOKEN_EXPIRED': {
    message: 'Your session has expired',
    action: 'Please sign in again'
  },
  'AUTH_EMAIL_NOT_VERIFIED': {
    message: 'Please verify your email address',
    action: 'Check your inbox for the verification link'
  },

  // Validation
  'VALIDATION_EMAIL_INVALID': {
    message: 'Email address format is invalid',
    action: 'Enter a valid email like user@example.com'
  },
  'VALIDATION_PASSWORD_WEAK': {
    message: 'Password is too weak',
    action: 'Use at least 8 characters with numbers and symbols'
  },

  // Resources
  'RESOURCE_NOT_FOUND': {
    message: 'The item you\'re looking for doesn\'t exist',
    action: 'It may have been deleted or you don\'t have permission'
  },
  'RESOURCE_ALREADY_EXISTS': {
    message: 'This already exists',
    action: 'Try a different name or check existing items'
  },

  // Permissions
  'PERMISSION_DENIED': {
    message: 'You don\'t have permission to do this',
    action: 'Contact your administrator for access'
  },

  // Rate Limiting
  'RATE_LIMIT_EXCEEDED': {
    message: 'Too many requests',
    action: 'Wait a few minutes and try again'
  },

  // Server
  'SERVER_ERROR': {
    message: 'Something went wrong on our end',
    action: 'Try again in a moment. If this persists, contact support'
  }
};

interface UserError {
  message: string;
  action?: string;
  field?: string;
}

export function mapError(error: any): UserError {
  // Extract error code from backend response
  const errorCode = error.response?.data?.error_code ||
                    error.response?.data?.code;

  // Check for field-specific validation errors
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;

    // FastAPI validation errors
    if (Array.isArray(detail)) {
      const firstError = detail[0];
      return {
        message: `${firstError.loc[1]}: ${firstError.msg}`,
        field: firstError.loc[1]
      };
    }
  }

  // Map known error codes
  if (errorCode && ERROR_MAP[errorCode]) {
    return ERROR_MAP[errorCode];
  }

  // HTTP status code fallbacks
  const status = error.response?.status;
  switch (status) {
    case 400:
      return {
        message: 'Invalid request',
        action: 'Check your input and try again'
      };
    case 401:
      return {
        message: 'Please sign in to continue',
        action: 'Your session may have expired'
      };
    case 403:
      return ERROR_MAP.PERMISSION_DENIED;
    case 404:
      return ERROR_MAP.RESOURCE_NOT_FOUND;
    case 429:
      return ERROR_MAP.RATE_LIMIT_EXCEEDED;
    case 500:
    case 502:
    case 503:
      return ERROR_MAP.SERVER_ERROR;
    default:
      return {
        message: 'An unexpected error occurred',
        action: 'Please try again or contact support'
      };
  }
}
```

## Error Handling Utilities

### Centralized Error Handler
```typescript
// utils/errorHandler.ts
import { mapError } from './errorMapper';

class ErrorHandler {
  static handleError(error: any, context?: string): UserError {
    // Log error for debugging (only in development)
    if (process.env.NODE_ENV === 'development') {
      console.error('Error in context:', context, error);
    }

    // Map to user-friendly message
    return mapError(error);
  }

  static handleApiError(error: any, context?: string): UserError {
    // Additional API-specific handling
    if (error.response) {
      // Server responded with error status
      return this.handleError(error, context);
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Unable to connect to server',
        action: 'Check your internet connection and try again'
      };
    } else {
      // Something else happened
      return {
        message: 'An unexpected error occurred',
        action: 'Please try again'
      };
    }
  }
}

export default ErrorHandler;
```

### Error Boundary Component (React)
```tsx
// components/ErrorBoundary.tsx
import React from 'react';
import ErrorHandler from '../utils/errorHandler';

interface Props {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: UserError }>;
}

interface State {
  hasError: boolean;
  error?: UserError;
}

class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: any): State {
    return {
      hasError: true,
      error: ErrorHandler.handleError(error, 'ErrorBoundary')
    };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return <FallbackComponent error={this.state.error} />;
    }

    return this.props.children;
  }
}

const DefaultErrorFallback: React.FC<{ error: UserError }> = ({ error }) => (
  <div className="error-container">
    <h2>Something went wrong</h2>
    <p>{error.message}</p>
    {error.action && <p>{error.action}</p>}
  </div>
);

export default ErrorBoundary;
```

## API Error Handling

### Service Layer Error Handling
```typescript
// services/apiService.ts
import axios, { AxiosResponse, AxiosRequestConfig } from 'axios';
import ErrorHandler from '../utils/errorHandler';

class ApiService {
  async request<T>(config: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    try {
      const response = await axios(config);
      return response;
    } catch (error) {
      const userError = ErrorHandler.handleApiError(error, config.url);

      // Optionally log to error tracking service
      if (window.Sentry) {
        window.Sentry.captureException(error);
      }

      // Throw user-friendly error
      throw userError;
    }
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.request<T>({ ...config, method: 'GET', url });
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.request<T>({ ...config, method: 'POST', url, data });
    return response.data;
  }
}

export const apiService = new ApiService();
```

### Form Validation Error Handler
```typescript
// utils/formErrorHandler.ts
import { mapError } from './errorMapper';

interface FormErrors {
  [field: string]: string;
}

export function handleFormErrors(error: any): FormErrors {
  const userError = mapError(error);

  if (userError.field) {
    // Field-specific error
    return { [userError.field]: userError.message };
  }

  // General error affecting entire form
  return { _form: userError.message };
}

// Usage in form components
/*
const handleSubmit = async () => {
  try {
    await submitForm(formData);
    // Success
  } catch (error) {
    const formErrors = handleFormErrors(error);
    setErrors(formErrors);
  }
};
*/
```

## Error Display Components

### Toast Notification Error
```tsx
// components/ToastError.tsx
import React, { useEffect } from 'react';
import { useToast } from '../hooks/useToast';

interface ToastErrorProps {
  error: UserError;
  duration?: number;
}

export const ToastError: React.FC<ToastErrorProps> = ({ error, duration = 5000 }) => {
  const { showToast } = useToast();

  useEffect(() => {
    showToast({
      type: 'error',
      title: error.message,
      description: error.action,
      duration
    });
  }, [error, duration]);

  return null;
};
```

### Inline Error Message
```tsx
// components/InlineErrorMessage.tsx
import React from 'react';

interface InlineErrorMessageProps {
  error: UserError;
  className?: string;
}

export const InlineErrorMessage: React.FC<InlineErrorMessageProps> = ({
  error,
  className = ''
}) => {
  return (
    <div
      className={`error-message ${className}`}
      role="alert"
      aria-live="polite"
    >
      <span className="error-text">{error.message}</span>
      {error.action && <span className="error-action"> {error.action}</span>}
    </div>
  );
};
```

## Error Logging Integration

### Sentry Integration
```typescript
// integrations/sentry.ts
import * as Sentry from '@sentry/react';
import { Integrations } from '@sentry/tracing';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [new Integrations.BrowserTracing()],
  tracesSampleRate: 0.1,
});

export const logError = (error: any, context?: any) => {
  Sentry.captureException(error, {
    contexts: {
      custom: context
    }
  });
};
```

### Custom Logger
```typescript
// utils/logger.ts
class Logger {
  static error(message: string, error?: any, context?: any) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: 'ERROR',
      message,
      error: error?.toString(),
      context,
      stack: error?.stack
    };

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error(logEntry);
    }

    // Send to error tracking service
    if (window.Sentry) {
      import('./integrations/sentry').then(({ logError }) => {
        logError(error, context);
      });
    }
  }

  static warn(message: string, context?: any) {
    if (process.env.NODE_ENV === 'development') {
      console.warn(message, context);
    }
  }
}

export default Logger;
```

## Framework-Specific Implementations

### Vue.js Error Handler
```vue
<!-- components/VueErrorHandler.vue -->
<template>
  <div v-if="error" class="error-container">
    <div class="error-message">{{ error.message }}</div>
    <div v-if="error.action" class="error-action">{{ error.action }}</div>
    <button @click="clearError">Dismiss</button>
  </div>
  <slot v-else />
</template>

<script>
import { mapError } from '@/utils/errorMapper';

export default {
  name: 'VueErrorHandler',
  props: {
    error: Object
  },
  methods: {
    clearError() {
      this.$emit('clear');
    }
  }
}
</script>
```

### Angular Error Handler
```typescript
// services/angular-error-handler.service.ts
import { Injectable, ErrorHandler } from '@angular/core';
import { mapError } from './errorMapper';

@Injectable()
export class CustomErrorHandler implements ErrorHandler {
  handleError(error: any): void {
    const userError = mapError(error);
    console.error('User-friendly error:', userError);

    // Handle error in UI
    this.displayError(userError);
  }

  private displayError(error: UserError) {
    // Show toast notification or modal
    // Could integrate with Angular Material snackbar
  }
}
```

## Best Practices
1. **User-friendly messages**: Never show raw technical errors
2. **Actionable guidance**: Tell users what they can do
3. **Consistent categorization**: Group similar errors
4. **Privacy protection**: Don't leak sensitive information
5. **Accessibility**: Ensure errors are readable by screen readers
6. **Logging**: Track errors for debugging while keeping user info safe

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing error handling patterns, UI framework, API response format |
| **Conversation** | User's specific error scenarios, preferred error display patterns |
| **Skill References** | Framework-specific error handling patterns, accessibility guidelines |
| **User Guidelines** | Project-specific error message style, privacy requirements |