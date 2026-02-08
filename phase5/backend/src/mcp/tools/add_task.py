"""MCP tool for adding tasks."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry
from src.models.task import Task


async def add_task_handler(
    user_id: str,
    title: str,
    session: AsyncSession,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    recurrence_pattern: str | None = None,
    recurrence_end_date: str | None = None,
    reminder_at: str | None = None,
) -> dict[str, Any]:
    """Create a new task for the user with optional advanced fields.

    Args:
        user_id: Owner user ID
        title: Task title
        session: Database session
        description: Optional task description
        priority: Task priority (low, medium, high) - defaults to medium
        tags: List of tags (max 10, each max 30 chars)
        due_date: Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        recurrence_pattern: Recurrence pattern (none, daily, weekly, monthly)
        recurrence_end_date: End date for recurrence in ISO format
        reminder_at: Reminder datetime in ISO format

    Returns:
        Dict with task details
    """
    # Validate priority
    valid_priorities = ["low", "medium", "high"]
    task_priority = priority.lower() if priority else "medium"
    if task_priority not in valid_priorities:
        task_priority = "medium"

    # Validate and limit tags
    task_tags = []
    if tags:
        # Limit to 10 tags, each max 30 chars
        task_tags = [tag[:30].strip() for tag in tags[:10] if tag and tag.strip()]

    # Parse due_date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            pass  # Invalid date format, ignore

    # Validate recurrence pattern
    valid_recurrence = ["none", "daily", "weekly", "monthly"]
    task_recurrence = recurrence_pattern.lower() if recurrence_pattern else "none"
    if task_recurrence not in valid_recurrence:
        task_recurrence = "none"

    # Parse recurrence_end_date
    parsed_recurrence_end = None
    if recurrence_end_date:
        try:
            parsed_recurrence_end = datetime.fromisoformat(recurrence_end_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Parse reminder_at
    parsed_reminder = None
    if reminder_at:
        try:
            parsed_reminder = datetime.fromisoformat(reminder_at.replace("Z", "+00:00"))
        except ValueError:
            pass

    task = Task(
        user_id=uuid.UUID(user_id),
        title=title,
        description=description,
        priority=task_priority,
        tags=task_tags,
        due_date=parsed_due_date,
        recurrence_pattern=task_recurrence,
        recurrence_end_date=parsed_recurrence_end,
        reminder_at=parsed_reminder,
    )
    session.add(task)
    await session.flush()

    return {
        "task_id": str(task.id),
        "status": "created",
        "title": task.title,
        "priority": task.priority,
        "tags": task.tags,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurrence_pattern": task.recurrence_pattern,
        "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
    }


# Register the tool
tool_registry.register(
    name="add_task",
    description="Create a new task for the user. Use this when the user wants to add, create, or remember something. Supports priority, tags, due dates, recurrence, and reminders.",
    parameters={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title of the task (1-200 characters)",
            },
            "description": {
                "type": "string",
                "description": "Optional description of the task",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Task priority level. Use 'high' for urgent/important tasks, 'low' for whenever/sometime tasks. Default is 'medium'.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tags for categorization (max 10 tags, each max 30 chars). Example: ['work', 'urgent']",
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS). Parse natural language dates like 'tomorrow', 'next Monday' to ISO format before calling.",
            },
            "recurrence_pattern": {
                "type": "string",
                "enum": ["none", "daily", "weekly", "monthly"],
                "description": "How often the task recurs. When a recurring task is completed, a new task is auto-created with the next due date.",
            },
            "recurrence_end_date": {
                "type": "string",
                "description": "End date for recurrence in ISO format. After this date, no new recurring tasks will be created.",
            },
            "reminder_at": {
                "type": "string",
                "description": "Reminder datetime in ISO format. When to remind the user about this task.",
            },
        },
        "required": ["title"],
    },
    handler=add_task_handler,
)
