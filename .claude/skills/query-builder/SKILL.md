---
name: query-builder
description: |
  Builds optimized SQLModel queries with filtering, sorting, pagination, and joins.
  Creates type-safe database queries with proper error handling, multi-tenant isolation,
  and performance optimization for FastAPI applications.
---

# Query Builder

Builds optimized SQLModel queries for database operations.

## What This Skill Does
- Constructs SQLModel select() queries
- Implements filtering with WHERE clauses
- Adds sorting with ORDER BY
- Implements pagination (offset/limit)
- Performs JOIN operations for relationships
- Filters by user_id for multi-tenant isolation
- Optimizes query performance with proper indexing
- Handles query errors gracefully

## What This Skill Does NOT Do
- Design database schema (use schema-designer)
- Create indexes (use index-optimizer)
- Generate CRUD endpoints (use fastapi-crud-generator)
- Configure relationships (use sqlmodel-relationship-mapper)

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing SQLModel models, current query patterns, database session setup |
| **Conversation** | Query requirements, filtering criteria, sorting needs, pagination limits |
| **Skill References** | SQLModel query patterns, PostgreSQL optimization techniques |
| **User Guidelines** | Performance requirements, query complexity limits |

## Required Clarifications

Ask about USER'S requirements:

1. **Query Purpose**: "What data do you need to retrieve (tasks, users, projects)?"
2. **Filtering**: "What filters should be applied (status, date range, user)?"
3. **Sorting**: "How should results be sorted (newest first, alphabetical)?"
4. **Pagination**: "Do you need pagination? What's the default page size?"

## Implementation Workflow

1. **Define Query Requirements**
   - Identify target model/table
   - List required filters
   - Determine sorting criteria
   - Decide pagination parameters

2. **Build Base Query**
   - Create select() statement
   - Add multi-tenant filter (user_id)
   - Include WHERE clauses

3. **Add Enhancements**
   - Apply sorting (ORDER BY)
   - Implement pagination (offset/limit)
   - Add JOINs if needed

4. **Execute and Handle Errors**
   - Execute query with session.exec()
   - Handle empty results
   - Catch database errors

## Query Patterns

### Basic Query (All Records)
```python
from sqlmodel import select, Session
from typing import List

def get_all_tasks(session: Session) -> List[Task]:
    """Get all tasks from database"""
    statement = select(Task)
    tasks = session.exec(statement).all()
    return tasks
```

### Filter by User (Multi-Tenant)
```python
def get_user_tasks(session: Session, user_id: str) -> List[Task]:
    """Get all tasks for a specific user"""
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

### Multiple Filters (AND Conditions)
```python
def get_incomplete_user_tasks(
    session: Session,
    user_id: str
) -> List[Task]:
    """Get incomplete tasks for a specific user"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.completed == False)
    )
    tasks = session.exec(statement).all()
    return tasks
```

**Alternative syntax:**
```python
from sqlmodel import and_

statement = select(Task).where(
    and_(
        Task.user_id == user_id,
        Task.completed == False
    )
)
```

### OR Conditions
```python
from sqlmodel import or_

def get_high_priority_or_overdue_tasks(
    session: Session,
    user_id: str,
    today: datetime
) -> List[Task]:
    """Get high priority OR overdue tasks"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(
            or_(
                Task.priority == "high",
                Task.due_date < today
            )
        )
    )
    tasks = session.exec(statement).all()
    return tasks
```

### Sorting (ORDER BY)
```python
def get_tasks_sorted(
    session: Session,
    user_id: str,
    sort_by: str = "created_at"
) -> List[Task]:
    """Get tasks sorted by specified column"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())  # Newest first
    )
    tasks = session.exec(statement).all()
    return tasks
```

**Dynamic sorting:**
```python
from sqlmodel import desc, asc

def get_tasks_with_dynamic_sort(
    session: Session,
    user_id: str,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[Task]:
    """Get tasks with dynamic sorting"""
    statement = select(Task).where(Task.user_id == user_id)

    # Get column to sort by
    sort_column = getattr(Task, sort_by, Task.created_at)

    # Apply sort order
    if sort_order == "desc":
        statement = statement.order_by(desc(sort_column))
    else:
        statement = statement.order_by(asc(sort_column))

    tasks = session.exec(statement).all()
    return tasks
```

### Pagination (Offset/Limit)
```python
def get_tasks_paginated(
    session: Session,
    user_id: str,
    offset: int = 0,
    limit: int = 20
) -> List[Task]:
    """Get paginated tasks"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    tasks = session.exec(statement).all()
    return tasks
