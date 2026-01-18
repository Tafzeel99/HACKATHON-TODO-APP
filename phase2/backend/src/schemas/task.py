"""Task Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


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


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(
        default=None, max_length=1000, description="Optional task description"
    )
    priority: Literal["low", "medium", "high"] = Field(
        default="medium", description="Task priority"
    )
    tags: list[str] = Field(
        default_factory=list, description="Task tags (max 10, max 30 chars each)"
    )
    due_date: datetime | None = Field(default=None, description="Task due date")
    recurrence_pattern: Literal["none", "daily", "weekly", "monthly"] = Field(
        default="none", description="Recurrence pattern"
    )
    recurrence_end_date: datetime | None = Field(
        default=None, description="End date for recurrence"
    )
    reminder_at: datetime | None = Field(default=None, description="Reminder datetime")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        for tag in v:
            if len(tag) > 30:
                raise ValueError("Each tag must be 30 characters or less")
            if not tag.strip():
                raise ValueError("Tags cannot be empty")
        return [tag.strip().lower() for tag in v]


class TaskUpdate(BaseModel):
    """Schema for task update request."""

    title: str | None = Field(
        default=None, min_length=1, max_length=200, description="New task title"
    )
    description: str | None = Field(
        default=None, max_length=1000, description="New task description"
    )
    priority: Literal["low", "medium", "high"] | None = Field(
        default=None, description="Task priority"
    )
    tags: list[str] | None = Field(default=None, description="Task tags")
    due_date: datetime | None = Field(default=None, description="Task due date")
    recurrence_pattern: Literal["none", "daily", "weekly", "monthly"] | None = Field(
        default=None, description="Recurrence pattern"
    )
    recurrence_end_date: datetime | None = Field(
        default=None, description="End date for recurrence"
    )
    reminder_at: datetime | None = Field(default=None, description="Reminder datetime")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        for tag in v:
            if len(tag) > 30:
                raise ValueError("Each tag must be 30 characters or less")
            if not tag.strip():
                raise ValueError("Tags cannot be empty")
        return [tag.strip().lower() for tag in v]


class TaskResponse(BaseModel):
    """Schema for single task response."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
    priority: str
    tags: list[str]
    due_date: datetime | None
    recurrence_pattern: str
    recurrence_end_date: datetime | None
    parent_task_id: uuid.UUID | None
    reminder_at: datetime | None
    is_overdue: bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def from_task(cls, task) -> "TaskResponse":
        """Create response from task with computed fields."""
        is_overdue = False
        if task.due_date and not task.completed:
            is_overdue = task.due_date < datetime.utcnow()

        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            created_at=task.created_at,
            updated_at=task.updated_at,
            priority=task.priority,
            tags=task.tags or [],
            due_date=task.due_date,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_end_date=task.recurrence_end_date,
            parent_task_id=task.parent_task_id,
            reminder_at=task.reminder_at,
            is_overdue=is_overdue,
        )


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
    total: int = Field(..., description="Total number of tasks")


class TagsResponse(BaseModel):
    """Schema for user tags response."""

    tags: list[str] = Field(..., description="List of unique tags used by user")
