# Data Migration Guide

This guide covers patterns and techniques for migrating data during database schema changes.

## Basic Data Migration Patterns

### Simple Data Transformation

```python
"""Migrate user status from string to enum

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-01-14 10:00:00.000000
"""
from alembic import op
from sqlalchemy import text

revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Add new status column with enum values
    op.execute("""
        ALTER TABLE user
        ADD COLUMN status_new VARCHAR(20) DEFAULT 'active'::VARCHAR
    """)

    # Migrate data from old to new column
    connection = op.get_bind()

    # Map old status values to new ones
    status_mapping = {
        'enabled': 'active',
        'disabled': 'inactive',
        'pending_activation': 'pending',
        'suspended': 'inactive'
    }

    for old_status, new_status in status_mapping.items():
        connection.execute(text(f"""
            UPDATE user
            SET status_new = '{new_status}'
            WHERE status = '{old_status}' AND status_new IS NULL
        """))

    # Verify all records are migrated
    unmigrated = connection.execute(text("""
        SELECT COUNT(*) FROM user WHERE status_new IS NULL
    """)).scalar()

    if unmigrated > 0:
        raise Exception(f"{unmigrated} records were not migrated")

def downgrade():
    # Data migration downgrades are often not possible
    # In this case, we might need to keep the old values somewhere
    pass
```

### Column Splitting Migration

```python
"""Split full name into first and last name

Revision ID: def456ghi789
Revises: abc123def456
Create Date: 2026-01-14 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'def456ghi789'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('user', sa.Column('first_name', sa.String(50), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(50), nullable=True))

    # Migrate data from full_name to first_name/last_name
    connection = op.get_bind()

    # Update first and last names by splitting the full name
    connection.execute(sa.text("""
        UPDATE user
        SET
            first_name = TRIM(SPLIT_PART(full_name, ' ', 1)),
            last_name = CASE
                WHEN SPLIT_PART(full_name, ' ', 2) != ''
                THEN TRIM(SUBSTRING(full_name, LENGTH(SPLIT_PART(full_name, ' ', 1)) + 2))
                ELSE TRIM(SPLIT_PART(full_name, ' ', 1))
            END
        WHERE full_name IS NOT NULL
    """))

    # Make new columns non-nullable after data migration
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('first_name', nullable=False)
        batch_op.alter_column('last_name', nullable=False)

def downgrade():
    # Recombine first and last names back to full_name
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE user
        SET full_name = CONCAT(first_name, ' ', last_name)
        WHERE full_name IS NULL
    """))

    # Drop new columns
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
```

## Complex Data Migration Patterns

### Foreign Key Data Migration

```python
"""Migrate category data to new structure

Revision ID: ghi789jkl012
Revises: def456ghi789
Create Date: 2026-01-14 12:00:00.000000
"""
from alembic import op
from sqlalchemy import text, MetaData, Table, Column, Integer, String

revision = 'ghi789jkl012'
down_revision = 'def456ghi789'
branch_labels = None
depends_on = None

def upgrade():
    # Create new category table
    op.create_table(
        'category_new',
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('slug', String(100), nullable=False, unique=True),
        Column('parent_id', Integer, nullable=True)
    )

    # Migrate data from old to new category structure
    connection = op.get_bind()

    # Create slug from name
    connection.execute(text("""
        INSERT INTO category_new (name, slug, parent_id)
        SELECT
            name,
            LOWER(REPLACE(name, ' ', '-')) as slug,
            NULL as parent_id
        FROM category
        WHERE name IS NOT NULL
    """))

    # Update tasks to use new category IDs
    # First, create a mapping between old and new category IDs
    category_mapping = connection.execute(text("""
        SELECT old_cat.id as old_id, new_cat.id as new_id
        FROM category old_cat
        JOIN category_new new_cat ON old_cat.name = new_cat.name
    """)).fetchall()

    # Update task category references
    for old_id, new_id in category_mapping:
        connection.execute(text(f"""
            UPDATE task
            SET category_id = {new_id}
            WHERE category_id = {old_id}
        """))

def downgrade():
    # Reverse the migration (complex, often not practical)
    # In real scenarios, you might keep both tables temporarily
    pass
```

### Bulk Data Migration with Validation

