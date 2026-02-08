"""Add intermediate and advanced fields to tasks table

Revision ID: 002
Revises: 001
Create Date: 2026-01-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add intermediate features columns
    op.add_column(
        "tasks",
        sa.Column(
            "priority",
            sa.String(10),
            nullable=False,
            server_default="medium",
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )

    # Add advanced features columns
    op.add_column(
        "tasks",
        sa.Column("due_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "recurrence_pattern",
            sa.String(10),
            nullable=False,
            server_default="none",
        ),
    )
    op.add_column(
        "tasks",
        sa.Column("recurrence_end_date", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "parent_task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "tasks",
        sa.Column("reminder_at", sa.DateTime(), nullable=True),
    )

    # Create indexes for new columns
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    op.create_index(
        "ix_tasks_tags",
        "tasks",
        ["tags"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_tasks_tags", table_name="tasks")
    op.drop_index("ix_tasks_due_date", table_name="tasks")
    op.drop_index("ix_tasks_priority", table_name="tasks")

    # Drop columns
    op.drop_column("tasks", "reminder_at")
    op.drop_column("tasks", "parent_task_id")
    op.drop_column("tasks", "recurrence_end_date")
    op.drop_column("tasks", "recurrence_pattern")
    op.drop_column("tasks", "due_date")
    op.drop_column("tasks", "tags")
    op.drop_column("tasks", "priority")
