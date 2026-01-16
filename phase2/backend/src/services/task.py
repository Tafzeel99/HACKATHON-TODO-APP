"""Task service layer."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task
from src.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


class TaskService:
    """Service for task operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, data: TaskCreate) -> Task:
        """Create a new task for a user."""
        task = Task(
            user_id=user_id,
            title=data.title,
            description=data.description,
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        status: str = "all",
        sort: str = "created",
        order: str = "desc",
    ) -> TaskListResponse:
        """List all tasks for a user with optional filtering and sorting."""
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            query = query.where(Task.completed == True)  # noqa: E712

        # Apply sorting
        if sort == "title":
            sort_column = Task.title
        else:
            sort_column = Task.created_at

        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return TaskListResponse(
            tasks=[TaskResponse.model_validate(task) for task in tasks],
            total=len(tasks),
        )

    async def get_by_id(self, task_id: uuid.UUID) -> Task | None:
        """Get a task by ID."""
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def update(self, task: Task, data: TaskUpdate) -> Task:
        """Update a task."""
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description

        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete(self, task: Task) -> None:
        """Delete a task."""
        await self.session.delete(task)
        await self.session.commit()

    async def toggle_complete(self, task: Task) -> Task:
        """Toggle task completion status."""
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task
