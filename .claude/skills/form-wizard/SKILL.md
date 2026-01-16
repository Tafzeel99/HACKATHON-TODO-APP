---
name: form-wizard
description: "Create forms with validation, error handling, and submission states. Use when user needs form components or validation logic."
version: "1.0.0"
---

# Form Wizard Skill

## When to Use This Skill
- User asks to "create a form" or "add validation"
- User mentions "submit", "input validation", or "error handling"
- User needs multi-step forms or form state management
- User wants type-safe form handling

## Procedure
1. **Define schema**: Create validation rules for each field
2. **Handle state**: Track form values, errors, touched fields
3. **Validate on blur**: Check individual fields when user leaves them
4. **Validate on submit**: Check entire form before submission
5. **Show errors**: Display field-specific and form-level errors
6. **Handle submission**: Loading states, success/error feedback

## Output Format
```typescript
// lib/form-validation.ts
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  validate?: (value: any) => boolean | string;
}

export interface FormSchema {
  [key: string]: ValidationRule;
}

// hooks/use-form.ts
export function useForm(schema: FormSchema, onSubmit: Function) {
  // Implementation
}
```

## Quality Criteria
- **Type Safety**: Full TypeScript support for form values
- **User Experience**: Validate on blur, show errors clearly
- **Accessibility**: Proper ARIA labels and error announcements
- **Performance**: Debounced validation for expensive checks
- **Flexibility**: Support custom validation rules

## Form Validation Library
```typescript
// lib/form-validation.ts

export interface ValidationRule {
  required?: boolean | string;
  minLength?: { value: number; message: string };
  maxLength?: { value: number; message: string };
  pattern?: { value: RegExp; message: string };
  min?: { value: number; message: string };
  max?: { value: number; message: string };
  validate?: (value: any, formValues?: any) => boolean | string;
  email?: boolean | string;
  url?: boolean | string;
}

export interface FormSchema {
  [key: string]: ValidationRule;
}

export const validateField = (
  value: any,
  rules: ValidationRule,
  formValues?: any
): string | null => {
  // Required
  if (rules.required) {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return typeof rules.required === 'string'
        ? rules.required
        : 'This field is required';
    }
  }

  // Skip other validations if empty and not required
  if (!value) return null;

  // Email
  if (rules.email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return typeof rules.email === 'string'
        ? rules.email
        : 'Please enter a valid email address';
    }
  }

  // URL
  if (rules.url) {
    try {
      new URL(value);
    } catch {
      return typeof rules.url === 'string'
        ? rules.url
        : 'Please enter a valid URL';
    }
  }

  // Min Length
  if (rules.minLength && value.length < rules.minLength.value) {
    return rules.minLength.message;
  }

  // Max Length
  if (rules.maxLength && value.length > rules.maxLength.value) {
    return rules.maxLength.message;
  }

  // Pattern
  if (rules.pattern && !rules.pattern.value.test(value)) {
    return rules.pattern.message;
  }

  // Min/Max (for numbers)
  if (rules.min !== undefined && Number(value) < rules.min.value) {
    return rules.min.message;
  }

  if (rules.max !== undefined && Number(value) > rules.max.value) {
    return rules.max.message;
  }

  // Custom validation
  if (rules.validate) {
    const result = rules.validate(value, formValues);
    if (result !== true) {
      return typeof result === 'string' ? result : 'Validation failed';
    }
  }

  return null;
};

export const validateForm = (
  values: Record<string, any>,
  schema: FormSchema
): Record<string, string> => {
  const errors: Record<string, string> = {};

  Object.keys(schema).forEach((field) => {
    const error = validateField(values[field], schema[field], values);
    if (error) {
      errors[field] = error;
    }
  });

  return errors;
};
```

