# Database Migration Patterns Guide

This guide covers advanced Alembic migration patterns and techniques.

## Basic Migration Patterns

### Adding Multiple Columns
```python
"""Add multiple columns to users table

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2026-01-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

revision = 'abc123def456'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # Add multiple columns in a single operation
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True))
        batch_op.add_column(sa.Column('birth_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_login')
        batch_op.drop_column('is_verified')
        batch_op.drop_column('birth_date')
        batch_op.drop_column('phone')
```

### Renaming Columns and Tables
```python
"""Rename user fields and table

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
    # Rename column
    op.alter_column('user', 'old_field_name', new_column_name='new_field_name')

    # Rename table (if needed)
    op.rename_table('old_table_name', 'new_table_name')

def downgrade():
    # Reverse renames
    op.alter_column('user', 'new_field_name', new_column_name='old_field_name')
    op.rename_table('new_table_name', 'old_table_name')
```

### Changing Column Types
```python
"""Change column types for improved precision

Revision ID: ghi789jkl012
Revises: def456ghi789
Create Date: 2026-01-14 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'ghi789jkl012'
down_revision = 'def456ghi789'
branch_labels = None
depends_on = None

def upgrade():
    # Change column type - be careful with data conversion
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('price', type_=sa.Numeric(precision=10, scale=2), existing_type=sa.Float())

def downgrade():
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('price', type_=sa.Float(), existing_type=sa.Numeric(precision=10, scale=2))
```

## Advanced Migration Patterns

### Complex Relationship Changes
```python
"""Add many-to-many relationship between users and roles

Revision ID: jkl012mno345
Revises: ghi789jkl012
Create Date: 2026-01-14 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'jkl012mno345'
down_revision = 'ghi789jkl012'
branch_labels = None
depends_on = None

def upgrade():
    # Create association table for many-to-many relationship
    op.create_table('user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Create indexes for performance
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'])

def downgrade():
    op.drop_table('user_roles')
```

### Conditional Migration Logic
```python
"""Add column with conditional logic based on existing data

Revision ID: mno345pqr678
Revises: jkl012mno345
Create Date: 2026-01-14 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = 'mno345pqr678'
down_revision = 'jkl012mno345'
branch_labels = None
depends_on = None

def upgrade():
    # Add new column with default
    op.add_column('user', sa.Column('status', sa.String(length=20), nullable=False, server_default='active'))

    # Get connection for data manipulation
    connection = op.get_bind()

    # Update existing records based on some condition
    user_table = table('user',
        column('id', sa.Integer),
        column('status', sa.String),
        column('is_active', sa.Boolean)
    )

    # Set status based on is_active field
    connection.execute(
        user_table.update()
        .where(user_table.c.is_active == True)
        .values(status='active')
    )

    connection.execute(
        user_table.update()
        .where(user_table.c.is_active == False)
        .values(status='inactive')
    )

def downgrade():
    op.drop_column('user', 'status')
```

### Migration with Raw SQL
```python
"""Complex migration using raw SQL for performance

Revision ID: pqr678stu901
Revises: mno345pqr678
Create Date: 2026-01-14 15:00:00.000000
"""
from alembic import op

revision = 'pqr678stu901'
down_revision = 'mno345pqr678'
branch_labels = None
depends_on = None

def upgrade():
    # Use raw SQL for complex operations
    op.execute("""
        CREATE INDEX CONCURRENTLY idx_user_email_lower
        ON user (LOWER(email));
    """)

    # Update statistics for better query planning
    op.execute("ANALYZE user;")

def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_user_email_lower;")
```

## Data Migration Patterns

### Batch Data Migration
```python
"""Migrate large dataset in batches

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

    # Process data in batches to avoid memory issues
    offset = 0
    batch_size = 1000

    while True:
        # Get batch of records to update
        result = connection.execute(text(f"""
            SELECT id, old_field FROM large_table
            WHERE new_field IS NULL
            LIMIT {batch_size} OFFSET {offset}
        """)).fetchall()

        if not result:
            break

        # Update each record in the batch
        for record in result:
            new_value = transform_data(record.old_field)
            connection.execute(text("""
                UPDATE large_table
                SET new_field = :new_value
                WHERE id = :id
            """), {"new_value": new_value, "id": record.id})

        offset += batch_size

def downgrade():
    # Since we're transforming data, downgrade might not be possible
    # or might require keeping the old values in a separate column
    pass

def transform_data(old_value):
    """Transform function for data migration"""
    # Implement your data transformation logic here
    return old_value.upper() if old_value else None
```

