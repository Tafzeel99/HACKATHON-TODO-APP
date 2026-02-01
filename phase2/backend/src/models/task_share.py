"""TaskShare SQLModel for task collaboration."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class SharePermission(str, Enum):
    """Permission levels for shared tasks."""

    VIEW = "view"
    EDIT = "edit"


class TaskShare(SQLModel, table=True):
    """TaskShare model representing a shared task relationship."""

    __tablename__ = "task_shares"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique share identifier",
    )
    task_id: uuid.UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
        index=True,
        description="Task being shared",
    )
    owner_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns the task",
    )
    shared_with_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User the task is shared with",
    )
    permission: str = Field(
        default="view",
        nullable=False,
        description="Permission level (view, edit)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Share creation timestamp",
    )
