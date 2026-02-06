"""Project SQLModel for database representation."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    """Project model representing a task container/list."""

    __tablename__ = "projects"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique project identifier",
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of this project",
    )
    name: str = Field(
        max_length=100,
        nullable=False,
        description="Project name (1-100 characters)",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional project description",
    )
    color: str = Field(
        default="#6366f1",
        max_length=7,
        nullable=False,
        description="Project color as hex code",
    )
    icon: str | None = Field(
        default=None,
        max_length=50,
        description="Project icon (emoji or icon name)",
    )
    is_default: bool = Field(
        default=False,
        nullable=False,
        description="Whether this is the default Inbox project",
    )
    position: int = Field(
        default=0,
        nullable=False,
        description="Position for ordering projects",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Project creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp",
    )
