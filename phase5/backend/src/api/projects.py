"""Project API endpoints."""

import uuid

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUser, DbSession
from src.schemas import (
    ProjectCreate,
    ProjectListResponse,
    ProjectReorder,
    ProjectResponse,
    ProjectUpdate,
)
from src.services import ProjectService

router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
)
async def create_project(
    data: ProjectCreate,
    current_user: CurrentUser,
    session: DbSession,
) -> ProjectResponse:
    """Create a new project for the authenticated user.

    - **name**: Project name (1-100 characters, required)
    - **description**: Project description (0-500 characters, optional)
    - **color**: Project color as hex code (default: #6366f1)
    - **icon**: Project icon (emoji or icon name, optional)
    """
    project_service = ProjectService(session)
    project = await project_service.create(current_user, data)
    return ProjectResponse.from_project(project)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List user's projects",
)
async def list_projects(
    current_user: CurrentUser,
    session: DbSession,
) -> ProjectListResponse:
    """List all projects for the authenticated user with task counts."""
    project_service = ProjectService(session)
    return await project_service.list_by_user(current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> ProjectResponse:
    """Get a single project by ID with task count.

    Returns 404 if project not found, 403 if project belongs to another user.
    """
    project_service = ProjectService(session)
    project, task_count = await project_service.get_with_task_count(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return ProjectResponse.from_project(project, task_count=task_count)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: CurrentUser,
    session: DbSession,
) -> ProjectResponse:
    """Update a project's properties.

    Returns 404 if project not found, 403 if project belongs to another user.
    Cannot update default Inbox project name.
    """
    project_service = ProjectService(session)
    project, task_count = await project_service.get_with_task_count(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    # Prevent renaming default project
    if project.is_default and data.name is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot rename the default Inbox project",
        )

    updated_project = await project_service.update(project, data)
    return ProjectResponse.from_project(updated_project, task_count=task_count)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    session: DbSession,
) -> None:
    """Delete a project.

    Tasks in this project will have their project_id set to NULL.
    Cannot delete the default Inbox project.
    Returns 404 if project not found, 403 if project belongs to another user.
    """
    project_service = ProjectService(session)
    project = await project_service.get_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    if project.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the default Inbox project",
        )

    await project_service.delete(project)


@router.patch(
    "/reorder",
    response_model=list[ProjectResponse],
    summary="Reorder projects",
)
async def reorder_projects(
    data: ProjectReorder,
    current_user: CurrentUser,
    session: DbSession,
) -> list[ProjectResponse]:
    """Reorder projects based on provided order."""
    project_service = ProjectService(session)
    projects = await project_service.reorder(current_user, data.project_ids)
    return projects
