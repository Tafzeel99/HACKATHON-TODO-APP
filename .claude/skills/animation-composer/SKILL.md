---
name: animation-composer
description: "Create micro-interactions and animations using CSS and lightweight techniques. Use when user needs animations or interactive effects."
version: "1.0.0"
---

# Animation Composer Skill

## When to Use This Skill
- User asks for "animations" or "transitions"
- User mentions "hover effects" or "micro-interactions"
- User wants to add "motion" or "interactivity"
- User needs entrance/exit animations

## Procedure
1. **Identify interaction**: Hover, click, scroll, or page load
2. **Choose animation type**: Fade, slide, scale, rotate, or bounce
3. **Set timing**: Duration and easing function
4. **Add accessibility**: Respect `prefers-reduced-motion`
5. **Optimize performance**: Use transform and opacity only

## Output Format
```typescript
// components/animated/[component-name].tsx
import React from 'react';

interface [Component]Props {
  children: React.ReactNode;
  animation?: 'fade' | 'slide' | 'scale';
  duration?: number;
  delay?: number;
}

export const [Component]: React.FC<[Component]Props> = ({ ... }) => {
  // Implementation
};
```

## Quality Criteria
- **Performance**: Use transform and opacity for 60fps
- **Accessibility**: Respect reduced motion preferences
- **Subtlety**: Animations should enhance, not distract
- **Consistency**: Use same timing and easing across app
- **Purpose**: Every animation should have a clear purpose

## Animation Utilities

### Fade In
```typescript
// components/animated/fade-in.tsx
import React, { useEffect, useState, useRef } from 'react';

interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right' | 'none';
  distance?: number;
  className?: string;
  once?: boolean;
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delay = 0,
  duration = 600,
  direction = 'up',
  distance = 20,
  className = '',
  once = true
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once) {
            observer.disconnect();
          }
        } else if (!once) {
          setIsVisible(false);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [once]);

  const getTransform = () => {
    if (!isVisible) {
      switch (direction) {
        case 'up': return `translateY(${distance}px)`;
        case 'down': return `translateY(-${distance}px)`;
        case 'left': return `translateX(${distance}px)`;
        case 'right': return `translateX(-${distance}px)`;
        default: return 'none';
      }
    }
    return 'none';
  };

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: getTransform(),
        transition: `opacity ${duration}ms ease-out ${delay}ms, transform ${duration}ms ease-out ${delay}ms`
      }}
    >
      {children}
    </div>
  );
};
```

### Stagger Children
```typescript
// components/animated/stagger.tsx
import React from 'react';

interface StaggerProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
}

export const Stagger: React.FC<StaggerProps> = ({
  children,
  delay = 100,
  duration = 400,
  className = ''
}) => {
  const childrenArray = React.Children.toArray(children);

  return (
    <div className={className}>
      {childrenArray.map((child, index) => (
        <div
          key={index}
          style={{
            animation: `fadeInUp ${duration}ms ease-out ${index * delay}ms both`
          }}
        >
          {child}
        </div>
      ))}
    </div>
  );
};
```

### Scale On Hover
```typescript
// components/animated/scale-hover.tsx
import React, { useState } from 'react';

interface ScaleHoverProps {
  children: React.ReactNode;
  scale?: number;
  duration?: number;
  className?: string;
}

export const ScaleHover: React.FC<ScaleHoverProps> = ({
  children,
  scale = 1.05,
  duration = 200,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        transform: isHovered ? `scale(${scale})` : 'scale(1)',
        transition: `transform ${duration}ms ease-out`
      }}
    >
      {children}
    </div>
  );
};
```

### Slide In
```typescript
// components/animated/slide-in.tsx
import React, { useEffect, useState } from 'react';

interface SlideInProps {
  children: React.ReactNode;
  direction?: 'left' | 'right' | 'up' | 'down';
  duration?: number;
  delay?: number;
  distance?: number;
  className?: string;
}

export const SlideIn: React.FC<SlideInProps> = ({
  children,
  direction = 'left',
  duration = 500,
  delay = 0,
  distance = 50,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const getInitialTransform = () => {
    switch (direction) {
      case 'left': return `translateX(-${distance}px)`;
      case 'right': return `translateX(${distance}px)`;
      case 'up': return `translateY(${distance}px)`;
      case 'down': return `translateY(-${distance}px)`;
    }
  };

  return (
    <div
      className={className}
      style={{
        transform: isVisible ? 'translate(0, 0)' : getInitialTransform(),
        opacity: isVisible ? 1 : 0,
        transition: `all ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`
      }}
    >
      {children}
    </div>
  );
};
```

