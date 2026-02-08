"""User preferences API endpoints."""

from fastapi import APIRouter, status

from src.api.deps import CurrentUser, DbSession
from src.schemas import UserPreferencesResponse, UserPreferencesUpdate
from src.services import PreferencesService

router = APIRouter()


@router.get(
    "",
    response_model=UserPreferencesResponse,
    summary="Get user preferences",
)
async def get_preferences(
    current_user: CurrentUser,
    session: DbSession,
) -> UserPreferencesResponse:
    """Get user preferences.

    Creates default preferences if none exist.
    """
    prefs_service = PreferencesService(session)
    return await prefs_service.get_response(current_user)


@router.put(
    "",
    response_model=UserPreferencesResponse,
    summary="Update user preferences",
)
async def update_preferences(
    data: UserPreferencesUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> UserPreferencesResponse:
    """Update user preferences.

    - **accent_color**: Theme accent color
    - **email_reminders**: Whether to send email reminders
    - **email_daily_digest**: Whether to send daily digest emails
    - **reminder_time**: Time for daily digest (HH:MM format)
    - **dashboard_layout**: Dashboard widget positions and visibility
    - **motivational_quotes**: Whether to show motivational quotes
    - **default_view**: Default task view (list, grid, kanban)
    - **timezone**: User timezone
    """
    prefs_service = PreferencesService(session)
    prefs = await prefs_service.update(current_user, data)
    return UserPreferencesResponse.from_preferences(prefs)
