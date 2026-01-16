"""Task SQLModel for database representation."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task model representing a single todo item."""

    __tablename__ = "tasks"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique task identifier",
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of this task",
    )
    title: str = Field(
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional task description (0-1000 characters)",
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Task completion status",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp",
    )
