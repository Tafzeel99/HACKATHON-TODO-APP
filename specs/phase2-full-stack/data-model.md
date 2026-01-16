# Data Model: Phase II - Todo Full-Stack Web Application

**Branch**: `phase2-full-stack`
**Date**: 2026-01-16
**Database**: Neon Serverless PostgreSQL

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Entity Relationships                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐         1:N         ┌─────────────────┐       │
│  │    User     │─────────────────────│      Task       │       │
│  ├─────────────┤                     ├─────────────────┤       │
│  │ id (PK)     │◄────────────────────│ user_id (FK)    │       │
│  │ email       │                     │ id (PK)         │       │
│  │ name        │                     │ title           │       │
│  │ created_at  │                     │ description     │       │
│  └─────────────┘                     │ completed       │       │
│                                      │ created_at      │       │
│                                      │ updated_at      │       │
│                                      └─────────────────┘       │
│                                                                 │
│  Cardinality:                                                   │
│  - One User has zero or more Tasks                              │
│  - Each Task belongs to exactly one User                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entities

### User

Represents an authenticated person using the system. Managed by Better Auth.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique identifier (from Better Auth) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| `name` | VARCHAR(100) | NULL | Optional display name |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |

**Notes**:
- User records are managed by Better Auth
- Backend only reads user data for display purposes
- Password is NOT stored here (Better Auth handles it)

### Task

Represents a single todo item owned by a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Globally unique task identifier |
| `user_id` | UUID | FK → users.id, NOT NULL, INDEX | Owner of this task |
| `title` | VARCHAR(200) | NOT NULL | Task title (1-200 chars) |
| `description` | VARCHAR(1000) | NULL | Optional task description (0-1000 chars) |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Completion status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Notes**:
- `user_id` + `completed` indexed for efficient filtering
- `updated_at` auto-updates on any modification
- Deletion is hard delete (no soft delete in Phase II)

---

## Database Schema (SQL)

```sql
-- Users table (managed by Better Auth, simplified here)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
```

---

## SQLModel Definitions

### User Model

```python
# models/user.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False)
    name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Task Model

```python
# models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

---

## Pydantic Schemas

### Task Schemas

```python
# schemas/task.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

# Request: Create task
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

# Request: Update task
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

# Response: Task details
class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response: Task list
class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
```

### User Schemas

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid

# Request: Signup
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = Field(default=None, max_length=100)

# Request: Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response: User info (no password)
class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Response: Auth token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
```

---

## Validation Rules

### Task Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| `title` | Required, 1-200 chars | "Title is required and must be 1-200 characters" |
| `description` | Optional, max 1000 chars | "Description must be at most 1000 characters" |
| `completed` | Boolean | (auto-validated) |

### User Validation (Better Auth)

| Field | Rule | Error Message |
|-------|------|---------------|
| `email` | Required, valid email, unique | "Invalid email" / "Email already registered" |
| `password` | Required, min 8 chars | "Password must be at least 8 characters" |
| `name` | Optional, max 100 chars | "Name must be at most 100 characters" |

---

## State Transitions

### Task States

```
┌─────────────┐         toggle          ┌─────────────┐
│   PENDING   │◄───────────────────────►│  COMPLETED  │
│ (completed  │                         │ (completed  │
│  = false)   │                         │  = true)    │
└─────────────┘                         └─────────────┘
       │                                       │
       │              DELETE                   │
       └───────────────┬───────────────────────┘
                       │
                       ▼
                 ┌───────────┐
                 │  DELETED  │
                 │ (removed) │
                 └───────────┘
```

### Task Lifecycle

1. **Create**: `pending` state (completed = false)
2. **Toggle**: Switch between `pending` ↔ `completed`
3. **Update**: Modify title/description, stays in current state
4. **Delete**: Permanently removed from database

---

## Indexes & Performance

### Query Patterns

| Query | Index Used | Expected Performance |
|-------|------------|---------------------|
| Get all tasks for user | `idx_tasks_user_id` | O(log n) + O(k) |
| Get pending tasks for user | `idx_tasks_user_completed` | O(log n) + O(k) |
| Get completed tasks for user | `idx_tasks_user_completed` | O(log n) + O(k) |
| Get task by ID | Primary key | O(log n) |
| Sort by created date | `idx_tasks_created_at` | O(log n) + O(k) |

### Index Strategy

- **Composite index** on `(user_id, completed)` for filtered queries
- **Single index** on `created_at DESC` for default sorting
- **Foreign key index** on `user_id` for JOIN operations

---

## Migration Strategy

### Initial Migration (Alembic)

```python
# alembic/versions/001_initial_schema.py
"""Initial schema for Phase II

Revision ID: 001
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])
    op.create_index('idx_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], postgresql_ops={'created_at': 'DESC'})

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```
