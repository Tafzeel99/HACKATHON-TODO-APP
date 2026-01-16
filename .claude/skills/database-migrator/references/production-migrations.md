# Production Migrations Guide

This guide covers best practices for running database migrations in production environments.

## Pre-Migration Checklist

### 1. Backup Strategy
```bash
# Always backup before production migrations
# PostgreSQL
pg_dump -h hostname -U username -d database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# MySQL
mysqldump -h hostname -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite
cp database.sqlite backup_$(date +%Y%m%d_%H%M%S).sqlite
```

### 2. Test Environment Validation
```python
# Before running in production, validate in staging
def validate_migration_staging():
    """
    Run comprehensive tests on staging environment before production
    """
    # 1. Test upgrade
    run_command("alembic upgrade head")

    # 2. Run data integrity tests
    run_data_integrity_tests()

    # 3. Test downgrade
    run_command("alembic downgrade -1")

    # 4. Test upgrade again
    run_command("alembic upgrade head")

    # 5. Run performance tests
    run_performance_tests()
```

### 3. Migration Validation Script
```python
# validate_migration.py
import subprocess
import sys
from sqlalchemy import create_engine, inspect

def validate_migration(connection_string, migration_revision):
    """
    Validate that a migration will work correctly
    """
    engine = create_engine(connection_string)
    inspector = inspect(engine)

    # Check current state
    current_tables = inspector.get_table_names()
    print(f"Current tables: {current_tables}")

    # Dry run migration (if supported by database)
    # This is database-specific

    # Validate migration file syntax
    try:
        # Import and validate migration file
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration", f"alembic/versions/{migration_revision}.py")
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)

        # Check if upgrade and downgrade functions exist
        assert hasattr(migration_module, 'upgrade'), "Missing upgrade function"
        assert hasattr(migration_module, 'downgrade'), "Missing downgrade function"

        print("Migration file syntax is valid")
        return True

    except Exception as e:
        print(f"Migration file validation failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_migration.py <connection_string> <revision_id>")
        sys.exit(1)

    connection_string = sys.argv[1]
    revision = sys.argv[2]

    success = validate_migration(connection_string, revision)
    sys.exit(0 if success else 1)
```

## Production Migration Procedures

### 1. Blue-Green Deployment Pattern
```bash
#!/bin/bash
# production_migration.sh

set -e  # Exit on any error

# Configuration
ENVIRONMENT="production"
DATABASE_URL="postgresql://user:pass@host/db"
MIGRATION_TARGET="head"
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"

echo "Starting production migration for $ENVIRONMENT"

# 1. Prepare backup
echo "Creating database backup..."
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# 2. Check current migration status
echo "Checking current migration status..."
alembic current

# 3. Validate migration script
echo "Validating migration script..."
python validate_migration.py "$DATABASE_URL" "$MIGRATION_TARGET"

# 4. Run migration in dry-run mode (if supported)
echo "Running migration dry-run..."
# Some databases support dry-run, others require transaction rollback test

# 5. Perform migration with monitoring
echo "Starting migration..."
START_TIME=$(date +%s)

# Redirect to file for logging
{
    alembic upgrade "$MIGRATION_TARGET"
} 2>&1 | tee migration_$(date +%Y%m%d_%H%M%S).log

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "Migration completed in ${DURATION}s"

# 6. Verify migration success
echo "Verifying migration..."
alembic current

# 7. Run post-migration health checks
echo "Running post-migration checks..."
python run_health_checks.py

echo "Production migration completed successfully!"
```

### 2. Gradual Rollout Pattern
```python
# gradual_migration.py
import time
import logging
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gradual_migration(database_urls, migration_steps):
    """
    Apply migrations gradually across multiple database instances
    """
    for i, db_url in enumerate(database_urls):
        logger.info(f"Migrating database instance {i+1}/{len(database_urls)}")

        # Create engine for this instance
        engine = create_engine(db_url)

        # Configure Alembic for this instance
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        # Apply migration to this instance
        for step in migration_steps:
            logger.info(f"Applying step: {step}")
            command.upgrade(alembic_cfg, step)

            # Health check after each step
            if not health_check(db_url):
                logger.error(f"Health check failed for instance {i+1}, rolling back...")
                # Implement rollback logic
                return False

            # Wait between instances to allow for traffic rebalancing
            if i < len(database_urls) - 1:  # Don't wait after last instance
                time.sleep(30)  # 30 seconds between instances

        logger.info(f"Successfully migrated instance {i+1}")

    return True

def health_check(db_url):
    """
    Perform health check on database instance
    """
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Simple query to test connectivity and basic functionality
            result = conn.execute("SELECT 1").fetchone()
            return result[0] == 1
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False
```

## Rollback Procedures

