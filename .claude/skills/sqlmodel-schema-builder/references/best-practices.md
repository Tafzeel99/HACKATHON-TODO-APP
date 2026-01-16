# SQLModel Schema Best Practices

This guide covers best practices for designing SQLModel schemas for optimal performance, maintainability, and data integrity.

## Schema Design Principles

### Normalization
- Follow database normalization rules to eliminate redundancy
- Separate concerns into distinct entities
- Use foreign keys to establish relationships between entities
- Avoid storing denormalized data unless for performance optimization

### Single Responsibility
- Each model should represent a single entity or concept
- Keep models focused on their core responsibilities
- Avoid mixing unrelated data in a single model

## Primary Key Strategies

### Auto-Increment vs UUID
```python
# For simple applications where ID exposure is not a concern
class SimpleModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

# For distributed systems or when privacy of IDs matters
import uuid
class SecureModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
```

### Natural vs Surrogate Keys
- Use surrogate keys (auto-increment/UUID) for primary keys
- Use natural keys as unique constraints where appropriate
- Avoid composite primary keys when possible

## Indexing Strategy

### When to Index
- Index all foreign key columns for join performance
- Index columns used in WHERE clauses frequently
- Index columns used for sorting (ORDER BY)
- Index columns used for grouping (GROUP BY)

### Indexing Best Practices
```python
class User(SQLModel, table=True):
    # Primary key - automatically indexed
    id: str = Field(primary_key=True)

    # Frequently queried fields
    email: str = Field(unique=True, index=True)  # Both unique and indexed

    # Search fields
    username: str = Field(unique=True, index=True)

    # Filter fields
    status: str = Field(default="active", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Foreign keys (always index)
    organization_id: int = Field(foreign_key="organization.id", index=True)
```

### Avoid Over-Indexing
- Each index impacts INSERT/UPDATE/DELETE performance
- Monitor query patterns and adjust indexes accordingly
- Remove unused indexes periodically

## Field Design

### Type Selection
```python
from decimal import Decimal
from datetime import datetime
from typing import Optional

class Product(SQLModel, table=True):
    # Use appropriate types for data integrity
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)  # Limit string lengths
    price: Decimal = Field(max_digits=10, decimal_places=2)  # Precise for money
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Timestamps
    is_available: bool = Field(default=True)  # Boolean flags
    quantity: int = Field(ge=0)  # Use validation constraints
    description: str | None = Field(default=None, max_length=1000)  # Optional fields
```

### Default Values
```python
from datetime import datetime
import uuid

class Record(SQLModel, table=True):
    # Static defaults
    is_active: bool = Field(default=True)
    retry_count: int = Field(default=0)

    # Dynamic defaults
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Conditional defaults
    status: str = Field(default="pending")
```

### Nullable Fields
```python
class User(SQLModel, table=True):
    # Required fields (not nullable)
    id: str = Field(primary_key=True)
    email: str  # Required field

    # Optional fields (nullable)
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = Field(default=None)  # Explicit None default
```

## Relationship Design

### Bidirectional Relationships
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str

    # Always use back_populates for bidirectional access
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)

    # Always use back_populates for bidirectional access
    user: User = Relationship(back_populates="tasks")
```

### Many-to-Many via Association Table
```python
# Association table
class UserRole(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole
    )

class Role(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    users: List[User] = Relationship(
        back_populates="roles",
        link_model=UserRole
    )
```

## Performance Considerations

### Query Optimization
```python
class BaseModel(SQLModel):
    """Base model with common fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class User(BaseModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True, index=True)

    # Efficient relationship design
    tasks: List["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "select"}  # Choose loading strategy
    )
```

### Avoid N+1 Queries
```python
# ❌ Problematic - causes N+1 queries
def get_users_with_tasks_bad(session: Session):
    users = session.exec(select(User)).all()
    for user in users:
        print(len(user.tasks))  # Each access triggers a new query!

# ✅ Better - use joins or eager loading when needed
def get_users_with_tasks_good(session: Session):
    # Use joinedload if you know you'll need the relationships
    statement = select(User).options(joinedload(User.tasks))
    users = session.exec(statement).all()
    for user in users:
        print(len(user.tasks))  # No additional query needed
```

## Security and Validation

### Input Validation
```python
class User(SQLModel, table=True):
    # Validate email format
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$')

    # Validate string lengths
    username: str = Field(min_length=3, max_length=50)

    # Validate numeric ranges
    age: int = Field(ge=0, le=150)

    # Validate specific values
    role: str = Field(regex=r'^(admin|user|moderator)$')
```

### Data Privacy
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    # Don't expose internal IDs in URLs if privacy is a concern
    # Consider using UUIDs or mapping IDs to random strings
```

## Schema Evolution

### Forward Compatibility
```python
class BaseModel(SQLModel):
    """Base model to share common fields across evolving schemas"""
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserV1(BaseModel, table=True):
    """Version 1 of User model"""
    email: str = Field(unique=True)

class UserV2(BaseModel, table=True):
    """Version 2 of User model - extends V1"""
    email: str = Field(unique=True)
    phone: str | None = Field(default=None)  # New optional field
    is_phone_verified: bool = Field(default=False)  # New field with safe default
```

### Safe Schema Changes
- Add new fields as optional (nullable) with safe defaults
- Never remove fields without proper migration
- Use database migrations for structural changes
- Maintain backward compatibility when possible

## Naming Conventions

### Database Naming
```python
class UserAccount(SQLModel, table=True):  # PascalCase for class names
    user_id: str = Field(primary_key=True)  # snake_case for field names
    email_address: str = Field(unique=True)  # Descriptive field names
    date_created: datetime = Field(default_factory=datetime.utcnow)
```

### Relationship Naming
- Use plural names for collections (e.g., `tasks: List[Task]`)
- Use singular names for single objects (e.g., `user: User`)
- Use descriptive names that indicate the relationship purpose

## Testing Considerations

### Schema Validation
```python
def test_schema_creation():
    # Test that model can be instantiated with valid data
    user = User(email="test@example.com")
    assert user.email == "test@example.com"

    # Test validation constraints
    with pytest.raises(ValidationError):
        User(email="invalid-email")  # Should fail validation
```

### Performance Testing
```python
def test_index_performance():
    # Ensure frequently queried fields are indexed
    # Test query performance with realistic data volumes
    pass
```

## Documentation and Maintenance

### Field Documentation
```python
class User(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        description="Unique identifier for the user account"
    )
    email: str = Field(
        unique=True,
        description="Primary email address used for authentication"
    )
    is_active: bool = Field(
        default=True,
        description="Indicates if the user account is active and can log in"
    )
```

Following these best practices will result in robust, performant, and maintainable SQLModel schemas that scale well with your application.