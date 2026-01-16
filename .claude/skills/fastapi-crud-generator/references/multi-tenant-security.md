# Multi-Tenant Security Guide

This guide covers security patterns for multi-tenant applications using FastAPI and SQLModel.

## Tenant Isolation Strategies

### User-Based Isolation
The most common approach where each user has their own data space:

```python
# Model with user_id for tenant isolation
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str  # Links record to specific user/tenant
    title: str
    description: Optional[str] = None
    completed: bool = False
```

### Organization-Based Isolation
For applications where users belong to organizations:

```python
class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: str  # Links record to specific organization
    title: str
    assigned_user_id: str
    completed: bool = False
```

## Data Access Patterns

### Query Filtering
Always filter queries by tenant identifier:

```python
def get_user_tasks(user_id: str, session: Session):
    # ✅ CORRECT: Filter by user_id
    tasks = session.exec(
        select(Task)
        .where(Task.user_id == user_id)
    ).all()
    return tasks

def get_task_by_id(task_id: int, user_id: str, session: Session):
    # ✅ CORRECT: Verify task belongs to user
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### Direct Access Prevention
Never allow access to records without tenant verification:

```python
# ❌ WRONG: Direct access without tenant check
def bad_get_task(task_id: int, session: Session):
    return session.get(Task, task_id)  # No tenant check!

# ✅ CORRECT: Always verify tenant
def good_get_task(task_id: int, user_id: str, session: Session):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return task
```

## Authentication Integration

### JWT Token Claims
Using JWT tokens with user information:

```python
from typing import Optional
from pydantic import BaseModel

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except (JWTError, ValidationError):
        raise credentials_exception

    # Verify user exists in database
    user = get_user_by_id(token_data.user_id, session)
    if user is None:
        raise credentials_exception

    return {"id": token_data.user_id, "email": user.email}
```

### Session-Based Authentication
For session-based authentication:

```python
def get_current_user_from_session(
    request: Request
) -> dict:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Verify user exists
    user = get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return {"id": user_id, "email": user.email}
```

## Endpoint Protection Patterns

### Path-Based Tenant Verification
```python
@app.get("/api/{user_id}/tasks/{task_id}")
def get_task(
    user_id: str,
    task_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify that the path user_id matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Now safely retrieve the task
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

### Custom Dependency for Tenant Verification
```python
def verify_user_owns_resource(expected_user_id: str = Path(...)):
    def user_verification(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["id"] != expected_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only access your own resources"
            )
        return current_user
    return user_verification

@app.get("/api/{user_id}/tasks/{task_id}")
def get_task(
    user_id: str,  # This will be validated by the dependency
    task_id: int,
    current_user: dict = Depends(verify_user_owns_resource),
    session: Session = Depends(get_session)
):
    # Retrieve and return task (already verified ownership)
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

## Cross-Tenant Access Prevention

### Database-Level Constraints
While application-level checks are essential, database constraints provide an extra layer:

```sql
-- Example: Ensure task.user_id matches the authenticated user
CREATE POLICY task_isolation ON tasks
    FOR ALL
    USING (user_id = current_user_id());
```

### Row-Level Security (RLS)
Enable row-level security in your database:

```python
# In your model, you can add comments that indicate RLS should be applied
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(description="Links to the owning user - RLS enforced")
    title: str
    description: Optional[str] = None
    completed: bool = False

    __table_args__ = (
        # Additional table constraints can be added here
    )
```

## Error Handling Best Practices

### Consistent Error Responses
Don't distinguish between "not found" and "access denied":

```python
# ❌ WRONG: Reveals existence of records
def bad_access_check(task_id: int, user_id: str, session: Session):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task does not exist")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

# ✅ CORRECT: Same response for both cases
def good_access_check(task_id: int, user_id: str, session: Session):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### Logging Security Events
Log access attempts without revealing sensitive information:

```python
import logging

logger = logging.getLogger(__name__)

def secure_get_task(task_id: int, user_id: str, session: Session):
    task = session.get(Task, task_id)
    if not task:
        logger.warning(f"User {user_id} attempted to access non-existent task {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        logger.warning(f"User {user_id} attempted to access task {task_id} owned by {task.user_id}")
        raise HTTPException(status_code=404, detail="Task not found")

    logger.info(f"User {user_id} accessed task {task_id}")
    return task
```

## Testing Multi-Tenant Security

### Unit Tests for Isolation
```python
def test_user_cannot_access_other_users_data():
    # Create test users
    user1 = create_test_user("user1@test.com")
    user2 = create_test_user("user2@test.com")

    # Create tasks for user1
    task1 = create_task_for_user(user1.id, "Task 1")

    # User2 should not be able to access user1's task
    with pytest.raises(HTTPException) as exc_info:
        get_task(task1.id, user2.id, session)

    assert exc_info.value.status_code == 404
```

### Integration Tests
```python
def test_multi_tenant_endpoints():
    # Authenticate as user1
    token1 = authenticate_user("user1@test.com")

    # Create a task as user1
    response = client.post(
        "/api/user1/tasks/",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    task_id = response.json()["id"]

    # Authenticate as user2
    token2 = authenticate_user("user2@test.com")

    # User2 should not see user1's task
    response = client.get(
        f"/api/user2/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 404
```

## Performance Considerations

### Indexing for Tenant Queries
Ensure proper indexing for tenant-based queries:

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Index for fast filtering
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed: bool = Field(default=False, index=True)
```

### Batch Operations
When performing bulk operations, always verify tenant ownership:

```python
def delete_user_tasks(user_id: str, session: Session):
    # Delete only tasks belonging to the user
    statement = delete(Task).where(Task.user_id == user_id)
    result = session.exec(statement)
    session.commit()
    return {"deleted_count": result.rowcount}
```