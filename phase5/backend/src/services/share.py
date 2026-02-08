"""Share service layer for task collaboration."""

import uuid
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task, TaskShare, User
from src.schemas.task_share import TaskShareListResponse, TaskShareResponse
from src.schemas.user import UserResponse
from src.services.activity import ActivityService


class ShareService:
    """Service for task sharing operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def share_task(
        self,
        task_id: uuid.UUID,
        owner_id: uuid.UUID,
        share_with_email: str,
        permission: str = "view",
    ) -> TaskShareResponse | None:
        """Share a task with another user by email."""
        # Find user by email
        result = await self.session.execute(
            select(User).where(User.email == share_with_email)
        )
        shared_with_user = result.scalar_one_or_none()

        if not shared_with_user:
            return None

        # Check if share already exists
        existing = await self.session.execute(
            select(TaskShare).where(
                and_(
                    TaskShare.task_id == task_id,
                    TaskShare.shared_with_id == shared_with_user.id,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Task already shared with this user")

        # Cannot share with yourself
        if shared_with_user.id == owner_id:
            raise ValueError("Cannot share task with yourself")

        # Create share
        share = TaskShare(
            task_id=task_id,
            owner_id=owner_id,
            shared_with_id=shared_with_user.id,
            permission=permission,
        )

        self.session.add(share)
        await self.session.commit()
        await self.session.refresh(share)

        # Log activity
        activity_service = ActivityService(self.session)
        await activity_service.log_activity(
            user_id=owner_id,
            task_id=task_id,
            action_type="shared",
            details={
                "shared_with_email": share_with_email,
                "shared_with_id": str(shared_with_user.id),
                "permission": permission,
            },
        )

        return TaskShareResponse(
            id=share.id,
            task_id=share.task_id,
            owner_id=share.owner_id,
            shared_with=UserResponse.model_validate(shared_with_user),
            permission=share.permission,
            created_at=share.created_at,
        )

    async def get_task_shares(
        self,
        task_id: uuid.UUID,
    ) -> TaskShareListResponse:
        """Get all shares for a task."""
        query = (
            select(TaskShare, User)
            .join(User, TaskShare.shared_with_id == User.id)
            .where(TaskShare.task_id == task_id)
            .order_by(TaskShare.created_at.desc())
        )

        result = await self.session.execute(query)
        rows = result.all()

        shares = []
        for share, user in rows:
            shares.append(
                TaskShareResponse(
                    id=share.id,
                    task_id=share.task_id,
                    owner_id=share.owner_id,
                    shared_with=UserResponse.model_validate(user),
                    permission=share.permission,
                    created_at=share.created_at,
                )
            )

        return TaskShareListResponse(shares=shares, total=len(shares))

    async def remove_share(
        self,
        share_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> bool:
        """Remove a task share."""
        result = await self.session.execute(
            select(TaskShare).where(
                and_(
                    TaskShare.id == share_id,
                    TaskShare.owner_id == owner_id,
                )
            )
        )
        share = result.scalar_one_or_none()

        if not share:
            return False

        # Log activity before deletion
        activity_service = ActivityService(self.session)
        await activity_service.log_activity(
            user_id=owner_id,
            task_id=share.task_id,
            action_type="unshared",
            details={"share_id": str(share_id)},
        )

        await self.session.delete(share)
        await self.session.commit()

        return True

    async def update_permission(
        self,
        share_id: uuid.UUID,
        owner_id: uuid.UUID,
        permission: str,
    ) -> TaskShareResponse | None:
        """Update share permission."""
        result = await self.session.execute(
            select(TaskShare, User)
            .join(User, TaskShare.shared_with_id == User.id)
            .where(
                and_(
                    TaskShare.id == share_id,
                    TaskShare.owner_id == owner_id,
                )
            )
        )
        row = result.first()

        if not row:
            return None

        share, user = row
        share.permission = permission

        await self.session.commit()
        await self.session.refresh(share)

        return TaskShareResponse(
            id=share.id,
            task_id=share.task_id,
            owner_id=share.owner_id,
            shared_with=UserResponse.model_validate(user),
            permission=share.permission,
            created_at=share.created_at,
        )

    async def get_shared_with_me(
        self,
        user_id: uuid.UUID,
    ) -> list[Task]:
        """Get tasks shared with a user."""
        query = (
            select(Task)
            .join(TaskShare, Task.id == TaskShare.task_id)
            .where(TaskShare.shared_with_id == user_id)
            .order_by(Task.created_at.desc())
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def can_access_task(
        self,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> tuple[bool, str | None]:
        """Check if user can access a task. Returns (can_access, permission)."""
        # Check if user owns the task
        task_result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()

        if not task:
            return False, None

        if task.user_id == user_id:
            return True, "owner"

        # Check if task is shared with user
        share_result = await self.session.execute(
            select(TaskShare).where(
                and_(
                    TaskShare.task_id == task_id,
                    TaskShare.shared_with_id == user_id,
                )
            )
        )
        share = share_result.scalar_one_or_none()

        if share:
            return True, share.permission

        return False, None

    async def get_share_count(self, task_id: uuid.UUID) -> int:
        """Get number of shares for a task."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(TaskShare.id)).where(TaskShare.task_id == task_id)
        )
        return result.scalar() or 0
