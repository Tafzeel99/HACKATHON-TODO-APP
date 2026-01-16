---
name: fastapi-crud-generator
description: |
  Auto-generates complete CRUD (Create, Read, Update, Delete) API endpoints for SQLModel database models.
  Creates RESTful routes with proper HTTP methods, Pydantic request/response schemas, database session
  management, error handling, and query filtering by user_id for multi-tenant applications.
---

# FastAPI CRUD Generator

Auto-generates complete CRUD (Create, Read, Update, Delete) API endpoints for SQLModel database models.

## What This Skill Does
- Generates complete CRUD endpoints (POST, GET, PUT, PATCH, DELETE) for SQLModel models
- Creates RESTful routes following standard patterns: /api/{user_id}/resource
- Generates Pydantic request/response schemas for input validation
- Implements database session management with dependency injection
- Adds proper error handling (404, 403, 422 responses)
- Implements user_id filtering for multi-tenant applications
- Creates database query logic with proper filtering

## What This Skill Does NOT Do
- Design database schema (uses provided SQLModel models)
- Implement frontend UI components
- Handle file uploads or complex relationships automatically
- Deploy or configure production infrastructure

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing SQLModel models, database session setup, current API patterns to integrate with |
| **Conversation** | Specific model to generate CRUD for, authentication method, filtering requirements |
| **Skill References** | Domain patterns from `references/` (SQLModel CRUD patterns, FastAPI dependency injection, multi-tenant best practices) |
| **User Guidelines** | Project-specific conventions, naming standards, existing auth patterns |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **Model Details**: "Which SQLModel model do you want to generate CRUD for?"
2. **Authentication**: "How is user authentication implemented in your application?"
3. **Custom Requirements**: "Do you need any custom fields or special validation in the Pydantic schemas?"

---

## Implementation Workflow

1. **Analyze Input Model**
   - Examine the provided SQLModel for fields and constraints
   - Identify primary keys and relationships
   - Determine which fields are required vs optional

2. **Generate Pydantic Schemas**
   - Create Create schema (exclude primary keys, user_id if auto-assigned)
   - Create Read schema (include all fields)
   - Create Update schema (make all fields optional)
   - Create Patch schema for partial updates

3. **Create Database Functions**
   - Create item function with user_id assignment
   - Read all items function with user_id filtering
   - Read single item function with user_id validation
   - Update item function with user_id validation
   - Delete item function with user_id validation

4. **Generate FastAPI Endpoints**
   - POST /api/{user_id}/resource - Create
   - GET /api/{user_id}/resource - List all
   - GET /api/{user_id}/resource/{id} - Get one
   - PUT /api/{user_id}/resource/{id} - Update
   - DELETE /api/{user_id}/resource/{id} - Delete

---

## CRUD Endpoint Templates

### Pydantic Schemas Generation

For a model like:
```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    title: str
    description: str | None = None
    completed: bool = False
```

The skill generates:

```python
from pydantic import BaseModel
from typing import List, Optional

# Create schema - excludes id (auto-generated), includes user_id if needed
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False

# Read schema - includes all fields
class TaskRead(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool

# Update schema - all fields optional for full updates
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

# Patch schema - all fields optional for partial updates
class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
```

### Database Functions

```python
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

def create_task_for_user(
    *,
    session: Session = Depends(get_session),
    user_id: str,
    task: TaskCreate
) -> Task:
    """
    Creates a new task for the specified user
    """
    db_task = Task.model_validate(task)
    db_task.user_id = user_id  # Assign user_id from path parameter

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def get_tasks_by_user(
    *,
    session: Session = Depends(get_session),
    user_id: str,
    offset: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Gets all tasks for the specified user
    """
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .offset(offset)
        .limit(limit)
    ).all()

    return tasks

def get_task_by_id_and_user(
    *,
    session: Session = Depends(get_session),
    task_id: int,
    user_id: str
) -> Task:
    """
    Gets a specific task by ID for the specified user
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return task

def update_task_by_id_and_user(
    *,
    session: Session = Depends(get_session),
    task_id: int,
    user_id: str,
    task_update: TaskUpdate
) -> Task:
    """
    Updates a specific task by ID for the specified user
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update the task with provided data
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def delete_task_by_id_and_user(
    *,
    session: Session = Depends(get_session),
    task_id: int,
    user_id: str
) -> dict:
    """
    Deletes a specific task by ID for the specified user
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
```

### FastAPI Endpoints

```python
from fastapi import FastAPI, Depends, Query
from typing import List

app = FastAPI()

@app.post("/api/{user_id}/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),  # Assumes authentication
    session: Session = Depends(get_session)
):
    # Verify that the user_id matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return create_task_for_user(session=session, user_id=user_id, task=task)


@app.get("/api/{user_id}/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),  # Assumes authentication
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=0, le=1000)
):
    # Verify that the user_id matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return get_tasks_by_user(session=session, user_id=user_id, offset=offset, limit=limit)


@app.get("/api/{user_id}/tasks/{task_id}", response_model=TaskRead)
def read_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),  # Assumes authentication
    session: Session = Depends(get_session)
):
    # Verify that the user_id matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return get_task_by_id_and_user(session=session, task_id=task_id, user_id=user_id)


@app.put("/api/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),  # Assumes authentication
    session: Session = Depends(get_session)
):
    # Verify that the user_id matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_task_by_id_and_user(
        session=session,
        task_id=task_id,
        user_id=user_id,
        task_update=task_update
    )


@app.delete("/api/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),  # Assumes authentication
    session: Session = Depends(get_session)
):
    # Verify that the user_id matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return delete_task_by_id_and_user(session=session, task_id=task_id, user_id=user_id)
```

---

## Multi-Tenant Security Considerations

### User Isolation
- All queries filter by user_id to prevent unauthorized access
- Each endpoint validates that the resource belongs to the authenticated user
- 403 Forbidden responses for access violations

### Authentication Integration
- Leverages existing authentication system (JWT, session, etc.)
- Validates user identity before processing requests
- Supports role-based access control if needed

---

## Error Handling

### HTTP Status Codes
- 200 OK: Successful GET, PUT, PATCH operations
- 201 Created: Successful POST operations
- 204 No Content: Successful DELETE operations
- 400 Bad Request: Invalid request format
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Access denied to resource
- 404 Not Found: Resource does not exist
- 422 Unprocessable Entity: Validation errors

### Error Response Format
```json
{
  "detail": "Descriptive error message"
}
```

---

## Output Checklist

Before delivering generated CRUD implementation, verify:
- [ ] All CRUD endpoints generated correctly (POST, GET, PUT, PATCH, DELETE)
- [ ] Pydantic schemas created for Create, Read, Update, Patch operations
- [ ] Database functions implement proper user_id filtering
- [ ] Authentication integration added to all endpoints
- [ ] Error handling covers all common scenarios
- [ ] Response models properly defined for each endpoint
- [ ] Session management implemented via dependency injection

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/sqlmodel-patterns.md` | When customizing database query patterns |
| `references/fastapi-dependencies.md` | When modifying dependency injection patterns |
| `references/multi-tenant-security.md` | When implementing advanced security measures |