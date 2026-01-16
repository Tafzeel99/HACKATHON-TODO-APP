# PostgreSQL Optimization Guidelines

Performance optimization strategies specifically for PostgreSQL databases used with SQLModel.

## Connection Management

### Connection Pooling
- Use connection pooling libraries like `SQLAlchemy's QueuePool`
- Configure appropriate pool sizes based on concurrent load
- Monitor pool exhaustion and adjust accordingly

### Connection Parameters
```python
# Recommended PostgreSQL connection string with optimization
postgresql+asyncpg://user:password@localhost/dbname?\
    server_settings={
        'application_name': 'myapp',
        'idle_in_transaction_session_timeout': 30000,  # 30 seconds
        'lock_timeout': 10000,  # 10 seconds
        'statement_timeout': 30000  # 30 seconds
    }
```

## Indexing Strategies

### Basic Indexing
```python
# SQLModel field with index
user_id: str = Field(foreign_key="user.id", index=True)

# This creates an index like:
# CREATE INDEX ix_task_user_id ON task (user_id);
```

### Composite Indexes
```python
# For queries filtering by multiple columns
class Task(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

# Consider composite index for common query patterns
# CREATE INDEX idx_task_user_status ON task (user_id, status);
# CREATE INDEX idx_task_user_created ON task (user_id, created_at DESC);
```

### Partial Indexes
```sql
-- For common filtered queries
CREATE INDEX idx_active_tasks ON task (user_id, created_at)
WHERE status = 'active';
```

### Expression Indexes
```sql
-- For case-insensitive searches
CREATE INDEX idx_user_lower_email ON "user" (LOWER(email));
```

## Query Optimization

### Use Appropriate Data Types
```python
# Use specific PostgreSQL types for better performance
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY

class Task(SQLModel, table=True):
    # UUID for globally unique identifiers
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # JSON for flexible data structures
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Array for simple lists (if normalized structure isn't needed)
    tags: Optional[list] = Field(default=None, sa_column=Column(ARRAY(String)))
```

### Efficient Query Patterns
```python
# Use LIMIT for pagination
def get_tasks_paginated(user_id: str, offset: int, limit: int):
    return select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)

# Use EXISTS instead of COUNT for existence checks
def user_has_tasks(user_id: str):
    return select(exists().where(Task.user_id == user_id))

# Use JOINs efficiently with proper indexes
def get_user_tasks_with_user_info(user_id: str):
    return select(Task, User).join(User).where(Task.user_id == user_id)
```

## Table Design Optimization

### Row Size Considerations
```python
# Keep rows reasonably sized for better cache efficiency
class Task(SQLModel, table=True):
    # Keep frequently accessed fields small
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)  # Reasonable limit

    # Store large text separately if rarely accessed
    description: Optional[str] = Field(default=None, max_length=1000)
```

### Partitioning for Large Tables
```sql
-- Range partitioning example for time-series data
CREATE TABLE task_partitioned (
    id SERIAL,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE task_2026_01 PARTITION OF task_partitioned
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

## Configuration Tuning

### Key PostgreSQL Parameters
```sql
-- Shared buffers (typically 25% of system RAM)
shared_buffers = 2GB

-- Work memory for sorting operations
work_mem = 16MB

-- Effective cache size (typically 50-75% of system RAM)
effective_cache_size = 6GB

-- Maintenance work memory
maintenance_work_mem = 1GB

-- Checkpoint settings
checkpoint_completion_target = 0.9
```

### Application-Level Caching
```python
from sqlalchemy import event
from sqlalchemy.pool import Pool

# Connection warmup
@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # For PostgreSQL, you might set session parameters
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TIME ZONE 'UTC';")
    cursor.close()
```

## Monitoring Queries

### Slow Query Detection
```sql
-- Enable slow query logging
SET log_min_duration_statement = 1000; -- Log queries taking more than 1 second

-- Common slow query patterns to watch for:
-- 1. Missing indexes
EXPLAIN ANALYZE SELECT * FROM task WHERE status = 'active';

-- 2. Inefficient joins
EXPLAIN ANALYZE SELECT t.*, u.name FROM task t
JOIN "user" u ON t.user_id = u.id;

-- 3. Unnecessary data transfer
EXPLAIN ANALYZE SELECT * FROM task WHERE user_id = 'some_user'; -- vs specific columns
```

## Vacuum and Maintenance

### Regular Maintenance
```sql
-- Regular vacuuming for tables with frequent updates
VACUUM ANALYZE task;

-- For heavily updated tables
VACUUM FULL ANALYZE task;
```

## Backup and Recovery Optimization

### Efficient Backup Strategies
```sql
-- Use pg_dump with appropriate options for speed
-- pg_dump -Fc --compress=6 --no-owner --no-privileges database_name

-- Consider logical replication for large databases
-- SET synchronous_commit = local; -- for faster writes (less durability)
```

## Concurrency Optimization

### Lock Management
```python
# Use appropriate isolation levels
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://...",
    isolation_level="READ_COMMITTED"  # Default and usually appropriate
)

# For specific transaction needs
def update_task_with_lock(task_id: int, session: Session):
    task = session.get(Task, task_id, with_for_update=True)
    # This uses SELECT FOR UPDATE to lock the row
    task.completed = True
    session.commit()
```

## Memory Optimization

### Connection Memory Management
```python
# Configure SQLAlchemy pool settings
engine = create_engine(
    "postgresql://...",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

These optimizations will help ensure your PostgreSQL database performs well with SQLModel-based applications, particularly for multi-tenant scenarios where query patterns and data volumes can vary significantly.