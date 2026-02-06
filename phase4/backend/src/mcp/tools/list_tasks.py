"""MCP tool for listing tasks."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry
from src.models.task import Task


async def list_tasks_handler(
    user_id: str,
    session: AsyncSession,
    status: str = "all",
    priority: str | None = None,
    tags: list[str] | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
    overdue_only: bool = False,
    search: str | None = None,
) -> dict[str, Any]:
    """List tasks for the user with advanced filtering options.

    Args:
        user_id: Owner user ID
        session: Database session
        status: Filter by status ('all', 'pending', 'completed')
        priority: Filter by priority ('low', 'medium', 'high')
        tags: Filter by tags (any match)
        due_before: Show tasks due before this date (ISO format)
        due_after: Show tasks due after this date (ISO format)
        overdue_only: Show only overdue tasks (past due date, not completed)
        search: Search keyword in title and description

    Returns:
        Dict with list of tasks and filters applied
    """
    query = select(Task).where(Task.user_id == uuid.UUID(user_id))

    # Status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Priority filter
    if priority:
        query = query.where(Task.priority == priority.lower())

    # Tags filter (any match)
    if tags:
        # JSON array contains any of the specified tags
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(func.json_contains(Task.tags, f'"{tag}"'))
        if tag_conditions:
            query = query.where(or_(*tag_conditions))

    # Due date range filters
    if due_before:
        try:
            due_before_dt = datetime.fromisoformat(due_before.replace("Z", "+00:00"))
            query = query.where(Task.due_date <= due_before_dt)
        except ValueError:
            pass

    if due_after:
        try:
            due_after_dt = datetime.fromisoformat(due_after.replace("Z", "+00:00"))
            query = query.where(Task.due_date >= due_after_dt)
        except ValueError:
            pass

    # Overdue filter
    if overdue_only:
        now = datetime.utcnow()
        query = query.where(
            Task.due_date < now,
            Task.completed == False,
        )

    # Search filter (case-insensitive search in title and description)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern),
            )
        )

    # Order by priority (high first), then due date (soonest first), then created_at
    query = query.order_by(
        Task.completed.asc(),  # Pending first
        Task.due_date.asc().nullslast(),  # Soonest due date first
        Task.created_at.desc(),
    )

    result = await session.execute(query)
    tasks = result.scalars().all()

    # Calculate is_overdue for each task
    now = datetime.utcnow()
    task_list = []
    for task in tasks:
        is_overdue = (
            task.due_date is not None
            and task.due_date < now
            and not task.completed
        )
        task_list.append({
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "tags": task.tags or [],
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_overdue": is_overdue,
            "recurrence_pattern": task.recurrence_pattern,
            "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        })

    # Build filters applied summary
    filters_applied = {"status": status}
    if priority:
        filters_applied["priority"] = priority
    if tags:
        filters_applied["tags"] = tags
    if due_before:
        filters_applied["due_before"] = due_before
    if due_after:
        filters_applied["due_after"] = due_after
    if overdue_only:
        filters_applied["overdue_only"] = True
    if search:
        filters_applied["search"] = search

    return {
        "tasks": task_list,
        "count": len(task_list),
        "filters": filters_applied,
    }


# Register the tool
tool_registry.register(
    name="list_tasks",
    description="List tasks with advanced filtering. Use for viewing tasks, searching, or filtering by priority/tags/dates. Supports multiple filter combinations.",
    parameters={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter by completion status: 'all' (default), 'pending' (incomplete), or 'completed'",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Filter by priority level. Use 'high' when user asks for urgent/important tasks.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by tags (returns tasks with ANY of these tags). Example: ['work', 'urgent']",
            },
            "due_before": {
                "type": "string",
                "description": "Show tasks due before this date (ISO format YYYY-MM-DD). For 'due this week', calculate the end of week date.",
            },
            "due_after": {
                "type": "string",
                "description": "Show tasks due after this date (ISO format YYYY-MM-DD). For 'due this week', use today's date.",
            },
            "overdue_only": {
                "type": "boolean",
                "description": "Set to true to show only overdue tasks (past due date and not completed). Use for 'show overdue' requests.",
            },
            "search": {
                "type": "string",
                "description": "Search keyword to find in task title or description. Case-insensitive. Use for 'find tasks about X' requests.",
            },
        },
    },
    handler=list_tasks_handler,
)
