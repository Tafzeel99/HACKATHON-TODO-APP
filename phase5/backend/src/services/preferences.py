"""User preferences service layer."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserPreferences
from src.schemas import UserPreferencesResponse, UserPreferencesUpdate


class PreferencesService:
    """Service for user preferences operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: uuid.UUID) -> UserPreferences:
        """Get user preferences, creating default if not exists."""
        result = await self.session.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalar_one_or_none()

        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            self.session.add(prefs)
            await self.session.commit()
            await self.session.refresh(prefs)

        return prefs

    async def update(
        self, user_id: uuid.UUID, data: UserPreferencesUpdate
    ) -> UserPreferences:
        """Update user preferences."""
        prefs = await self.get_or_create(user_id)

        if data.accent_color is not None:
            prefs.accent_color = data.accent_color
        if data.email_reminders is not None:
            prefs.email_reminders = data.email_reminders
        if data.email_daily_digest is not None:
            prefs.email_daily_digest = data.email_daily_digest
        if data.reminder_time is not None:
            prefs.reminder_time = data.reminder_time
        if data.dashboard_layout is not None:
            prefs.dashboard_layout = data.dashboard_layout
        if data.motivational_quotes is not None:
            prefs.motivational_quotes = data.motivational_quotes
        if data.default_view is not None:
            prefs.default_view = data.default_view
        if data.timezone is not None:
            prefs.timezone = data.timezone

        prefs.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(prefs)

        return prefs

    async def get_response(self, user_id: uuid.UUID) -> UserPreferencesResponse:
        """Get user preferences as response model."""
        prefs = await self.get_or_create(user_id)
        return UserPreferencesResponse.from_preferences(prefs)
