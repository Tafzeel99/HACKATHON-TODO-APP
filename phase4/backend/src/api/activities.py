"""Activity API endpoints."""

import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession
from src.schemas.activity import ActivityListResponse
from src.services import ActivityService, ShareService

router = APIRouter()


@router.get(
    "/tasks/{task_id}/activities",
    response_model=ActivityListResponse,
    summary="Get task activities",
)
async def get_task_activities(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(50, ge=1, le=100, description="Maximum activities to return"),
) -> ActivityListResponse:
    """Get activity history for a specific task."""
    # Verify user can access the task
    share_service = ShareService(session)
    can_access, _ = await share_service.can_access_task(current_user, task_id)

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    activity_service = ActivityService(session)
    return await activity_service.get_task_activities(task_id, limit)


@router.get(
    "",
    response_model=ActivityListResponse,
    summary="Get user activity feed",
)
async def get_user_activities(
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(50, ge=1, le=100, description="Maximum activities to return"),
    action_type: str | None = Query(
        None,
        description="Filter by action types (comma-separated)",
    ),
) -> ActivityListResponse:
    """Get activity feed for the current user.

    Returns activities performed by the user and activities on their tasks.
    """
    activity_service = ActivityService(session)

    action_types = None
    if action_type:
        action_types = [t.strip() for t in action_type.split(",") if t.strip()]

    return await activity_service.get_user_activities(
        current_user, limit, action_types
    )


@router.get(
    "/feed",
    response_model=ActivityListResponse,
    summary="Get activity feed",
)
async def get_activity_feed(
    current_user: CurrentUser,
    session: DbSession,
    limit: int = Query(50, ge=1, le=100, description="Maximum activities to return"),
) -> ActivityListResponse:
    """Get combined activity feed including shared task activities."""
    activity_service = ActivityService(session)
    return await activity_service.get_feed_for_user(current_user, limit)
