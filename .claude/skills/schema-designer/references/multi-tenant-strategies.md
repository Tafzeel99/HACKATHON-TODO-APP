# Multi-Tenant Database Strategies

Implementation patterns for secure and efficient multi-tenant database architectures.

## Core Principles

### Data Isolation
- Each tenant's data must be securely isolated from others
- No tenant should be able to access another tenant's data
- Queries must always filter by tenant identifier

### Performance Considerations
- Efficient indexing for tenant-based queries
- Minimal overhead for tenant identification
- Scalable partitioning strategies

## Tenant Identification Patterns

### User-Based Tenancy
```python
class TenantScopedModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
    # All data belongs to a specific user
```

### Organization-Based Tenancy
```python
class TenantScopedModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id", index=True, nullable=False)
    # All data belongs to a specific organization
```

### Mixed Tenancy (User + Organization)
```python
class TenantScopedModel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
    organization_id: int = Field(foreign_key="organization.id", index=True, nullable=False)
```

## Security Implementation

### Mandatory Tenant Filtering
Every query must include tenant filtering:
```python
# Safe - includes tenant filter
def get_user_tasks(user_id: str, session: Session):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

# Unsafe - missing tenant filter
def get_all_tasks(session: Session):
    return session.exec(select(Task)).all()  # DANGEROUS!
```

### Route-Level Protection
```python
from fastapi import Depends

async def verify_tenant_access(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> dict:
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Cannot access another user's data"
        )
    return current_user
```

## Schema Design Patterns

### Single Table Per Entity (Recommended)
All tenant data in the same table with tenant identifier:
```python
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
    title: str = Field(max_length=200)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Advantages:
- Simpler queries and maintenance
- Better resource utilization
- Easier reporting across tenants
- Efficient indexing strategies

### Disadvantages:
- Potential for data leakage if queries miss tenant filter
- Larger table sizes
- Need for careful access controls

## Indexing Strategies

### Essential Indexes for Multi-Tenant Tables
```python
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    # Critical: Always index tenant identifier
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)

    # Common query patterns should be indexed
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Composite indexes for common query patterns
    # Index both tenant and status for filtered queries
```

### Composite Index Examples
```python
from sqlalchemy import Index

# Create composite index for common query pattern
Index('idx_task_user_status', Task.user_id, Task.status)
Index('idx_task_user_created', Task.user_id, Task.created_at.desc())
```

## Query Patterns

### Safe Query Patterns
```python
# Always filter by tenant
def get_user_tasks(user_id: str, status: str = None):
    query = select(Task).where(Task.user_id == user_id)
    if status:
        query = query.where(Task.status == status)
    return query.order_by(Task.created_at.desc())

# Count with tenant filter
def count_user_tasks(user_id: str):
    return select(func.count(Task.id)).where(Task.user_id == user_id)
```

### Unsafe Query Patterns to Avoid
```python
# NEVER do this - no tenant filter
def get_all_tasks():
    return select(Task)  # DANGEROUS!

# Be careful with joins
def get_user_tasks_with_details(user_id: str):
    # Make sure all joined tables are also tenant-filtered
    return select(Task, User).join(User).where(Task.user_id == user_id)
```

## Tenant Administration

### Admin Access Patterns
```python
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

def get_current_user_with_role(token: str = Depends(oauth2_scheme)):
    # Verify token and return user with role
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return {
        "id": payload.get("sub"),
        "role": payload.get("role", "user")
    }

def get_tasks_for_admin(
    current_user: dict = Depends(get_current_user_with_role)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    # Admins might have broader access, but still need controlled access
    return select(Task)  # Still need appropriate filters
```

## Performance Optimization

### Connection Pooling
- Use connection pooling efficiently
- Consider separate pools for different tenant loads
- Monitor query performance across tenants

### Caching Strategies
- Cache tenant-specific data separately
- Invalidate caches per tenant, not globally
- Consider Redis with tenant prefixes

### Partitioning (Advanced)
For very large deployments, consider table partitioning:
```sql
-- Example PostgreSQL partitioning by tenant
CREATE TABLE tasks_partitioned (
    id SERIAL,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY HASH (user_id);
```

## Testing Multi-Tenant Security

### Unit Tests for Tenant Isolation
```python
def test_tenant_data_isolation():
    # Create tasks for different users
    user1_tasks = create_test_tasks(user_id="user1")
    user2_tasks = create_test_tasks(user_id="user2")

    # Verify user1 can only see their own tasks
    user1_view = get_tasks_for_user("user1")
    assert len(user1_view) == len(user1_tasks)
    assert all(task.user_id == "user1" for task in user1_view)

    # Verify user2 can only see their own tasks
    user2_view = get_tasks_for_user("user2")
    assert len(user2_view) == len(user2_tasks)
    assert all(task.user_id == "user2" for task in user2_view)
```

## Error Handling

### Common Multi-Tenant Errors
```python
def get_task_safely(task_id: int, user_id: str, session: Session):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Critical: Verify the task belongs to the requesting user
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return task
```

## Migration Considerations

### Adding Multi-Tenancy to Existing Schema
```python
# Migration to add tenant isolation to existing table
def upgrade():
    op.add_column('task', sa.Column('user_id', sa.String(), nullable=True))
    op.create_index('ix_task_user_id', 'task', ['user_id'])

    # IMPORTANT: Populate user_id for existing records
    # This depends on your existing data structure

    # Make user_id required after populating
    op.alter_column('task', 'user_id', nullable=False)

    # Add foreign key constraint
    op.create_foreign_key('fk_task_user', 'task', 'user', ['user_id'], ['id'])
```

## Monitoring and Auditing

### Tenant Access Logs
```python
class AuditLog(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, nullable=False)
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

This ensures accountability and helps detect unauthorized access attempts.