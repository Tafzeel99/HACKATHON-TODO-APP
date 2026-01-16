# SQLModel Field Constraints Guide

This guide covers all available field constraints and options in SQLModel.

## Primary Key Configuration

### Auto-Increment Integer Primary Key
```python
from sqlmodel import Field
from typing import Optional

class Model(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
```

### String Primary Key
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # Usually for UUIDs or custom IDs
```

### UUID Primary Key
```python
import uuid
from sqlmodel import Field
from typing import Optional

class Session(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
```

## Field Constraints

### String Field Constraints
```python
class Product(SQLModel, table=True):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    sku: str = Field(regex=r"^[A-Z0-9_-]+$")  # Regular expression constraint
```

### Numeric Field Constraints
```python
from decimal import Decimal

class Item(SQLModel, table=True):
    quantity: int = Field(ge=0, le=1000)  # greater than or equal, less than or equal
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    rating: float = Field(ge=0.0, le=5.0)
```

### Boolean Field Constraints
```python
class User(SQLModel, table=True):
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
```

## Indexing Options

### Single Column Indexes
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)  # Both unique and indexed
    username: str = Field(unique=True)  # Only unique
    last_login: datetime = Field(index=True)  # Only indexed
    name: str = Field(index=True)  # Indexed for search queries
```

### Composite Indexes
```python
from sqlalchemy import Index

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    category: str = Field(index=True)
    timestamp: datetime = Field(index=True)

    __table_args__ = (Index('idx_user_category_timestamp', 'user_id', 'category', 'timestamp'),)
```

## Unique Constraints

### Single Column Unique
```python
class User(SQLModel, table=True):
    email: str = Field(unique=True)  # Email must be unique across all users
    username: str = Field(unique=True)  # Username must be unique
```

### Multi-Column Unique Constraint
```python
from sqlalchemy import UniqueConstraint

class UserPreference(SQLModel, table=True):
    user_id: str
    preference_key: str
    value: str

    __table_args__ = (UniqueConstraint('user_id', 'preference_key'),)
```

## Default Values and Factories

### Static Default Values
```python
class Task(SQLModel, table=True):
    title: str
    completed: bool = Field(default=False)
    priority: str = Field(default="normal")
    retry_count: int = Field(default=0)
```

### Dynamic Default Factories
```python
from datetime import datetime
import uuid

class Record(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    external_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

## Foreign Key Constraints

### Basic Foreign Key
```python
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")  # References user.id
```

### Foreign Key with Additional Options
```python
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(
        foreign_key="user.id",
        ondelete="CASCADE",  # Delete orders when user is deleted
        index=True  # Index for performance
    )
```

### Self-Referencing Foreign Key
```python
class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    parent_id: int | None = Field(default=None, foreign_key="category.id")  # Self-referencing
```

## Validation Patterns

### Custom Validation with Pydantic Validators
```python
from pydantic import validator

class User(SQLModel, table=True):
    email: str
    age: int

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')
        return v.lower()

    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

### Field-Level Validation
```python
from pydantic import constr, conint

class Product(SQLModel, table=True):
    # Using Pydantic constrained types
    name: constr(min_length=1, max_length=100)
    quantity: conint(ge=0, le=10000)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
```

## Field Metadata and Documentation

### Adding Documentation to Fields
```python
class User(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        description="Unique identifier for the user"
    )
    email: str = Field(
        unique=True,
        description="User's email address, used for login"
    )
    status: str = Field(
        default="active",
        description="Current status of the user account"
    )
```

### Field Comments
```python
class AuditLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    action: str = Field(sa_column_kwargs={"comment": "Type of action performed"})
    user_id: str = Field(
        foreign_key="user.id",
        sa_column_kwargs={"comment": "ID of user who performed the action"}
    )
```

## Field Nullability

### Required vs Optional Fields
```python
class Profile(SQLModel, table=True):
    # Required fields (cannot be None)
    user_id: str = Field(primary_key=True)
    display_name: str  # Required field

    # Optional fields (can be None)
    bio: str | None = None
    avatar_url: str | None = Field(default=None)
    birth_date: datetime | None = Field(default=None)
```

### Nullable with Default
```python
class Task(SQLModel, table=True):
    title: str  # Required
    description: str | None = Field(default=None)  # Optional with explicit default
    estimated_hours: float | None = Field(default=None)  # Optional numeric field
```

These patterns ensure proper schema design with appropriate constraints, validations, and performance optimizations.