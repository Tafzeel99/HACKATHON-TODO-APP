"""MCP tool for assigning tasks to users."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry


async def assign_task_handler(
    user_id: str,
    session: AsyncSession,
    task_id: str,
    assignee_email: str | None = None,
) -> dict[str, Any]:
    """Assign a task to another user or unassign.

    Args:
        user_id: Owner user ID
        session: Database session
        task_id: ID of the task to assign
        assignee_email: Email of the user to assign to, or None to unassign

    Returns:
        Dict with assignment details
    """
    from src.models.task import Task
    from src.models.user import User

    # Find the task
    task = await session.get(Task, uuid.UUID(task_id))
    if not task:
        return {"error": "Task not found", "task_id": task_id}

    # Verify ownership
    if str(task.user_id) != user_id:
        return {"error": "You can only assign your own tasks", "task_id": task_id}

    # Handle unassignment
    if not assignee_email:
        # Check if task has assigned_to field
        if hasattr(task, "assigned_to"):
            task.assigned_to = None
            task.updated_at = datetime.utcnow()
            await session.flush()
            return {
                "status": "unassigned",
                "task_id": task_id,
                "task_title": task.title,
                "message": f"Task '{task.title}' is now unassigned",
            }
        return {"error": "Task assignment feature not available"}

    # Find the assignee user
    query = select(User).where(User.email == assignee_email)
    result = await session.execute(query)
    assignee = result.scalar_one_or_none()

    if not assignee:
        return {"error": f"User with email '{assignee_email}' not found"}

    # Check if task has assigned_to field
    if not hasattr(task, "assigned_to"):
        return {"error": "Task assignment feature not available for this task model"}

    # Assign the task
    task.assigned_to = assignee.id
    task.updated_at = datetime.utcnow()
    await session.flush()

    return {
        "status": "assigned",
        "task_id": task_id,
        "task_title": task.title,
        "assigned_to": assignee_email,
        "assignee_name": assignee.name,
        "message": f"Task '{task.title}' assigned to {assignee.name or assignee_email}",
    }


# Register the tool
tool_registry.register(
    name="assign_task",
    description="Assign a task to another user by their email. Use without assignee_email to unassign.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to assign",
            },
            "assignee_email": {
                "type": "string",
                "description": "Email of the user to assign the task to. Omit or set to null to unassign.",
            },
        },
        "required": ["task_id"],
    },
    handler=assign_task_handler,
)
