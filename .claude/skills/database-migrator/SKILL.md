---
name: database-migrator
description: |
  Generates and manages Alembic database migration scripts for schema changes. Creates version-controlled
  migrations for table creation, column additions, index management, and relationship modifications.
  Ensures safe database evolution with rollback capability and handles data migration when schema changes
  affect existing records.
---

# Database Migrator

Generates and manages Alembic database migration scripts for schema changes.

## What This Skill Does
- Generates Alembic migration scripts for SQLModel schema changes
- Creates version-controlled migrations for table creation, modification, and deletion
- Manages column additions, removals, and modifications with proper data handling
- Handles index creation, modification, and deletion
- Manages relationship changes and foreign key constraints
- Provides safe database evolution with rollback capability
- Handles data migration when schema changes affect existing records
- Creates database initialization and seed scripts

## What This Skill Does NOT Do
- Execute database migrations automatically (requires manual approval)
- Directly modify production databases without review
- Handle complex business logic migrations (requires custom implementation)
- Manage database backup and recovery (should be handled separately)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing SQLModel schemas, current database structure, alembic configuration |
| **Conversation** | Migration requirements, schema changes needed, deployment environment specifics |
| **Skill References** | Domain patterns from `references/` (migration patterns, SQLModel integration, Alembic best practices) |
| **User Guidelines** | Project-specific database conventions, deployment procedures, rollback requirements |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **Schema Changes**: "What specific SQLModel schema changes do you need to migrate?"
2. **Environment**: "What database environment (dev/staging/prod) and deployment process do you use?"
3. **Data Migration**: "Do you need to migrate existing data during schema changes?"

---

## Implementation Workflow

1. **Analyze Schema Changes**
   - Identify SQLModel model changes (new models, field changes, relationships)
   - Determine migration approach (autogenerate vs manual)
   - Assess impact on existing data

2. **Generate Migration Files**
   - Create Alembic migration with proper revision IDs
   - Implement upgrade and downgrade functions
   - Add appropriate index and constraint management

3. **Implement Data Migration Logic**
   - Create data transformation logic if needed
   - Handle schema changes that affect existing records
   - Add validation for migrated data

4. **Test Migration Safely**
   - Test upgrade and downgrade on development database
   - Verify data integrity after migration
   - Validate rollback capability

---

## Migration Patterns

### Basic Table Creation Migration

```python
"""Create tasks table

Revision ID: abc123def456
Revises:
Create Date: 2026-01-14 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the tasks table
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create indexes
    op.create_index('ix_task_user_id', 'task', ['user_id'])
    op.create_index('ix_task_completed', 'task', ['completed'])

    # Add foreign key constraint (if user table exists)
    op.create_foreign_key(
        'fk_task_user_id',
        'task', 'user',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_task_user_id', 'task', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_task_completed', table_name='task')
    op.drop_index('ix_task_user_id', table_name='task')

    # Drop the table
    op.drop_table('task')
```

### Column Addition/Modification Migration

```python
"""Add priority column to tasks

Revision ID: def456ghi789
Revises: abc123def456
Create Date: 2026-01-14 11:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

revision = 'def456ghi789'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None

def upgrade():
    # Add new column with appropriate default
    op.add_column('task', sa.Column('priority',
                                  sqlmodel.sql.sqltypes.AutoString(length=20),
                                  nullable=False,
                                  server_default='medium'))

    # Create index for new column
    op.create_index('ix_task_priority', 'task', ['priority'])

    # Update the default value after creation (optional)
    op.alter_column('task', 'priority', server_default=None)

def downgrade():
    # Drop index first
    op.drop_index('ix_task_priority', table_name='task')

    # Drop column
    op.drop_column('task', 'priority')
```

### Data Migration Migration

```python
"""Migrate task titles to uppercase

Revision ID: ghi789jkl012
Revises: def456ghi789
Create Date: 2026-01-14 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = 'ghi789jkl012'
down_revision = 'def456ghi789'
branch_labels = None
depends_on = None

def upgrade():
    # Define the table structure for data manipulation
    task_table = table('task',
        column('id', sa.Integer),
        column('title', sa.String)
    )

    # Update all task titles to uppercase
    connection = op.get_bind()
    connection.execute(
        task_table.update().values(title=sa.func.upper(task_table.c.title))
    )

def downgrade():
    # For downgrade, we might not be able to revert the uppercase conversion
    # So we'll just log this limitation
    pass
```

