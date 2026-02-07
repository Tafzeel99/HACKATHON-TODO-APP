"""Task service layer."""

import uuid
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task
from src.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


class TaskService:
    """Service for task operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: uuid.UUID, data: TaskCreate) -> Task:
        """Create a new task for a user."""
        # Get max position for ordering
        max_pos_result = await self.session.execute(
            select(func.max(Task.position)).where(
                Task.user_id == user_id,
                Task.project_id == data.project_id,
                Task.board_status == data.board_status,
            )
        )
        max_pos = max_pos_result.scalar() or 0

        task = Task(
            user_id=user_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            tags=data.tags,
            due_date=data.due_date,
            recurrence_pattern=data.recurrence_pattern,
            recurrence_end_date=data.recurrence_end_date,
            reminder_at=data.reminder_at,
            project_id=data.project_id,
            color=data.color,
            board_status=data.board_status,
            position=max_pos + 1,
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
        priority: str | None = None,
        tags: list[str] | None = None,
        search: str | None = None,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
        overdue_only: bool = False,
        project_id: uuid.UUID | None = None,
        archived: bool | None = None,
        board_status: str | None = None,
        pinned: bool | None = None,
    ) -> TaskListResponse:
        """List all tasks for a user with optional filtering and sorting."""
        query = select(Task).where(Task.user_id == user_id)

        # Apply archive filter (default: show non-archived)
        if archived is not None:
            query = query.where(Task.archived == archived)
        else:
            query = query.where(Task.archived == False)  # noqa: E712

        # Apply project filter
        if project_id is not None:
            query = query.where(Task.project_id == project_id)

        # Apply board status filter
        if board_status is not None:
            query = query.where(Task.board_status == board_status)

        # Apply pinned filter
        if pinned is not None:
            query = query.where(Task.pinned == pinned)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)  # noqa: E712
        elif status == "completed":
            query = query.where(Task.completed == True)  # noqa: E712

        # Apply priority filter
        if priority and priority != "all":
            query = query.where(Task.priority == priority)

        # Apply tags filter (any tag matches)
        if tags:
            # Use PostgreSQL JSONB containment operator for tag filtering
            tag_conditions = [Task.tags.contains([tag]) for tag in tags]
            query = query.where(or_(*tag_conditions))

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )

        # Apply due date filters
        if due_before:
            query = query.where(Task.due_date <= due_before)
        if due_after:
            query = query.where(Task.due_date >= due_after)

        # Apply overdue filter
        if overdue_only:
            query = query.where(
                Task.due_date < datetime.utcnow(),
                Task.completed == False,  # noqa: E712
            )

        # Apply sorting
        priority_order = {"high": 0, "medium": 1, "low": 2}

        if sort == "title":
            sort_column = Task.title
        elif sort == "priority":
            # Custom priority ordering using case expression
            from sqlalchemy import case

            sort_column = case(
                (Task.priority == "high", 0),
                (Task.priority == "medium", 1),
                (Task.priority == "low", 2),
                else_=3,
            )
        elif sort == "due_date":
            # Sort by due date, nulls last
            sort_column = Task.due_date
        else:
            sort_column = Task.created_at

        if order == "asc":
            if sort == "due_date":
                # For due date, put nulls last when ascending
                query = query.order_by(Task.due_date.asc().nullslast())
            else:
                query = query.order_by(sort_column.asc())
        else:
            if sort == "due_date":
                # For due date, put nulls last when descending
                query = query.order_by(Task.due_date.desc().nullslast())
            else:
                query = query.order_by(sort_column.desc())

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return TaskListResponse(
            tasks=[TaskResponse.from_task(task) for task in tasks],
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
        if data.priority is not None:
            task.priority = data.priority
        if data.tags is not None:
            task.tags = data.tags
        if data.due_date is not None:
            task.due_date = data.due_date
        if data.recurrence_pattern is not None:
            task.recurrence_pattern = data.recurrence_pattern
        if data.recurrence_end_date is not None:
            task.recurrence_end_date = data.recurrence_end_date
        if data.reminder_at is not None:
            task.reminder_at = data.reminder_at
        # Organization fields
        if data.project_id is not None:
            task.project_id = data.project_id
        if data.pinned is not None:
            task.pinned = data.pinned
        if data.archived is not None:
            task.archived = data.archived
        if data.color is not None:
            task.color = data.color
        if data.board_status is not None:
            task.board_status = data.board_status
        if data.position is not None:
            task.position = data.position

        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete(self, task: Task) -> None:
        """Delete a task (orphan any child tasks by removing parent reference)."""
        from sqlalchemy import select as sql_select, update

        # Remove parent reference from any child tasks (orphan them)
        await self.session.execute(
            update(Task)
            .where(Task.parent_task_id == task.id)
            .values(parent_task_id=None)
        )

        # Now delete the task
        await self.session.delete(task)
        await self.session.commit()

    async def toggle_complete(self, task: Task) -> tuple[Task, Task | None]:
        """Toggle task completion status.

        Returns tuple of (updated_task, next_occurrence or None).
        If task is recurring and being completed, creates next occurrence.
        """
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        next_task = None

        # If completing a recurring task, create next occurrence
        if task.completed and task.recurrence_pattern != "none" and task.due_date:
            next_task = await self._create_next_occurrence(task)

        await self.session.commit()
        await self.session.refresh(task)

        if next_task:
            await self.session.refresh(next_task)

        return task, next_task

    async def _create_next_occurrence(self, task: Task) -> Task | None:
        """Create the next occurrence of a recurring task."""
        next_due_date = self._calculate_next_due_date(
            task.due_date, task.recurrence_pattern
        )

        # Check if we've passed the recurrence end date
        if task.recurrence_end_date and next_due_date > task.recurrence_end_date:
            return None

        # Calculate new reminder if original had one
        new_reminder = None
        if task.reminder_at and task.due_date:
            reminder_delta = task.due_date - task.reminder_at
            new_reminder = next_due_date - reminder_delta

        next_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due_date,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_end_date=task.recurrence_end_date,
            parent_task_id=task.id,
            reminder_at=new_reminder,
        )

        self.session.add(next_task)
        return next_task

    def _calculate_next_due_date(
        self, current_due: datetime, pattern: str
    ) -> datetime:
        """Calculate the next due date based on recurrence pattern."""
        if pattern == "daily":
            return current_due + timedelta(days=1)
        elif pattern == "weekly":
            return current_due + timedelta(weeks=1)
        elif pattern == "monthly":
            return current_due + relativedelta(months=1)
        else:
            return current_due

    async def get_user_tags(self, user_id: uuid.UUID) -> list[str]:
        """Get all unique tags used by a user."""
        # Use PostgreSQL's jsonb_array_elements to extract tags
        query = select(func.jsonb_array_elements_text(Task.tags).label("tag")).where(
            Task.user_id == user_id
        ).distinct()

        result = await self.session.execute(query)
        tags = [row.tag for row in result.fetchall()]
        return sorted(set(tags))

    async def toggle_pin(self, task: Task) -> Task:
        """Toggle task pinned status."""
        task.pinned = not task.pinned
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def toggle_archive(self, task: Task) -> Task:
        """Toggle task archived status."""
        task.archived = not task.archived
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def bulk_archive(
        self,
        user_id: uuid.UUID,
        task_ids: list[uuid.UUID] | None = None,
        archive: bool = True,
    ) -> int:
        """Bulk archive/unarchive tasks.

        If task_ids is None, archives all completed tasks.
        Returns the number of tasks affected.
        """
        if task_ids is None:
            # Archive all completed tasks
            query = select(Task).where(
                Task.user_id == user_id,
                Task.completed == True,  # noqa: E712
                Task.archived == (not archive),  # Only affect tasks not already in target state
            )
        else:
            query = select(Task).where(
                Task.id.in_(task_ids),
                Task.user_id == user_id,
            )

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        count = 0
        for task in tasks:
            task.archived = archive
            task.updated_at = datetime.utcnow()
            count += 1

        await self.session.commit()
        return count

    async def reorder_tasks(
        self,
        user_id: uuid.UUID,
        task_ids: list[uuid.UUID],
        board_status: str | None = None,
    ) -> list[Task]:
        """Reorder tasks based on provided order.

        If board_status is provided, also updates the board_status for all tasks.
        """
        tasks = []
        for idx, task_id in enumerate(task_ids):
            result = await self.session.execute(
                select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id,
                )
            )
            task = result.scalar_one_or_none()
            if task:
                task.position = idx
                if board_status is not None:
                    task.board_status = board_status
                    # Auto-complete if moved to done
                    if board_status == "done" and not task.completed:
                        task.completed = True
                    elif board_status != "done" and task.completed:
                        task.completed = False
                task.updated_at = datetime.utcnow()
                tasks.append(task)

        await self.session.commit()
        return tasks

    async def list_archived(self, user_id: uuid.UUID) -> TaskListResponse:
        """List all archived tasks for a user."""
        query = (
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.archived == True,  # noqa: E712
            )
            .order_by(Task.updated_at.desc())
        )

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return TaskListResponse(
            tasks=[TaskResponse.from_task(task) for task in tasks],
            total=len(tasks),
        )