### 1. Automated Rollback Script
```python
# rollback_migration.py
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rollback_migration(database_url, target_revision=None, steps_back=1):
    """
    Rollback migration with safety checks
    """
    try:
        # Configure Alembic
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        # Get current revision before rollback
        current_rev = command.current(alembic_cfg)
        logger.info(f"Current revision before rollback: {current_rev}")

        # Determine target revision
        if target_revision:
            rollback_target = target_revision
        else:
            rollback_target = f"-{steps_back}"

        logger.info(f"Rolling back to: {rollback_target}")

        # Perform rollback
        command.downgrade(alembic_cfg, rollback_target)

        # Verify rollback
        new_rev = command.current(alembic_cfg)
        logger.info(f"Current revision after rollback: {new_rev}")

        if new_rev != target_revision and steps_back == 1:
            # Verify we moved back one revision
            # This is a simplified check - implement more sophisticated verification as needed
            pass

        logger.info("Rollback completed successfully")
        return True

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        return False

def emergency_rollback(database_url, backup_file):
    """
    Emergency rollback using database backup
    """
    logger.info("Starting emergency rollback...")

    # 1. Stop application traffic to database
    stop_application_traffic()

    # 2. Restore from backup
    restore_from_backup(database_url, backup_file)

    # 3. Restart application
    start_application_traffic()

    logger.info("Emergency rollback completed")

def stop_application_traffic():
    """
    Implementation depends on your deployment setup
    """
    # Examples:
    # - Update load balancer to drain connections
    # - Scale down application instances
    # - Update DNS to point to standby
    pass

def restore_from_backup(database_url, backup_file):
    """
    Restore database from backup file
    """
    import subprocess

    if database_url.startswith('postgresql'):
        cmd = f"psql {database_url} < {backup_file}"
    elif database_url.startswith('mysql'):
        cmd = f"mysql {database_url} < {backup_file}"
    elif database_url.endswith('.sqlite'):
        cmd = f"cp {backup_file} {database_url.replace('sqlite:///', '')}"
    else:
        raise ValueError(f"Unsupported database type: {database_url}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Restore failed: {result.stderr}")

    logger.info(f"Restored from backup: {backup_file}")

def start_application_traffic():
    """
    Resume application traffic
    """
    # Reverse of stop_application_traffic
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rollback_migration.py <database_url> [target_revision|steps_back]")
        sys.exit(1)

    db_url = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None

    if target and target.startswith('-'):
        # It's a number of steps back
        steps = int(target)
        success = rollback_migration(db_url, steps_back=abs(steps))
    else:
        # It's a target revision
        success = rollback_migration(db_url, target_revision=target)

    sys.exit(0 if success else 1)
```

### 2. Migration Safety Wrapper
```python
# safe_migration_runner.py
import time
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command

logger = logging.getLogger(__name__)

class SafeMigrationRunner:
    def __init__(self, database_url, alembic_ini="alembic.ini"):
        self.database_url = database_url
        self.alembic_ini = alembic_ini
        self.engine = create_engine(database_url)
        self.alembic_cfg = Config(alembic_ini)
        self.alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    @contextmanager
    def migration_context(self, timeout_minutes=30):
        """
        Context manager for safe migration execution
        """
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        # Store original state
        original_revision = command.current(self.alembic_cfg)
        logger.info(f"Starting migration from revision: {original_revision}")

        try:
            yield
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            # Attempt rollback
            try:
                logger.info("Attempting automatic rollback...")
                command.downgrade(self.alembic_cfg, original_revision)
                logger.info("Automatic rollback completed")
            except Exception as rollback_error:
                logger.error(f"Automatic rollback failed: {rollback_error}")
                logger.error("Manual intervention required!")

            raise
        finally:
            # Check if we're still within timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.warning(f"Migration took {elapsed:.2f}s, exceeding timeout of {timeout_seconds}s")

    def run_migration(self, target="head", validate_after=True):
        """
        Run migration with safety checks
        """
        with self.migration_context():
            # Pre-migration validation
            if not self.pre_migration_check():
                raise Exception("Pre-migration validation failed")

            # Run migration
            logger.info(f"Running migration to: {target}")
            command.upgrade(self.alembic_cfg, target)

            # Post-migration validation
            if validate_after and not self.post_migration_check():
                raise Exception("Post-migration validation failed")

            logger.info("Migration completed successfully")

    def pre_migration_check(self):
        """
        Perform pre-migration validation
        """
        # Check database connectivity
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Database connectivity check failed: {e}")
            return False

        # Check available disk space (implementation depends on your needs)
        # Check for long-running transactions
        # Check replication lag (for replicated databases)

        logger.info("Pre-migration checks passed")
        return True

    def post_migration_check(self):
        """
        Perform post-migration validation
        """
        # Check database connectivity
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Post-migration connectivity check failed: {e}")
            return False

        # Run basic application queries to ensure functionality
        # Check for any obvious data corruption
        # Verify that expected tables/columns exist

        logger.info("Post-migration checks passed")
        return True

# Usage
if __name__ == "__main__":
    runner = SafeMigrationRunner("postgresql://user:pass@host/db")
    runner.run_migration(target="head")
```

