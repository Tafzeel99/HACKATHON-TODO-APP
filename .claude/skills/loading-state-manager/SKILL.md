---
name: loading-state-manager
description: "Create skeleton screens, spinners, and loading states for better UX. Use when user needs loading indicators or placeholders."
version: "1.0.0"
---

# Loading State Manager Skill

## When to Use This Skill
- User asks for "loading spinner" or "skeleton screen"
- User mentions "loading state" or "placeholder"
- User needs to show progress during data fetching
- User wants to improve perceived performance

## Procedure
1. **Identify loading type**: Spinner, skeleton, progress bar, or pulse
2. **Match content structure**: Skeleton should mirror actual content
3. **Add accessibility**: ARIA labels for screen readers
4. **Animate smoothly**: Use CSS animations for smooth transitions
5. **Handle errors**: Show error states when loading fails

## Output Format
```typescript
// components/loading/[component-name].tsx
import React from 'react';

interface [Component]Props {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const [Component]: React.FC<[Component]Props> = ({ size, className }) => {
  // Implementation
};
```

## Quality Criteria
- **Accessibility**: Proper ARIA labels and roles
- **Performance**: Use CSS animations over JS
- **Matching Layout**: Skeleton matches final content layout
- **Smooth Transitions**: Fade in/out animations
- **Responsive**: Works on all screen sizes

## Loading Components

### Spinner
```typescript
// components/loading/spinner.tsx
import React from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'white' | 'gray';
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = ''
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const colors = {
    primary: 'border-blue-600',
    white: 'border-white',
    gray: 'border-gray-600'
  };

  return (
    <div
      className={`
        ${sizes[size]}
        border-4 border-gray-200
        ${colors[color]}
        border-t-transparent
        rounded-full
        animate-spin
        ${className}
      `}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};
```

### Skeleton
```typescript
// components/loading/skeleton.tsx
import React from 'react';

interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  className?: string;
  animation?: 'pulse' | 'wave';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
  animation = 'pulse'
}) => {
  const variants = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md'
  };

  const animations = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]'
  };

  const style: React.CSSProperties = {
    width: width || (variant === 'text' ? '100%' : '40px'),
    height: height || (variant === 'circular' ? '40px' : undefined)
  };

  return (
    <div
      className={`
        bg-gray-200
        ${variants[variant]}
        ${animations[animation]}
        ${className}
      `}
      style={style}
      aria-label="Loading placeholder"
    />
  );
};
```

### Skeleton Card
```typescript
// components/loading/skeleton-card.tsx
import React from 'react';
import { Skeleton } from './skeleton';

export const SkeletonCard: React.FC = () => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-4 mb-4">
        <Skeleton variant="circular" width={48} height={48} />
        <div className="flex-1">
          <Skeleton width="60%" className="mb-2" />
          <Skeleton width="40%" />
        </div>
      </div>
      <Skeleton variant="rectangular" height={120} className="mb-4" />
      <Skeleton width="80%" className="mb-2" />
      <Skeleton width="90%" />
    </div>
  );
};
```

### Progress Bar
```typescript
// components/loading/progress-bar.tsx
import React from 'react';

interface ProgressBarProps {
  value: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  size = 'md',
  color = 'primary',
  showLabel = false,
  className = ''
}) => {
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const colors = {
    primary: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    error: 'bg-red-600'
  };

  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={className}>
      <div
        className={`w-full ${sizes[size]} bg-gray-200 rounded-full overflow-hidden`}
        role="progressbar"
        aria-valuenow={clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={`${sizes[size]} ${colors[color]} rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-sm text-gray-600 mt-1 text-right">
          {clampedValue}%
        </p>
      )}
    </div>
  );
};
```

### Loading Overlay
```typescript
// components/loading/loading-overlay.tsx
import React from 'react';
import { Spinner } from './spinner';

interface LoadingOverlayProps {
  message?: string;
  fullScreen?: boolean;
  transparent?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = 'Loading...',
  fullScreen = false,
  transparent = false
}) => {
  return (
    <div
      className={`
        flex flex-col items-center justify-center gap-4
        ${fullScreen ? 'fixed inset-0 z-50' : 'absolute inset-0'}
        ${transparent ? 'bg-white/80' : 'bg-white'}
      `}
    >
      <Spinner size="lg" />
      <p className="text-gray-600 font-medium">{message}</p>
    </div>
  );
};
```

### Dots Loader
```typescript
// components/loading/dots-loader.tsx
import React from 'react';

interface DotsLoaderProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'gray' | 'white';
  className?: string;
}

export const DotsLoader: React.FC<DotsLoaderProps> = ({
  size = 'md',
  color = 'primary',
  className = ''
}) => {
  const sizes = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2.5 h-2.5',
    lg: 'w-4 h-4'
  };

  const colors = {
    primary: 'bg-blue-600',
    gray: 'bg-gray-600',
    white: 'bg-white'
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div
        className={`${sizes[size]} ${colors[color]} rounded-full animate-bounce`}
        style={{ animationDelay: '0ms' }}
      />
      <div
        className={`${sizes[size]} ${colors[color]} rounded-full animate-bounce`}
        style={{ animationDelay: '150ms' }}
      />
      <div
        className={`${sizes[size]} ${colors[color]} rounded-full animate-bounce`}
        style={{ animationDelay: '300ms' }}
      />
    </div>
  );
};
```

## React Hook for Loading States
```typescript
// hooks/use-loading.ts
import { useState } from 'react';

