"""MCP tool for deleting tasks."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry
from src.models.task import Task


async def delete_task_handler(
    user_id: str,
    task_id: str,
    session: AsyncSession,
) -> dict[str, Any]:
    """Delete a task.

    Args:
        user_id: Owner user ID
        task_id: Task ID to delete
        session: Database session

    Returns:
        Dict with task_id, status, and title
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

    title = task.title
    await session.delete(task)
    await session.flush()

    return {
        "task_id": str(task_uuid),
        "status": "deleted",
        "title": title,
        "message": f"Task '{title}' has been deleted.",
    }


# Register the tool
tool_registry.register(
    name="delete_task",
    description="Delete a task. Use this when the user wants to remove, delete, or cancel a task.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to delete",
            },
        },
        "required": ["task_id"],
    },
    handler=delete_task_handler,
)