## Monitoring and Observability

### 1. Migration Monitoring Script
```python
# monitor_migration.py
import time
import logging
import psutil
from sqlalchemy import create_engine
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationMonitor:
    def __init__(self, database_url):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.start_time = None
        self.metrics = {}

    def start_monitoring(self):
        """
        Start monitoring system resources during migration
        """
        self.start_time = time.time()
        logger.info("Starting migration monitoring...")

        # Monitor initial state
        self.metrics['start_time'] = datetime.now().isoformat()
        self.metrics['initial_cpu'] = psutil.cpu_percent()
        self.metrics['initial_memory'] = psutil.virtual_memory().percent
        self.metrics['initial_disk'] = psutil.disk_usage('/').percent

        # Start background monitoring
        import threading
        self.monitoring_thread = threading.Thread(target=self._continuous_monitor)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def _continuous_monitor(self):
        """
        Continuously monitor system resources
        """
        max_cpu = self.metrics['initial_cpu']
        max_memory = self.metrics['initial_memory']
        max_disk = self.metrics['initial_disk']

        while True:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            max_cpu = max(max_cpu, cpu)
            max_memory = max(max_memory, memory)
            max_disk = max(max_disk, disk)

            # Log warnings if resources exceed thresholds
            if cpu > 90:
                logger.warning(f"High CPU usage: {cpu}%")
            if memory > 90:
                logger.warning(f"High memory usage: {memory}%")
            if disk > 90:
                logger.warning(f"High disk usage: {disk}%")

            time.sleep(5)  # Monitor every 5 seconds

    def stop_monitoring(self):
        """
        Stop monitoring and return metrics
        """
        end_time = time.time()
        duration = end_time - self.start_time

        self.metrics['duration_seconds'] = duration
        self.metrics['end_time'] = datetime.now().isoformat()

        logger.info(f"Migration completed in {duration:.2f} seconds")
        return self.metrics

# Integration with migration runner
def run_monitored_migration(database_url, target_revision):
    """
    Run migration with monitoring
    """
    monitor = MigrationMonitor(database_url)
    monitor.start_monitoring()

    try:
        # Run your migration here
        # This is where you'd call alembic upgrade
        pass
    finally:
        metrics = monitor.stop_monitoring()
        logger.info(f"Migration metrics: {metrics}")

        # Log to monitoring system
        log_metrics_to_monitoring_system(metrics)

def log_metrics_to_monitoring_system(metrics):
    """
    Send metrics to your monitoring system (Prometheus, DataDog, etc.)
    """
    # Implementation depends on your monitoring setup
    pass
```

## Zero-Downtime Migration Patterns

### 1. Online Schema Change Pattern
```python
# online_schema_change.py
import time
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

def online_column_addition(database_url, table_name, column_definition):
    """
    Add column with minimal locking (MySQL/PostgreSQL specific)
    """
    engine = create_engine(database_url)

    # For MySQL with pt-online-schema-change or similar tools
    # For PostgreSQL, ADD COLUMN is typically fast
    with engine.connect() as conn:
        # Begin transaction
        trans = conn.begin()

        try:
            # Add column (usually fast in PostgreSQL)
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_definition}"
            conn.execute(text(alter_sql))

            # Commit transaction
            trans.commit()
            logger.info(f"Column added to {table_name}")

        except Exception as e:
            trans.rollback()
            logger.error(f"Column addition failed: {e}")
            raise

def online_data_migration(database_url, source_query, target_table, batch_size=1000):
    """
    Migrate data in batches to minimize lock time
    """
    engine = create_engine(database_url)

    offset = 0
    total_processed = 0

    while True:
        with engine.connect() as conn:
            # Get batch of data to migrate
            batch_query = f"""
                {source_query}
                LIMIT {batch_size} OFFSET {offset}
            """

            result = conn.execute(text(batch_query))
            rows = result.fetchall()

            if not rows:
                break  # No more data to migrate

            # Insert batch into target table
            # Implementation depends on your data structure
            for row in rows:
                # Process and insert row
                pass

            total_processed += len(rows)
            logger.info(f"Processed {total_processed} rows...")

            # Small delay between batches to reduce system load
            time.sleep(0.1)
            offset += batch_size

    logger.info(f"Data migration completed: {total_processed} rows processed")
```

These patterns ensure safe, reliable, and observable database migrations in production environments.