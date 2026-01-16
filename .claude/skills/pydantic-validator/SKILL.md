---
name: pydantic-validator
description: |
  Creates type-safe Pydantic models for API request validation and response serialization.
  Defines schemas with field validators, custom error messages, computed fields, and ensures
  data consistency between frontend TypeScript and backend Python. Implements input sanitization,
  format validation, and automatic OpenAPI documentation generation.
---

# Pydantic Validator

Creates type-safe Pydantic models for API request validation and response serialization.

## What This Skill Does
- Creates type-safe Pydantic models for API request/response validation
- Defines field validators with custom error messages
- Implements computed fields for derived values
- Ensures data consistency between frontend and backend
- Implements input sanitization and format validation
- Generates automatic OpenAPI documentation from models
- Creates request/response schemas for different use cases (Create, Update, Read)

## What This Skill Does NOT Do
- Generate database models (handled by SQLModel or other ORMs)
- Create the actual API endpoints (handled by FastAPI or other frameworks)
- Implement business logic beyond data validation
- Handle complex business rule validation (though basic validation is included)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing Pydantic models, naming conventions, validation patterns to integrate with |
| **Conversation** | API endpoint requirements, field constraints, validation rules, custom error message needs |
| **Skill References** | Domain patterns from `references/` (validation patterns, computed fields, error handling) |
| **User Guidelines** | Project-specific conventions, type safety requirements, serialization needs |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **API Requirements**: "What are the specific API endpoint requirements and data structures?"
2. **Validation Rules**: "What custom validation rules or constraints are needed?"
3. **Error Handling**: "What custom error messages or error handling patterns are required?"

---

## Implementation Workflow

1. **Analyze API Requirements**
   - Identify request/response schemas needed
   - Determine field types and constraints
   - Identify validation rules and requirements

2. **Design Pydantic Models**
   - Create request schemas (Create, Update)
   - Create response schemas (Read)
   - Define field types with appropriate constraints

3. **Implement Validation Logic**
   - Add field validators for custom validation
   - Create computed fields for derived values
   - Implement custom error messages

4. **Apply Best Practices**
   - Ensure type safety with proper type hints
   - Follow consistent naming conventions
   - Optimize for OpenAPI documentation generation

---

## Schema Design Patterns

### Basic Request/Response Models

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request schema for creating a resource
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: str = Field(default="medium", regex=r"^(low|medium|high)$")

# Request schema for updating a resource
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, regex=r"^(low|medium|high)$")

# Response schema for reading a resource
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    completed: bool = False
    created_at: datetime
    updated_at: datetime
```

### Field Validation with Custom Validators

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UserCreate(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    age: int = Field(..., ge=0, le=150, description="User's age")
    username: str = Field(..., min_length=3, max_length=50, regex=r"^[a-zA-Z0-9_]+$")

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @field_validator('age')
    @classmethod
    def validate_age_range(cls, v: int) -> int:
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

### Computed Fields

```python
from pydantic import BaseModel, computed_field, Field
from typing import Optional

class Product(BaseModel):
    id: int
    name: str
    price: float = Field(..., gt=0)
    discount_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    quantity: int = Field(default=0, ge=0)

    @computed_field
    @property
    def discounted_price(self) -> float:
        """Computed field for discounted price"""
        return round(self.price * (1 - self.discount_percent / 100), 2)

    @computed_field
    @property
    def in_stock(self) -> bool:
        """Computed field to check if product is in stock"""
        return self.quantity > 0

    @computed_field
    @property
    def total_value(self) -> float:
        """Computed field for total inventory value"""
        return self.quantity * self.price
```

### Custom Error Messages

```python
from pydantic_core import PydanticCustomError
from pydantic import BaseModel, Field, field_validator