### Bounce
```typescript
// components/animated/bounce.tsx
import React from 'react';

interface BounceProps {
  children: React.ReactNode;
  active?: boolean;
  className?: string;
}

export const Bounce: React.FC<BounceProps> = ({
  children,
  active = false,
  className = ''
}) => {
  return (
    <div
      className={`${className} ${active ? 'animate-bounce' : ''}`}
    >
      {children}
    </div>
  );
};
```

### Rotate On Hover
```typescript
// components/animated/rotate-hover.tsx
import React, { useState } from 'react';

interface RotateHoverProps {
  children: React.ReactNode;
  degrees?: number;
  duration?: number;
  className?: string;
}

export const RotateHover: React.FC<RotateHoverProps> = ({
  children,
  degrees = 180,
  duration = 300,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        transform: isHovered ? `rotate(${degrees}deg)` : 'rotate(0deg)',
        transition: `transform ${duration}ms ease-in-out`
      }}
    >
      {children}
    </div>
  );
};
```

### Pulse
```typescript
// components/animated/pulse.tsx
import React from 'react';

interface PulseProps {
  children: React.ReactNode;
  duration?: number;
  scale?: number;
  className?: string;
}

export const Pulse: React.FC<PulseProps> = ({
  children,
  duration = 1000,
  scale = 1.05,
  className = ''
}) => {
  return (
    <div
      className={className}
      style={{
        animation: `pulse ${duration}ms ease-in-out infinite`
      }}
    >
      {children}
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(${scale}); }
        }
      `}</style>
    </div>
  );
};
```

### Page Transition
```typescript
// components/animated/page-transition.tsx
import React, { useState, useEffect } from 'react';

interface PageTransitionProps {
  children: React.ReactNode;
  duration?: number;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  duration = 300,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div
      className={className}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(10px)',
        transition: `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`
      }}
    >
      {children}
    </div>
  );
};
```

## Custom Hooks

### useHover
```typescript
// hooks/use-hover.ts
import { useState, useRef, useEffect } from 'react';

export function useHover<T extends HTMLElement = HTMLElement>() {
  const [isHovered, setIsHovered] = useState(false);
  const ref = useRef<T>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    const handleMouseEnter = () => setIsHovered(true);
    const handleMouseLeave = () => setIsHovered(false);

    node.addEventListener('mouseenter', handleMouseEnter);
    node.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      node.removeEventListener('mouseenter', handleMouseEnter);
      node.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return { ref, isHovered };
}
```

### useInView
```typescript
// hooks/use-in-view.ts
import { useState, useEffect, useRef } from 'react';

interface UseInViewOptions {
  threshold?: number;
  once?: boolean;
}

export function useInView<T extends HTMLElement = HTMLElement>(
  options: UseInViewOptions = {}
) {
  const { threshold = 0.1, once = true } = options;
  const [isInView, setIsInView] = useState(false);
  const ref = useRef<T>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          if (once) {
            observer.disconnect();
          }
        } else if (!once) {
          setIsInView(false);
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold, once]);

  return { ref, isInView };
}
```

## Tailwind Animations Config
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' }
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' }
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' }
        }
      },
      animation: {
        fadeInUp: 'fadeInUp 0.5s ease-out',
        fadeInDown: 'fadeInDown 0.5s ease-out',
        slideInLeft: 'slideInLeft 0.5s ease-out',
        slideInRight: 'slideInRight 0.5s ease-out',
        scaleIn: 'scaleIn 0.3s ease-out'
      }
    }
  }
}
```

## Usage Examples

