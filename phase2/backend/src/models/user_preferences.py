"""UserPreferences SQLModel for database representation."""

import uuid
from datetime import datetime

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON


class UserPreferences(SQLModel, table=True):
    """User preferences model for storing user settings."""

    __tablename__ = "user_preferences"

    user_id: uuid.UUID = Field(
        primary_key=True,
        foreign_key="users.id",
        description="User ID (also primary key)",
    )
    accent_color: str = Field(
        default="indigo",
        max_length=20,
        nullable=False,
        description="Theme accent color",
    )
    email_reminders: bool = Field(
        default=True,
        nullable=False,
        description="Whether to send email reminders",
    )
    email_daily_digest: bool = Field(
        default=False,
        nullable=False,
        description="Whether to send daily digest emails",
    )
    reminder_time: str = Field(
        default="09:00",
        max_length=5,
        nullable=False,
        description="Time for daily digest (HH:MM format)",
    )
    dashboard_layout: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False, server_default="{}"),
        description="Dashboard widget positions and visibility",
    )
    motivational_quotes: bool = Field(
        default=True,
        nullable=False,
        description="Whether to show motivational quotes",
    )
    default_view: str = Field(
        default="list",
        max_length=20,
        nullable=False,
        description="Default task view (list, grid, kanban)",
    )
    timezone: str = Field(
        default="UTC",
        max_length=50,
        nullable=False,
        description="User timezone",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Preferences creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp",
    )
