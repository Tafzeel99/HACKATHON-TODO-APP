---
name: index-optimizer
description: |
  Creates strategic database indexes to optimize query performance for SQLModel applications.
  Analyzes query patterns, identifies slow queries, and generates appropriate B-tree, composite,
  and partial indexes for PostgreSQL/Neon databases.
---

# Index Optimizer

Creates strategic database indexes for optimal query performance.

## What This Skill Does
- Analyzes query patterns to identify indexing opportunities
- Creates B-tree indexes for frequently queried columns
- Generates composite indexes for multi-column queries
- Implements partial indexes for conditional queries
- Adds indexes on foreign keys for join performance
- Optimizes multi-tenant queries with user_id indexes
- Balances read performance vs write overhead

## What This Skill Does NOT Do
- Design database schema (use schema-designer)
- Configure relationships (use sqlmodel-relationship-mapper)
- Generate migration files (use migration-generator)
- Write query logic (use query-builder)

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing models, current indexes, query patterns in code |
| **Conversation** | Most frequent queries, performance bottlenecks, filtering patterns |
| **Skill References** | PostgreSQL indexing strategies, query optimization patterns from `references/` |
| **User Guidelines** | Performance requirements, acceptable query times |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S requirements:

1. **Query Patterns**: "What are the most frequently executed queries in your application?"
2. **Filtering**: "Which columns are most commonly used in WHERE clauses?"
3. **Performance**: "Are there any slow queries or performance issues currently?"
4. **Data Volume**: "What's the expected data volume (rows per table)?"

---

## Implementation Workflow

1. **Analyze Query Patterns**
   - Identify frequently queried columns
   - List columns used in WHERE, ORDER BY, JOIN clauses
   - Note filtering patterns (equality, range, pattern matching)

2. **Determine Index Types**
   - Single-column indexes for simple queries
   - Composite indexes for multi-column filters
   - Partial indexes for conditional queries
   - Unique indexes for constraints

3. **Generate Index Definitions**
   - Add index=True in SQLModel Field()
   - Create explicit sa_column_kwargs for complex indexes
   - Document index purpose and expected impact

4. **Validate Index Strategy**
   - Ensure foreign keys are indexed
   - Check for duplicate/redundant indexes
   - Balance read performance vs write cost

---

## Index Patterns

### Single-Column Index
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Index on user_id for filtering by user
    user_id: str = Field(
        foreign_key="user.id",
        index=True  # ← Creates B-tree index
    )

    # Index on completed for status filtering
    completed: bool = Field(
        default=False,
        index=True  # ← Creates B-tree index
    )

    title: str
```

**Generated SQL:**
```sql
CREATE INDEX ix_task_user_id ON task (user_id);
CREATE INDEX ix_task_completed ON task (completed);
```

**Optimizes queries like:**
```python
# Fast: Uses ix_task_user_id index
tasks = session.exec(
    select(Task).where(Task.user_id == "user123")
).all()

# Fast: Uses ix_task_completed index
pending_tasks = session.exec(
    select(Task).where(Task.completed == False)
).all()
```

---

### Composite Index (Multi-Column)

For queries filtering by multiple columns:
```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    __table_args__ = (
        # Composite index for (user_id, completed) queries
        Index("ix_task_user_completed", "user_id", "completed"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    completed: bool = Field(default=False)
    title: str
```

**Generated SQL:**
```sql
CREATE INDEX ix_task_user_completed ON task (user_id, completed);
```

**Optimizes queries like:**
```python
# Fast: Uses composite index
pending_user_tasks = session.exec(
    select(Task)
    .where(Task.user_id == "user123")
    .where(Task.completed == False)
).all()
```

---

### Partial Index (Conditional)

For queries with common filter conditions:
```python
from sqlalchemy import Index, text

class Task(SQLModel, table=True):
    __table_args__ = (
        # Partial index only on incomplete tasks
        Index(
            "ix_task_incomplete_by_user",
            "user_id",
            postgresql_where=text("completed = false")
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    completed: bool = Field(default=False)
    title: str
```

**Generated SQL:**
```sql
CREATE INDEX ix_task_incomplete_by_user
ON task (user_id)
WHERE completed = false;
```

**Benefits:**
- Smaller index size (only incomplete tasks)
- Faster queries on incomplete tasks
- Lower write overhead

---

### Unique Index (Constraint)
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)

    # Unique index ensures no duplicate emails
    email: str = Field(
        unique=True,
        index=True  # ← Creates unique B-tree index
    )

    name: str
```

**Generated SQL:**
```sql
CREATE UNIQUE INDEX ix_user_email ON user (email);
```

---

## Multi-Tenant Index Strategy

For multi-tenant applications, ALWAYS index user_id:
```python
class Task(SQLModel, table=True):
    __table_args__ = (
        # Composite index for common multi-tenant query
        Index("ix_task_user_status", "user_id", "completed"),

        # Composite index for user's tasks ordered by date
        Index("ix_task_user_created", "user_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")  # Will be indexed via composite
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    title: str
```

**Optimizes:**
- User's pending tasks: `WHERE user_id = ? AND completed = false`
- User's tasks by date: `WHERE user_id = ? ORDER BY created_at`

---

## Index Best Practices

### DO Index:
✅ Foreign keys (user_id, project_id)
✅ Columns in WHERE clauses (status, completed)
✅ Columns in ORDER BY (created_at, updated_at)
✅ Columns in JOIN conditions
✅ Unique constraint columns (email)

### DON'T Index:
❌ Low-cardinality columns (gender with 2 values)
❌ Frequently updated columns (write-heavy)
❌ Small tables (<1000 rows)
❌ Columns never used in queries

---

## Index Maintenance

### Monitor Index Usage
```sql
-- Check index usage (PostgreSQL)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

### Remove Unused Indexes
```sql
-- Drop unused index
DROP INDEX IF EXISTS ix_task_old_column;
```

---

## Performance Impact

| Index Type | Read Speed | Write Speed | Storage |
|------------|------------|-------------|---------|
| **No Index** | Slow (full scan) | Fast | Minimal |
| **Single B-tree** | Fast | Slightly slower | Small |
| **Composite** | Very fast | Slower | Medium |
| **Partial** | Very fast | Fast (fewer rows) | Small |

---

## Best Practices from References

For detailed indexing strategies and advanced optimization techniques, refer to:
- `references/postgresql-indexes.md` - PostgreSQL-specific index types and usage
- `references/query-optimization.md` - Analyzing and optimizing slow queries
- `references/index-maintenance.md` - Index monitoring and maintenance procedures
- `references/performance-patterns.md` - Performance tuning patterns and benchmarks

---

## Output Checklist

Before delivering index strategy:
- [ ] All foreign keys indexed
- [ ] Common WHERE clause columns indexed
- [ ] Composite indexes for multi-column queries
- [ ] Partial indexes for filtered queries
- [ ] user_id indexed in multi-tenant tables
- [ ] No redundant/duplicate indexes
- [ ] Index names follow convention (ix_table_column)
- [ ] Expected query performance improvement documented
- [ ] Write performance impact assessed
- [ ] Storage requirements estimated