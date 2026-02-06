"""MCP tool for completing tasks."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.relativedelta import relativedelta

from src.mcp.server import tool_registry
from src.models.task import Task


def calculate_next_due_date(current_due: datetime, pattern: str) -> datetime:
    """Calculate the next due date based on recurrence pattern.

    Args:
        current_due: Current due date
        pattern: Recurrence pattern (daily, weekly, monthly)

    Returns:
        Next due date
    """
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_due + relativedelta(months=1)
    return current_due


async def complete_task_handler(
    user_id: str,
    task_id: str,
    session: AsyncSession,
) -> dict[str, Any]:
    """Mark a task as complete. For recurring tasks, automatically creates the next occurrence.

    Args:
        user_id: Owner user ID
        task_id: Task ID to complete
        session: Database session

    Returns:
        Dict with task_id, status, title, and optionally next_task info
    """
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        return {
            "error": "invalid_task_id",
            "message": f"Invalid task ID format: {task_id}",
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

    if task.completed:
        return {
            "task_id": str(task.id),
            "status": "already_completed",
            "title": task.title,
            "message": f"Task '{task.title}' was already marked as complete.",
        }

    # Mark task as complete
    task.completed = True
    task.updated_at = datetime.utcnow()

    response = {
        "task_id": str(task.id),
        "status": "completed",
        "title": task.title,
        "message": f"Task '{task.title}' has been marked as complete!",
    }

    # Handle recurring tasks
    if task.recurrence_pattern and task.recurrence_pattern != "none":
        # Check if we should create next occurrence
        should_create_next = True

        # Calculate next due date
        current_due = task.due_date or datetime.utcnow()
        next_due = calculate_next_due_date(current_due, task.recurrence_pattern)

        # Check if past recurrence end date
        if task.recurrence_end_date and next_due > task.recurrence_end_date:
            should_create_next = False
            response["message"] += " Recurrence has ended (past end date)."

        if should_create_next:
            # Calculate next reminder if original had one
            next_reminder = None
            if task.reminder_at and task.due_date:
                # Maintain same offset between reminder and due date
                reminder_offset = task.due_date - task.reminder_at
                next_reminder = next_due - reminder_offset

            # Create next occurrence
            next_task = Task(
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                tags=task.tags,
                due_date=next_due,
                recurrence_pattern=task.recurrence_pattern,
                recurrence_end_date=task.recurrence_end_date,
                parent_task_id=task.id,  # Link to parent
                reminder_at=next_reminder,
            )
            session.add(next_task)
            await session.flush()

            response["next_task"] = {
                "task_id": str(next_task.id),
                "title": next_task.title,
                "due_date": next_task.due_date.isoformat() if next_task.due_date else None,
            }
            response["message"] += f" Next occurrence created for {next_due.strftime('%Y-%m-%d')}."

    await session.flush()
    return response


# Register the tool
tool_registry.register(
    name="complete_task",
    description="Mark a task as complete. Use this when the user says they've finished, completed, or done with a task.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to mark as complete",
            },
        },
        "required": ["task_id"],
    },
    handler=complete_task_handler,
)