class Order(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    customer_email: str

    @field_validator('quantity')
    @classmethod
    def validate_minimum_order(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        if v > 1000:
            raise PydanticCustomError(
                'excessive_quantity',
                'Order quantity {requested} exceeds maximum allowed ({max_allowed})',
                {'requested': v, 'max_allowed': 1000}
            )
        return v

    @field_validator('customer_email')
    @classmethod
    def validate_corporate_email(cls, v: str) -> str:
        if '@' not in v:
            raise PydanticCustomError(
                'invalid_email_format',
                'Email {email} is not in a valid format',
                {'email': v}
            )
        return v
```

### Advanced Validation with Model Validators

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional

class Booking(BaseModel):
    start_date: datetime
    end_date: datetime
    room_capacity: int = Field(..., gt=0)
    attendees: int = Field(..., ge=0)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError('End date must be after start date')
        return self

    @model_validator(mode='after')
    def validate_capacity(self):
        if self.attendees > self.room_capacity:
            raise ValueError(f'Number of attendees ({self.attendees}) exceeds room capacity ({self.room_capacity})')
        return self

    @field_validator('attendees')
    @classmethod
    def validate_attendees_count(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Attendees count cannot be negative')
        return v
```

---

## Validation Patterns

### Multiple Field Validation
```python
class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode='after')
    def validate_date_range(self):
        if self.start_date >= self.end_date:
            raise ValueError('End date must be after start date')
        return self
```

### Conditional Validation
```python
class User(BaseModel):
    is_company: bool
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @model_validator(mode='after')
    def validate_name_fields(self):
        if self.is_company:
            if not self.company_name:
                raise ValueError('Company name is required for company accounts')
        else:
            if not self.first_name or not self.last_name:
                raise ValueError('First and last name are required for personal accounts')
        return self
```

### Cross-field Validation
```python
class PasswordReset(BaseModel):
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def validate_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
```

---

## Type Safety and Frontend Consistency

### Type Hints for Frontend Generation
```python
from typing import List, Optional
from pydantic import BaseModel, Field

class ApiResponse[T](BaseModel):
    """Generic response wrapper for API responses"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

class Task(BaseModel):
    id: int
    title: str
    completed: bool

# This enables proper TypeScript generation for frontend
response: ApiResponse[List[Task]] = ApiResponse(
    success=True,
    data=[Task(id=1, title="Sample task", completed=False)]
)
```

### Serialization Configuration
```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: int
    email: str
    password_hash: str  # This should be excluded from responses
    created_at: datetime

    model_config = ConfigDict(
        # Exclude sensitive fields from serialization
        json_encoders={datetime: lambda dt: dt.isoformat()},
        # Allow extra fields during validation but exclude from serialization
        extra='ignore',
        # Use aliases for API field names
        populate_by_name=True
    )

    def model_dump(self, exclude_password=True, **kwargs):
        """Custom serialization method to exclude sensitive fields"""
        exclude_set = {'password_hash'}
        if exclude_password:
            exclude_set.add('password_hash')
        return super().model_dump(exclude=exclude_set, **kwargs)
```

---

## Best Practices

### Field Definitions
- Use `Field(...)` for required fields
- Use `Field(default=value)` for optional fields with defaults
- Use `Field(None, ...)` for optional fields with constraints
- Always add descriptions for API documentation

### Validation Approach
- Use `@field_validator` for single-field validation
- Use `@model_validator` for cross-field validation
- Use `PydanticCustomError` for detailed error messages
- Implement validation in the order of complexity (simplest first)

### Error Handling
- Provide clear, actionable error messages
- Use custom error types for specific validation failures
- Include context in error messages when helpful
- Group related validation logic together

### Performance
- Avoid expensive validation in hot paths
- Cache computed fields when appropriate
- Use appropriate data types for validation efficiency

---

## Output Checklist

Before delivering generated Pydantic models, verify:
- [ ] All models inherit from BaseModel
- [ ] Proper type hints are used throughout
- [ ] Required fields are marked with `Field(...)`
- [ ] Optional fields have appropriate defaults or None values
- [ ] Field constraints (min_length, max_length, gt, lt, etc.) are properly applied
- [ ] Custom validators are implemented where needed
- [ ] Computed fields are properly defined with `@computed_field`
- [ ] Error messages are clear and actionable
- [ ] Model configuration is set for proper serialization
- [ ] Frontend/backend type consistency is maintained

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/validation-patterns.md` | When implementing complex validation logic |
| `references/error-handling.md` | When creating custom error messages and handling |
| `references/type-safety.md` | When ensuring type consistency between frontend and backend |