---
name: sqlmodel-schema-builder
description: |
  Designs and generates SQLModel database models with proper field types, constraints, relationships (foreign keys),
  and table configurations. Creates normalized schemas following database best practices including primary keys,
  nullable fields, default values, and relationship definitions (one-to-many, many-to-one).
---

# SQLModel Schema Builder

Designs and generates SQLModel database models with proper field types, constraints, relationships, and table configurations.

## What This Skill Does
- Creates normalized SQLModel schemas following database best practices
- Defines proper field types, constraints, and default values
- Implements foreign key relationships with appropriate configurations
- Creates relationship attributes with back_populates for bidirectional access
- Adds indexes on frequently queried fields and foreign keys
- Includes timestamps (created_at, updated_at) when appropriate
- Applies unique constraints where needed

## What This Skill Does NOT Do
- Generate database migrations (handled by Alembic or similar tools)
- Create the actual database tables (requires session execution)
- Implement business logic beyond schema design
- Handle complex custom validators (though basic ones are shown)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing models, naming conventions, current database patterns to integrate with |
| **Conversation** | Entity relationships, field requirements, indexing needs, constraint specifications |
| **Skill References** | Domain patterns from `references/` (SQLModel best practices, field constraints, relationship patterns) |
| **User Guidelines** | Project-specific conventions, naming standards, existing model patterns |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **Entity Requirements**: "What entities and relationships do you need to model?"
2. **Indexing Needs**: "Which fields will be frequently queried and need indexing?"
3. **Constraint Specifications**: "Are there any unique constraints or specific field validations needed?"

---

## Implementation Workflow

1. **Analyze Entity Requirements**
   - Identify entities and their attributes
   - Determine relationships (one-to-many, many-to-one, many-to-many)
   - Identify primary keys and unique constraints

2. **Design Field Types and Constraints**
   - Select appropriate Python/SQL types for each field
   - Add indexes on frequently queried fields and foreign keys
   - Set default values and nullability appropriately

3. **Implement Relationships**
   - Define foreign key fields with proper references
   - Create bidirectional relationship attributes with back_populates
   - Configure cascade options if needed

4. **Apply Best Practices**
   - Add timestamps where appropriate (created_at, updated_at)
   - Ensure proper indexing strategy
   - Apply unique constraints where needed

---

## Schema Design Patterns

### Basic Model with Primary Key

```python
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # Use str for UUID or int for auto-increment
    email: str = Field(unique=True, index=True)  # Unique and indexed
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Model with Foreign Keys and Relationships

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to child entities
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)  # Auto-increment integer ID
    user_id: str = Field(foreign_key="user.id", index=True)  # Foreign key with index
    title: str = Field(max_length=200)
    description: str | None = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to parent entity
    user: User = Relationship(back_populates="tasks")
```

### Advanced Field Constraints

```python
from decimal import Decimal
from sqlmodel import Field
from typing import Optional

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100, index=True)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    sku: str = Field(unique=True, min_length=3, max_length=50)  # Unique constraint
    stock_quantity: int = Field(default=0, ge=0)  # Greater than or equal to 0
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### UUID Primary Keys

```python
import uuid
from sqlmodel import Field
from typing import Optional

class Session(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    token: str = Field(unique=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Many-to-Many Relationship with Join Table

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List

# Association table for many-to-many relationship
class TeamHero(SQLModel, table=True):
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: Optional[int] = Field(default=None, foreign_key="hero.id", primary_key=True)

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    # Many-to-many relationship via association table
    heroes: List["Hero"] = Relationship(
        back_populates="teams",
        link_model=TeamHero
    )

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str

    # Many-to-many relationship via association table
    teams: List[Team] = Relationship(
        back_populates="heroes",
        link_model=TeamHero
    )
```

---

## Field Configuration Options

### Primary Keys
- Use `int | None = Field(default=None, primary_key=True)` for auto-increment integers
- Use `str = Field(primary_key=True)` for string IDs (UUIDs, custom IDs)
- Use `uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)` for UUIDs

### Foreign Keys
- Always add `index=True` to foreign key fields for performance
- Use lowercase table name with `.id` format: `foreign_key="user.id"`
- Consider `ondelete="RESTRICT"` to prevent deletion if related records exist

### Indexes
- Add `index=True` to fields used in WHERE clauses frequently
- Foreign keys should typically have indexes
- Text search fields benefit from indexing

### Constraints
- Use `unique=True` for fields that must be unique across the table
- Use `min_length` and `max_length` for string fields
- Use `ge`, `le`, `gt`, `lt` for numeric validation
- Use `max_digits` and `decimal_places` for Decimal fields

---

## Relationship Patterns

### One-to-Many / Many-to-One
```python
# Parent model
class User(SQLModel, table=True):
    # ...
    children: List["Child"] = Relationship(back_populates="parent")

# Child model
class Child(SQLModel, table=True):
    # ...
    parent_id: int = Field(foreign_key="user.id", index=True)
    parent: User = Relationship(back_populates="children")
```

### Many-to-Many (via Association Table)
```python
# Association table
class ModelA_ModelB(SQLModel, table=True):
    model_a_id: int = Field(foreign_key="modela.id", primary_key=True)
    model_b_id: int = Field(foreign_key="modelb.id", primary_key=True)

# Model A
class ModelA(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    model_bs: List["ModelB"] = Relationship(
        back_populates="model_as",
        link_model=ModelA_ModelB
    )

# Model B
class ModelB(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    model_as: List[ModelA] = Relationship(
        back_populates="model_bs",
        link_model=ModelA_ModelB
    )
```

---

## Best Practices

### Primary Keys
- Always include a primary key in each table
- Use auto-increment integers for simple IDs unless you have a specific need for UUIDs
- Consider UUIDs for distributed systems or when privacy of IDs matters

### Indexing Strategy
- Index foreign keys (essential for JOIN performance)
- Index fields used in WHERE clauses frequently
- Index fields used for sorting (ORDER BY)
- Be cautious with over-indexing (impacts INSERT/UPDATE performance)

### Field Naming
- Use snake_case for database columns
- Use descriptive names that clearly indicate the field's purpose
- Follow consistent naming patterns across models

### Timestamps
- Include `created_at` with `default_factory=datetime.utcnow`
- Include `updated_at` with `default_factory=datetime.utcnow` (updated manually in business logic)
- Consider using timezone-aware datetimes if needed

### Relationships
- Always define bidirectional relationships with `back_populates`
- Use string forward references (`"ModelName"`) to avoid circular import issues
- Consider lazy loading options for performance in large datasets

---

## Output Checklist

Before delivering generated schema, verify:
- [ ] All models have proper primary keys defined
- [ ] Foreign key relationships are properly configured with indexes
- [ ] Bidirectional relationships have back_populates defined
- [ ] Appropriate indexes are added to frequently queried fields
- [ ] Field constraints (unique, length, etc.) are properly applied
- [ ] Default values and factories are correctly specified
- [ ] Timestamp fields (created_at, updated_at) are included where appropriate
- [ ] Many-to-many relationships use proper association tables if needed

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/field-constraints.md` | When configuring field validations and constraints |
| `references/relationship-patterns.md` | When implementing complex relationship structures |
| `references/best-practices.md` | When optimizing schema for performance and maintainability |