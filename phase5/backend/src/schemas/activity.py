"""Activity Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.schemas.user import UserResponse


ActionType = Literal[
    "created",
    "updated",
    "completed",
    "uncompleted",
    "deleted",
    "shared",
    "unshared",
    "commented",
    "assigned",
    "unassigned",
]


class ActivityResponse(BaseModel):
    """Schema for activity response."""

    id: uuid.UUID
    task_id: uuid.UUID | None
    user: UserResponse
    action_type: str
    details: dict
    created_at: datetime
    task_title: str | None = None

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    """Schema for list of activities."""

    activities: list[ActivityResponse]
    total: int = Field(..., description="Total number of activities")
