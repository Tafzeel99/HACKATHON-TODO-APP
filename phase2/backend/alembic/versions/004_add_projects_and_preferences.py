"""Add projects, user_preferences tables and task organization fields

Revision ID: 004
Revises: 003
Create Date: 2026-01-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = :table)"
        ),
        {"table": table_name},
    )
    return result.scalar()


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column)"
        ),
        {"table": table_name, "column": column_name},
    )
    return result.scalar()


def upgrade() -> None:
    # Create projects table if not exists
    if not table_exists("projects"):
        op.create_table(
            "projects",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column(
                "user_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("description", sa.String(500), nullable=True),
            sa.Column("color", sa.String(7), nullable=False, server_default="#6366f1"),
            sa.Column("icon", sa.String(50), nullable=True),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )
        op.create_index("ix_projects_user_id", "projects", ["user_id"])

    # Create user_preferences table if not exists
    if not table_exists("user_preferences"):
        op.create_table(
            "user_preferences",
            sa.Column(
                "user_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column(
                "accent_color", sa.String(20), nullable=False, server_default="indigo"
            ),
            sa.Column("email_reminders", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "email_daily_digest", sa.Boolean(), nullable=False, server_default="false"
            ),
            sa.Column("reminder_time", sa.String(5), nullable=False, server_default="09:00"),
            sa.Column(
                "dashboard_layout",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default="{}",
            ),
            sa.Column(
                "motivational_quotes", sa.Boolean(), nullable=False, server_default="true"
            ),
            sa.Column("default_view", sa.String(20), nullable=False, server_default="list"),
            sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )

    # Add organization fields to tasks table (only if not exists)
    if not column_exists("tasks", "project_id"):
        op.add_column(
            "tasks",
            sa.Column(
                "project_id",
                postgresql.UUID(as_uuid=True),
                nullable=True,
            ),
        )
        # Add FK constraint separately
        op.create_foreign_key(
            "fk_tasks_project_id",
            "tasks",
            "projects",
            ["project_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if not column_exists("tasks", "pinned"):
        op.add_column(
            "tasks",
            sa.Column("pinned", sa.Boolean(), nullable=False, server_default="false"),
        )

    if not column_exists("tasks", "archived"):
        op.add_column(
            "tasks",
            sa.Column("archived", sa.Boolean(), nullable=False, server_default="false"),
        )

    if not column_exists("tasks", "color"):
        op.add_column(
            "tasks",
            sa.Column("color", sa.String(7), nullable=True),
        )

    if not column_exists("tasks", "board_status"):
        op.add_column(
            "tasks",
            sa.Column("board_status", sa.String(20), nullable=False, server_default="todo"),
        )

    if not column_exists("tasks", "position"):
        op.add_column(
            "tasks",
            sa.Column("position", sa.Integer(), nullable=True),
        )

    # Create indexes for new task columns (ignore if exists)
    try:
        op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    except Exception:
        pass
    try:
        op.create_index("ix_tasks_archived", "tasks", ["archived"])
    except Exception:
        pass
    try:
        op.create_index("ix_tasks_board_status", "tasks", ["board_status"])
    except Exception:
        pass


def downgrade() -> None:
    # Drop indexes from tasks
    op.drop_index("ix_tasks_board_status", table_name="tasks")
    op.drop_index("ix_tasks_archived", table_name="tasks")
    op.drop_index("ix_tasks_project_id", table_name="tasks")

    # Drop columns from tasks
    op.drop_column("tasks", "position")
    op.drop_column("tasks", "board_status")
    op.drop_column("tasks", "color")
    op.drop_column("tasks", "archived")
    op.drop_column("tasks", "pinned")
    op.drop_column("tasks", "project_id")

    # Drop user_preferences table
    op.drop_table("user_preferences")

    # Drop projects table
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_table("projects")
