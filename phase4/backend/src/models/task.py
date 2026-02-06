"""Task SQLModel for database representation."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON

if TYPE_CHECKING:
    pass


class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


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

    # Intermediate features
    priority: str = Field(
        default="medium",
        nullable=False,
        index=True,
        description="Task priority (low, medium, high)",
    )
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False, server_default="[]"),
        description="Task tags (max 10, max 30 chars each)",
    )

    # Advanced features
    due_date: datetime | None = Field(
        default=None,
        nullable=True,
        index=True,
        description="Task due date",
    )
    recurrence_pattern: str = Field(
        default="none",
        nullable=False,
        description="Recurrence pattern (none, daily, weekly, monthly)",
    )
    recurrence_end_date: datetime | None = Field(
        default=None,
        nullable=True,
        description="End date for recurrence",
    )
    parent_task_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="tasks.id",
        nullable=True,
        description="Parent task ID for recurring task chain",
    )
    reminder_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Reminder datetime",
    )

    # Collaboration features
    assigned_to: uuid.UUID | None = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        index=True,
        description="User this task is assigned to",
    )

    # Organization features (Phase 2/3 enhancements)
    project_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="projects.id",
        nullable=True,
        index=True,
        description="Project/list this task belongs to",
    )
    pinned: bool = Field(
        default=False,
        nullable=False,
        description="Whether task is pinned to top",
    )
    archived: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Whether task is archived",
    )
    color: str | None = Field(
        default=None,
        max_length=7,
        nullable=True,
        description="Task color as hex code",
    )
    board_status: str = Field(
        default="todo",
        max_length=20,
        nullable=False,
        index=True,
        description="Kanban board status (todo, in_progress, done)",
    )
    position: int | None = Field(
        default=None,
        nullable=True,
        description="Position for ordering within column/list",
    )
