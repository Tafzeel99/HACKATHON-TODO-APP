"""Conversation model for chat sessions."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.message import Message


class Conversation(SQLModel, table=True):
    """Represents a chat conversation session for a user."""

    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique conversation identifier",
    )
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Owner user ID",
    )
    title: str | None = Field(
        default=None,
        max_length=200,
        description="Optional conversation title",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp",
    )

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
