---
name: migration-generator
description: |
  Auto-generates Alembic database migration files for SQLModel schema changes. Creates
  version-controlled migrations for table creation, column modifications, index management,
  and relationship updates. Ensures safe database evolution with rollback capability.
---

# Migration Generator

Auto-generates Alembic migration scripts for database schema changes.

## What This Skill Does
- Generates Alembic migration files from SQLModel changes
- Creates upgrade() and downgrade() functions
- Detects schema differences automatically
- Handles table creation/deletion
- Manages column additions/modifications/deletions
- Creates/drops indexes and constraints
- Implements foreign key relationships
- Ensures version control of database schema

## What This Skill Does NOT Do
- Design database schema (use schema-designer)
- Configure relationships (use sqlmodel-relationship-mapper)
- Create indexes (use index-optimizer)
- Write application queries (use query-builder)

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Current SQLModel models, existing migrations, database connection config |
| **Conversation** | Schema changes needed, migration description, rollback strategy |
| **Skill References** | Alembic patterns, PostgreSQL migration best practices |
| **User Guidelines** | Migration naming conventions, deployment process |

## Required Clarifications

Ask about USER'S requirements:

1. **Schema Changes**: "What schema changes do you need (new table, add column, modify constraint)?"
2. **Data Migration**: "Does this require data migration or just schema changes?"
3. **Rollback**: "What should happen if this migration needs to be rolled back?"

## Implementation Workflow

1. **Setup Alembic (First Time)**
   - Initialize Alembic in project
   - Configure alembic.ini with database URL
   - Set up env.py with SQLModel metadata

2. **Detect Schema Changes**
   - Compare current SQLModel models with database
   - Identify new tables, columns, indexes
   - Detect modified or deleted elements

3. **Generate Migration File**
   - Run `alembic revision --autogenerate`
   - Review generated migration code
   - Add custom data migration logic if needed
   - Write meaningful migration message

4. **Test Migration**
   - Apply migration to development database
   - Verify schema changes
   - Test rollback (downgrade)
   - Check data integrity

## Alembic Setup (First Time)

### 1. Install Alembic
```bash
pip install alembic
```

### 2. Initialize Alembic
```bash
alembic init alembic
```

**Project structure:**
```
backend/
├── alembic/
│   ├── versions/          # Migration files go here
│   ├── env.py            # Alembic environment config
│   └── script.py.mako    # Migration template
├── alembic.ini           # Alembic configuration
├── models.py             # SQLModel models
└── main.py
```

### 3. Configure alembic.ini
```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .

# Database URL (use environment variable in production)
sqlalchemy.url = postgresql://user:password@localhost/dbname

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

### 4. Configure env.py
```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import SQLModel and all models
from sqlmodel import SQLModel
from models import Task, User, Project  # Import all your models

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to SQLModel metadata
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Creating Migrations

### Auto-Generate Migration
```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Create tasks table"
```

### Manual Migration (for data changes)
```bash
# Create empty migration
alembic revision -m "Add default categories"
```

## Migration File Examples

### Example 1: Create Table
```python
"""Create tasks table

Revision ID: abc123def456
Revises:
Create Date: 2026-01-14 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from datetime import datetime

# revision identifiers
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tasks table
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('ix_task_user_id', 'task', ['user_id'])
    op.create_index('ix_task_completed', 'task', ['completed'])
    op.create_index('ix_task_user_completed', 'task', ['user_id', 'completed'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_task_user_completed', table_name='task')
    op.drop_index('ix_task_completed', table_name='task')
    op.drop_index('ix_task_user_id', table_name='task')

    # Drop table
    op.drop_table('task')
```

### Example 2: Add Column
```python
"""Add priority column to tasks

Revision ID: def456ghi789
Revises: abc123def456
Create Date: 2026-01-15 14:20:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'def456ghi789'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add priority column
    op.add_column(
        'task',
        sa.Column('priority', sa.String(length=20), nullable=True, server_default='medium')
    )

    # Create index on priority
    op.create_index('ix_task_priority', 'task', ['priority'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_task_priority', table_name='task')

    # Drop column
    op.drop_column('task', 'priority')
```

### Example 3: Modify Column
```python
"""Increase title max length to 300

Revision ID: ghi789jkl012
Revises: def456ghi789
Create Date: 2026-01-16 09:15:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'ghi789jkl012'
down_revision = 'def456ghi789'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alter column type
    op.alter_column(
        'task',
        'title',
        type_=sa.String(length=300),
        existing_type=sa.String(length=200),
        nullable=False
    )


def downgrade() -> None:
    # Revert column type (may lose data if titles > 200 chars exist)
    op.alter_column(
        'task',
        'title',
        type_=sa.String(length=200),
        existing_type=sa.String(length=300),
        nullable=False
    )
```

