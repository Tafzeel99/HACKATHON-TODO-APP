"""Project Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for project creation request."""

    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: str | None = Field(
        default=None, max_length=500, description="Optional project description"
    )
    color: str = Field(
        default="#6366f1",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Project color as hex code",
    )
    icon: str | None = Field(
        default=None, max_length=50, description="Project icon (emoji or icon name)"
    )


class ProjectUpdate(BaseModel):
    """Schema for project update request."""

    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="New project name"
    )
    description: str | None = Field(
        default=None, max_length=500, description="New project description"
    )
    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="New project color as hex code",
    )
    icon: str | None = Field(
        default=None, max_length=50, description="New project icon"
    )


class ProjectReorder(BaseModel):
    """Schema for project reorder request."""

    project_ids: list[uuid.UUID] = Field(
        ..., description="Ordered list of project IDs"
    )


class ProjectResponse(BaseModel):
    """Schema for single project response."""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    color: str
    icon: str | None
    is_default: bool
    position: int
    created_at: datetime
    updated_at: datetime
    task_count: int = 0

    model_config = {"from_attributes": True}

    @classmethod
    def from_project(cls, project, task_count: int = 0) -> "ProjectResponse":
        """Create response from project with computed fields."""
        return cls(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            color=project.color,
            icon=project.icon,
            is_default=project.is_default,
            position=project.position,
            created_at=project.created_at,
            updated_at=project.updated_at,
            task_count=task_count,
        )


class ProjectListResponse(BaseModel):
    """Schema for project list response."""

    projects: list[ProjectResponse]
    total: int = Field(..., description="Total number of projects")
