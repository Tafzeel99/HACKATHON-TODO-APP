"""Comment service layer for task comments."""

import uuid
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Comment, User
from src.schemas.comment import CommentListResponse, CommentResponse
from src.schemas.user import UserResponse
from src.services.activity import ActivityService


class CommentService:
    """Service for comment operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_comment(
        self,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
        parent_id: uuid.UUID | None = None,
    ) -> CommentResponse:
        """Create a new comment on a task."""
        comment = Comment(
            task_id=task_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
        )

        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)

        # Get user for response
        user_result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one()

        # Log activity
        activity_service = ActivityService(self.session)
        await activity_service.log_activity(
            user_id=user_id,
            task_id=task_id,
            action_type="commented",
            details={
                "comment_id": str(comment.id),
                "content_preview": content[:100] if len(content) > 100 else content,
                "is_reply": parent_id is not None,
            },
        )

        return CommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            user=UserResponse.model_validate(user),
            parent_id=comment.parent_id,
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[],
        )

    async def get_comments(
        self,
        task_id: uuid.UUID,
        include_replies: bool = True,
    ) -> CommentListResponse:
        """Get all comments for a task with optional threading."""
        # Get top-level comments first
        query = (
            select(Comment, User)
            .join(User, Comment.user_id == User.id)
            .where(
                and_(
                    Comment.task_id == task_id,
                    Comment.parent_id.is_(None),
                )
            )
            .order_by(Comment.created_at.asc())
        )

        result = await self.session.execute(query)
        rows = result.all()

        comments = []
        for comment, user in rows:
            comment_response = CommentResponse(
                id=comment.id,
                task_id=comment.task_id,
                user=UserResponse.model_validate(user),
                parent_id=comment.parent_id,
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                replies=[],
            )

            # Load replies if requested
            if include_replies:
                replies = await self._get_replies(comment.id)
                comment_response.replies = replies

            comments.append(comment_response)

        # Count total including replies
        count_result = await self.session.execute(
            select(func.count(Comment.id)).where(Comment.task_id == task_id)
        )
        total = count_result.scalar() or 0

        return CommentListResponse(comments=comments, total=total)

    async def _get_replies(
        self,
        parent_id: uuid.UUID,
    ) -> list[CommentResponse]:
        """Get replies to a comment."""
        query = (
            select(Comment, User)
            .join(User, Comment.user_id == User.id)
            .where(Comment.parent_id == parent_id)
            .order_by(Comment.created_at.asc())
        )

        result = await self.session.execute(query)
        rows = result.all()

        replies = []
        for comment, user in rows:
            reply = CommentResponse(
                id=comment.id,
                task_id=comment.task_id,
                user=UserResponse.model_validate(user),
                parent_id=comment.parent_id,
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                replies=[],
            )
            # Recursively get nested replies
            nested = await self._get_replies(comment.id)
            reply.replies = nested
            replies.append(reply)

        return replies

    async def get_comment_by_id(
        self,
        comment_id: uuid.UUID,
    ) -> tuple[Comment, User] | None:
        """Get a comment by ID."""
        result = await self.session.execute(
            select(Comment, User)
            .join(User, Comment.user_id == User.id)
            .where(Comment.id == comment_id)
        )
        row = result.first()
        return row if row else None

    async def update_comment(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> CommentResponse | None:
        """Update a comment (only by owner)."""
        result = await self.session.execute(
            select(Comment, User)
            .join(User, Comment.user_id == User.id)
            .where(
                and_(
                    Comment.id == comment_id,
                    Comment.user_id == user_id,
                )
            )
        )
        row = result.first()

        if not row:
            return None

        comment, user = row
        comment.content = content
        comment.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(comment)

        return CommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            user=UserResponse.model_validate(user),
            parent_id=comment.parent_id,
            content=comment.content,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[],
        )

    async def delete_comment(
        self,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a comment (only by owner)."""
        result = await self.session.execute(
            select(Comment).where(
                and_(
                    Comment.id == comment_id,
                    Comment.user_id == user_id,
                )
            )
        )
        comment = result.scalar_one_or_none()

        if not comment:
            return False

        # Delete comment (cascade will handle replies)
        await self.session.delete(comment)
        await self.session.commit()

        return True

    async def get_comment_count(self, task_id: uuid.UUID) -> int:
        """Get number of comments for a task."""
        result = await self.session.execute(
            select(func.count(Comment.id)).where(Comment.task_id == task_id)
        )
        return result.scalar() or 0
