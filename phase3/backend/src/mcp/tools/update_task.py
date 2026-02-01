"""MCP tool for updating tasks."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry
from src.mcp.tools.add_task import Task


async def update_task_handler(
    user_id: str,
    task_id: str,
    session: AsyncSession,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    recurrence_pattern: str | None = None,
    recurrence_end_date: str | None = None,
    reminder_at: str | None = None,
) -> dict[str, Any]:
    """Update any task fields including priority, tags, due dates, and recurrence.

    Args:
        user_id: Owner user ID
        task_id: Task ID to update
        session: Database session
        title: New title (optional)
        description: New description (optional)
        priority: New priority (low, medium, high)
        tags: New tags list (replaces existing)
        due_date: New due date in ISO format
        recurrence_pattern: New recurrence pattern (none, daily, weekly, monthly)
        recurrence_end_date: New recurrence end date in ISO format
        reminder_at: New reminder datetime in ISO format

    Returns:
        Dict with task_id, status, and updated fields
    """
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return {
            "error": "invalid_task_id",
            "message": f"Invalid task ID format: {task_id}",
        }

    # Check if any updates provided
    has_updates = any([
        title, description is not None, priority, tags is not None,
        due_date is not None, recurrence_pattern, recurrence_end_date is not None,
        reminder_at is not None,
    ])

    if not has_updates:
        return {
            "error": "no_updates",
            "message": "No updates provided. Please specify what to change.",
        }

    result = await session.execute(
        select(Task).where(
            Task.id == task_uuid,
            Task.user_id == uuid.UUID(user_id),
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        return {
            "error": "task_not_found",
            "message": f"Task with ID {task_id} not found. Would you like to see your task list?",
        }

    updates = []

    # Update title
    if title:
        old_title = task.title
        task.title = title
        updates.append(f"title changed from '{old_title}' to '{title}'")

    # Update description
    if description is not None:
        task.description = description
        updates.append("description updated")

    # Update priority
    if priority:
        valid_priorities = ["low", "medium", "high"]
        new_priority = priority.lower()
        if new_priority in valid_priorities:
            old_priority = task.priority
            task.priority = new_priority
            updates.append(f"priority changed from '{old_priority}' to '{new_priority}'")

    # Update tags
    if tags is not None:
        task_tags = [tag[:30].strip() for tag in tags[:10] if tag and tag.strip()]
        task.tags = task_tags
        updates.append(f"tags set to {task_tags}")

    # Update due_date
    if due_date is not None:
        if due_date == "" or due_date.lower() == "none":
            task.due_date = None
            updates.append("due date removed")
        else:
            try:
                parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                task.due_date = parsed_due
                updates.append(f"due date set to {parsed_due.strftime('%Y-%m-%d')}")
            except ValueError:
                pass

    # Update recurrence_pattern
    if recurrence_pattern:
        valid_recurrence = ["none", "daily", "weekly", "monthly"]
        new_recurrence = recurrence_pattern.lower()
        if new_recurrence in valid_recurrence:
            task.recurrence_pattern = new_recurrence
            updates.append(f"recurrence set to '{new_recurrence}'")

    # Update recurrence_end_date
    if recurrence_end_date is not None:
        if recurrence_end_date == "" or recurrence_end_date.lower() == "none":
            task.recurrence_end_date = None
            updates.append("recurrence end date removed")
        else:
            try:
                parsed_end = datetime.fromisoformat(recurrence_end_date.replace("Z", "+00:00"))
                task.recurrence_end_date = parsed_end
                updates.append(f"recurrence ends on {parsed_end.strftime('%Y-%m-%d')}")
            except ValueError:
                pass

    # Update reminder_at
    if reminder_at is not None:
        if reminder_at == "" or reminder_at.lower() == "none":
            task.reminder_at = None
            updates.append("reminder removed")
        else:
            try:
                parsed_reminder = datetime.fromisoformat(reminder_at.replace("Z", "+00:00"))
                task.reminder_at = parsed_reminder
                updates.append(f"reminder set for {parsed_reminder.strftime('%Y-%m-%d %H:%M')}")
            except ValueError:
                pass

    task.updated_at = datetime.utcnow()
    await session.flush()

    return {
        "task_id": str(task.id),
        "status": "updated",
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "tags": task.tags,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurrence_pattern": task.recurrence_pattern,
        "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
        "updates": updates,
        "message": f"Task updated: {', '.join(updates)}",
    }


# Register the tool
tool_registry.register(
    name="update_task",
    description="Update any task field including title, description, priority, tags, due date, recurrence, or reminder. Use when user wants to change/modify a task.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to update",
            },
            "title": {
                "type": "string",
                "description": "New title for the task",
            },
            "description": {
                "type": "string",
                "description": "New description for the task",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "New priority level",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "New tags list (replaces existing tags)",
            },
            "due_date": {
                "type": "string",
                "description": "New due date in ISO format. Use empty string or 'none' to remove due date.",
            },
            "recurrence_pattern": {
                "type": "string",
                "enum": ["none", "daily", "weekly", "monthly"],
                "description": "New recurrence pattern. Use 'none' to stop recurrence.",
            },
            "recurrence_end_date": {
                "type": "string",
                "description": "End date for recurrence in ISO format. Use empty string to remove.",
            },
            "reminder_at": {
                "type": "string",
                "description": "New reminder datetime in ISO format. Use empty string or 'none' to remove reminder.",
            },
        },
        "required": ["task_id"],
    },
    handler=update_task_handler,
)