```python
"""Migrate large dataset with validation

Revision ID: jkl012mno345
Revises: ghi789jkl012
Create Date: 2026-01-14 13:00:00.000000
"""
from alembic import op
from sqlalchemy import text
import hashlib

revision = 'jkl012mno345'
down_revision = 'ghi789jkl012'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Count total records to migrate
    total_count = connection.execute(text("SELECT COUNT(*) FROM large_table")).scalar()
    print(f"Starting migration of {total_count} records...")

    # Add checksum column for validation
    op.add_column('large_table', sa.Column('data_checksum', sa.String(64), nullable=True))

    batch_size = 1000
    offset = 0
    processed = 0

    while True:
        # Get batch of records to migrate
        records = connection.execute(text(f"""
            SELECT id, old_data_field
            FROM large_table
            WHERE new_data_field IS NULL
            LIMIT {batch_size} OFFSET {offset}
        """)).fetchall()

        if not records:
            break

        # Process and migrate each record in the batch
        for record in records:
            # Transform data
            new_value = transform_record(record.old_data_field)

            # Calculate checksum
            checksum = hashlib.sha256(new_value.encode()).hexdigest()

            # Update record
            connection.execute(text(f"""
                UPDATE large_table
                SET new_data_field = :new_value,
                    data_checksum = :checksum
                WHERE id = :id
            """), {
                "new_value": new_value,
                "checksum": checksum,
                "id": record.id
            })

        processed += len(records)
        offset += batch_size

        print(f"Processed {processed}/{total_count} ({processed/total_count*100:.1f}%)")

    # Validate migration completeness
    remaining = connection.execute(text("""
        SELECT COUNT(*) FROM large_table
        WHERE new_data_field IS NULL
    """)).scalar()

    if remaining > 0:
        raise Exception(f"{remaining} records were not migrated")

    print(f"Migration completed: {processed} records processed")

def transform_record(data):
    """
    Transform function for data migration
    """
    # Implement your specific transformation logic
    if isinstance(data, str):
        return data.strip().lower().replace('  ', ' ')
    return data

def downgrade():
    # Reset migrated data for downgrade
    connection = op.get_bind()
    connection.execute(text("UPDATE large_table SET new_data_field = NULL, data_checksum = NULL"))
```

## Migration with Background Processing

### Async Data Migration

```python
"""Start async data migration job

Revision ID: mno345pqr678
Revises: jkl012mno345
Create Date: 2026-01-14 14:00:00.000000
"""
from alembic import op
from sqlalchemy import text
import uuid

revision = 'mno345pqr678'
down_revision = 'jkl012mno345'
branch_labels = None
depends_on = None

def upgrade():
    # Add migration tracking columns
    op.add_column('user', sa.Column('migration_job_id', sa.String(36), nullable=True))
    op.add_column('user', sa.Column('migration_status', sa.String(20), default='pending'))
    op.add_column('user', sa.Column('migration_started_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('migration_completed_at', sa.DateTime(), nullable=True))

    # Create migration jobs table
    op.create_table(
        'migration_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('progress', sa.Integer, default=0),
        sa.Column('total_records', sa.Integer),
        sa.Column('processed_records', sa.Integer, default=0),
        sa.Column('started_at', sa.DateTime()),
        sa.Column('completed_at', sa.DateTime())
    )

    # Create migration job for this migration
    job_id = str(uuid.uuid4())
    connection = op.get_bind()

    connection.execute(text(f"""
        INSERT INTO migration_jobs (id, job_type, status, total_records)
        VALUES ('{job_id}', 'user_data_migration', 'pending',
                (SELECT COUNT(*) FROM user WHERE migration_status = 'pending'))
    """))

    # Assign users to this migration job
    connection.execute(text(f"""
        UPDATE user
        SET migration_job_id = '{job_id}', migration_status = 'pending'
        WHERE migration_job_id IS NULL
    """))

    print(f"Created migration job: {job_id}")
    print("Run background migration process separately")

def downgrade():
    connection = op.get_bind()

    # Cancel any pending jobs
    connection.execute(text("""
        UPDATE migration_jobs
        SET status = 'cancelled', completed_at = NOW()
        WHERE status = 'pending' OR status = 'in_progress'
    """))

    # Reset user migration status
    connection.execute(text("""
        UPDATE user
        SET migration_job_id = NULL,
            migration_status = NULL,
            migration_started_at = NULL,
            migration_completed_at = NULL
    """))

    # Drop migration tracking columns
    op.drop_column('user', 'migration_completed_at')
    op.drop_column('user', 'migration_started_at')
    op.drop_column('user', 'migration_status')
    op.drop_column('user', 'migration_job_id')

    # Drop jobs table
    op.drop_table('migration_jobs')
```

## Data Validation Patterns

### Migration with Integrity Checks

