"""Task API endpoints."""

import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession
from src.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from src.services import TaskService

router = APIRouter()


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
)
async def create_task(
    data: TaskCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskResponse:
    """Create a new task for the authenticated user.

    - **title**: Task title (1-200 characters, required)
    - **description**: Task description (0-1000 characters, optional)
    """
    task_service = TaskService(session)
    task = await task_service.create(current_user, data)
    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List user's tasks",
)
async def list_tasks(
    current_user: CurrentUser,
    session: DbSession,
    status_filter: Literal["all", "pending", "completed"] = Query(
        "all", alias="status", description="Filter by completion status"
    ),
    sort: Literal["created", "title"] = Query(
        "created", description="Sort field"
    ),
    order: Literal["asc", "desc"] = Query(
        "desc", description="Sort direction"
    ),
) -> TaskListResponse:
    """List all tasks for the authenticated user.

    - **status**: Filter by completion status (all/pending/completed)
    - **sort**: Sort by created date or title
    - **order**: Sort direction (asc/desc)
    """
    task_service = TaskService(session)
    return await task_service.list_by_user(
        current_user,
        status=status_filter,
        sort=sort,
        order=order,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
)
async def get_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskResponse:
    """Get a single task by ID.

    Returns 404 if task not found, 403 if task belongs to another user.
    """
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
            detail="Forbidden",
        )

    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskResponse:
    """Update a task's title and/or description.

    Returns 404 if task not found, 403 if task belongs to another user.
    """
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
            detail="Forbidden",
        )

    updated_task = await task_service.update(task, data)
    return TaskResponse.model_validate(updated_task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
async def delete_task(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> None:
    """Delete a task permanently.

    Returns 404 if task not found, 403 if task belongs to another user.
    """
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
            detail="Forbidden",
        )

    await task_service.delete(task)


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion status",
)
async def toggle_task_complete(
    task_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> TaskResponse:
    """Toggle task completion status (pending <-> completed).

    Returns 404 if task not found, 403 if task belongs to another user.
    """
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
            detail="Forbidden",
        )

    updated_task = await task_service.toggle_complete(task)
    return TaskResponse.model_validate(updated_task)
