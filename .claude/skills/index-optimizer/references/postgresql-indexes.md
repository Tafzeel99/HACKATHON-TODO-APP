# PostgreSQL Index Types and Usage

Comprehensive guide to PostgreSQL index types and their optimal usage patterns.

## B-tree Indexes (Default)

Most common index type, good for equality and range queries.

```sql
-- Default index type created with SQLModel
CREATE INDEX ix_task_user_id ON task USING btree (user_id);

-- Optimizes queries like:
SELECT * FROM task WHERE user_id = 'user123';
SELECT * FROM task WHERE created_at > '2023-01-01';
SELECT * FROM task WHERE title LIKE 'Meeting%';
```

### When to Use B-tree Indexes:
- Equality comparisons (=)
- Range queries (>, <, BETWEEN)
- Pattern matching with leading wildcards (LIKE 'prefix%')
- ORDER BY and GROUP BY clauses
- Foreign key columns

## Hash Indexes

Optimized for equality comparisons only.

```sql
-- Create hash index (PostgreSQL 10+)
CREATE INDEX ix_user_hash_email ON user USING hash (email);

-- Only optimizes equality queries:
SELECT * FROM user WHERE email = 'user@example.com';
```

### When to Use Hash Indexes:
- Equality comparisons only
- Fixed-length keys
- When disk space is a concern (hash indexes are smaller)
- NOT suitable for range queries or ORDER BY

## GiST Indexes (Generalized Search Tree)

Supports multiple operators and data types.

```sql
-- For geometric data
CREATE INDEX ix_boxes_box ON boxes USING gist (box_col);

-- For range types
CREATE INDEX ix_reservation_period ON reservations USING gist (during);

-- For text search
CREATE INDEX ix_document_gist ON documents USING gist (textsearchable_plain_col_gist);
```

### When to Use GiST Indexes:
- Geometric data types
- Range types
- Full-text search
- Custom data types with GiST support

## GIN Indexes (Generalized Inverted)

Optimized for containment queries.

```sql
-- For array columns
CREATE INDEX ix_task_tags ON task USING gin (tags);

-- For JSON columns
CREATE INDEX ix_product_attrs ON product USING gin (attributes);

-- For full-text search
CREATE INDEX ix_document_gin ON documents USING gin (search_vector);
```

### When to Use GIN Indexes:
- Array columns (checking if element exists in array)
- JSON/JSONB columns (key/value existence)
- Full-text search
- When values have many elements (arrays, JSON objects)

## BRIN Indexes (Block Range INdex)

Space-efficient for large, naturally ordered tables.

```sql
-- For large tables with ordered data
CREATE INDEX ix_large_log_timestamp ON large_log_table USING brin (timestamp_col);

-- For tables with monotonic data
CREATE INDEX ix_events_created ON events USING brin (created_at);
```

### When to Use BRIN Indexes:
- Very large tables (millions of rows)
- Naturally ordered data (timestamps, sequential IDs)
- When most queries use range predicates
- When disk space is severely constrained
- Less effective for random data distribution

## Operator Classes and Collations

### Text Collation Indexes
```sql
-- Case-insensitive index
CREATE INDEX ix_user_lower_name ON user (lower(name));

-- Custom collation for locale-specific sorting
CREATE INDEX ix_user_name_de ON user (name) COLLATE "de_DE";
```

### Custom Operator Classes
```sql
-- For custom data types
CREATE INDEX ix_custom_geom ON my_table USING gist (geom gist_geometry_ops);

-- For specific operator usage
CREATE INDEX ix_text_pattern ON my_table (text_col text_pattern_ops);
```

## Advanced Index Features

### Partial Indexes
```sql
-- Index only active users
CREATE INDEX ix_active_users ON users (email) WHERE active = true;

-- Index only high-priority tasks
CREATE INDEX ix_high_priority_tasks ON tasks (created_at) WHERE priority = 'high';

-- Index with complex conditions
CREATE INDEX ix_recent_completed_tasks ON tasks (updated_at)
WHERE status = 'completed' AND updated_at > CURRENT_DATE - INTERVAL '30 days';
```

### Expression Indexes
```sql
-- Index computed values
CREATE INDEX ix_user_lower_email ON users (lower(email));

-- Index substring
CREATE INDEX ix_filename_ext ON files ((substring(filename from '[^.]*$')));

-- Index with functions
CREATE INDEX ix_task_deadline_week ON tasks (deadline + INTERVAL '7 days');
```

### Multi-Column Indexes
```sql
-- B-tree composite index
CREATE INDEX ix_user_status_created ON users (status, created_at);

-- With custom sort order
CREATE INDEX ix_events_venue_time ON events (venue_id, event_time DESC);

-- With operator classes
CREATE INDEX ix_text_search ON articles (title text_pattern_ops, content text_pattern_ops);
```

## Index Performance Considerations

### Fillfactor Parameter
```sql
-- For frequently updated tables
CREATE INDEX ix_frequently_updated ON my_table (col) WITH (fillfactor = 70);

-- For mostly read tables
CREATE INDEX ix_read_only ON my_table (col) WITH (fillfactor = 100);
```

### Concurrent Index Creation
```sql
-- Create index without locking table
CREATE INDEX CONCURRENTLY ix_slow_index ON large_table (slow_column);
```

## Monitoring and Maintenance

### Index Statistics
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- Check table vs index scans
SELECT schemaname, tablename, seq_scan, idx_scan
FROM pg_stat_user_tables
ORDER BY seq_scan DESC;
```

### Index Size
```sql
-- Check index sizes
SELECT
    t.tablename,
    indexname,
    c.reltuples::BIGINT AS num_rows,
    pg_size_pretty(pg_relation_size(quote_ident(t.tablename)::text)) AS table_size,
    pg_size_pretty(pg_relation_size(quote_ident(indexrelname)::text)) AS index_size,
    CASE WHEN x.is_unique THEN 'Y' ELSE 'N' END AS unique,
    idx_scan AS number_of_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_tables t
LEFT JOIN pg_class c ON t.tablename=c.relname
LEFT JOIN pg_indexes x ON t.tablename = x.tablename
LEFT JOIN pg_stat_user_indexes psui ON x.indexname = psui.indexrelname
WHERE t.schemaname='public'
ORDER BY 1,2;
```

## Index Anti-Patterns

### Over-Indexing
```sql
-- DON'T do this - too many indexes on one table
CREATE INDEX ix_col1 ON table (col1);
CREATE INDEX ix_col2 ON table (col2);
CREATE INDEX ix_col3 ON table (col3);
CREATE INDEX ix_col4 ON table (col4);
-- ... every column has an index

-- DO this instead - focus on query patterns
CREATE INDEX ix_common_query ON table (col1, col2);  -- For common queries
CREATE INDEX ix_lookup ON table (col3);             -- For lookups
```

### Wrong Column Order in Composite Indexes
```sql
-- WRONG - if queries often filter by status first
CREATE INDEX ix_wrong_order ON tasks (user_id, status);

-- CORRECT - put most selective/queried column first
CREATE INDEX ix_correct_order ON tasks (status, user_id);
```

These PostgreSQL-specific indexing strategies will help optimize your SQLModel applications for maximum performance.