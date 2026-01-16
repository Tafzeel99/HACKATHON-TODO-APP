# Performance Tuning Patterns and Benchmarks

Performance optimization patterns and benchmarking methodologies for database applications.

## Performance Patterns

### Multi-Tenant Query Optimization
```python
# Pattern: Always filter by tenant first in multi-tenant applications
class Task(SQLModel, table=True):
    __table_args__ = (
        # Composite index with tenant ID first
        Index("ix_task_user_status", "user_id", "status"),
        Index("ix_task_user_created", "user_id", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)  # Secondary index
    status: str = Field(default="pending", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Efficient query pattern
def get_user_tasks_efficient(user_id: str, status: str = None, session):
    query = select(Task).where(Task.user_id == user_id)  # Uses composite index
    if status:
        query = query.where(Task.status == status)       # Still uses composite index
    return session.exec(query.order_by(Task.created_at.desc())).all()

# Inefficient query pattern (DON'T do this)
def get_user_tasks_inefficient(status: str, session):
    # This forces a sequential scan or inefficient index usage
    return session.exec(
        select(Task).where(Task.status == status)
    ).all()
```

### Batch Processing Patterns
```python
# Pattern: Use batch operations for bulk inserts/updates
def batch_insert_tasks(tasks: List[Task], session, batch_size: int = 1000):
    """Efficiently insert tasks in batches to avoid transaction locks"""
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        session.add_all(batch)
        session.flush()  # Sync IDs without committing
    session.commit()

def batch_update_tasks(task_updates: List[dict], session, batch_size: int = 1000):
    """Efficiently update tasks in batches"""
    for i in range(0, len(task_updates), batch_size):
        batch = task_updates[i:i + batch_size]
        for update_data in batch:
            task = session.get(Task, update_data["id"])
            for key, value in update_data.items():
                setattr(task, key, value)
        session.flush()
    session.commit()
```

### Connection Pooling Patterns
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Pattern: Configure appropriate connection pooling
engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=20,              # Number of connections to maintain
    max_overflow=30,           # Additional connections beyond pool_size
    pool_pre_ping=True,        # Validate connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False                 # Set to True for query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pattern: Use sessions efficiently
