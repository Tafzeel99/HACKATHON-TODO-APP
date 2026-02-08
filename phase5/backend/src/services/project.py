"""Project service layer."""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Project, Task
from src.schemas import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate


class ProjectService:
    """Service for project operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, data: ProjectCreate) -> Project:
        """Create a new project for a user."""
        # Get max position for ordering
        max_pos_result = await self.session.execute(
            select(func.max(Project.position)).where(Project.user_id == user_id)
        )
        max_pos = max_pos_result.scalar() or 0

        project = Project(
            user_id=user_id,
            name=data.name,
            description=data.description,
            color=data.color,
            icon=data.icon,
            position=max_pos + 1,
        )

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def list_by_user(self, user_id: uuid.UUID) -> ProjectListResponse:
        """List all projects for a user with task counts."""
        # Get projects
        query = (
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.position.asc())
        )
        result = await self.session.execute(query)
        projects = result.scalars().all()

        # Get task counts for each project
        project_responses = []
        for project in projects:
            task_count_result = await self.session.execute(
                select(func.count(Task.id)).where(
                    Task.project_id == project.id,
                    Task.archived == False,  # noqa: E712
                )
            )
            task_count = task_count_result.scalar() or 0
            project_responses.append(
                ProjectResponse.from_project(project, task_count=task_count)
            )

        return ProjectListResponse(projects=project_responses, total=len(projects))

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Get a project by ID."""
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_with_task_count(
        self, project_id: uuid.UUID
    ) -> tuple[Project | None, int]:
        """Get a project by ID with task count."""
        project = await self.get_by_id(project_id)
        if not project:
            return None, 0

        task_count_result = await self.session.execute(
            select(func.count(Task.id)).where(
                Task.project_id == project.id,
                Task.archived == False,  # noqa: E712
            )
        )
        task_count = task_count_result.scalar() or 0

        return project, task_count

    async def update(self, project: Project, data: ProjectUpdate) -> Project:
        """Update a project."""
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        if data.color is not None:
            project.color = data.color
        if data.icon is not None:
            project.icon = data.icon

        project.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def delete(self, project: Project) -> None:
        """Delete a project (tasks will have project_id set to NULL)."""
        await self.session.delete(project)
        await self.session.commit()

    async def reorder(
        self, user_id: uuid.UUID, project_ids: list[uuid.UUID]
    ) -> list[Project]:
        """Reorder projects based on provided order."""
        # Update positions
        for idx, project_id in enumerate(project_ids):
            result = await self.session.execute(
                select(Project).where(
                    Project.id == project_id,
                    Project.user_id == user_id,
                )
            )
            project = result.scalar_one_or_none()
            if project:
                project.position = idx
                project.updated_at = datetime.utcnow()

        await self.session.commit()

        # Return updated list
        return (await self.list_by_user(user_id)).projects

    async def get_or_create_inbox(self, user_id: uuid.UUID) -> Project:
        """Get or create the default Inbox project for a user."""
        result = await self.session.execute(
            select(Project).where(
                Project.user_id == user_id,
                Project.is_default == True,  # noqa: E712
            )
        )
        inbox = result.scalar_one_or_none()

        if not inbox:
            inbox = Project(
                user_id=user_id,
                name="Inbox",
                description="Default project for uncategorized tasks",
                color="#6b7280",
                icon="inbox",
                is_default=True,
                position=0,
            )
            self.session.add(inbox)
            await self.session.commit()
            await self.session.refresh(inbox)

        return inbox