```python
"""Migrate with data integrity validation

Revision ID: pqr678stu901
Revises: mno345pqr678
Create Date: 2026-01-14 15:00:00.000000
"""
from alembic import op
from sqlalchemy import text

revision = 'pqr678stu901'
down_revision = 'mno35pqr678'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Store original counts for validation
    original_user_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()
    original_task_count = connection.execute(text("SELECT COUNT(*) FROM task")).scalar()

    # Perform data migration
    op.add_column('user', sa.Column('email_normalized', sa.String(255), nullable=True))

    # Normalize emails
    connection.execute(text("""
        UPDATE user
        SET email_normalized = LOWER(TRIM(email))
        WHERE email IS NOT NULL
    """))

    # Validate data integrity after migration
    new_user_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()
    new_task_count = connection.execute(text("SELECT COUNT(*) FROM task")).scalar()

    # Check that counts haven't changed unexpectedly
    if original_user_count != new_user_count:
        raise Exception(f"User count changed from {original_user_count} to {new_user_count}")

    if original_task_count != new_task_count:
        raise Exception(f"Task count changed from {original_task_count} to {new_task_count}")

    # Validate that normalized emails match expectations
    invalid_emails = connection.execute(text("""
        SELECT COUNT(*) FROM user
        WHERE email IS NOT NULL
          AND email_normalized != LOWER(TRIM(email))
    """)).scalar()

    if invalid_emails > 0:
        raise Exception(f"{invalid_emails} emails were not normalized correctly")

    # Validate no NULL values where not expected
    null_normalized = connection.execute(text("""
        SELECT COUNT(*) FROM user
        WHERE email IS NOT NULL AND email_normalized IS NULL
    """)).scalar()

    if null_normalized > 0:
        raise Exception(f"{null_normalized} users have NULL normalized email despite having email")

    print("Data migration completed with integrity validation")

def downgrade():
    op.drop_column('user', 'email_normalized')
```

### Cross-Table Data Migration

```python
"""Migrate related data across multiple tables

Revision ID: stu901vwx234
Revises: pqr678stu901
Create Date: 2026-01-14 16:00:00.000000
"""
from alembic import op
from sqlalchemy import text

revision = 'stu901vwx234'
down_revision = 'pqr678stu901'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Add new column to related tables
    op.add_column('user', sa.Column('migration_version', sa.Integer, default=1))
    op.add_column('task', sa.Column('migration_version', sa.Integer, default=1))

    # Migrate user data first
    connection.execute(text("""
        UPDATE user
        SET migration_version = 2
        WHERE created_at > '2025-01-01'
    """))

    # Migrate related task data based on user migration
    connection.execute(text("""
        UPDATE task
        SET migration_version = 2
        FROM user
        WHERE task.user_id = user.id AND user.migration_version = 2
    """))

    # Validate referential integrity
    orphaned_tasks = connection.execute(text("""
        SELECT COUNT(*) FROM task t
        LEFT JOIN user u ON t.user_id = u.id
        WHERE u.id IS NULL
    """)).scalar()

    if orphaned_tasks > 0:
        raise Exception(f"{orphaned_tasks} tasks have no corresponding user")

    # Validate that all migrated users have migrated tasks
    users_without_tasks = connection.execute(text("""
        SELECT COUNT(*) FROM user u
        LEFT JOIN task t ON u.id = t.user_id
        WHERE u.migration_version = 2 AND t.user_id IS NULL
    """)).scalar()

    print(f"Migration completed: {orphaned_tasks} orphaned tasks, {users_without_tasks} users without tasks")

def downgrade():
    connection = op.get_bind()

    # Reset migration version
    connection.execute(text("""
        UPDATE user SET migration_version = 1 WHERE migration_version = 2
    """))
    connection.execute(text("""
        UPDATE task SET migration_version = 1 WHERE migration_version = 2
    """))

    # Drop columns
    op.drop_column('task', 'migration_version')
    op.drop_column('user', 'migration_version')
```

## Performance Optimization Patterns

### Batch Migration with Progress Tracking

