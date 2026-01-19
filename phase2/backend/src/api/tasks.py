"""Task API endpoints."""

import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession
from src.schemas import TagsResponse, TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
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
    - **priority**: Task priority (low/medium/high, default: medium)
    - **tags**: Task tags (max 10 tags, max 30 chars each)
    - **due_date**: Optional due date
    - **recurrence_pattern**: Recurrence pattern (none/daily/weekly/monthly)
    - **recurrence_end_date**: Optional end date for recurrence
    - **reminder_at**: Optional reminder datetime
    """
    task_service = TaskService(session)
    task = await task_service.create(current_user, data)
    return TaskResponse.from_task(task)


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
    sort: Literal["created", "title", "priority", "due_date"] = Query(
        "created", description="Sort field"
    ),
    order: Literal["asc", "desc"] = Query(
        "desc", description="Sort direction"
    ),
    priority: Literal["all", "low", "medium", "high"] | None = Query(
        None, description="Filter by priority"
    ),
    tags: str | None = Query(
        None, description="Filter by tags (comma-separated)"
    ),
    search: str | None = Query(
        None, description="Search in title and description"
    ),
    due_before: datetime | None = Query(
        None, description="Filter tasks due before this date"
    ),
    due_after: datetime | None = Query(
        None, description="Filter tasks due after this date"
    ),
    overdue_only: bool = Query(
        False, description="Only show overdue tasks"
    ),
) -> TaskListResponse:
    """List all tasks for the authenticated user with filtering and sorting.

    - **status**: Filter by completion status (all/pending/completed)
    - **sort**: Sort by created/title/priority/due_date
    - **order**: Sort direction (asc/desc)
    - **priority**: Filter by priority (all/low/medium/high)
    - **tags**: Filter by tags (comma-separated list)
    - **search**: Search keyword in title and description
    - **due_before**: Filter tasks due before this date
    - **due_after**: Filter tasks due after this date
    - **overdue_only**: Only show overdue tasks
    """
    task_service = TaskService(session)

    # Parse tags from comma-separated string
    tag_list = None
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]

    return await task_service.list_by_user(
        current_user,
        status=status_filter,
        sort=sort,
        order=order,
        priority=priority,
        tags=tag_list,
        search=search,
        due_before=due_before,
        due_after=due_after,
        overdue_only=overdue_only,
    )


@router.get(
    "/tags",
    response_model=TagsResponse,
    summary="Get user's tags",
)
async def get_user_tags(
    current_user: CurrentUser,
    session: DbSession,
) -> TagsResponse:
    """Get all unique tags used by the authenticated user.

    Useful for autocomplete in the frontend.
    """
    task_service = TaskService(session)
    tags = await task_service.get_user_tags(current_user)
    return TagsResponse(tags=tags)


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

    return TaskResponse.from_task(task)


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
    """Update a task's properties.

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
    return TaskResponse.from_task(updated_task)


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

    For recurring tasks, completing creates the next occurrence.
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

    updated_task, _next_task = await task_service.toggle_complete(task)
    return TaskResponse.from_task(updated_task)
