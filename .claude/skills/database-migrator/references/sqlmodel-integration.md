# SQLModel Integration Guide

This guide covers integrating SQLModel with Alembic for database migrations.

## Setting Up SQLModel with Alembic

### Alembic Environment Configuration for SQLModel

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Import all your SQLModel models here
# Make sure to import all models that need migrations
from app.models.user import User
from app.models.task import Task
from app.models.category import Category

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Use batch mode for SQLite compatibility
        render_as_batch=True,
        # Include naming convention for consistency
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Use batch mode for SQLite compatibility
            render_as_batch=True,
            # Include naming convention for consistency
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Organizing SQLModel Models for Migrations

```python
# app/models/__init__.py
# Import all models here to ensure they're registered with SQLModel.metadata
from .user import User
from .task import Task
from .category import Category
from .user_task import UserTask  # Many-to-many relationship table

# This ensures all models are registered with SQLModel.metadata
__all__ = ["User", "Task", "Category", "UserTask"]
```

### SQLModel Model Example

```python
# app/models/task.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: "User" = Relationship(back_populates="tasks")
```

## Autogenerating Migrations

### Running Autogenerate

```bash
# Generate migration automatically based on model changes
alembic revision --autogenerate -m "Add priority field to tasks"

# If you get warnings about unmet dependencies, make sure all models are imported in env.py
```

### Common Autogenerate Issues and Solutions

```python
# If autogenerate doesn't detect changes, ensure your models are properly imported in alembic/env.py
# Make sure all models inherit from SQLModel and have table=True

# Example of a properly defined SQLModel for migration detection
class ProperModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key is required for migrations
    name: str = Field(max_length=100)  # Field constraints are preserved in migrations
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Default values are handled

class RelationshipModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    related_id: int = Field(foreign_key="propermodel.id", index=True)  # Foreign key relationships

    # Relationship field (not stored in DB, but affects migration generation)
    related: Optional[ProperModel] = Relationship(back_populates="related_items")
```

## Handling SQLModel-Specific Migration Patterns

### Field Type Migrations

```python
"""Handle SQLModel field type changes

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-01-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # SQLModel uses sqlmodel.sql.sqltypes.AutoString for String fields
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'email',
            type_=sqlmodel.sql.sqltypes.AutoString(length=255),
            existing_type=sa.String(length=100)
        )

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'email',
            type_=sa.String(length=100),
            existing_type=sqlmodel.sql.sqltypes.AutoString(length=255)
        )
```

### Relationship Migration

```python
"""Handle relationship changes

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
    # Add foreign key constraint for relationship
    op.create_foreign_key(
        'fk_task_user_id',
        'task', 'user',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Create index for foreign key (recommended for performance)
    op.create_index('ix_task_user_id', 'task', ['user_id'])

def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_task_user_id', 'task', type_='foreignkey')

    # Drop index
    op.drop_index('ix_task_user_id', table_name='task')
```

### Relationship Table Migration

```python
"""Create many-to-many relationship table

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
    # Create association table for many-to-many relationship
    op.create_table(
        'user_task_association',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'task_id')
    )

    # Create indexes for performance
    op.create_index('ix_user_task_assoc_user_id', 'user_task_association', ['user_id'])
    op.create_index('ix_user_task_assoc_task_id', 'user_task_association', ['task_id'])

def downgrade():
    op.drop_table('user_task_association')
```

## Advanced SQLModel Migration Patterns

### Migration with Custom SQLModel Types

```python
"""Handle custom SQLModel types

Revision ID: jkl012mno345
Revises: ghi789jkl012
Create Date: 2026-01-14 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from decimal import Decimal

revision = 'jkl012mno345'
down_revision = 'ghi789jkl012'
branch_labels = None
depends_on = None

def upgrade():
    # For PostgreSQL, use specific types
    if op.get_context().dialect.name == 'postgresql':
        op.add_column('product', sa.Column('price', postgresql.NUMERIC(precision=10, scale=2)))
    else:
        # For other databases, use standard types
        op.add_column('product', sa.Column('price', sa.Numeric(precision=10, scale=2)))

def downgrade():
    op.drop_column('product', 'price')
```

### Migration with JSON Fields

```python
"""Handle JSON fields

Revision ID: mno345pqr678
Revises: jkl012mno345
Create Date: 2026-01-14 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'mno345pqr678'
down_revision = 'jkl012mno345'
branch_labels = None
depends_on = None

def upgrade():
    # JSON fields are handled differently in different databases
    if op.get_context().dialect.name == 'postgresql':
        op.add_column('user', sa.Column('preferences', postgresql.JSONB()))
    else:
        op.add_column('user', sa.Column('preferences', sa.JSON()))

def downgrade():
    op.drop_column('user', 'preferences')
```

## Testing SQLModel Migrations

### Migration Testing Patterns

```python
"""Test migration with SQLModel

Revision ID: pqr678stu901
Revises: mno345pqr678
Create Date: 2026-01-14 15:00:00.000000
"""
from alembic import op
from sqlalchemy import text
from sqlmodel import Session, select
from app.models import User, Task

revision = 'pqr678stu901'
down_revision = 'mno345pqr678'
branch_labels = None
depends_on = None

def upgrade():
    # Add new column
    op.add_column('user', sa.Column('migration_tested', sa.Boolean(), nullable=False, server_default='false'))

    # Test that migration worked as expected
    connection = op.get_bind()
    result = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()
    print(f"Testing migration: {result} users found")

def downgrade():
    op.drop_column('user', 'migration_tested')
```

### Migration Validation with SQLModel

```python
"""Validate migration with SQLModel models

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
    # Add new field
    op.add_column('task', sa.Column('tags', sa.String(length=500), nullable=True))

    # Validate the migration
    connection = op.get_bind()

    # Check if column exists
    result = connection.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'task' AND column_name = 'tags'
    """)).fetchone()

    if not result:
        raise Exception("Migration failed: tags column was not created")

def downgrade():
    op.drop_column('task', 'tags')
```

## Production Considerations

### Zero-Downtime Migration Patterns

```python
"""Zero-downtime migration pattern

Revision ID: vwx234yz567
Revises: stu901vwx234
Create Date: 2026-01-14 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'vwx234yz567'
down_revision = 'stu901vwx234'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Add new column (can coexist with old)
    op.add_column('user', sa.Column('email_new', sa.String(length=255), nullable=True))

    # Step 2: Copy data from old to new (done in application code in production)
    # This would typically be handled by the application during deployment

    # Step 3: Add index to new column
    op.create_index('ix_user_email_new', 'user', ['email_new'])

def downgrade():
    op.drop_column('user', 'email_new')
```

### Migration with Data Transformation

```python
"""Migration with data transformation

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
    # Add new column
    op.add_column('user', sa.Column('status_normalized', sa.String(length=20), nullable=True))

    # Transform data
    connection = op.get_bind()

    # Map old status values to new standardized values
    status_mapping = {
        'active_now': 'active',
        'inactive_temp': 'inactive',
        'paused': 'inactive',
        'active': 'active'
    }

    for old_status, new_status in status_mapping.items():
        connection.execute(text(f"""
            UPDATE user
            SET status_normalized = '{new_status}'
            WHERE status = '{old_status}' AND status_normalized IS NULL
        """))

    # Make new column non-nullable after data migration
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('status_normalized', nullable=False)

def downgrade():
    op.drop_column('user', 'status_normalized')
```

These patterns ensure smooth integration between SQLModel and Alembic for reliable database migrations.