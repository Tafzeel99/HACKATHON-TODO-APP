"""Message model for chat messages."""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.conversation import Conversation


class MessageRole(str, Enum):
    """Message role in conversation."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Represents a single chat message in a conversation."""

    __tablename__ = "messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique message identifier",
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False,
        description="Parent conversation ID",
    )
    user_id: str = Field(
        index=True,
        nullable=False,
        description="Owner user ID",
    )
    role: str = Field(
        nullable=False,
        description="Message role: 'user' or 'assistant'",
    )
    content: str = Field(
        nullable=False,
        description="Message content",
    )
    tool_calls: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="MCP tool calls made (if any)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp",
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