### Migration with Validation
```python
"""Migration with data validation

Revision ID: vwx234yz567
Revises: stu901vwx234
Create Date: 2026-01-14 17:00:00.000000
"""
from alembic import op
from sqlalchemy import text

revision = 'vwx234yz567'
down_revision = 'stu901vwx234'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Validate data before migration
    invalid_records = connection.execute(text("""
        SELECT COUNT(*) FROM user WHERE email IS NULL OR email = ''
    """)).scalar()

    if invalid_records > 0:
        raise ValueError(f"Cannot migrate: {invalid_records} records have invalid email")

    # Add new column
    op.add_column('user', sa.Column('email_normalized', sa.String(255), nullable=True))

    # Update with normalized emails
    connection.execute(text("""
        UPDATE user
        SET email_normalized = LOWER(TRIM(email))
        WHERE email IS NOT NULL
    """))

    # Validate after migration
    invalid_after = connection.execute(text("""
        SELECT COUNT(*) FROM user
        WHERE email IS NOT NULL AND email_normalized IS NULL
    """)).scalar()

    if invalid_after > 0:
        raise ValueError("Migration resulted in invalid data")

def downgrade():
    op.drop_column('user', 'email_normalized')
```

## Migration Safety Patterns

### Safe Column Removal
```python
"""Safely remove column after verifying no dependencies

Revision ID: yz567abc890
Revises: vwx234yz567
Create Date: 2026-01-14 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'yz567abc890'
down_revision = 'vwx234yz567'
branch_labels = None
depends_on = None

def upgrade():
    # Instead of dropping immediately, first make it nullable and set default
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Set all values to a safe default first
        batch_op.alter_column('deprecated_field', nullable=True)

    # In a future migration, you can then drop the column
    # For now, we'll just add a comment that it's deprecated
    op.execute("COMMENT ON COLUMN user.deprecated_field IS 'Deprecated field, to be removed in future migration'")

def downgrade():
    # We don't restore the column since it's deprecated
    pass
```

### Migration with Rollback Validation
```python
"""Migration with rollback validation

Revision ID: abc890def123
Revises: yz567abc890
Create Date: 2026-01-14 19:00:00.000000
"""
from alembic import op
from sqlalchemy import text

revision = 'abc890def123'
down_revision = 'yz567abc890'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Store original state for validation
    original_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()

    # Perform migration
    op.add_column('user', sa.Column('new_field', sa.String(50), nullable=True))

    # Validate migration success
    new_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()

    if original_count != new_count:
        raise ValueError("Migration changed row count unexpectedly")

    print(f"Upgrade completed: {original_count} rows unchanged")

def downgrade():
    connection = op.get_bind()

    # Validate before downgrade
    user_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()

    # Perform downgrade
    op.drop_column('user', 'new_field')

    # Validate downgrade success
    after_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()

    if user_count != after_count:
        raise ValueError("Downgrade changed row count unexpectedly")

    print(f"Downgrade completed: {user_count} rows unchanged")
```

## Performance Optimization Patterns

### Migration with Progress Tracking
```python
"""Large migration with progress tracking

Revision ID: def123ghi456
Revises: abc890def123
Create Date: 2026-01-14 20:00:00.000000
"""
from alembic import op
from sqlalchemy import text
import time

revision = 'def123ghi456'
down_revision = 'abc890def123'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Get total count for progress tracking
    total_count = connection.execute(text("SELECT COUNT(*) FROM large_table")).scalar()
    print(f"Starting migration of {total_count} records...")

    processed = 0
    batch_size = 1000
    start_time = time.time()

    while True:
        result = connection.execute(text(f"""
            UPDATE large_table
            SET processed = TRUE
            WHERE id IN (
                SELECT id FROM large_table
                WHERE processed IS NOT TRUE
                LIMIT {batch_size}
            )
            RETURNING id
        """)).rowcount

        if result == 0:
            break

        processed += result
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        remaining = total_count - processed
        eta = remaining / rate if rate > 0 else 0

        print(f"Processed {processed}/{total_count} ({processed/total_count*100:.1f}%) - "
              f"Rate: {rate:.1f} rec/s - ETA: {eta:.0f}s")

    print(f"Migration completed in {time.time() - start_time:.2f}s")

def downgrade():
    connection = op.get_bind()
    connection.execute(text("UPDATE large_table SET processed = FALSE"))
    print("Downgrade completed")
```

These patterns ensure safe, reliable, and efficient database migrations for your applications.