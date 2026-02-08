"""Activity service layer for audit logging."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Activity, Task, User
from src.schemas.activity import ActivityListResponse, ActivityResponse
from src.schemas.user import UserResponse


class ActivityService:
    """Service for activity/audit log operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_activity(
        self,
        user_id: uuid.UUID,
        action_type: str,
        task_id: uuid.UUID | None = None,
        details: dict | None = None,
    ) -> Activity:
        """Log an activity."""
        activity = Activity(
            user_id=user_id,
            task_id=task_id,
            action_type=action_type,
            details=details or {},
        )

        self.session.add(activity)
        await self.session.commit()
        await self.session.refresh(activity)

        return activity

    async def get_task_activities(
        self,
        task_id: uuid.UUID,
        limit: int = 50,
    ) -> ActivityListResponse:
        """Get activities for a specific task."""
        query = (
            select(Activity, User, Task)
            .join(User, Activity.user_id == User.id)
            .outerjoin(Task, Activity.task_id == Task.id)
            .where(Activity.task_id == task_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        rows = result.all()

        activities = []
        for activity, user, task in rows:
            activities.append(
                ActivityResponse(
                    id=activity.id,
                    task_id=activity.task_id,
                    user=UserResponse.model_validate(user),
                    action_type=activity.action_type,
                    details=activity.details,
                    created_at=activity.created_at,
                    task_title=task.title if task else None,
                )
            )

        return ActivityListResponse(activities=activities, total=len(activities))

    async def get_user_activities(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        action_types: list[str] | None = None,
    ) -> ActivityListResponse:
        """Get activities for a user (their own actions or actions on their tasks)."""
        # Get activities where user performed the action
        query = (
            select(Activity, User, Task)
            .join(User, Activity.user_id == User.id)
            .outerjoin(Task, Activity.task_id == Task.id)
            .where(Activity.user_id == user_id)
        )

        if action_types:
            query = query.where(Activity.action_type.in_(action_types))

        query = query.order_by(Activity.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        rows = result.all()

        activities = []
        for activity, user, task in rows:
            activities.append(
                ActivityResponse(
                    id=activity.id,
                    task_id=activity.task_id,
                    user=UserResponse.model_validate(user),
                    action_type=activity.action_type,
                    details=activity.details,
                    created_at=activity.created_at,
                    task_title=task.title if task else None,
                )
            )

        return ActivityListResponse(activities=activities, total=len(activities))

    async def get_feed_for_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> ActivityListResponse:
        """Get activity feed for user including activities on tasks shared with them."""
        # Get task IDs the user owns
        owned_tasks_query = select(Task.id).where(Task.user_id == user_id)
        owned_result = await self.session.execute(owned_tasks_query)
        owned_task_ids = [row[0] for row in owned_result.all()]

        # Get activities on owned tasks or by the user
        query = (
            select(Activity, User, Task)
            .join(User, Activity.user_id == User.id)
            .outerjoin(Task, Activity.task_id == Task.id)
            .where(
                (Activity.user_id == user_id)
                | (Activity.task_id.in_(owned_task_ids))
            )
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        rows = result.all()

        activities = []
        for activity, user, task in rows:
            activities.append(
                ActivityResponse(
                    id=activity.id,
                    task_id=activity.task_id,
                    user=UserResponse.model_validate(user),
                    action_type=activity.action_type,
                    details=activity.details,
                    created_at=activity.created_at,
                    task_title=task.title if task else None,
                )
            )

        return ActivityListResponse(activities=activities, total=len(activities))
