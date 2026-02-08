"""Comment SQLModel for task comments."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Comment(SQLModel, table=True):
    """Comment model representing a comment on a task."""

    __tablename__ = "comments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique comment identifier",
    )
    task_id: uuid.UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
        index=True,
        description="Task this comment belongs to",
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who wrote the comment",
    )
    parent_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="comments.id",
        nullable=True,
        index=True,
        description="Parent comment ID for threading",
    )
    content: str = Field(
        max_length=2000,
        nullable=False,
        description="Comment content (1-2000 characters)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Comment creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp",
    )
