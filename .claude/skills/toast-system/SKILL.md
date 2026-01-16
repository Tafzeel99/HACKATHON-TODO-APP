---
name: toast-system
description: "Create toast notifications for success, error, warning, and info messages. Use when user needs temporary feedback messages."
version: "1.0.0"
---

# Toast System Skill

## When to Use This Skill
- User asks for "notifications" or "toast messages"
- User mentions "success message" or "error alert"
- User needs temporary feedback for actions
- User wants non-blocking notifications

## Procedure
1. **Create context**: Global toast state management
2. **Define types**: Success, error, warning, info
3. **Add positioning**: Top-right, top-center, bottom-right, etc.
4. **Auto-dismiss**: Remove toasts after timeout
5. **Add animations**: Slide in/out smoothly
6. **Include actions**: Close button and action callbacks

## Output Format
```typescript
// components/toast/toast-provider.tsx
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Implementation
};

// hooks/use-toast.ts
export function useToast() {
  return {
    success: (message: string) => {},
    error: (message: string) => {},
    warning: (message: string) => {},
    info: (message: string) => {}
  };
}
```

## Quality Criteria
- **Accessibility**: Proper ARIA roles and live regions
- **Performance**: Smooth animations, efficient state management
- **Stacking**: Multiple toasts stack nicely
- **Customization**: Support custom duration, position, actions
- **Responsive**: Work on all screen sizes

## Toast Implementation

### Toast Types
```typescript
// types/toast.ts
export type ToastType = 'success' | 'error' | 'warning' | 'info';
export type ToastPosition = 'top-right' | 'top-center' | 'top-left' | 'bottom-right' | 'bottom-center' | 'bottom-left';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  description?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

### Toast Context
```typescript
// contexts/toast-context.tsx
import React, { createContext, useState, useContext, useCallback } from 'react';
import { Toast, ToastType } from '@/types/toast';

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: Toast = { ...toast, id };

    setToasts(prev => [...prev, newToast]);

    // Auto-dismiss
    const duration = toast.duration || 5000;
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
    </ToastContext.Provider>
  );
};

export const useToastContext = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToastContext must be used within ToastProvider');
  }
  return context;
};
```

### useToast Hook
```typescript
// hooks/use-toast.ts
import { useToastContext } from '@/contexts/toast-context';
import { ToastType } from '@/types/toast';

export function useToast() {
  const { addToast } = useToastContext();

  const show = (
    type: ToastType,
    message: string,
    description?: string,
    duration?: number,
    action?: { label: string; onClick: () => void }
  ) => {
    addToast({ type, message, description, duration, action });
  };

  return {
    success: (message: string, description?: string, duration?: number) =>
      show('success', message, description, duration),

    error: (message: string, description?: string, duration?: number) =>
      show('error', message, description, duration),

    warning: (message: string, description?: string, duration?: number) =>
      show('warning', message, description, duration),

    info: (message: string, description?: string, duration?: number) =>
      show('info', message, description, duration),

    custom: (message: string, description?: string, duration?: number, action?: { label: string; onClick: () => void }) =>
      addToast({ type: 'info', message, description, duration, action })
  };
}
```

### Toast Component
```typescript
// components/toast/toast.tsx
import React, { useEffect, useState } from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { Toast as ToastType } from '@/types/toast';

interface ToastProps {
  toast: ToastType;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ toast, onClose }) => {
  const [isExiting, setIsExiting] = useState(false);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(onClose, 300);
  };

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-green-600" />,
    error: <AlertCircle className="w-5 h-5 text-red-600" />,
    warning: <AlertTriangle className="w-5 h-5 text-yellow-600" />,
    info: <Info className="w-5 h-5 text-blue-600" />
  };

  const colors = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-blue-50 border-blue-200'
  };

  return (
    <div
      className={`
        flex items-start gap-3 p-4 rounded-lg border shadow-lg max-w-md w-full
        ${colors[toast.type]}
        ${isExiting ? 'animate-slide-out' : 'animate-slide-in'}
      `}
      role="alert"
      aria-live="polite"
    >
      <div className="flex-shrink-0">{icons[toast.type]}</div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900">{toast.message}</p>
        {toast.description && (
          <p className="text-sm text-gray-600 mt-1">{toast.description}</p>
        )}
        {toast.action && (
          <button
            onClick={toast.action.onClick}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 mt-2"
          >
            {toast.action.label}
          </button>
        )}
      </div>

      <button
        onClick={handleClose}
        className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Close notification"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
};
```

### Toast Container
```typescript
// components/toast/toast-container.tsx
import React from 'react';
import { useToastContext } from '@/contexts/toast-context';
import { Toast } from './toast';