### Example 4: Data Migration
```python
"""Add default tags for existing tasks

Revision ID: jkl012mno345
Revises: ghi789jkl012
Create Date: 2026-01-17 11:45:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'jkl012mno345'
down_revision = 'ghi789jkl012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection
    connection = op.get_bind()

    # Add tags column
    op.add_column('task', sa.Column('tags', sa.JSON(), nullable=True))

    # Migrate existing data: set empty tags array
    connection.execute(
        sa.text("UPDATE task SET tags = '[]'::jsonb WHERE tags IS NULL")
    )

    # Make column non-nullable after data migration
    op.alter_column('task', 'tags', nullable=False)


def downgrade() -> None:
    # Drop tags column
    op.drop_column('task', 'tags')
```

## Running Migrations

### Apply Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade abc123def456

# Apply next migration only
alembic upgrade +1
```

### Rollback Migrations
```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123def456

# Rollback all migrations
alembic downgrade base
```

### Check Migration Status
```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## Migration Best Practices

### DO:
✅ Always review auto-generated migrations
✅ Test migrations on development database first
✅ Write meaningful migration messages
✅ Include both upgrade() and downgrade()
✅ Backup database before applying migrations
✅ Use server_default for new NOT NULL columns
✅ Handle data migration separately if complex

### DON'T:
❌ Edit old migrations (create new ones instead)
❌ Apply untested migrations to production
❌ Skip migration testing
❌ Leave incomplete downgrade() functions
❌ Forget to import new models in env.py
❌ Use DROP without data backup

## Environment-Specific Configurations

### Development
```bash
# Use local database
export DATABASE_URL="postgresql://localhost/todo_dev"
alembic upgrade head
```

### Production
```bash
# Use production database (from environment variable)
export DATABASE_URL="postgresql://neon.tech/todo_prod"
alembic upgrade head
```

### Docker
```dockerfile
# Dockerfile
FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Run migrations on container start
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0"]
```

## Troubleshooting

### Migration Conflicts
```bash
# If multiple developers create migrations simultaneously
alembic merge heads -m "Merge migrations"
```

### Failed Migration
```bash
# Mark migration as resolved (use carefully!)
alembic stamp head

# Or rollback and reapply
alembic downgrade -1
alembic upgrade head
```

### Schema Mismatch
```bash
# Generate migration from current state
alembic revision --autogenerate -m "Sync schema with models"
```

## Output Checklist

Before delivering migration:
- [ ] Migration file generated in alembic/versions/
- [ ] Meaningful revision message
- [ ] upgrade() function complete
- [ ] downgrade() function complete
- [ ] Tested on development database
- [ ] Rollback tested successfully
- [ ] Indexes and constraints included
- [ ] Data migration handled (if needed)
- [ ] Migration committed to Git

## Python Implementation

