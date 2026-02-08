"""Comment Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.user import UserResponse


class CommentCreate(BaseModel):
    """Schema for creating a comment."""

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Comment content"
    )
    parent_id: uuid.UUID | None = Field(
        default=None, description="Parent comment ID for replies"
    )


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    content: str = Field(
        ..., min_length=1, max_length=2000, description="Updated comment content"
    )


class CommentResponse(BaseModel):
    """Schema for comment response."""

    id: uuid.UUID
    task_id: uuid.UUID
    user: UserResponse
    parent_id: uuid.UUID | None
    content: str
    created_at: datetime
    updated_at: datetime
    replies: list["CommentResponse"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    """Schema for list of comments."""

    comments: list[CommentResponse]
    total: int = Field(..., description="Total number of comments")
