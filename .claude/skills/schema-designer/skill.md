name: schema-designer
description: |
  Generates normalized database schemas with proper table structures, field types, constraints,
  and relationships. Follows database normalization principles, ensures data integrity with
  primary/foreign keys, and creates schemas optimized for multi-tenant applications.
  This skill should be used when users need to design SQLModel database schemas for
  PostgreSQL/Neon databases with proper normalization and multi-tenancy support.
---

# Schema Designer

Generates normalized database schemas for PostgreSQL/Neon databases using SQLModel.

## What This Skill Does
- Designs normalized database schemas (1NF, 2NF, 3NF)
- Defines table structures with proper field types
- Establishes primary keys and unique constraints
- Plans foreign key relationships between tables
- Implements multi-tenant isolation via user_id
- Adds timestamp fields (created_at, updated_at)
- Ensures data integrity with NOT NULL constraints
- Creates optimized schemas for multi-tenant applications

## What This Skill Does NOT Do
- Generate actual migration files (use database-migrator)
- Create indexes (use index-optimizer)
- Write query logic (use query-builder)
- Seed test data (use seed-data-creator)
- Deploy schemas to production databases

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing database models, naming conventions, current schema patterns |
| **Conversation** | Business entities, data relationships, required fields, constraints |
| **Skill References** | Database normalization rules, PostgreSQL best practices, multi-tenant patterns from `references/` |
| **User Guidelines** | Project-specific field naming, data types standards |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S requirements:

1. **Entities**: "What are the main entities/tables you need (e.g., users, tasks, projects)?"
2. **Relationships**: "How are these entities related (one-to-many, many-to-many)?"
3. **Required Fields**: "What are the essential fields for each entity?"
4. **Constraints**: "Are there any unique constraints or special validation rules?"
5. **Multi-tenancy**: "Do you need user isolation and access control for multi-tenant support?"

---

## Implementation Workflow

1. **Analyze Requirements**
   - Identify all entities from user requirements
   - Map entity relationships (1:1, 1:N, N:M)
   - List required vs optional fields

2. **Design Schema**
   - Apply normalization principles
   - Define primary keys (auto-increment or UUID)
   - Add user_id for multi-tenant isolation
   - Include timestamp fields

3. **Define Constraints**
   - NOT NULL for required fields
   - UNIQUE for fields like email
   - DEFAULT values where applicable
   - CHECK constraints for validation

4. **Generate SQLModel Classes**
   - Create table models with proper types
   - Add Field() configurations
   - Document relationships (will be mapped later)

---

## Schema Design Template

### Basic Entity Schema
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task entity for todo application
    Normalized schema with multi-tenant isolation
    """
    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Multi-tenant isolation
    user_id: str = Field(foreign_key="user.id", index=True)

    # Required fields
    title: str = Field(max_length=200, nullable=False)

    # Optional fields
    description: Optional[str] = Field(default=None, max_length=1000)

    # Status fields
    completed: bool = Field(default=False)

    # Timestamps (auto-managed)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Entity with Relationships
```python
class User(SQLModel, table=True):
    """User account entity"""
    id: str = Field(primary_key=True)  # From Better Auth
    email: str = Field(unique=True, index=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Project(SQLModel, table=True):
    """Project entity with user relationship"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    """Task entity with user and project relationships"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    project_id: Optional[int] = Field(foreign_key="project.id", index=True)
    title: str = Field(max_length=200)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Normalization Guidelines

### 1st Normal Form (1NF)
- Atomic values only (no arrays/lists in columns)
- Each column has a unique name
- Each row is unique (has primary key)

### 2nd Normal Form (2NF)
- Meets 1NF requirements
- All non-key attributes depend on entire primary key
- No partial dependencies

### 3rd Normal Form (3NF)
- Meets 2NF requirements
- No transitive dependencies
- Non-key attributes depend only on primary key

---

## Field Type Best Practices

| Data Type | Use For | SQLModel Type |
|-----------|---------|---------------|
| **Integer** | IDs, counts, quantities | `int` |
| **String** | Names, titles, short text | `str` with `max_length` |
| **Text** | Long descriptions | `Optional[str]` |
| **Boolean** | Yes/No flags | `bool` |
| **DateTime** | Timestamps | `datetime` |
| **UUID** | Unique identifiers | `str` (UUID string) |
| **Enum** | Fixed choices | `str` with validation |

---

## Multi-Tenant Schema Pattern

Every user-owned table MUST include:
```python
user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
```

This ensures:
- Data isolation between users
- Fast queries with indexed user_id
- Referential integrity with foreign key

---

## Best Practices from References

For detailed database design patterns and advanced SQLModel usage, refer to:
- `references/normalization-rules.md` - Detailed normalization guidelines
- `references/sqlmodel-patterns.md` - Advanced SQLModel field configurations
- `references/multi-tenant-strategies.md` - Multi-tenancy implementation patterns
- `references/postgresql-optimization.md` - PostgreSQL-specific optimizations

---

## Output Checklist

Before delivering schema design:
- [ ] All entities identified and modeled
- [ ] Primary keys defined (auto-increment or explicit)
- [ ] user_id added to all user-owned tables
- [ ] Foreign keys planned (relationships documented)
- [ ] Required fields marked as NOT NULL
- [ ] Timestamp fields (created_at, updated_at) added
- [ ] Field constraints specified (max_length, unique, default)
- [ ] Schema follows normalization principles
- [ ] Multi-tenant isolation implemented where needed
- [ ] Proper indexing strategy applied
- [ ] Security considerations addressed (data isolation)