### Relationship and Foreign Key Migration

```python
"""Add category relationship to tasks

Revision ID: jkl012mno345
Revises: ghi789jkl012
Create Date: 2026-01-14 13:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

revision = 'jkl012mno345'
down_revision = 'ghi789jkl012'
branch_labels = None
depends_on = None

def upgrade():
    # Create the category table first
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Add category_id column to task table
    op.add_column('task', sa.Column('category_id', sa.Integer(), nullable=True))

    # Create index for the new column
    op.create_index('ix_task_category_id', 'task', ['category_id'])

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_task_category',
        'task', 'category',
        ['category_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_task_category', 'task', type_='foreignkey')

    # Drop index
    op.drop_index('ix_task_category_id', table_name='task')

    # Drop column
    op.drop_column('task', 'category_id')

    # Drop category table
    op.drop_table('category')
```

---

## Alembic Configuration

### Alembic Environment Configuration

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlmodel import SQLModel

# Import your SQLModel models
from app.models import *  # Import all models that need migrations

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
        render_as_batch=True
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
            # Add naming convention for consistency
            include_object=include_object,
            compare_type=compare_type,
            compare_server_default=compare_server_default
        )

        with context.begin_transaction():
            context.run_migrations()

def include_object(object, name, type_, reflected, compare_to):
    """
    Custom function to include/exclude objects from autogeneration
    """
    if type_ == "table":
        # Exclude tables that shouldn't be managed by Alembic
        if name in ["alembic_version", "spatial_ref_sys"]:  # spatial_ref_sys is for PostGIS
            return False
    return True

def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """
    Custom function to compare column types
    """
    return False  # Return False to let Alembic handle type comparison

def compare_server_default(context, inspected_default, metadata_default, inspected_column, metadata_column):
    """
    Custom function to compare server defaults
    """
    return False  # Return False to let Alembic handle default comparison

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Alembic Ini Configuration

```ini
# alembic.ini
[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# max_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format
# version_num_format = %04d

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = sqlite:///./test.db


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are to be
# executed whenever a "revision" command creates a new revision file.
# See the documentation for further detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

---

## Migration Commands

### Common Alembic Commands

```bash
# Initialize Alembic (run once)
alembic init alembic

# Generate migration automatically (detects changes in SQLModel)
alembic revision --autogenerate -m "Description of changes"

# Generate empty migration (for manual editing)
alembic revision -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Apply to specific version
alembic upgrade abc123def456

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123def456

# Show current migration status
alembic current

# Show migration history
alembic history

# Show migration history with verbose details
alembic history -v
```

### Advanced Migration Commands

```bash
# Create branch point
alembic revision --rev-id new_branch_point

# Merge multiple heads (when there are conflicting migration branches)
alembic merge -m "Merge migration branches"

# Stamp database with specific revision (without running migration)
alembic stamp abc123def456

# Check current head revision without changing anything
alembic heads
```

---

## Best Practices

### Migration Safety
- Always test migrations on a copy of production data
- Create backups before running migrations on production
- Use transactions when possible to ensure atomicity
- Test both upgrade and downgrade operations
- Keep migration files small and focused on single changes

### Data Migration
- When migrating data, consider performance implications
- For large datasets, consider batch processing
- Always validate migrated data after migration
- Consider the impact of downtime during data migration

### SQLModel Integration
- Import all SQLModel models in alembic/env.py
- Use render_as_batch=True for SQLite compatibility
- Follow naming conventions for consistency
- Use appropriate default values for new columns

### Version Control
- Commit migration files to version control
- Include meaningful commit messages
- Coordinate with team members on migration timing
- Document migration dependencies and requirements

---

## Output Checklist

Before delivering migration files, verify:
- [ ] Migration file has proper revision ID and dependencies
- [ ] Upgrade function creates/updates schema as expected
- [ ] Downgrade function reverses all changes made in upgrade
- [ ] Indexes are properly created and dropped
- [ ] Foreign key constraints are properly managed
- [ ] Data migration logic is safe and tested
- [ ] Migration has been tested in development environment
- [ ] Rollback capability has been verified
- [ ] Migration follows naming conventions
- [ ] Migration handles edge cases appropriately

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/migration-patterns.md` | When implementing complex schema changes |
| `references/sqlmodel-integration.md` | When integrating with SQLModel models |
| `references/production-migrations.md` | When preparing migrations for production |
| `references/data-migration.md` | When handling data transformation during schema changes |