```python
"""Efficient batch migration with progress tracking

Revision ID: vwx234yz567
Revises: stu901vwx234
Create Date: 2026-01-14 17:00:00.000000
"""
from alembic import op
from sqlalchemy import text
import time

revision = 'vwx234yz567'
down_revision = 'stu901vwx234'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Get total count for progress tracking
    total_count = connection.execute(text("""
        SELECT COUNT(*) FROM large_table WHERE needs_migration = TRUE
    """)).scalar()

    if total_count == 0:
        print("No records need migration, skipping")
        return

    print(f"Starting migration of {total_count} records...")

    # Add progress tracking column
    op.add_column('migration_log', sa.Column('progress_percentage', sa.Integer, default=0))

    batch_size = 500
    offset = 0
    processed = 0
    start_time = time.time()

    while True:
        # Process batch
        result = connection.execute(text(f"""
            UPDATE large_table
            SET
                migrated_field = UPPER(migrated_field),
                migration_complete = TRUE
            WHERE id IN (
                SELECT id FROM large_table
                WHERE needs_migration = TRUE
                LIMIT {batch_size} OFFSET {offset}
            )
            RETURNING id
        """))

        batch_processed = result.rowcount

        if batch_processed == 0:
            break

        processed += batch_processed
        offset += batch_size

        # Calculate progress and performance metrics
        elapsed = time.time() - start_time
        progress_pct = (processed / total_count) * 100
        rate = processed / elapsed if elapsed > 0 else 0
        remaining = total_count - processed
        eta = (remaining / rate) if rate > 0 else 0

        # Log progress
        print(f"Progress: {processed}/{total_count} ({progress_pct:.1f}%) | "
              f"Rate: {rate:.1f} rec/s | ETA: {eta:.0f}s")

        # Update progress tracking
        connection.execute(text(f"""
            INSERT INTO migration_log (batch_id, processed_count, total_count, progress_percentage)
            VALUES ('{time.time()}', {processed}, {total_count}, {progress_pct})
            ON CONFLICT (batch_id) DO UPDATE SET
                processed_count = EXCLUDED.processed_count,
                progress_percentage = EXCLUDED.progress_percentage
        """))

        # Small delay to reduce system load
        time.sleep(0.1)

    print(f"Migration completed in {time.time() - start_time:.2f}s")

def downgrade():
    connection = op.get_bind()

    # Rollback the migration
    connection.execute(text("""
        UPDATE large_table
        SET migrated_field = LOWER(migrated_field), migration_complete = FALSE
        WHERE migration_complete = TRUE
    """))
```

### Migration with Rollback Safety

```python
"""Safe migration with rollback capability

Revision ID: yz567abc890
Revises: vwx234yz567
Create Date: 2026-01-14 18:00:00.000000
"""
from alembic import op
from sqlalchemy import text

revision = 'yz567abc890'
down_revision = 'vwx234yz567'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Create backup of original data before migration
    connection.execute(text("""
        CREATE TABLE user_backup AS
        SELECT id, email, created_at, updated_at
        FROM user
    """))

    # Add temporary columns for migration
    op.add_column('user', sa.Column('email_backup', sa.String(255), nullable=True))
    op.add_column('user', sa.Column('migration_step', sa.String(20), default='start'))

    # Perform migration in steps with validation
    try:
        # Step 1: Backup original emails
        connection.execute(text("""
            UPDATE user
            SET email_backup = email, migration_step = 'backup_done'
        """))

        # Validate backup
        backup_count = connection.execute(text("""
            SELECT COUNT(*) FROM user WHERE email_backup IS NOT NULL
        """)).scalar()

        original_count = connection.execute(text("""
            SELECT COUNT(*) FROM user
        """)).scalar()

        if backup_count != original_count:
            raise Exception("Email backup failed")

        # Step 2: Perform main migration
        connection.execute(text("""
            UPDATE user
            SET email = LOWER(TRIM(email)), migration_step = 'migration_done'
        """))

        # Step 3: Validate migration
        invalid_emails = connection.execute(text("""
            SELECT COUNT(*) FROM user
            WHERE email IS NOT NULL AND email != LOWER(TRIM(email_backup))
        """)).scalar()

        if invalid_emails > 0:
            raise Exception(f"{invalid_emails} emails were not properly migrated")

        print(f"Migration completed successfully: {original_count} records")

    except Exception as e:
        # If any step fails, we can rollback from backup
        print(f"Migration failed: {e}")
        print("Migration can be rolled back using backup table")
        raise

def downgrade():
    connection = op.get_bind()

    # Restore from backup
    connection.execute(text("""
        UPDATE user
        SET email = email_backup
        FROM user_backup
        WHERE user.id = user_backup.id
    """))

    # Clean up temporary columns
    op.drop_column('user', 'migration_step')
    op.drop_column('user', 'email_backup')

    # Drop backup table
    connection.execute(text("DROP TABLE IF EXISTS user_backup"))
```

These patterns ensure safe, reliable, and efficient data migration during database schema changes.