interface ToastContainerProps {
  position?: 'top-right' | 'top-center' | 'top-left' | 'bottom-right' | 'bottom-center' | 'bottom-left';
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ position = 'top-right' }) => {
  const { toasts, removeToast } = useToastContext();

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
    'bottom-left': 'bottom-4 left-4'
  };

  return (
    <div
      className={`fixed ${positionClasses[position]} z-50 flex flex-col gap-2 pointer-events-none`}
      aria-live="polite"
      aria-atomic="false"
    >
      {toasts.map(toast => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast toast={toast} onClose={() => removeToast(toast.id)} />
        </div>
      ))}
    </div>
  );
};
```

### Progress Bar Toast
```typescript
// components/toast/toast-with-progress.tsx
import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { Toast as ToastType } from '@/types/toast';

interface ToastWithProgressProps {
  toast: ToastType;
  onClose: () => void;
}

export const ToastWithProgress: React.FC<ToastWithProgressProps> = ({ toast, onClose }) => {
  const [progress, setProgress] = useState(100);
  const duration = toast.duration || 5000;

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev - (100 / (duration / 100));
        return newProgress <= 0 ? 0 : newProgress;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [duration]);

  return (
    <div className="relative overflow-hidden bg-white rounded-lg border border-gray-200 shadow-lg max-w-md w-full">
      {/* Progress bar */}
      <div
        className="absolute bottom-0 left-0 h-1 bg-blue-600 transition-all duration-100"
        style={{ width: `${progress}%` }}
      />

      {/* Content */}
      <div className="flex items-start gap-3 p-4">
        <div className="flex-1">
          <p className="font-medium text-gray-900">{toast.message}</p>
          {toast.description && (
            <p className="text-sm text-gray-600 mt-1">{toast.description}</p>
          )}
        </div>

        <button
          onClick={onClose}
          className="flex-shrink-0 text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};
```

## Tailwind Animation Config
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        'slide-in': {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' }
        },
        'slide-out': {
          '0%': { transform: 'translateX(0)', opacity: '1' },
          '100%': { transform: 'translateX(100%)', opacity: '0' }
        }
      },
      animation: {
        'slide-in': 'slide-in 0.3s ease-out',
        'slide-out': 'slide-out 0.3s ease-in'
      }
    }
  }
}
```

## Usage Examples

### Basic Usage
```typescript
import { ToastProvider } from '@/contexts/toast-context';
import { ToastContainer } from '@/components/toast/toast-container';

function App() {
  return (
    <ToastProvider>
      <YourApp />
      <ToastContainer position="top-right" />
    </ToastProvider>
  );
}
```

### In Components
```typescript
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';

function SaveButton() {
  const toast = useToast();
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      await saveData();
      toast.success('Saved successfully!', 'Your changes have been saved.');
    } catch (error) {
      toast.error('Save failed', 'Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button onClick={handleSave} isLoading={loading}>
      Save Changes
    </Button>
  );
}
```

### With Action Button
```typescript
import { useToast } from '@/hooks/use-toast';

function DeleteButton({ itemId }) {
  const toast = useToast();

  const handleDelete = () => {
    toast.warning(
      'Item deleted',
      'The item has been moved to trash.',
      7000,
      {
        label: 'Undo',
        onClick: () => {
          // Restore item
          toast.success('Item restored');
        }
      }
    );
  };

  return <button onClick={handleDelete}>Delete</button>;
}
```

### Form Submission
```typescript
import { useToast } from '@/hooks/use-toast';
import { useForm } from '@/hooks/use-form';

function ContactForm() {
  const toast = useToast();

  const { values, errors, handleChange, handleSubmit, isSubmitting } = useForm({
    initialValues: { name: '', email: '', message: '' },
    schema: {
      name: { required: true },
      email: { required: true, email: true },
      message: { required: true }
    },
    onSubmit: async (values) => {
      try {
        await submitForm(values);
        toast.success('Message sent!', 'We\'ll get back to you soon.');
      } catch (error) {
        toast.error('Failed to send', 'Please check your connection and try again.');
      }
    }
  });

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <Button type="submit" isLoading={isSubmitting}>
        Send Message
      </Button>
    </form>
  );
}
```

### Promise-based Toast
```typescript
import { useToast } from '@/hooks/use-toast';

function usePromiseToast() {
  const toast = useToast();

  const promiseToast = async <T,>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: string;
      error: string;
    }
  ): Promise<T> => {
    toast.info(messages.loading, undefined, 0); // 0 = no auto-dismiss

    try {
      const result = await promise;
      toast.success(messages.success);
      return result;
    } catch (error) {
      toast.error(messages.error);
      throw error;
    }
  };

  return promiseToast;
}

// Usage
function Component() {
  const promiseToast = usePromiseToast();

  const handleAction = async () => {
    await promiseToast(
      fetchData(),
      {
        loading: 'Loading data...',
        success: 'Data loaded successfully!',
        error: 'Failed to load data'
      }
    );
  };

  return <button onClick={handleAction}>Load Data</button>;
}
```

### Multiple Toast Types
```typescript
import { useToast } from '@/hooks/use-toast';

function NotificationExamples() {
  const toast = useToast();

  return (
    <div className="space-x-2">
      <button onClick={() => toast.success('Operation successful!')}>
        Success
      </button>

      <button onClick={() => toast.error('Something went wrong!')}>
        Error
      </button>

      <button onClick={() => toast.warning('Please review your changes')}>
        Warning
      </button>

      <button onClick={() => toast.info('New feature available!')}>
        Info
      </button>
    </div>
  );
}
```

## Advanced Features

### Toast Queue
```typescript
// Limit number of visible toasts
const MAX_TOASTS = 3;

const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
  const id = Math.random().toString(36).substr(2, 9);
  const newToast: Toast = { ...toast, id };

  setToasts(prev => {
    const updated = [...prev, newToast];
    // Keep only last MAX_TOASTS
    return updated.slice(-MAX_TOASTS);
  });

  // Auto-dismiss logic...
}, []);
```

### Persistent Toast
```typescript
// Toast that doesn't auto-dismiss
toast.custom(
  'Important notice',
  'This message requires your attention',
  0 // duration: 0 means no auto-dismiss
);
```

## Best Practices
1. **Keep Messages Short**: Toast messages should be concise
2. **Use Appropriate Types**: Success for completions, error for failures
3. **Meaningful Descriptions**: Provide context when needed
4. **Action Buttons**: Offer undo for destructive actions
5. **Limit Toasts**: Don't show too many toasts at once
6. **Accessible**: Proper ARIA labels and live regions
7. **Auto-dismiss**: Most toasts should auto-dismiss after 3-7 seconds
8. **Position**: Top-right is most common, choose based on app layout
9. **Animations**: Smooth slide-in/out animations
10. **Error Handling**: Always provide helpful error messages

## Testing Guidelines
- Verify toasts appear and disappear correctly
- Test accessibility with screen readers
- Check different toast positions
- Validate auto-dismiss functionality
- Test action button functionality
- Verify proper ARIA attributes

## Output Checklist
- [ ] Toast context with proper state management
- [ ] useToast hook with all toast types
- [ ] Toast component with proper styling
- [ ] Toast container with positioning options
- [ ] Accessibility attributes included
- [ ] TypeScript interfaces for all types
- [ ] Animation configurations
- [ ] Usage examples provided
- [ ] Auto-dismiss functionality
- [ ] Action button support