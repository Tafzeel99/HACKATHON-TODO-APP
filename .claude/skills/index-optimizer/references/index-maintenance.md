# Index Maintenance Procedures

Procedures and best practices for maintaining database indexes over time.

## Index Health Monitoring

### Identifying Bloated Indexes
```sql
-- Find indexes with high bloat ratio
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(real_size) AS real_size,
    pg_size_pretty(bloat_size) AS bloat_size,
    ROUND(bloat_ratio, 2) AS bloat_ratio,
    btree_entries_ct,
    page_hdr,
    maxalign
FROM (
    SELECT
        schemaname,
        tablename,
        indexname,
        btree_page_itemsPerPage::INTEGER AS btree_entries_ct,
        page_hdr,
        maxalign,
        fillfactor,
        basect,
        bs,
        page_opaque_ct,
        COALESCE(btree_page_allocated, 0) AS real_size,
        COALESCE(btree_page_wasted, 0) AS bloat_size,
        CASE
            WHEN btree_page_allocated > 0 THEN btree_page_wasted::FLOAT / btree_page_allocated
            ELSE 0
        END AS bloat_ratio
    FROM (
        SELECT
            schemaname,
            tablename,
            indexname,
            24 AS page_hdr,
            8 AS maxalign,
            20 AS page_opaque_ct,
            8192 AS bs,
            20 AS fillfactor,
            20 AS basect,
            (20 + (maxalign - (20 % maxalign)) % maxalign) AS btree_page_itemsPerPage,
            (bs - page_hdr) / ((maxalign - (tuple_data_hdr % maxalign)) % maxalign + tuple_data_len + target_page_fill * (page_opaque_ct + 1)) AS btree_page_allocated,
            (bs - page_hdr) / ((maxalign - (tuple_data_hdr % maxalign)) % maxalign + tuple_data_len + target_page_fill * (page_opaque_ct + 1)) - (bs - page_hdr) / ((maxalign - (tuple_data_hdr % maxalign)) % maxalign + tuple_data_len + target_page_fill * (page_opaque_ct + 1)) * (fillfactor / 100) AS btree_page_wasted
        FROM (
            SELECT
                schemaname,
                tablename,
                indexname,
                24 AS page_hdr,
                8 AS maxalign,
                (20 + (maxalign - (20 % maxalign)) % maxalign) AS tuple_data_hdr,
                20 AS tuple_data_len,
                0.9 AS target_page_fill
            FROM pg_stat_user_indexes
        ) AS sub
    ) AS sub2
) AS bloat_calc
WHERE bloat_size > 1024^2  -- Only show indexes with more than 1MB bloat
ORDER BY bloat_size DESC;
```

## Index Maintenance Operations

### Rebuilding Indexes
```sql
-- Rebuild fragmented index
REINDEX INDEX ix_tasks_user_id;

-- Rebuild all indexes on a table
REINDEX TABLE tasks;

-- Rebuild indexes concurrently (doesn't lock table)
REINDEX INDEX CONCURRENTLY ix_tasks_user_id;

-- Rebuild with specific fillfactor
CREATE INDEX CONCURRENTLY ix_tasks_user_id_new ON tasks (user_id) WITH (fillfactor = 80);
DROP INDEX ix_tasks_user_id;
ALTER INDEX ix_tasks_user_id_new RENAME TO ix_tasks_user_id;
```

### Analyzing Table Statistics
```sql
-- Update statistics for better query planning
ANALYZE tasks;

-- Update statistics for specific columns
ANALYZE tasks (user_id, status, created_at);

-- Update statistics for all tables in schema
ANALYZE;
```

### Vacuum Operations
```sql
-- Standard vacuum (reclaims space and updates statistics)
VACUUM tasks;

-- Full vacuum (reclaims space and compacts table)
VACUUM FULL tasks;

-- Analyze with vacuum
VACUUM ANALYZE tasks;

-- Concurrent vacuum for large tables (PostgreSQL 12+)
VACUUM (FREEZE, ANALYZE) tasks;
```

## Performance Monitoring

### Query Performance Tracking
```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Track slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE userid = (SELECT usesysid FROM pg_user WHERE usename = current_user)
ORDER BY mean_time DESC
LIMIT 10;
```

### Index Performance Comparison
```sql
-- Compare index usage before and after optimization
WITH before AS (
    SELECT 'before' as period, indexname, idx_scan, idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE indexname = 'ix_tasks_user_status'
),
after AS (
    SELECT 'after' as period, indexname, idx_scan, idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE indexname = 'ix_tasks_user_status'
)
SELECT
    b.period,
    b.idx_scan as before_scans,
    a.idx_scan as after_scans,
    a.idx_scan - b.idx_scan as scan_difference,
    b.idx_tup_fetch as before_fetches,
    a.idx_tup_fetch as after_fetches
FROM before b
CROSS JOIN after a;
```

