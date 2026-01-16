---
name: accessibility-checker
description: "Generate WCAG 2.1 compliant markup with proper ARIA attributes, semantic HTML, and keyboard navigation. Use when user needs accessible components."
version: "1.0.0"
---

# Accessibility Checker Skill

## When to Use This Skill
- User asks for "accessible components" or "WCAG compliance"
- User mentions "screen reader support" or "keyboard navigation"
- User needs "ARIA labels" or "semantic HTML"
- User wants to improve accessibility

## Procedure
1. **Use semantic HTML**: Choose correct elements (button, nav, main, etc.)
2. **Add ARIA attributes**: Labels, roles, states for screen readers
3. **Keyboard navigation**: Ensure all interactive elements are keyboard accessible
4. **Focus management**: Visible focus indicators and logical tab order
5. **Color contrast**: Ensure text meets WCAG AA standards (4.5:1 ratio)
6. **Alternative text**: Provide alt text for images and labels for inputs

## Output Format
```typescript
// components/accessible/[component-name].tsx
import React from 'react';

interface [Component]Props {
  // Accessibility props
  ariaLabel?: string;
  ariaDescribedBy?: string;
  // Other props
}

export const [Component]: React.FC<[Component]Props> = ({ ... }) => {
  // Implementation with accessibility features
};
```

## Quality Criteria
- **WCAG 2.1 Level AA**: Meet AA standards minimum
- **Keyboard Support**: All functionality via keyboard
- **Screen Reader**: Proper announcements and navigation
- **Focus Visible**: Clear focus indicators on all interactive elements
- **Semantic HTML**: Use correct HTML elements for their purpose

## Accessible Components

### Accessible Button
```typescript
// components/accessible/button.tsx
import React from 'react';

interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  loadingText?: string;
  ariaLabel?: string;
  children: React.ReactNode;
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  loadingText = 'Loading',
  ariaLabel,
  children,
  disabled,
  ...props
}) => {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      className={`
        ${variants[variant]}
        ${sizes[size]}
        rounded-md font-medium transition-colors
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        inline-flex items-center justify-center gap-2
      `}
      disabled={disabled || isLoading}
      aria-label={ariaLabel}
      aria-busy={isLoading}
      aria-disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <span
            className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
            role="status"
            aria-hidden="true"
          />
          <span>{loadingText}</span>
        </>
      ) : (
        children
      )}
    </button>
  );
};
```

### Accessible Form Input
```typescript
// components/accessible/input.tsx
import React, { useId } from 'react';

interface AccessibleInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  hideLabel?: boolean;
}

export const AccessibleInput: React.FC<AccessibleInputProps> = ({
  label,
  error,
  helperText,
  required = false,
  hideLabel = false,
  id,
  ...props
}) => {
  const generatedId = useId();
  const inputId = id || generatedId;
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;

  return (
    <div className="w-full">
      <label
        htmlFor={inputId}
        className={`
          block text-sm font-medium text-gray-700 mb-1
          ${hideLabel ? 'sr-only' : ''}
        `}
      >
        {label}
        {required && (
          <span className="text-red-600 ml-1" aria-label="required">
            *
          </span>
        )}
      </label>

      <input
        id={inputId}
        className={`
          w-full px-3 py-2 border rounded-md
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:bg-gray-100 disabled:cursor-not-allowed
          ${error ? 'border-red-500' : 'border-gray-300'}
        `}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={
          error ? errorId : helperText ? helperId : undefined
        }
        aria-required={required}
        required={required}
        {...props}
      />

      {error && (
        <p
          id={errorId}
          className="mt-1 text-sm text-red-600"
          role="alert"
          aria-live="polite"
        >
          {error}
        </p>
      )}

      {helperText && !error && (
        <p id={helperId} className="mt-1 text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
};
```

### Accessible Modal
```typescript
// components/accessible/modal.tsx
import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  description?: string;
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  description
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Focus management
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousActiveElement.current?.focus();
    }
  }, [isOpen]);

  // Trap focus inside modal
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }

      if (e.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (!focusableElements || focusableElements.length === 0) return;

        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby={description ? 'modal-description' : undefined}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        ref={modalRef}
        className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6"
        tabIndex={-1}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 id="modal-title" className="text-xl font-semibold text-gray-900">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            aria-label="Close modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Description */}
        {description && (
          <p id="modal-description" className="text-gray-600 mb-4">
            {description}
          </p>
        )}

        {/* Content */}
        <div>{children}</div>
      </div>
    </div>
  );
};
```

### Accessible Dropdown
```typescript
// components/accessible/dropdown.tsx
import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface DropdownOption {
  value: string;
  label: string;
}

interface AccessibleDropdownProps {
  label: string;
  options: DropdownOption[];
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const AccessibleDropdown: React.FC<AccessibleDropdownProps> = ({
  label,
  options,
  value,
  onChange,
  placeholder = 'Select an option'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const selectedOption = options.find(opt => opt.value === value);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else if (selectedIndex >= 0) {
          onChange(options[selectedIndex].value);
          setIsOpen(false);
          buttonRef.current?.focus();
        }
        break;
      case 'Escape':
        setIsOpen(false);
        buttonRef.current?.focus();
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setSelectedIndex(prev => Math.min(prev + 1, options.length - 1));
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (isOpen) {
          setSelectedIndex(prev => Math.max(prev - 1, 0));
        }
        break;
    }
  };

  return (
    <div ref={dropdownRef} className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>

      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        className="w-full px-3 py-2 text-left border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby="dropdown-label"
      >
        <span className="block truncate">
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
      </button>

      {isOpen && (
        <ul
          className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto"
          role="listbox"
          aria-labelledby="dropdown-label"
        >
          {options.map((option, index) => (
            <li
              key={option.value}
              role="option"
              aria-selected={option.value === value}
              className={`
                px-3 py-2 cursor-pointer
                ${index === selectedIndex ? 'bg-blue-100' : ''}
                ${option.value === value ? 'bg-blue-50 font-medium' : ''}
                hover:bg-gray-100
              `}
              onClick={() => {
                onChange(option.value);
                setIsOpen(false);
                buttonRef.current?.focus();
              }}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

### Accessible Tabs
```typescript
// components/accessible/tabs.tsx
import React, { useState, useRef, useEffect } from 'react';

interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface AccessibleTabsProps {
  tabs: Tab[];
  defaultTab?: string;
}

export const AccessibleTabs: React.FC<AccessibleTabsProps> = ({
  tabs,
  defaultTab
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0].id);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const activeIndex = tabs.findIndex(tab => tab.id === activeTab);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowLeft':
        e.preventDefault();
        const prevIndex = index === 0 ? tabs.length - 1 : index - 1;
        setActiveTab(tabs[prevIndex].id);
        tabRefs.current[prevIndex]?.focus();
        break;
      case 'ArrowRight':
        e.preventDefault();
        const nextIndex = index === tabs.length - 1 ? 0 : index + 1;
        setActiveTab(tabs[nextIndex].id);
        tabRefs.current[nextIndex]?.focus();
        break;
      case 'Home':
        e.preventDefault();
        setActiveTab(tabs[0].id);
        tabRefs.current[0]?.focus();
        break;
      case 'End':
        e.preventDefault();
        const lastIndex = tabs.length - 1;
        setActiveTab(tabs[lastIndex].id);
        tabRefs.current[lastIndex]?.focus();
        break;
    }
  };

  return (
    <div>
      {/* Tab List */}
      <div
        role="tablist"
        aria-label="Content tabs"
        className="flex border-b border-gray-200"
      >
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            ref={el => tabRefs.current[index] = el}
            role="tab"
            aria-selected={tab.id === activeTab}
            aria-controls={`tabpanel-${tab.id}`}
            id={`tab-${tab.id}`}
            tabIndex={tab.id === activeTab ? 0 : -1}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            className={`
              px-4 py-2 font-medium transition-colors
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              ${tab.id === activeTab
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      {tabs.map(tab => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`tabpanel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={tab.id !== activeTab}
          tabIndex={0}
          className="py-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
};
```

### Skip Navigation Link
```typescript
// components/accessible/skip-link.tsx
import React from 'react';

export const SkipLink: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="
        sr-only focus:not-sr-only
        fixed top-4 left-4 z-50
        px-4 py-2 bg-blue-600 text-white rounded
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
      "
    >
      Skip to main content
    </a>
  );
};

// Usage: Place at the top of your app
// Then add id="main-content" to your main content area
```

## Accessibility Utilities

### Focus Trap Hook
```typescript
// hooks/use-focus-trap.ts
import { useEffect, useRef } from 'react';

export function useFocusTrap<T extends HTMLElement>() {
  const ref = useRef<T>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const focusableElements = element.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement?.focus();
          e.preventDefault();
        }
      }
    };

    element.addEventListener('keydown', handleKeyDown);
    firstElement?.focus();

    return () => element.removeEventListener('keydown', handleKeyDown);
  }, []);

  return ref;
}
```

### Screen Reader Only CSS
```css
/* Add to your global styles */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.sr-only:focus,
.sr-only:active {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

## WCAG Checklist

### Level A (Minimum)
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only visual means
- [ ] No keyboard traps
- [ ] Page has a title
- [ ] Focus order is logical
- [ ] Link purpose is clear from text

### Level AA (Recommended)
- [ ] Color contrast ratio 4.5:1 for normal text
- [ ] Color contrast ratio 3:1 for large text
- [ ] Text can be resized to 200%
- [ ] Images of text are avoided
- [ ] Multiple ways to navigate
- [ ] Headings and labels are descriptive
- [ ] Focus is visible
- [ ] All functionality available via keyboard

## Best Practices
1. **Semantic HTML**: Use correct elements (button, nav, main, article)
2. **ARIA Labels**: Add descriptive labels for screen readers
3. **Keyboard Navigation**: Ensure all interactive elements are keyboard accessible
4. **Focus Management**: Maintain focus in modals and dialogs
5. **Color Contrast**: Ensure sufficient contrast for readability
6. **Alt Text**: Provide meaningful alternative text for images
7. **Labels**: Associate form controls with their labels
8. **Progress Indicators**: Announce loading states to screen readers
9. **Error Handling**: Provide clear error messages and recovery
10. **Consistent Navigation**: Maintain consistent navigation structure

## Testing Guidelines
- Test with screen readers (NVDA, JAWS, VoiceOver)
- Navigate using keyboard only
- Verify color contrast ratios
- Test with reduced motion settings
- Validate ARIA attributes
- Check focus order and visibility
- Test with zoom and high contrast modes

## Output Checklist
- [ ] Semantic HTML elements used appropriately
- [ ] ARIA attributes included for complex components
- [ ] Keyboard navigation supported
- [ ] Focus management implemented
- [ ] Color contrast meets WCAG standards
- [ ] Form controls properly labeled
- [ ] Screen reader announcements provided
- [ ] Skip links included for navigation
- [ ] Alternative text for images
- [ ] TypeScript interfaces for accessibility props