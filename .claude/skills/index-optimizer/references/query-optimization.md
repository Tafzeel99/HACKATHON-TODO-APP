# Query Optimization Strategies

Techniques and patterns for analyzing and optimizing slow queries in PostgreSQL.

## Query Analysis Tools

### EXPLAIN and EXPLAIN ANALYZE
```sql
-- Basic query plan
EXPLAIN SELECT * FROM tasks WHERE user_id = 'user123';

-- Actual execution statistics
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 'user123';

-- Detailed format
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM tasks WHERE user_id = 'user123';
```

### Understanding Query Plans
```sql
-- Sample output interpretation
Seq Scan on tasks  (cost=0.00..18.50 rows=5 width=140) (actual time=0.021..0.112 rows=5 loops=1)
  Filter: ((user_id)::text = 'user123'::text)
  Rows Removed by Filter: 95

-- Key metrics:
-- cost: Estimated startup cost and total cost
-- rows: Estimated number of rows output
-- width: Average row size in bytes
-- actual time: Actual execution time
-- loops: Number of times this plan node was executed
```

## Common Query Performance Issues

### Sequential Scans
```sql
-- PROBLEM: Full table scan
Seq Scan on tasks  (cost=0.00..18.50 rows=5 width=140)
  Filter: ((user_id)::text = 'user123'::text)

-- SOLUTION: Add index
CREATE INDEX ix_tasks_user_id ON tasks (user_id);

-- OPTIMIZED: Index scan
Index Scan using ix_tasks_user_id on tasks  (cost=0.00..8.27 rows=5 width=140)
```

### Inefficient Joins
```sql
-- PROBLEM: Nested loop join on large tables
EXPLAIN SELECT u.name, t.title
FROM users u
JOIN tasks t ON u.id = t.user_id;

-- SOLUTION: Ensure join columns are indexed
CREATE INDEX ix_tasks_user_id ON tasks (user_id);
CREATE INDEX ix_users_id ON users (id);  -- Usually primary key

-- OPTIMIZED: Hash join or merge join
Hash Join  (cost=25.50..50.75 rows=100 width=140)
  Hash Cond: (t.user_id = u.id)
```

### Missing Indexes
```sql
-- PROBLEM: No index for WHERE clause
SELECT * FROM tasks
WHERE status = 'completed' AND created_at > '2023-01-01';

-- SOLUTION: Create composite index
CREATE INDEX ix_tasks_status_created ON tasks (status, created_at);
```

## Index Optimization Techniques

### Index Usage Analysis
```sql
-- Check which indexes are being used
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0  -- Unused indexes
ORDER BY idx_tup_read ASC;

-- Check table scan statistics
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;
```

### Index Candidate Identification
```sql
-- Find queries with high execution time
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Find queries with many calls
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;
```

## Query Rewrite Techniques

### Avoid SELECT *
```sql
-- SLOW: Fetches all columns
SELECT * FROM tasks WHERE user_id = 'user123';

-- FAST: Fetch only needed columns
SELECT id, title, completed FROM tasks WHERE user_id = 'user123';
```

### Optimize WHERE Clauses
```sql
-- SLOW: Function on column prevents index usage
SELECT * FROM tasks WHERE lower(title) = lower('Important');

-- FAST: Function on constant or use ILIKE
SELECT * FROM tasks WHERE title ILIKE 'Important';

-- SLOW: Leading wildcard prevents index usage
SELECT * FROM tasks WHERE title LIKE '%meeting%';

-- FAST: If possible, use leading text
SELECT * FROM tasks WHERE title LIKE 'meeting%';
```

### Efficient Pagination
```sql
-- SLOW: OFFSET becomes slower with large offsets
SELECT * FROM tasks ORDER BY id LIMIT 10 OFFSET 10000;

-- FAST: Cursor-based pagination
SELECT * FROM tasks WHERE id > 10000 ORDER BY id LIMIT 10;
```

## Advanced Query Optimization

### Query Hints and Force Indexing
```sql
-- Disable sequential scans temporarily for testing
SET enable_seqscan = OFF;

-- Force index usage
SELECT /*+ IndexScan(tasks ix_tasks_user_id) */ * FROM tasks WHERE user_id = 'user123';
```

### Partitioning for Large Tables
```sql
-- Range partitioning example
CREATE TABLE tasks_partitioned (
    id SERIAL,
    user_id VARCHAR(255),
    title TEXT,
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE tasks_2023_01 PARTITION OF tasks_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

-- This makes queries with date ranges much faster
SELECT * FROM tasks_partitioned WHERE created_at BETWEEN '2023-01-15' AND '2023-01-20';
```

### Materialized Views for Complex Aggregations
```sql
-- Create materialized view for expensive aggregations
CREATE MATERIALIZED VIEW user_task_summary AS
SELECT
    user_id,
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE completed = true) as completed_tasks,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_completion_time
FROM tasks
GROUP BY user_id;

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY user_task_summary;

-- Query becomes very fast
SELECT * FROM user_task_summary WHERE user_id = 'user123';
```

## Slow Query Identification

### Using pg_stat_statements
```sql
-- Enable pg_stat_statements if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slowest queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE userid = (SELECT usesysid FROM pg_user WHERE usename = current_user)
ORDER BY mean_time DESC
LIMIT 10;
```

### Using Log Analysis
```sql
-- Enable slow query logging
SET log_min_duration_statement = 1000; -- Log queries taking more than 1 second

-- In postgresql.conf
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

## Monitoring and Profiling

### Real-time Query Monitoring
```sql
-- Active queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
AND state = 'active';
```

### Performance Metrics Collection
```sql
-- Collect performance metrics
SELECT
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_tup_hot_upd,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_tup_upd DESC;
```

## Common Optimization Patterns

### For Multi-Tenant Applications
```sql
-- PROBLEM: Slow multi-tenant queries
SELECT * FROM tasks WHERE user_id = 'user123' AND status = 'active';

-- SOLUTION: Composite index with tenant first
CREATE INDEX ix_tasks_user_status ON tasks (user_id, status);

-- Even better: Partial index for common tenant patterns
CREATE INDEX ix_active_user_tasks ON tasks (user_id) WHERE status = 'active';
```

### For Time-Series Data
```sql
-- PROBLEM: Slow date range queries
SELECT * FROM events WHERE created_at BETWEEN '2023-01-01' AND '2023-01-31';

-- SOLUTION: Index on date column
CREATE INDEX ix_events_created_at ON events (created_at);

-- For range queries, consider BRIN for large tables
CREATE INDEX ix_large_events_brin ON events USING brin (created_at);
```

### For Text Search
```sql
-- PROBLEM: Slow text search
SELECT * FROM documents WHERE content LIKE '%search_term%';

-- SOLUTION: Full-text search
CREATE INDEX ix_documents_content_search ON documents USING gin (to_tsvector('english', content));

-- Query becomes:
SELECT * FROM documents
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'search_term');
```

These query optimization techniques will help identify and resolve performance bottlenecks in your PostgreSQL database, particularly for SQLModel-based applications.