```python
import os
import subprocess
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import sqlmodel
from alembic import command
from alembic.config import Config

class MigrationGenerator:
    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.alembic_dir = self.project_dir / "alembic"
        self.alembic_ini = self.project_dir / "alembic.ini"

    def initialize_alembic(self, database_url: Optional[str] = None):
        """Initialize Alembic in the project if not already initialized."""
        if self.alembic_dir.exists():
            print("Alembic already initialized.")
            return

        # Create alembic configuration
        self._create_alembic_ini(database_url)

        # Initialize alembic
        subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"],
                      cwd=self.project_dir, check=True)

        # Update env.py to work with SQLModel
        self._configure_env_py()

    def _create_alembic_ini(self, database_url: Optional[str] = None):
        """Create alembic.ini configuration file."""
        db_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./todo.db")

        alembic_ini_content = f'''[alembic]
script_location = alembic
prepend_sys_path = .

# Database URL (use environment variable in production)
sqlalchemy.url = {db_url}

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
'''

        with open(self.alembic_ini, 'w') as f:
            f.write(alembic_ini_content)

    def _configure_env_py(self):
        """Configure alembic/env.py to work with SQLModel."""
        env_py_path = self.alembic_dir / "env.py"

        env_py_content = '''from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path to import models
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import SQLModel and all models
from sqlmodel import SQLModel

# Import your models here - adjust imports as needed
try:
    # Common model locations
    from models import *  # Try importing from models module
except ImportError:
    try:
        from src.models import *  # Try from src.models
    except ImportError:
        try:
            from backend.models import *  # Try from backend.models
        except ImportError:
            print("Warning: Could not import models. Please ensure your models are imported in env.py.")

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to SQLModel metadata
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

        with open(env_py_path, 'w') as f:
            f.write(env_py_content)

    def generate_migration(self, message: str, autogenerate: bool = True):
        """Generate a new migration file."""
        if not self.alembic_ini.exists():
            raise FileNotFoundError(f"Alembic not initialized. Run initialize_alembic() first.")

        try:
            # Generate migration using alembic command
            alembic_cfg = Config(str(self.alembic_ini))

            if autogenerate:
                command.revision(alembic_cfg, message=message, autogenerate=True)
            else:
                command.revision(alembic_cfg, message=message)

            print(f"Migration created with message: '{message}'")

        except Exception as e:
            print(f"Error generating migration: {e}")
            # Fallback to subprocess if direct command fails
            cmd = [sys.executable, "-m", "alembic", "revision"]
            if autogenerate:
                cmd.extend(["--autogenerate"])
            cmd.extend(["-m", message])

            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Subprocess error: {result.stderr}")
                raise Exception(f"Failed to generate migration: {result.stderr}")
            else:
                print(result.stdout)

    def run_migrations(self, revision: str = "head"):
        """Apply migrations to the database."""
        if not self.alembic_ini.exists():
            raise FileNotFoundError(f"Alembic not initialized. Run initialize_alembic() first.")

        try:
            alembic_cfg = Config(str(self.alembic_ini))
            command.upgrade(alembic_cfg, revision)
            print(f"Migrations applied up to: {revision}")
        except Exception as e:
            print(f"Error running migrations: {e}")
            # Fallback to subprocess
            result = subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", revision
            ], cwd=self.project_dir, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Subprocess error: {result.stderr}")
                raise Exception(f"Failed to run migrations: {result.stderr}")
            else:
                print(result.stdout)

    def rollback_migrations(self, revision: str = "-1"):
        """Rollback migrations."""
        if not self.alembic_ini.exists():
            raise FileNotFoundError(f"Alembic not initialized. Run initialize_alembic() first.")

        try:
            alembic_cfg = Config(str(self.alembic_ini))
            command.downgrade(alembic_cfg, revision)
            print(f"Migrations rolled back to: {revision}")
        except Exception as e:
            print(f"Error rolling back migrations: {e}")
            # Fallback to subprocess
            result = subprocess.run([
                sys.executable, "-m", "alembic", "downgrade", revision
            ], cwd=self.project_dir, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Subprocess error: {result.stderr}")
                raise Exception(f"Failed to rollback migrations: {result.stderr}")
            else:
                print(result.stdout)

    def check_status(self):
        """Check migration status."""
        if not self.alembic_ini.exists():
            raise FileNotFoundError(f"Alembic not initialized. Run initialize_alembic() first.")

        result = subprocess.run([
            sys.executable, "-m", "alembic", "current"
        ], cwd=self.project_dir, capture_output=True, text=True)

        if result.returncode == 0:
            print("Current migration status:")
            print(result.stdout)
        else:
            print(f"Error checking status: {result.stderr}")

def generate_migration_skill(schema_changes: str, migration_description: str,
                          data_migration_needed: bool = False,
                          database_url: Optional[str] = None):
    """
    Main function to generate database migrations.

    Args:
        schema_changes: Description of schema changes needed
        migration_description: Brief description of the migration
        data_migration_needed: Whether this requires data migration
        database_url: Database URL to use (optional)
    """
    generator = MigrationGenerator()

    # Initialize alembic if needed
    generator.initialize_alembic(database_url)

    # Generate the migration
    if data_migration_needed:
        # For data migrations, create empty migration and user will fill in details
        generator.generate_migration(migration_description, autogenerate=False)
        print("\\nNote: This is a data migration. You'll need to manually edit the generated migration file to add your data migration logic.")
    else:
        # For schema changes, use autogenerate
        generator.generate_migration(migration_description, autogenerate=True)

    print(f"\\nMigration created for changes: {schema_changes}")
    print(f"Description: {migration_description}")
    print(f"Data migration needed: {data_migration_needed}")

    return f"Migration file created for: {migration_description}"

# Example usage:
# generate_migration_skill(
#     schema_changes="Add priority column to tasks table",
#     migration_description="Add priority column to tasks",
#     data_migration_needed=False
# )
```

## Usage Examples

### Basic Schema Change
```python
generate_migration_skill(
    schema_changes="Add priority column to tasks table",
    migration_description="Add priority column to tasks",
    data_migration_needed=False
)
```

### Table Creation
```python
generate_migration_skill(
    schema_changes="Create users table with email and password",
    migration_description="Create users table",
    data_migration_needed=False
)
```

### Data Migration
```python
generate_migration_skill(
    schema_changes="Set default priority for existing tasks",
    migration_description="Set default priority for existing tasks",
    data_migration_needed=True
)
```

## Best Practices

- Always review auto-generated migrations before applying
- Test migrations on development database first
- Include both upgrade() and downgrade() functions
- Backup database before applying migrations to production
- Use meaningful migration descriptions