"""Task Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(
        default=None, max_length=1000, description="Optional task description"
    )


class TaskUpdate(BaseModel):
    """Schema for task update request."""

    title: str | None = Field(
        default=None, min_length=1, max_length=200, description="New task title"
    )
    description: str | None = Field(
        default=None, max_length=1000, description="New task description"
    )


class TaskResponse(BaseModel):
    """Schema for single task response."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
    total: int = Field(..., description="Total number of tasks")