def get_db():
    """FastAPI dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Query Optimization Patterns

### Efficient Filtering
```python
# Pattern: Use EXISTS instead of COUNT for existence checks
def user_has_active_tasks(user_id: str, session):
    # Efficient - stops at first match
    stmt = select(exists().where(and_(Task.user_id == user_id, Task.status == "active")))
    return session.exec(stmt).scalar()

def user_has_active_tasks_slow(user_id: str, session):
    # Inefficient - counts all matches
    stmt = select(func.count(Task.id)).where(and_(Task.user_id == user_id, Task.status == "active"))
    count = session.exec(stmt).scalar()
    return count > 0
```

### Pagination Optimization
```python
# Pattern: Use cursor-based pagination for large datasets
def get_tasks_cursor_pagination(
    user_id: str,
    last_task_id: Optional[int] = None,
    limit: int = 50,
    session
):
    """Efficient pagination using cursor-based approach"""
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.id)

    if last_task_id:
        stmt = stmt.where(Task.id > last_task_id)

    stmt = stmt.limit(limit)
    return session.exec(stmt).all()

def get_tasks_offset_pagination(
    user_id: str,
    offset: int = 0,
    limit: int = 50,
    session
):
    """Less efficient offset-based pagination (performance degrades with large offsets)"""
    stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.id)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(stmt).all()
```

### Join Optimization
```python
# Pattern: Optimize joins with proper indexing
class Task(SQLModel, table=True):
    __table_args__ = (
        Index("ix_task_user_project", "user_id", "project_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    project_id: Optional[int] = Field(foreign_key="project.id", index=True)

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str

# Efficient join query
def get_user_tasks_with_projects(user_id: str, session):
    stmt = (
        select(Task, Project)
        .join(Project, Task.project_id == Project.id)
        .where(Task.user_id == user_id)  # Uses composite index
        .where(Project.user_id == user_id)  # Additional tenant filter
    )
    return session.exec(stmt).all()
```

## Caching Patterns

### Application-Level Caching
```python
from functools import lru_cache
import hashlib

# Pattern: Cache expensive queries
@lru_cache(maxsize=128)
def get_user_summary_cached(user_id: str, session_hash: str):
    """Cache user summary data"""
    # This is a simplified example - in practice you'd need cache invalidation
    pass

# Pattern: Use Redis for distributed caching
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_user_tasks_with_cache(user_id: str, session, ttl: int = 300):
    """Get user tasks with Redis caching"""
    cache_key = f"user_tasks:{user_id}"

    # Try to get from cache
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    # Fetch from database
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    # Cache the result
    redis_client.setex(
        cache_key,
        ttl,
        json.dumps([task.dict() for task in tasks])
    )

    return tasks
```

## Benchmarking Methodologies

### Performance Testing Framework
```python
import time
import statistics
from contextlib import contextmanager
from typing import Callable, Any

@contextmanager
def timer():
    """Context manager to time code execution"""
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"Execution time: {end - start:.4f} seconds")

def benchmark_function(
    func: Callable,
    *args,
    iterations: int = 10,
    **kwargs
) -> dict:
    """Benchmark a function with multiple iterations"""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "times": times
    }

# Example usage
def benchmark_query_performance(session):
    """Benchmark different query approaches"""

    # Benchmark 1: Query with index
    with timer():
        results1 = session.exec(
            select(Task).where(Task.user_id == "user123")
        ).all()

    # Benchmark 2: Query without index (if applicable)
    with timer():
        results2 = session.exec(
            select(Task).where(Task.title.contains("important"))
        ).all()

    return {"indexed_query": len(results1), "full_scan_query": len(results2)}
```

### Load Testing Patterns
```python
import asyncio
import aiohttp
from typing import List

async def simulate_concurrent_load(
    base_url: str,
    endpoints: List[str],
    concurrency: int = 10,
    requests_per_client: int = 100
):
    """Simulate concurrent load on API endpoints"""

    async def make_request(session: aiohttp.ClientSession, url: str):
        start = time.time()
        try:
            async with session.get(url) as response:
                resp_time = time.time() - start
                return {
                    "url": url,
                    "status": response.status,
                    "response_time": resp_time,
                    "success": response.status == 200
                }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "response_time": time.time() - start,
                "success": False
            }

    async def client(client_id: int):
        async with aiohttp.ClientSession() as session:
            results = []
            for _ in range(requests_per_client):
                endpoint = endpoints[client_id % len(endpoints)]
                url = f"{base_url}{endpoint}"
                result = await make_request(session, url)
                results.append(result)
            return results

    # Run concurrent clients
    tasks = [client(i) for i in range(concurrency)]
    all_results = await asyncio.gather(*tasks)

    # Flatten results
    flat_results = [item for sublist in all_results for item in sublist]

    # Calculate statistics
    successful_requests = [r for r in flat_results if r["success"]]
    response_times = [r["response_time"] for r in successful_requests]

    return {
        "total_requests": len(flat_results),
        "successful_requests": len(successful_requests),
        "failure_rate": (len(flat_results) - len(successful_requests)) / len(flat_results),
        "avg_response_time": statistics.mean(response_times) if response_times else 0,
        "p95_response_time": sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0,
        "results": flat_results
    }
```

## Performance Monitoring

### Query Performance Monitoring
```python
import logging
from functools import wraps

def monitor_query_performance(threshold_ms: float = 100.0):
    """Decorator to monitor query performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()

            duration_ms = (end - start) * 1000

            if duration_ms > threshold_ms:
                logging.warning(
                    f"SLOW QUERY: {func.__name__} took {duration_ms:.2f}ms "
                    f"(threshold: {threshold_ms}ms)"
                )

            return result
        return wrapper
    return decorator

# Usage
@monitor_query_performance(threshold_ms=50.0)
def get_user_tasks(user_id: str, session):
    return session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
```

### Database Performance Indicators
```python
def get_database_performance_indicators(session):
    """Get key database performance indicators"""

    # Query cache hit ratio
    cache_hit_query = """
        SELECT
            sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
        FROM pg_statio_user_tables;
    """

    # Index usage statistics
    index_usage_query = """
        SELECT
            schemaname,
            tablename,
            (100 * idx_scan / (seq_scan + idx_scan)) as percent_of_times_index_used,
            n_live_tup as rows_in_table
        FROM pg_stat_user_tables
        WHERE (seq_scan + idx_scan) > 0
        ORDER BY n_live_tup DESC;
    """

    # Slow queries
    slow_queries_query = """
        SELECT
            query,
            mean_time,
            calls,
            total_time
        FROM pg_stat_statements
        ORDER BY mean_time DESC
        LIMIT 10;
    """

    # Execute queries and return results
    # (Implementation would depend on how you access these PostgreSQL-specific queries)

    return {
        "cache_hit_ratio": 0.95,  # Example value
        "large_tables": [],       # Tables with high row counts
        "inefficient_indexes": [], # Indexes with low usage
        "slow_queries": []        # List of slow queries
    }
```

These performance patterns and benchmarking methodologies will help optimize your SQLModel applications and ensure they scale effectively with growing data volumes and user loads.