## Automated Maintenance

### Maintenance Schedule
```sql
-- Example cron job for daily maintenance
-- 02:00 AM: Update statistics
0 2 * * * psql -d mydb -c "ANALYZE;"

# Weekly: Vacuum analyze all tables
0 3 * * 0 psql -d mydb -c "VACUUM ANALYZE;"

# Monthly: Rebuild heavily fragmented indexes
0 4 1 * * psql -d mydb -c "REINDEX DATABASE mydb;"
```

### Maintenance Script
```sql
-- Function to identify and rebuild fragmented indexes
CREATE OR REPLACE FUNCTION check_and_rebuild_indexes(threshold_bloat_mb INTEGER DEFAULT 100)
RETURNS TABLE(index_name TEXT, bloat_mb INTEGER, action_taken TEXT) AS $$
DECLARE
    index_record RECORD;
BEGIN
    FOR index_record IN
        SELECT indexname
        FROM pg_stat_user_indexes
        WHERE pg_relation_size(indexrelid) > threshold_bloat_mb * 1024 * 1024
        AND idx_scan > 100  -- Only consider indexes that are actually used
    LOOP
        -- Log the action
        index_name := index_record.indexname;
        bloat_mb := pg_size_bytes(pg_size_pretty(pg_relation_size(index_record.indexname::regclass))) / (1024*1024);
        action_taken := 'REINDEX CONCURRENTLY ' || index_record.indexname;

        -- Perform reindex (comment out in production until tested)
        -- EXECUTE 'REINDEX INDEX CONCURRENTLY ' || index_record.indexname;

        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Use the function
SELECT * FROM check_and_rebuild_indexes(50);  -- Check indexes with >50MB bloat
```

## Index Lifecycle Management

### Adding New Indexes
```sql
-- Create index with monitoring
CREATE INDEX CONCURRENTLY ix_new_index ON table (column);

-- Verify the index is being used
SELECT * FROM pg_stat_user_indexes WHERE indexname = 'ix_new_index';

-- Check query performance improvement
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM table WHERE column = 'value';
```

### Removing Unused Indexes
```sql
-- First, monitor for a period to ensure it's truly unused
SELECT indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE indexname = 'candidate_for_removal'
AND idx_scan = 0;

-- If confirmed unused, drop the index
DROP INDEX IF EXISTS candidate_for_removal;

-- Monitor performance after removal to ensure no regression
```

## Performance Benchmarks

### Baseline Measurement
```sql
-- Establish baseline query performance
CREATE TEMP TABLE perf_baseline AS
SELECT
    'query_1' as query_name,
    EXTRACT(EPOCH FROM NOW()) as timestamp,
    (SELECT mean_time FROM pg_stat_statements WHERE query ~ 'SELECT.*FROM tasks.*WHERE user_id') as mean_time
LIMIT 1;

-- Compare performance before and after index changes
```

### Regression Testing
```sql
-- Function to test query performance
CREATE OR REPLACE FUNCTION test_query_performance(query_text TEXT, iterations INTEGER DEFAULT 100)
RETURNS TABLE(avg_time_ms NUMERIC, min_time_ms NUMERIC, max_time_ms NUMERIC) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    total_time INTERVAL := '0';
    min_time INTERVAL;
    max_time INTERVAL;
    i INTEGER;
    single_time INTERVAL;
BEGIN
    FOR i IN 1..iterations LOOP
        start_time := clock_timestamp();
        EXECUTE query_text;
        end_time := clock_timestamp();
        single_time := end_time - start_time;

        total_time := total_time + single_time;
        IF i = 1 OR single_time < min_time THEN
            min_time := single_time;
        END IF;
        IF i = 1 OR single_time > max_time THEN
            max_time := single_time;
        END IF;
    END LOOP;

    avg_time_ms := EXTRACT(EPOCH FROM (total_time / iterations)) * 1000;
    min_time_ms := EXTRACT(EPOCH FROM min_time) * 1000;
    max_time_ms := EXTRACT(EPOCH FROM max_time) * 1000;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Use the function to test performance
SELECT * FROM test_query_performance('SELECT * FROM tasks WHERE user_id = ''user123''');
```

These maintenance procedures will help ensure your indexes remain effective and efficient over time, preventing performance degradation as data volumes grow.