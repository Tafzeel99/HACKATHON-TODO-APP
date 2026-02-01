"""Activity SQLModel for audit logging."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class ActionType(str, Enum):
    """Types of actions that can be logged."""

    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    UNCOMPLETED = "uncompleted"
    DELETED = "deleted"
    SHARED = "shared"
    UNSHARED = "unshared"
    COMMENTED = "commented"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"


class Activity(SQLModel, table=True):
    """Activity model representing an audit log entry."""

    __tablename__ = "activities"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique activity identifier",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="tasks.id",
        nullable=True,
        index=True,
        description="Task related to this activity (null for user-level)",
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who performed the action",
    )
    action_type: str = Field(
        nullable=False,
        index=True,
        description="Type of action performed",
    )
    details: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
        description="Additional action details",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Activity timestamp",
    )
