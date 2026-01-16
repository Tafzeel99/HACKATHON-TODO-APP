---
name: sqlmodel-relationship-mapper
description: |
  Configures SQLModel relationships including foreign keys, one-to-many, many-to-one, and
  many-to-many associations. Implements bidirectional relationships with back_populates,
  ensures referential integrity, and optimizes relationship loading strategies.
---

# SQLModel Relationship Mapper

Configures database relationships between SQLModel entities with proper foreign keys.

## What This Skill Does
- Defines foreign key constraints between tables
- Configures one-to-many relationships
- Configures many-to-one relationships
- Sets up many-to-many associations (via junction tables)
- Implements bidirectional relationships (back_populates)
- Optimizes relationship loading (lazy vs eager)
- Ensures referential integrity with cascade options

## What This Skill Does NOT Do
- Design the initial schema (use schema-designer)
- Generate migration files (use migration-generator)
- Write query logic (use query-builder)
- Create indexes (use index-optimizer)

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing SQLModel models, current relationships, database structure |
| **Conversation** | Entity relationships, cardinality (1:1, 1:N, N:M), cascade behavior |
| **Skill References** | SQLModel relationship patterns, foreign key best practices from `references/` |
| **User Guidelines** | Project-specific relationship conventions |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S requirements:

1. **Relationship Type**: "Is this a one-to-many, many-to-one, or many-to-many relationship?"
2. **Cascade Behavior**: "What should happen when a parent record is deleted (cascade, restrict, set null)?"
3. **Bidirectional**: "Do you need to access the relationship from both sides?"

---

## Implementation Workflow

1. **Identify Relationships**
   - Map entity connections
   - Determine cardinality (1:1, 1:N, N:M)
   - Identify parent-child hierarchies

2. **Define Foreign Keys**
   - Add foreign_key fields to child tables
   - Index foreign key columns
   - Set nullable appropriately

3. **Configure Relationships**
   - Add Relationship() attributes
   - Set back_populates for bidirectional access
   - Choose loading strategy (lazy/eager)

4. **Handle Many-to-Many**
   - Create junction tables if needed
   - Link both entities through junction

---

## Relationship Patterns

### One-to-Many (User → Tasks)
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True)
    name: str

    # One user has many tasks
    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str

    # Many tasks belong to one user
    user: Optional[User] = Relationship(back_populates="tasks")
```

**Usage:**
```python
# Access user's tasks
user = session.get(User, "user123")
user_tasks = user.tasks  # List of Task objects

# Access task's user
task = session.get(Task, 1)
task_owner = task.user  # User object
```

---

### Many-to-One (Tasks → Project)
```python
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # One project has many tasks
    tasks: List["Task"] = Relationship(back_populates="project")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(foreign_key="project.id", index=True)
    title: str

    # Many tasks belong to one project
    project: Optional[Project] = Relationship(back_populates="tasks")
```

---

### Many-to-Many (Tasks ↔ Tags) via Junction Table
```python
class TaskTagLink(SQLModel, table=True):
    """Junction table for many-to-many relationship"""
    task_id: Optional[int] = Field(
        foreign_key="task.id",
        primary_key=True
    )
    tag_id: Optional[int] = Field(
        foreign_key="tag.id",
        primary_key=True
    )


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    # Many tasks can have many tags
    tags: List["Tag"] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    # Many tags can be on many tasks
    tasks: List[Task] = Relationship(
        back_populates="tags",
        link_model=TaskTagLink
    )
```

**Usage:**
```python
# Add tags to task
task = Task(title="Buy groceries")
tag1 = Tag(name="shopping")
tag2 = Tag(name="urgent")
task.tags = [tag1, tag2]
session.add(task)
session.commit()

# Access task's tags
task_tags = task.tags  # [Tag(name="shopping"), Tag(name="urgent")]

# Access tag's tasks
shopping_tasks = tag1.tasks  # [Task(title="Buy groceries"), ...]
```

---

### Self-Referential (Task → Subtasks)
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    parent_task_id: Optional[int] = Field(foreign_key="task.id", index=True)

    # One task can have many subtasks
    subtasks: List["Task"] = Relationship(
        back_populates="parent_task",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )

    # Many subtasks belong to one parent task
    parent_task: Optional["Task"] = Relationship(back_populates="subtasks")
```

---

## Cascade Options

### ON DELETE Behavior
```python
# CASCADE: Delete children when parent is deleted
user_id: str = Field(
    foreign_key="user.id",
    ondelete="CASCADE"
)

# RESTRICT: Prevent deletion of parent if children exist
project_id: int = Field(
    foreign_key="project.id",
    ondelete="RESTRICT"
)

# SET NULL: Set foreign key to NULL when parent is deleted
category_id: Optional[int] = Field(
    foreign_key="category.id",
    ondelete="SET NULL"
)
```

---

## Loading Strategies

### Lazy Loading (Default)
```python
# Relationships loaded on access (N+1 queries possible)
tasks: List["Task"] = Relationship(back_populates="user")
```

### Eager Loading
```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Load user with all tasks in single query
statement = (
    select(User)
    .options(selectinload(User.tasks))
    .where(User.id == "user123")
)
user = session.exec(statement).first()
```

---

## Multi-Tenant Relationship Pattern

For multi-tenant apps, ALWAYS include user_id in child tables:
```python
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str

    tasks: List["Task"] = Relationship(back_populates="project")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)  # ← Required
    project_id: Optional[int] = Field(foreign_key="project.id", index=True)
    title: str

    project: Optional[Project] = Relationship(back_populates="tasks")
```

This ensures:
- Tasks can be queried independently by user
- No accidental cross-user data access
- Efficient filtering in queries

---

## Best Practices from References

For detailed relationship patterns and advanced configurations, refer to:
- `references/sqlmodel-relationships.md` - Advanced relationship configurations
- `references/cascade-patterns.md` - ON DELETE behavior patterns
- `references/loading-strategies.md` - Performance optimization for relationship loading
- `references/self-referential-patterns.md` - Complex hierarchical relationships

---

## Output Checklist

Before delivering relationship configuration:
- [ ] Foreign key fields added to child tables
- [ ] Foreign keys indexed for performance
- [ ] Relationship() attributes configured
- [ ] back_populates set for bidirectional access
- [ ] CASCADE behavior specified where needed
- [ ] Many-to-many junction tables created
- [ ] user_id included in multi-tenant relationships
- [ ] Type hints added (List[], Optional[])
- [ ] Self-referential relationships handled correctly
- [ ] Loading strategies optimized for performance
- [ ] Referential integrity ensured with proper constraints