## useForm Hook
```typescript
// hooks/use-form.ts
import { useState } from 'react';
import { FormSchema, validateField, validateForm } from '@/lib/form-validation';

interface UseFormOptions<T> {
  initialValues: T;
  schema: FormSchema;
  onSubmit: (values: T) => Promise<void> | void;
}

export function useForm<T extends Record<string, any>>({
  initialValues,
  schema,
  onSubmit
}: UseFormOptions<T>) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleChange = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    setSubmitError(null);
    setSubmitSuccess(false);

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleBlur = (name: string) => {
    setTouched(prev => ({ ...prev, [name]: true }));

    // Validate field on blur
    if (schema[name]) {
      const error = validateField(values[name], schema[name], values);
      if (error) {
        setErrors(prev => ({ ...prev, [name]: error }));
      }
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    // Validate all fields
    const newErrors = validateForm(values, schema);
    setErrors(newErrors);

    // Mark all fields as touched
    const allTouched = Object.keys(schema).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {} as Record<string, boolean>);
    setTouched(allTouched);

    // If there are errors, don't submit
    if (Object.keys(newErrors).length > 0) {
      setIsSubmitting(false);
      return;
    }

    try {
      await onSubmit(values);
      setSubmitSuccess(true);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const reset = (newValues?: T) => {
    setValues(newValues || initialValues);
    setErrors({});
    setTouched({});
    setSubmitError(null);
    setSubmitSuccess(false);
  };

  const setFieldValue = (name: string, value: any) => {
    handleChange(name, value);
  };

  const setFieldError = (name: string, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  return {
    values,
    errors,
    touched,
    isSubmitting,
    submitError,
    submitSuccess,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
    setFieldValue,
    setFieldError
  };
}
```

## Form Component Helpers
```typescript
// components/forms/form-field.tsx
import React from 'react';
import { Input } from '@/components/ui/input';

interface FormFieldProps {
  name: string;
  label: string;
  type?: string;
  value: any;
  error?: string;
  touched?: boolean;
  onChange: (name: string, value: any) => void;
  onBlur: (name: string) => void;
  placeholder?: string;
  helperText?: string;
  required?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({
  name,
  label,
  type = 'text',
  value,
  error,
  touched,
  onChange,
  onBlur,
  placeholder,
  helperText,
  required
}) => {
  return (
    <Input
      id={name}
      name={name}
      type={type}
      label={label}
      value={value}
      error={touched ? error : undefined}
      helperText={!touched || !error ? helperText : undefined}
      onChange={(e) => onChange(name, e.target.value)}
      onBlur={() => onBlur(name)}
      placeholder={placeholder}
      required={required}
    />
  );
};
```

## Multi-Step Form Hook
```typescript
// hooks/use-multi-step-form.ts
import { useState } from 'react';

export function useMultiStepForm(steps: number) {
  const [currentStep, setCurrentStep] = useState(0);

  const next = () => {
    setCurrentStep((prev) => Math.min(prev + 1, steps - 1));
  };

  const prev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const goTo = (step: number) => {
    setCurrentStep(Math.min(Math.max(step, 0), steps - 1));
  };

  const reset = () => {
    setCurrentStep(0);
  };

  return {
    currentStep,
    isFirstStep: currentStep === 0,
    isLastStep: currentStep === steps - 1,
    progress: ((currentStep + 1) / steps) * 100,
    next,
    prev,
    goTo,
    reset
  };
}
```

## Usage Examples

### Basic Form
```typescript
import { useForm } from '@/hooks/use-form';
import { FormField } from '@/components/forms/form-field';
import { Button } from '@/components/ui/button';

function LoginForm() {
  const { values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit } = useForm({
    initialValues: {
      email: '',
      password: ''
    },
    schema: {
      email: {
        required: true,
        email: true
      },
      password: {
        required: 'Password is required',
        minLength: { value: 8, message: 'Password must be at least 8 characters' }
      }
    },
    onSubmit: async (values) => {
      // API call
      await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify(values)
      });
    }
  });

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormField
        name="email"
        label="Email"
        type="email"
        value={values.email}
        error={errors.email}
        touched={touched.email}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder="you@example.com"
      />

      <FormField
        name="password"
        label="Password"
        type="password"
        value={values.password}
        error={errors.password}
        touched={touched.password}
        onChange={handleChange}
        onBlur={handleBlur}
      />

      <Button type="submit" isLoading={isSubmitting} className="w-full">
        Log In
      </Button>
    </form>
  );
}
```