### Fade In on Scroll
```typescript
import { FadeIn } from '@/components/animated/fade-in';

function Features() {
  return (
    <div className="space-y-8">
      <FadeIn direction="up" delay={0}>
        <h2>Feature 1</h2>
        <p>Description</p>
      </FadeIn>

      <FadeIn direction="up" delay={200}>
        <h2>Feature 2</h2>
        <p>Description</p>
      </FadeIn>

      <FadeIn direction="up" delay={400}>
        <h2>Feature 3</h2>
        <p>Description</p>
      </FadeIn>
    </div>
  );
}
```

### Staggered List
```typescript
import { Stagger } from '@/components/animated/stagger';

function ItemList({ items }) {
  return (
    <Stagger delay={100}>
      {items.map(item => (
        <div key={item.id} className="p-4 bg-white rounded shadow">
          {item.name}
        </div>
      ))}
    </Stagger>
  );
}
```

### Hover Effects
```typescript
import { ScaleHover } from '@/components/animated/scale-hover';
import { useHover } from '@/hooks/use-hover';

function Card() {
  const { ref, isHovered } = useHover();

  return (
    <ScaleHover scale={1.02}>
      <div
        ref={ref}
        className="p-6 bg-white rounded-lg shadow transition-shadow"
        style={{ boxShadow: isHovered ? '0 10px 30px rgba(0,0,0,0.2)' : undefined }}
      >
        <h3>Card Title</h3>
        <p>Card content</p>
      </div>
    </ScaleHover>
  );
}
```

### Entrance Animation
```typescript
import { SlideIn } from '@/components/animated/slide-in';

function Hero() {
  return (
    <div>
      <SlideIn direction="down" duration={600}>
        <h1 className="text-5xl font-bold">Welcome</h1>
      </SlideIn>

      <SlideIn direction="up" duration={600} delay={200}>
        <p className="text-xl">Subtitle text here</p>
      </SlideIn>

      <SlideIn direction="up" duration={600} delay={400}>
        <button>Get Started</button>
      </SlideIn>
    </div>
  );
}
```

### Button with Ripple Effect
```typescript
import { useState } from 'react';

function RippleButton({ children, onClick }) {
  const [ripples, setRipples] = useState([]);

  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newRipple = {
      x,
      y,
      id: Date.now()
    };

    setRipples([...ripples, newRipple]);
    setTimeout(() => {
      setRipples(ripples => ripples.filter(r => r.id !== newRipple.id));
    }, 600);

    onClick?.(e);
  };

  return (
    <button
      className="relative overflow-hidden px-4 py-2 bg-blue-600 text-white rounded"
      onClick={handleClick}
    >
      {children}
      {ripples.map(ripple => (
        <span
          key={ripple.id}
          className="absolute bg-white rounded-full animate-ping"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: 20,
            height: 20,
            transform: 'translate(-50%, -50%)',
            opacity: 0.6
          }}
        />
      ))}
    </button>
  );
}
```

## Accessibility
```css
/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Best Practices
1. **Use Transform & Opacity**: Best performance for animations
2. **60fps Target**: Keep animations smooth at 60 frames per second
3. **Subtle Motion**: Animations should enhance, not distract
4. **Consistent Timing**: Use same easing and duration across app
5. **Purpose-Driven**: Every animation should have a clear purpose
6. **Respect Preferences**: Honor `prefers-reduced-motion`
7. **Progressive Enhancement**: Work without animations
8. **Test Performance**: Check on low-end devices
9. **Meaningful Motion**: Animations should guide user attention
10. **Don't Overdo It**: Less is often more with animations

## Testing Guidelines
- Verify animations work across different browsers
- Test with reduced motion preferences enabled
- Check performance on mobile devices
- Ensure animations don't cause accessibility issues
- Validate that content remains accessible during animations

## Output Checklist
- [ ] Animation components with proper performance optimizations
- [ ] Accessibility considerations included
- [ ] TypeScript interfaces for all components
- [ ] Custom hooks for common animation patterns
- [ ] Tailwind configuration for animations
- [ ] Usage examples for different scenarios
- [ ] Proper easing and timing functions
- [ ] Performance optimization with transform/opacity only
- [ ] Responsive animations that work on all devices
- [ ] Clean, reusable animation components