export function useLoading(initialState: boolean = false) {
  const [loading, setLoading] = useState(initialState);

  const startLoading = () => setLoading(true);
  const stopLoading = () => setLoading(false);

  const withLoading = async <T,>(fn: () => Promise<T>): Promise<T> => {
    startLoading();
    try {
      return await fn();
    } finally {
      stopLoading();
    }
  };

  return {
    loading,
    startLoading,
    stopLoading,
    withLoading
  };
}
```

## Skeleton Templates

### User Profile Skeleton
```typescript
// components/loading/skeleton-user-profile.tsx
import React from 'react';
import { Skeleton } from './skeleton';

export const SkeletonUserProfile: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Skeleton variant="circular" width={80} height={80} />
        <div className="flex-1">
          <Skeleton width="40%" height={24} className="mb-2" />
          <Skeleton width="30%" height={16} />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="p-4 border border-gray-200 rounded-lg">
            <Skeleton width="60%" className="mb-2" />
            <Skeleton width="40%" height={28} />
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="space-y-3">
        <Skeleton variant="rectangular" height={120} />
        <Skeleton width="90%" />
        <Skeleton width="85%" />
        <Skeleton width="75%" />
      </div>
    </div>
  );
};
```

### Table Skeleton
```typescript
// components/loading/skeleton-table.tsx
import React from 'react';
import { Skeleton } from './skeleton';

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
}

export const SkeletonTable: React.FC<SkeletonTableProps> = ({
  rows = 5,
  columns = 4
}) => {
  return (
    <div className="w-full">
      {/* Header */}
      <div className="grid gap-4 p-4 border-b border-gray-200" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} width="70%" height={16} />
        ))}
      </div>

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          className="grid gap-4 p-4 border-b border-gray-200"
          style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} />
          ))}
        </div>
      ))}
    </div>
  );
};
```

### List Skeleton
```typescript
// components/loading/skeleton-list.tsx
import React from 'react';
import { Skeleton } from './skeleton';

interface SkeletonListProps {
  items?: number;
  showAvatar?: boolean;
}

export const SkeletonList: React.FC<SkeletonListProps> = ({
  items = 5,
  showAvatar = true
}) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg">
          {showAvatar && <Skeleton variant="circular" width={48} height={48} />}
          <div className="flex-1">
            <Skeleton width="60%" className="mb-2" />
            <Skeleton width="80%" />
          </div>
        </div>
      ))}
    </div>
  );
};
```

## Usage Examples

### With Data Fetching
```typescript
import { useState, useEffect } from 'react';
import { SkeletonCard } from '@/components/loading/skeleton-card';
import { userService } from '@/services/user-service';

function UserDashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const data = await userService.getUsers();
        setUsers(data.users);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map(i => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

### With Button
```typescript
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/loading/spinner';

function SubmitButton() {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      alert('Success!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button onClick={handleClick} disabled={loading}>
      {loading ? (
        <>
          <Spinner size="sm" color="white" />
          <span>Processing...</span>
        </>
      ) : (
        'Submit'
      )}
    </Button>
  );
}
```

### With Progress
```typescript
import { useState, useEffect } from 'react';
import { ProgressBar } from '@/components/loading/progress-bar';

function FileUpload() {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    setUploading(true);
    setProgress(0);

    // Simulate upload
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setUploading(false);
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  return (
    <div>
      <button onClick={handleUpload} disabled={uploading}>
        Upload File
      </button>
      {uploading && (
        <div className="mt-4">
          <ProgressBar value={progress} showLabel />
        </div>
      )}
    </div>
  );
}
```

## Tailwind Config for Shimmer Animation
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' }
        }
      },
      animation: {
        shimmer: 'shimmer 2s infinite linear'
      }
    }
  }
}
```

## Best Practices
1. **Match Content**: Skeleton should mirror actual content layout
2. **Smooth Transitions**: Fade in content when loading completes
3. **Accessibility**: Include ARIA labels and roles
4. **Performance**: Use CSS animations, not JavaScript
5. **Consistent Timing**: Use same animation duration across components
6. **Error States**: Show error message if loading fails
7. **Progressive Loading**: Load critical content first
8. **Avoid Layout Shift**: Maintain space during loading
9. **Context Awareness**: Different loading states for different scenarios

## Testing Guidelines
- Verify loading states appear and disappear correctly
- Test accessibility with screen readers
- Check loading states on different screen sizes
- Validate that content doesn't shift during loading
- Test error states when loading fails
- Ensure animations are smooth and performant

## Output Checklist
- [ ] Spinner component with size/color variants
- [ ] Skeleton component with different shapes
- [ ] Progress bar with customizable appearance
- [ ] Loading overlay component
- [ ] React hook for managing loading states
- [ ] Accessibility attributes included
- [ ] CSS animations for smooth transitions
- [ ] Responsive design considerations
- [ ] TypeScript interfaces for all components
- [ ] Usage examples provided