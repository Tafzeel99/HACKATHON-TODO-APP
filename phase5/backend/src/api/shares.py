"""Task Share API endpoints."""

import uuid

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DbSession
from src.schemas.task import TaskListResponse, TaskResponse
from src.schemas.task_share import (
    TaskShareCreate,
    TaskShareListResponse,
    TaskShareResponse,
    TaskShareUpdate,
)
from src.services import ShareService, TaskService

router = APIRouter()


@router.post(
    "/{task_id}/shares",
    response_model=TaskShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Share task with user",
)
async def share_task(
    task_id: uuid.UUID,
    data: TaskShareCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskShareResponse:
    """Share a task with another user by email.

    - **user_email**: Email of user to share with
    - **permission**: Permission level (view/edit)
    """
    # Verify user owns the task
    task_service = TaskService(session)
    task = await task_service.get_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task owner can share",
        )

    share_service = ShareService(session)
    try:
        share = await share_service.share_task(
            task_id=task_id,
            owner_id=current_user,
            share_with_email=data.user_email,
            permission=data.permission,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return share


@router.get(
    "/{task_id}/shares",
    response_model=TaskShareListResponse,
    summary="Get task shares",
)
async def get_task_shares(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskShareListResponse:
    """Get all shares for a task."""
    # Verify user can access the task
    share_service = ShareService(session)
    can_access, _ = await share_service.can_access_task(current_user, task_id)

    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return await share_service.get_task_shares(task_id)


@router.delete(
    "/{task_id}/shares/{share_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove share",
)
async def remove_share(
    task_id: uuid.UUID,
    share_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> None:
    """Remove a share from a task."""
    share_service = ShareService(session)
    success = await share_service.remove_share(share_id, current_user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found or not authorized",
        )


@router.patch(
    "/{task_id}/shares/{share_id}",
    response_model=TaskShareResponse,
    summary="Update share permission",
)
async def update_share(
    task_id: uuid.UUID,
    share_id: uuid.UUID,
    data: TaskShareUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskShareResponse:
    """Update a share's permission level."""
    share_service = ShareService(session)
    share = await share_service.update_permission(
        share_id, current_user, data.permission
    )

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found or not authorized",
        )

    return share


@router.get(
    "/shared-with-me",
    response_model=TaskListResponse,
    summary="Get tasks shared with me",
)
async def get_shared_with_me(
    current_user: CurrentUser,
    session: DbSession,
) -> TaskListResponse:
    """Get all tasks that have been shared with the current user."""
    share_service = ShareService(session)
    tasks = await share_service.get_shared_with_me(current_user)

    return TaskListResponse(
        tasks=[TaskResponse.from_task(task) for task in tasks],
        total=len(tasks),
    )
