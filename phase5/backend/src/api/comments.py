"""Comment API endpoints."""

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession
from src.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from src.services import CommentService, ShareService

router = APIRouter()


@router.get(
    "/tasks/{task_id}/comments",
    response_model=CommentListResponse,
    summary="Get task comments",
)
async def get_task_comments(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
    include_replies: bool = Query(True, description="Include nested replies"),
) -> CommentListResponse:
    """Get all comments for a task with optional threading."""
    # Verify user can access the task
    share_service = ShareService(session)
    can_access, _ = await share_service.can_access_task(current_user, task_id)

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    comment_service = CommentService(session)
    return await comment_service.get_comments(task_id, include_replies)


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add comment to task",
)
async def create_comment(
    task_id: uuid.UUID,
    data: CommentCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> CommentResponse:
    """Add a comment to a task.

    - **content**: Comment content (1-2000 characters)
    - **parent_id**: Optional parent comment ID for replies
    """
    # Verify user can access the task (at least view permission)
    share_service = ShareService(session)
    can_access, _ = await share_service.can_access_task(current_user, task_id)

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    comment_service = CommentService(session)
    return await comment_service.create_comment(
        task_id=task_id,
        user_id=current_user,
        content=data.content,
        parent_id=data.parent_id,
    )


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    summary="Update comment",
)
async def update_comment(
    comment_id: uuid.UUID,
    data: CommentUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> CommentResponse:
    """Update a comment (only by owner)."""
    comment_service = CommentService(session)
    comment = await comment_service.update_comment(
        comment_id=comment_id,
        user_id=current_user,
        content=data.content,
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized",
        )

    return comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> None:
    """Delete a comment (only by owner)."""
    comment_service = CommentService(session)
    success = await comment_service.delete_comment(comment_id, current_user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized",
        )