```

**With total count:**
```python
from sqlmodel import func

def get_tasks_with_count(
    session: Session,
    user_id: str,
    offset: int = 0,
    limit: int = 20
) -> tuple[List[Task], int]:
    """Get paginated tasks with total count"""
    # Get total count
    count_statement = (
        select(func.count())
        .select_from(Task)
        .where(Task.user_id == user_id)
    )
    total = session.exec(count_statement).one()

    # Get paginated results
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    tasks = session.exec(statement).all()

    return tasks, total
```

### Search (Pattern Matching)
```python
def search_tasks(
    session: Session,
    user_id: str,
    search_term: str
) -> List[Task]:
    """Search tasks by title or description"""
    search_pattern = f"%{search_term}%"

    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
    )
    tasks = session.exec(statement).all()
    return tasks
```

### JOIN Queries (Relationships)
```python
from sqlalchemy.orm import selectinload

def get_tasks_with_project(
    session: Session,
    user_id: str
) -> List[Task]:
    """Get tasks with related project data"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .options(selectinload(Task.project))  # Eager load project
    )
    tasks = session.exec(statement).all()

    # Now task.project is loaded without additional queries
    return tasks
```

**Multiple relationships:**
```python
def get_tasks_with_all_relations(
    session: Session,
    user_id: str
) -> List[Task]:
    """Get tasks with all related data"""
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .options(
            selectinload(Task.project),
            selectinload(Task.tags),
            selectinload(Task.user)
        )
    )
    tasks = session.exec(statement).all()
    return tasks
```

### Aggregations (COUNT, SUM, AVG)
```python
from sqlmodel import func

def get_task_statistics(
    session: Session,
    user_id: str
) -> dict:
    """Get task statistics for user"""
    # Total tasks
    total_statement = (
        select(func.count())
        .select_from(Task)
        .where(Task.user_id == user_id)
    )
    total = session.exec(total_statement).one()

    # Completed tasks
    completed_statement = (
        select(func.count())
        .select_from(Task)
        .where(Task.user_id == user_id)
        .where(Task.completed == True)
    )
    completed = session.exec(completed_statement).one()

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": (completed / total * 100) if total > 0 else 0
    }
```

### Complex Query Example
```python
from datetime import datetime, timedelta

def get_filtered_tasks(
    session: Session,
    user_id: str,
    status: str | None = None,
    priority: str | None = None,
    project_id: int | None = None,
    search: str | None = None,
    due_before: datetime | None = None,
    offset: int = 0,
    limit: int = 20
) -> tuple[List[Task], int]:
    """Get tasks with multiple optional filters"""
    # Base query
    statement = select(Task).where(Task.user_id == user_id)

    # Apply filters conditionally
    if status == "completed":
        statement = statement.where(Task.completed == True)
    elif status == "pending":
        statement = statement.where(Task.completed == False)

    if priority:
        statement = statement.where(Task.priority == priority)

    if project_id:
        statement = statement.where(Task.project_id == project_id)

    if search:
        search_pattern = f"%{search}%"
        statement = statement.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )

    if due_before:
        statement = statement.where(Task.due_date < due_before)

    # Get total count
    count_statement = statement.with_only_columns(func.count())
    total = session.exec(count_statement).one()

    # Apply sorting and pagination
    statement = (
        statement
        .order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    tasks = session.exec(statement).all()

    return tasks, total
```

## Error Handling
```python
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

def get_task_by_id_safe(
    session: Session,
    task_id: int,
    user_id: str
) -> Task:
    """Get task with error handling"""
    try:
        statement = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
        )
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return task

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
```

## Query Optimization Tips

### Use Indexes
```python
# Ensure columns in WHERE, ORDER BY are indexed
statement = (
    select(Task)
    .where(Task.user_id == user_id)  # ← Needs index
    .order_by(Task.created_at.desc())  # ← Needs index
)
```

### Avoid N+1 Queries
```python
# ❌ Bad: N+1 queries
tasks = session.exec(select(Task)).all()
for task in tasks:
    print(task.project.name)  # Separate query for each task!

# ✅ Good: Eager loading
statement = select(Task).options(selectinload(Task.project))
tasks = session.exec(statement).all()
for task in tasks:
    print(task.project.name)  # No additional queries
```

### Limit Result Sets
```python
# Always use pagination for large datasets
statement = select(Task).limit(100)  # Max 100 results
```

## Output Checklist

Before delivering query implementation:
- [ ] Query filters by user_id (multi-tenant)
- [ ] Error handling implemented
- [ ] Pagination added (if needed)
- [ ] Sorting implemented correctly
- [ ] JOINs use eager loading (selectinload)
- [ ] Proper indexes exist on filtered columns
- [ ] Type hints added to functions
- [ ] Query tested with sample data

## Python Implementation

```python
from sqlmodel import select, func, Session
from sqlalchemy.orm import selectinload
from typing import List, Tuple, Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import inspect

class QueryBuilder:
    def __init__(self, model_class):
        self.model_class = model_class
        self.statement = select(model_class)
        self.filters = []
        self.sort_orders = []
        self.joins = []
        self.options = []
        self.offset_val = None
        self.limit_val = None

    def where(self, condition):
        """Add WHERE clause to query"""
        self.filters.append(condition)
        self.statement = self.statement.where(condition)
        return self

    def filter_by_user(self, user_id_field: str, user_id: str):
        """Add user-based filter for multi-tenant isolation"""
        model_attr = getattr(self.model_class, user_id_field)
        self.statement = self.statement.where(model_attr == user_id)
        return self

    def order_by(self, column, descending: bool = False):
        """Add ORDER BY clause"""
        if descending:
            from sqlmodel import desc
            self.statement = self.statement.order_by(desc(column))
        else:
            from sqlmodel import asc
            self.statement = self.statement.order_by(asc(column))
        return self

    def paginate(self, offset: int = 0, limit: int = 20):
        """Add pagination (OFFSET and LIMIT)"""
        self.statement = self.statement.offset(offset).limit(limit)
        return self

    def join_with(self, relationship_field, lazy_load: bool = True):
        """Add JOIN with relationship and option for eager loading"""
        if lazy_load:
            self.options.append(selectinload(getattr(self.model_class, relationship_field)))
            self.statement = self.statement.options(selectinload(getattr(self.model_class, relationship_field)))
        return self

    def search(self, search_fields: List[str], search_term: str):
        """Add full-text search across multiple fields"""
        from sqlmodel import or_

        search_conditions = []
        for field_name in search_fields:
            field = getattr(self.model_class, field_name)
            search_conditions.append(field.ilike(f"%{search_term}%"))

        self.statement = self.statement.where(or_(*search_conditions))
        return self

    def build(self):
        """Return the final statement"""
        return self.statement

    def execute(self, session: Session):
        """Execute the query and return results"""
        try:
            return session.exec(self.statement).all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def execute_single(self, session: Session):
        """Execute the query and return single result"""
        try:
            result = session.exec(self.statement).first()
            if not result:
                raise HTTPException(status_code=404, detail="Item not found")
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    def count(self, session: Session):
        """Execute count query"""
        count_statement = self.statement.with_only_columns(func.count()).select_from(self.model_class)
        try:
            return session.exec(count_statement).one()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def build_query_skill(
    model_class,
    filters: Optional[Dict[str, Any]] = None,
    user_filter: Optional[Tuple[str, str]] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = True,
    search_fields: Optional[List[str]] = None,
    search_term: Optional[str] = None,
    relationships: Optional[List[str]] = None,
    pagination: Optional[Tuple[int, int]] = None
) -> str:
    """
    Main function to build SQLModel queries with various options.

    Args:
        model_class: The SQLModel class to query
        filters: Dictionary of field-value pairs to filter by
        user_filter: Tuple of (field_name, user_id) for multi-tenant filtering
        sort_by: Field name to sort by
        sort_desc: Whether to sort in descending order
        search_fields: List of fields to search in
        search_term: Term to search for
        relationships: List of relationships to eager load
        pagination: Tuple of (offset, limit) for pagination
    """
    # Create query builder instance
    qb = QueryBuilder(model_class)

    # Add user filter for multi-tenant isolation
    if user_filter:
        user_field, user_id = user_filter
        qb.filter_by_user(user_field, user_id)

    # Add individual filters
    if filters:
        for field_name, value in filters.items():
            field = getattr(model_class, field_name)
            qb.where(field == value)

    # Add search functionality
    if search_term and search_fields:
        qb.search(search_fields, search_term)

    # Add sorting
    if sort_by:
        sort_field = getattr(model_class, sort_by)
        qb.order_by(sort_field, sort_desc)

    # Add relationships for eager loading
    if relationships:
        for rel in relationships:
            qb.join_with(rel)

    # Add pagination
    if pagination:
        offset, limit = pagination
        qb.paginate(offset, limit)

    # Generate code example
    code_example = _generate_query_code(
        model_class, filters, user_filter, sort_by, sort_desc,
        search_fields, search_term, relationships, pagination
    )

    print(f"Query built for model: {model_class.__name__}")
    print(f"Filters applied: {len(filters or [])}")
    print(f"Multi-tenant filter: {'Yes' if user_filter else 'No'}")
    print(f"Sort: {sort_by} ({'desc' if sort_desc else 'asc'})")
    print(f"Pagination: {'Yes' if pagination else 'No'}")
    print(f"Relationships: {len(relationships or [])}")
    print(f"Search: {'Yes' if search_term else 'No'}")

    return code_example


def _generate_query_code(
    model_class, filters, user_filter, sort_by, sort_desc,
    search_fields, search_term, relationships, pagination
) -> str:
    """Generate the actual query code as a string"""
    lines = [
        "from sqlmodel import select, func, Session",
        "from sqlalchemy.orm import selectinload",
        "from fastapi import HTTPException",
        "from sqlalchemy.exc import SQLAlchemyError",
        ""
    ]

    # Function definition
    func_name = f"get_{model_class.__name__.lower()}s"
    lines.append(f"def {func_name}(session: Session")

    # Add parameters based on what's needed
    params = []
    if user_filter:
        params.append(f", user_id: str")
    if filters:
        for field, value in filters.items():
            params.append(f", {field}: {type(value).__name__} = {repr(value)}")
    if search_term:
        params.append(", search_term: str = None")
    if pagination:
        params.append(", offset: int = 0")
        params.append(", limit: int = 20")

    lines[-1] = lines[-1] + "".join(params) + ") -> list:"

    # Add docstring
    lines.append(f'    """Get {model_class.__name__} with filters and options."""')
    lines.append("")

    # Build the query
    lines.append("    # Build query statement")
    lines.append(f"    statement = select({model_class.__name__})")

    # Add user filter
    if user_filter:
        user_field, _ = user_filter
        lines.append(f"    statement = statement.where({model_class.__name__}.{user_field} == user_id)")

    # Add other filters
    if filters:
        for field, value in filters.items():
            if isinstance(value, str):
                lines.append(f"    statement = statement.where({model_class.__name__}.{field} == '{value}')")
            else:
                lines.append(f"    statement = statement.where({model_class.__name__}.{field} == {value})")

    # Add search
    if search_term and search_fields:
        lines.append("    if search_term:")
        search_conditions = []
        for field in search_fields:
            search_conditions.append(f"{model_class.__name__}.{field}.ilike(f'%{{search_term}}%')")
        or_conditions = " or_({})".format(", ".join(search_conditions))
        lines.append(f"        from sqlmodel import or_")
        lines.append(f"        statement = statement.where({or_conditions})")

    # Add sorting
    if sort_by:
        order = "desc()" if sort_desc else "asc()"
        lines.append(f"    statement = statement.order_by({model_class.__name__}.{sort_by}.{order})")

    # Add pagination
    if pagination:
        lines.append("    statement = statement.offset(offset).limit(limit)")

    # Add eager loading for relationships
    if relationships:
        lines.append("    # Eager load relationships to avoid N+1 queries")
        for rel in relationships:
            lines.append(f"    statement = statement.options(selectinload({model_class.__name__}.{rel}))")

    # Execute query
    lines.append("")
    lines.append("    try:")
    lines.append("        results = session.exec(statement).all()")
    lines.append("        return results")
    lines.append("    except SQLAlchemyError as e:")
    lines.append("        raise HTTPException(status_code=500, detail=f'Database error: {{str(e)}}')")

    return "\\n".join(lines)


# Example usage:
# query_code = build_query_skill(
#     Task,
#     filters={"completed": False},
#     user_filter=("user_id", "user123"),
#     sort_by="created_at",
#     sort_desc=True,
#     search_fields=["title", "description"],
#     search_term="important",
#     relationships=["user", "project"],
#     pagination=(0, 20)
# )
```

## Usage Examples

### Basic Query
```python
query_code = build_query_skill(
    model_class=Task,
    filters={"completed": False},
    user_filter=("user_id", "user123"),
    sort_by="created_at",
    pagination=(0, 20)
)
```

### Complex Query with Search
```python
query_code = build_query_skill(
    model_class=Task,
    user_filter=("user_id", "user123"),
    filters={"priority": "high"},
    search_fields=["title", "description"],
    search_term="urgent",
    relationships=["user", "project"],
    sort_by="due_date",
    sort_desc=True,
    pagination=(0, 50)
)
```