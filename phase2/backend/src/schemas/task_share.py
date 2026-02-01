"""TaskShare Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse


class TaskShareCreate(BaseModel):
    """Schema for creating a task share."""

    user_email: EmailStr = Field(..., description="Email of user to share with")
    permission: Literal["view", "edit"] = Field(
        default="view", description="Permission level"
    )


class TaskShareUpdate(BaseModel):
    """Schema for updating a task share."""

    permission: Literal["view", "edit"] = Field(..., description="New permission level")


class TaskShareResponse(BaseModel):
    """Schema for task share response."""

    id: uuid.UUID
    task_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with: UserResponse
    permission: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskShareListResponse(BaseModel):
    """Schema for list of task shares."""

    shares: list[TaskShareResponse]
    total: int = Field(..., description="Total number of shares")
