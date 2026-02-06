"""User SQLModel for database representation."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User model representing an authenticated person."""

    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique user identifier",
    )
    email: str = Field(
        max_length=255,
        unique=True,
        nullable=False,
        index=True,
        description="User's email address",
    )
    hashed_password: str = Field(
        nullable=False,
        description="Hashed password (never store plain text)",
    )
    name: str | None = Field(
        default=None,
        max_length=100,
        description="Optional display name",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp",
    )
