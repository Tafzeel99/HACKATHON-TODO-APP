"""UserPreferences Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserPreferencesUpdate(BaseModel):
    """Schema for user preferences update request."""

    accent_color: (
        Literal["indigo", "purple", "blue", "green", "orange", "pink", "red", "teal"]
        | None
    ) = Field(default=None, description="Theme accent color")
    email_reminders: bool | None = Field(
        default=None, description="Whether to send email reminders"
    )
    email_daily_digest: bool | None = Field(
        default=None, description="Whether to send daily digest emails"
    )
    reminder_time: str | None = Field(
        default=None,
        pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
        description="Time for daily digest (HH:MM format)",
    )
    dashboard_layout: dict | None = Field(
        default=None, description="Dashboard widget positions and visibility"
    )
    motivational_quotes: bool | None = Field(
        default=None, description="Whether to show motivational quotes"
    )
    default_view: Literal["list", "grid", "kanban"] | None = Field(
        default=None, description="Default task view"
    )
    timezone: str | None = Field(default=None, description="User timezone")

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        # Basic validation - more thorough validation could use pytz
        if len(v) > 50:
            raise ValueError("Timezone must be 50 characters or less")
        return v


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""

    user_id: uuid.UUID
    accent_color: str
    email_reminders: bool
    email_daily_digest: bool
    reminder_time: str
    dashboard_layout: dict
    motivational_quotes: bool
    default_view: str
    timezone: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_preferences(cls, prefs) -> "UserPreferencesResponse":
        """Create response from user preferences model."""
        return cls(
            user_id=prefs.user_id,
            accent_color=prefs.accent_color,
            email_reminders=prefs.email_reminders,
            email_daily_digest=prefs.email_daily_digest,
            reminder_time=prefs.reminder_time,
            dashboard_layout=prefs.dashboard_layout or {},
            motivational_quotes=prefs.motivational_quotes,
            default_view=prefs.default_view,
            timezone=prefs.timezone,
            created_at=prefs.created_at,
            updated_at=prefs.updated_at,
        )


class UserPreferencesDefault(BaseModel):
    """Default user preferences."""

    accent_color: str = "indigo"
    email_reminders: bool = True
    email_daily_digest: bool = False
    reminder_time: str = "09:00"
    dashboard_layout: dict = Field(default_factory=dict)
    motivational_quotes: bool = True
    default_view: str = "list"
    timezone: str = "UTC"
