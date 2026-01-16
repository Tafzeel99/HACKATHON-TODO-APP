# Relationship Loading Strategies

Optimization patterns for loading SQLModel relationships efficiently.

## Loading Types

### Lazy Loading (Default)
Relationships are loaded when accessed.

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tasks")

# Lazy loading - triggers additional queries when accessing relationships
user = session.get(User, 1)
print(user.tasks)  # Triggers query to load tasks
task = session.get(Task, 1)
print(task.user)   # Triggers query to load user
```

### Eager Loading
Relationships are loaded in the same query.

```python
from sqlalchemy.orm import selectinload, joinedload

# SelectIN loading - separate query with IN clause
def get_user_with_tasks_selectin(user_id: int, session):
    statement = (
        select(User)
        .options(selectinload(User.tasks))
        .where(User.id == user_id)
    )
    return session.exec(statement).first()

# Joined loading - single query with JOIN
def get_user_with_tasks_joined(user_id: int, session):
    statement = (
        select(User)
        .options(joinedload(User.tasks))
        .where(User.id == user_id)
    )
    return session.exec(statement).first()
```

## Loading Strategy Comparison

### SelectIN Loading
- Pros: Efficient for large result sets, avoids Cartesian product
- Cons: Additional query for each relationship

```python
# Good for loading many users with their tasks
def get_many_users_with_tasks(session):
    statement = select(User).options(selectinload(User.tasks))
    users = session.exec(statement).all()
    for user in users:
        print(f"{user.name} has {len(user.tasks)} tasks")  # No additional queries
```

### Joined Loading
- Pros: Single query for related data
- Cons: Can cause Cartesian product with multiple relationships

```python
# Good when you need to filter on related data
def get_users_with_active_tasks(session):
    statement = (
        select(User)
        .join(Task)
        .options(joinedload(User.tasks))
        .where(Task.status == "active")
    )
    return session.exec(statement).all()
```

### Subquery Loading
- Pros: Good for complex nested relationships
- Cons: Additional query complexity

```python
from sqlalchemy.orm import subqueryload

def get_user_with_tasks_and_comments(session):
    statement = (
        select(User)
        .options(
            selectinload(User.tasks)
            .selectinload(Task.comments)
        )
    )
    return session.exec(statement).all()
```

## Complex Loading Patterns

### Multiple Relationship Loading
```python
from sqlalchemy.orm import selectinload

def get_user_with_complex_data(user_id: int, session):
    statement = (
        select(User)
        .options(
            selectinload(User.tasks)
            .selectinload(Task.category),
            selectinload(User.profile),
            selectinload(User.projects)
            .selectinload(Project.team)
        )
        .where(User.id == user_id)
    )
    return session.exec(statement).first()
```

### Conditional Loading
```python
def get_user_with_tasks_conditionally(include_tasks: bool, user_id: int, session):
    statement = select(User).where(User.id == user_id)
    if include_tasks:
        statement = statement.options(selectinload(User.tasks))
    return session.exec(statement).first()
```

### Prefetching Related Data
```python
def get_users_with_prefetched_data(session):
    # Load users with their most recent task only
    from sqlalchemy import func

    # First get the latest task ID for each user
    latest_task_ids = (
        select(func.max(Task.id).label('latest_task_id'))
        .join(User)
        .group_by(Task.user_id)
        .subquery()
    )

    # Then join to get users with their latest task
    statement = (
        select(User, Task)
        .join(Task, User.id == Task.user_id)
        .join(latest_task_ids, Task.id == latest_task_ids.c.latest_task_id)
    )
    return session.exec(statement).all()
```

## Performance Optimization Strategies

### Avoiding N+1 Query Problems
```python
# N+1 problem - DON'T DO THIS
def bad_get_users_with_tasks(session):
    users = session.exec(select(User)).all()
    for user in users:
        print(len(user.tasks))  # Triggers N additional queries

# Solution - Eager loading
def good_get_users_with_tasks(session):
    users = session.exec(
        select(User).options(selectinload(User.tasks))
    ).all()
    for user in users:
        print(len(user.tasks))  # No additional queries
```

### Batch Loading for Deep Relationships
```python
def get_users_with_tasks_and_categories(session):
    statement = (
        select(User)
        .options(
            selectinload(User.tasks)
            .selectinload(Task.category)
        )
    )
    return session.exec(statement).all()
```

### Dynamic Loading
```python
from sqlalchemy.orm import selectinload

def get_user_dynamic_loading(user_id: int, load_tasks: bool, session):
    query = select(User).where(User.id == user_id)

    if load_tasks:
        query = query.options(selectinload(User.tasks))

    return session.exec(query).first()
```

### Lazy Loading with Limits
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # Lazy loading with a property that limits results
    def get_recent_tasks(self, session, limit: int = 5):
        return session.exec(
            select(Task)
            .where(Task.user_id == self.id)
            .order_by(Task.created_at.desc())
            .limit(limit)
        ).all()
```

## Multi-Tenant Loading Patterns

### Tenant-Isolated Loading
```python
class TenantScopedModel(SQLModel, table=True):
    __abstract__ = True
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)

class Project(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str
    tasks: List["Task"] = Relationship(back_populates="project")

class Task(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    title: str
    project: Optional[Project] = Relationship(back_populates="tasks")

# Safe tenant-isolated loading
def get_user_projects_with_tasks(user_id: str, session):
    statement = (
        select(Project)
        .where(Project.user_id == user_id)
        .options(selectinload(Project.tasks))
    )
    return session.exec(statement).all()
```

## Loading Strategy Selection Guidelines

### When to Use Each Strategy

| Scenario | Recommended Strategy | Reason |
|----------|---------------------|---------|
| Large number of records | SelectIN loading | Avoids Cartesian product |
| Need to filter on related data | Joined loading | Single query with JOIN |
| Deep nesting (3+ levels) | Subquery loading | Better performance for deep relationships |
| Small result sets | Joined loading | Fewer round trips |
| Memory constraints | Lazy loading | Only load what's needed |
| Frequently accessed relationships | Eager loading | Reduce queries |

### Performance Monitoring
```python
import time
from contextlib import contextmanager

@contextmanager
def monitor_query_performance():
    start_time = time.time()
    yield
    duration = time.time() - start_time
    if duration > 1.0:  # Log slow queries (>1 second)
        print(f"Slow query detected: {duration:.2f}s")

# Usage
with monitor_query_performance():
    users = session.exec(
        select(User).options(selectinload(User.tasks))
    ).all()
```

## Advanced Loading Techniques

### Custom Loader Strategies
```python
from sqlalchemy.orm.interfaces import MapperOption

class CustomLoader(MapperOption):
    def __init__(self, attr):
        self.attr = attr

    def process_query(self, query):
        # Custom loading logic
        pass

# Usage with custom loading
def get_user_with_custom_strategy(user_id: int, session):
    statement = (
        select(User)
        .where(User.id == user_id)
        .execution_options(loader_strategy=(CustomLoader, User.tasks))
    )
    return session.exec(statement).first()
```

These loading strategies help optimize SQLModel relationship performance by reducing query count, minimizing data transfer, and improving application responsiveness.