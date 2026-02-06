"""Task Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def to_naive_utc(dt: datetime | str | None) -> datetime | None:
    """Convert timezone-aware datetime to naive UTC datetime."""
    if dt is None:
        return None

    # Handle string input (before Pydantic coercion)
    if isinstance(dt, str):
        try:
            # Parse ISO format string
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            # Let Pydantic handle invalid strings
            return dt  # type: ignore

    if dt.tzinfo is not None:
        # Convert to UTC and remove timezone info
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


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


class BoardStatus(str, Enum):
    """Task board status for Kanban."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


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
    assigned_to: uuid.UUID | None = Field(
        default=None, description="User ID to assign task to"
    )
    # Organization fields
    project_id: uuid.UUID | None = Field(
        default=None, description="Project/list this task belongs to"
    )
    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Task color as hex code",
    )
    board_status: Literal["todo", "in_progress", "done"] = Field(
        default="todo", description="Kanban board status"
    )

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

    @field_validator("due_date", "recurrence_end_date", "reminder_at", mode="before")
    @classmethod
    def convert_to_naive_utc(cls, v: datetime | None) -> datetime | None:
        return to_naive_utc(v)


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
    assigned_to: uuid.UUID | None = Field(
        default=None, description="User ID to assign task to"
    )
    # Organization fields
    project_id: uuid.UUID | None = Field(
        default=None, description="Project/list this task belongs to"
    )
    pinned: bool | None = Field(default=None, description="Whether task is pinned")
    archived: bool | None = Field(default=None, description="Whether task is archived")
    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Task color as hex code",
    )
    board_status: Literal["todo", "in_progress", "done"] | None = Field(
        default=None, description="Kanban board status"
    )
    position: int | None = Field(default=None, description="Position in list/column")

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

    @field_validator("due_date", "recurrence_end_date", "reminder_at", mode="before")
    @classmethod
    def convert_to_naive_utc(cls, v: datetime | None) -> datetime | None:
        return to_naive_utc(v)


class UserBasic(BaseModel):
    """Basic user info for embedding in responses."""

    id: uuid.UUID
    email: str
    name: str | None

    model_config = {"from_attributes": True}


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
    assigned_to: uuid.UUID | None = None
    assignee: UserBasic | None = None
    comment_count: int = 0
    share_count: int = 0
    # Organization fields
    project_id: uuid.UUID | None = None
    pinned: bool = False
    archived: bool = False
    color: str | None = None
    board_status: str = "todo"
    position: int | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_task(
        cls,
        task,
        assignee=None,
        comment_count: int = 0,
        share_count: int = 0,
    ) -> "TaskResponse":
        """Create response from task with computed fields."""
        is_overdue = False
        if task.due_date and not task.completed:
            is_overdue = task.due_date < datetime.utcnow()

        assignee_data = None
        if assignee:
            assignee_data = UserBasic(
                id=assignee.id,
                email=assignee.email,
                name=assignee.name,
            )

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
            assigned_to=task.assigned_to,
            assignee=assignee_data,
            comment_count=comment_count,
            share_count=share_count,
            project_id=getattr(task, "project_id", None),
            pinned=getattr(task, "pinned", False),
            archived=getattr(task, "archived", False),
            color=getattr(task, "color", None),
            board_status=getattr(task, "board_status", "todo"),
            position=getattr(task, "position", None),
        )


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
    total: int = Field(..., description="Total number of tasks")


class TagsResponse(BaseModel):
    """Schema for user tags response."""

    tags: list[str] = Field(..., description="List of unique tags used by user")


class TaskReorder(BaseModel):
    """Schema for task reorder request."""

    task_ids: list[uuid.UUID] = Field(..., description="Ordered list of task IDs")
    board_status: Literal["todo", "in_progress", "done"] | None = Field(
        default=None, description="Target board status for all tasks"
    )


class BulkArchive(BaseModel):
    """Schema for bulk archive request."""

    task_ids: list[uuid.UUID] | None = Field(
        default=None, description="Specific task IDs to archive (null = all completed)"
    )
    archive: bool = Field(default=True, description="True to archive, False to unarchive")
