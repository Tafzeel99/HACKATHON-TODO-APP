"""Add collaboration tables (task_shares, comments, activities) and assigned_to

Revision ID: 003
Revises: 002
Create Date: 2026-01-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add assigned_to column to tasks table
    op.add_column(
        "tasks",
        sa.Column(
            "assigned_to",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_tasks_assigned_to", "tasks", ["assigned_to"])

    # Create task_shares table
    op.create_table(
        "task_shares",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "shared_with_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "permission",
            sa.String(10),
            nullable=False,
            server_default="view",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("task_id", "shared_with_id", name="uq_task_shares_task_user"),
    )
    op.create_index("ix_task_shares_task_id", "task_shares", ["task_id"])
    op.create_index("ix_task_shares_owner_id", "task_shares", ["owner_id"])
    op.create_index("ix_task_shares_shared_with_id", "task_shares", ["shared_with_id"])

    # Create comments table
    op.create_table(
        "comments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("comments.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("content", sa.Text(), nullable=False),
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
    op.create_index("ix_comments_task_id", "comments", ["task_id"])
    op.create_index("ix_comments_user_id", "comments", ["user_id"])
    op.create_index("ix_comments_parent_id", "comments", ["parent_id"])

    # Create activities table
    op.create_table(
        "activities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action_type", sa.String(20), nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_activities_task_id", "activities", ["task_id"])
    op.create_index("ix_activities_user_id", "activities", ["user_id"])
    op.create_index("ix_activities_action_type", "activities", ["action_type"])
    op.create_index("ix_activities_created_at", "activities", ["created_at"])


def downgrade() -> None:
    # Drop activities table
    op.drop_index("ix_activities_created_at", table_name="activities")
    op.drop_index("ix_activities_action_type", table_name="activities")
    op.drop_index("ix_activities_user_id", table_name="activities")
    op.drop_index("ix_activities_task_id", table_name="activities")
    op.drop_table("activities")

    # Drop comments table
    op.drop_index("ix_comments_parent_id", table_name="comments")
    op.drop_index("ix_comments_user_id", table_name="comments")
    op.drop_index("ix_comments_task_id", table_name="comments")
    op.drop_table("comments")

    # Drop task_shares table
    op.drop_index("ix_task_shares_shared_with_id", table_name="task_shares")
    op.drop_index("ix_task_shares_owner_id", table_name="task_shares")
    op.drop_index("ix_task_shares_task_id", table_name="task_shares")
    op.drop_table("task_shares")

    # Drop assigned_to from tasks
    op.drop_index("ix_tasks_assigned_to", table_name="tasks")
    op.drop_column("tasks", "assigned_to")