### Multi-Step Form
```typescript
import { useForm } from '@/hooks/use-form';
import { useMultiStepForm } from '@/hooks/use-multi-step-form';
import { FormField } from '@/components/forms/form-field';
import { Button } from '@/components/ui/button';

function RegistrationForm() {
  const { currentStep, isFirstStep, isLastStep, next, prev, progress } = useMultiStepForm(3);

  const { values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit } = useForm({
    initialValues: {
      // Step 1
      firstName: '',
      lastName: '',
      email: '',
      // Step 2
      company: '',
      role: '',
      // Step 3
      password: '',
      confirmPassword: ''
    },
    schema: {
      firstName: { required: true },
      lastName: { required: true },
      email: { required: true, email: true },
      company: { required: true },
      role: { required: true },
      password: {
        required: true,
        minLength: { value: 8, message: 'Password must be at least 8 characters' }
      },
      confirmPassword: {
        required: true,
        validate: (value, formValues) => {
          return value === formValues.password || 'Passwords do not match';
        }
      }
    },
    onSubmit: async (values) => {
      await fetch('/api/register', {
        method: 'POST',
        body: JSON.stringify(values)
      });
    }
  });

  const handleNext = () => {
    // Validate current step fields before proceeding
    const currentStepFields = getCurrentStepFields();
    const hasErrors = currentStepFields.some(field => errors[field]);

    if (!hasErrors) {
      next();
    }
  };

  const getCurrentStepFields = () => {
    switch (currentStep) {
      case 0: return ['firstName', 'lastName', 'email'];
      case 1: return ['company', 'role'];
      case 2: return ['password', 'confirmPassword'];
      default: return []
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="h-2 bg-gray-200 rounded-full">
          <div
            className="h-2 bg-blue-600 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-sm text-gray-600 mt-2">Step {currentStep + 1} of 3</p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Step 1: Personal Info */}
        {currentStep === 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Personal Information</h2>
            <FormField
              name="firstName"
              label="First Name"
              value={values.firstName}
              error={errors.firstName}
              touched={touched.firstName}
              onChange={handleChange}
              onBlur={handleBlur}
            />
            <FormField
              name="lastName"
              label="Last Name"
              value={values.lastName}
              error={errors.lastName}
              touched={touched.lastName}
              onChange={handleChange}
              onBlur={handleBlur}
            />
            <FormField
              name="email"
              label="Email"
              type="email"
              value={values.email}
              error={errors.email}
              touched={touched.email}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </div>
        )}

        {/* Step 2: Company Info */}
        {currentStep === 1 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Company Information</h2>
            <FormField
              name="company"
              label="Company"
              value={values.company}
              error={errors.company}
              touched={touched.company}
              onChange={handleChange}
              onBlur={handleBlur}
            />
            <FormField
              name="role"
              label="Role"
              value={values.role}
              error={errors.role}
              touched={touched.role}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </div>
        )}

        {/* Step 3: Password */}
        {currentStep === 2 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Create Password</h2>
            <FormField
              name="password"
              label="Password"
              type="password"
              value={values.password}
              error={errors.password}
              touched={touched.password}
              onChange={handleChange}
              onBlur={handleBlur}
            />
            <FormField
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              value={values.confirmPassword}
              error={errors.confirmPassword}
              touched={touched.confirmPassword}
              onChange={handleChange}
              onBlur={handleBlur}
            />
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button
            type="button"
            variant="outline"
            onClick={prev}
            disabled={isFirstStep}
          >
            Previous
          </Button>

          {isLastStep ? (
            <Button type="submit" isLoading={isSubmitting}>
              Submit
            </Button>
          ) : (
            <Button type="button" onClick={handleNext}>
              Next
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
```

## Best Practices
1. **Validate on Blur**: Check fields when users leave them
2. **Show Errors After Touch**: Don't show errors until user interacts
3. **Clear Errors on Type**: Remove errors as user fixes them
4. **Loading States**: Disable submit button during submission
5. **Success Feedback**: Show success message after successful submission
6. **Error Recovery**: Allow users to easily fix validation errors

## Testing Guidelines
- Verify all validation rules work correctly
- Test form submission with valid and invalid data
- Ensure proper error messaging
- Check accessibility attributes
- Verify keyboard navigation works
- Test multi-step forms for proper progression

## Output Checklist
- [ ] Validation rules defined for all fields
- [ ] Form state managed properly
- [ ] Error messages displayed clearly
- [ ] Loading states implemented
- [ ] Accessibility features included
- [ ] Multi-step form support (if needed)
- [ ] TypeScript interfaces provided
- [ ] Proper event handling
- [ ] Success/error feedback included