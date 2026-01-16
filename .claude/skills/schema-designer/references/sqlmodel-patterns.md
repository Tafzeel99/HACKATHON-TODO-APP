# SQLModel Field Configuration Patterns

Advanced patterns and best practices for configuring SQLModel fields.

## Primary Key Patterns

### Auto-Increment Integer IDs
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Entity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
```

### UUID Primary Keys
```python
import uuid
from sqlmodel import SQLModel, Field

class Entity(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
```

### String Primary Keys (for external IDs)
```python
class Entity(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g., from external auth system
```

## String Field Patterns

### Variable Length Strings with Limits
```python
title: str = Field(min_length=1, max_length=200)
description: Optional[str] = Field(default=None, max_length=1000)
```

### Unique Constraints
```python
email: str = Field(unique=True, max_length=100)
username: str = Field(unique=True, min_length=3, max_length=50)
```

### Regex Validation
```python
username: str = Field(regex=r'^[a-zA-Z0-9_]{3,50}$')
phone: Optional[str] = Field(default=None, regex=r'^\+?[1-9]\d{1,14}$')
```

## Numeric Field Patterns

### Integer with Range Constraints
```python
age: int = Field(ge=0, le=150)
rating: int = Field(ge=1, le=5)  # 1-5 rating
quantity: int = Field(ge=0)  # Non-negative
```

### Decimal with Precision
```python
from decimal import Decimal

price: Decimal = Field(decimal_places=2, max_digits=10)
percentage: Decimal = Field(ge=0, le=100, decimal_places=2, max_digits=5)
```

## Boolean Field Patterns

### With Default Values
```python
is_active: bool = Field(default=True)
is_verified: bool = Field(default=False)
completed: bool = Field(default=False)
```

## DateTime Field Patterns

### Automatic Timestamps
```python
from datetime import datetime

created_at: datetime = Field(default_factory=datetime.utcnow)
updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Optional Datetime
```python
due_date: Optional[datetime] = Field(default=None)
deleted_at: Optional[datetime] = Field(default=None, nullable=True)
```

## Foreign Key Patterns

### Basic Foreign Key
```python
user_id: int = Field(foreign_key="user.id", index=True)
```

### Nullable Foreign Key
```python
category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)
```

### Cascade Options (if supported by SQLModel)
```python
user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
```

## Relationship Patterns

### One-to-Many
```python
from sqlmodel import Relationship
from typing import List

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    user: User = Relationship(back_populates="tasks")
```

### Many-to-Many (through association table)
```python
# Association table
class UserProject(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    projects: List["Project"] = Relationship(
        back_populates="users",
        link_model=UserProject
    )

class Project(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    users: List[User] = Relationship(
        back_populates="projects",
        link_model=UserProject
    )
```

## Field Validation Patterns

### Custom Validators
```python
from pydantic import field_validator

class Product(SQLModel, table=True):
    name: str
    price: float

    @field_validator('price')
    @classmethod
    def validate_positive_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

### Model-Level Validation
```python
from pydantic import model_validator

class Booking(SQLModel, table=True):
    start_date: datetime
    end_date: datetime

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError('End date must be after start date')
        return self
```

## Enum Field Patterns

### String-based Enums
```python
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    status: TaskStatus = Field(default=TaskStatus.PENDING)
```

### Integer-based Enums
```python
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task(SQLModel, table=True):
    priority: Priority = Field(default=Priority.MEDIUM)
```

## Computed Field Patterns

### Read-only Computed Properties
```python
from pydantic import computed_field

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price: float
    tax_rate: float = Field(default=0.1)

    @computed_field
    @property
    def total_price(self) -> float:
        return round(self.price * (1 + self.tax_rate), 2)
```

## Security and Privacy Patterns

### Sensitive Data Handling
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password_hash: str  # Never store plain text passwords
    api_key: Optional[str] = Field(default=None, nullable=True)  # Could be encrypted

    def model_dump(self, include_sensitive=False, **kwargs):
        exclude_set = set()
        if not include_sensitive:
            exclude_set.update({'password_hash', 'api_key'})
        return super().model_dump(exclude=exclude_set, **kwargs)
```

## Multi-Tenant Field Patterns

### Required Tenant Isolation
```python
class TenantScopedModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
    # All user-specific data must have user_id
```

## Performance Optimization Patterns

### Proper Indexing
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)  # For lookups
    status: str = Field(default="active", index=True)  # For filtering
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)  # For ordering
```

### Large Text Fields
```python
class Article(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)  # Indexed by default
    content: str = Field(sa_column_kwargs={"server_default": ""})  # Large text, not indexed
```