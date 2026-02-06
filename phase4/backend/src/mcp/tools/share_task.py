"""MCP tool for sharing tasks with other users."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Column, Field, SQLModel

from src.mcp.server import tool_registry
from src.models.task_share import TaskShare
from src.models.user import User


async def share_task_handler(
    user_id: str,
    session: AsyncSession,
    task_id: str,
    user_email: str,
    permission: str = "view",
) -> dict[str, Any]:
    """Share a task with another user.

    Args:
        user_id: Owner user ID
        session: Database session
        task_id: ID of the task to share
        user_email: Email of the user to share with
        permission: Permission level (view or edit)

    Returns:
        Dict with share details
    """
    from src.models.task import Task

    # Validate permission
    if permission not in ["view", "edit"]:
        permission = "view"

    # Find the task
    task = await session.get(Task, uuid.UUID(task_id))
    if not task:
        return {"error": "Task not found", "task_id": task_id}

    # Verify ownership
    if str(task.user_id) != user_id:
        return {"error": "You can only share your own tasks", "task_id": task_id}

    # Find the user to share with
    query = select(User).where(User.email == user_email)
    result = await session.execute(query)
    target_user = result.scalar_one_or_none()

    if not target_user:
        return {"error": f"User with email '{user_email}' not found"}

    if str(target_user.id) == user_id:
        return {"error": "Cannot share a task with yourself"}

    # Check if already shared
    existing_query = select(TaskShare).where(
        TaskShare.task_id == task.id,
        TaskShare.shared_with_id == target_user.id,
    )
    existing_result = await session.execute(existing_query)
    existing_share = existing_result.scalar_one_or_none()

    if existing_share:
        # Update permission if different
        if existing_share.permission != permission:
            existing_share.permission = permission
            await session.flush()
            return {
                "status": "updated",
                "share_id": str(existing_share.id),
                "task_id": task_id,
                "shared_with": user_email,
                "permission": permission,
                "message": f"Updated share permission to '{permission}'",
            }
        return {
            "status": "already_shared",
            "share_id": str(existing_share.id),
            "task_id": task_id,
            "shared_with": user_email,
            "permission": existing_share.permission,
            "message": f"Task is already shared with {user_email}",
        }

    # Create new share
    share = TaskShare(
        task_id=task.id,
        owner_id=uuid.UUID(user_id),
        shared_with_id=target_user.id,
        permission=permission,
    )
    session.add(share)
    await session.flush()

    return {
        "status": "shared",
        "share_id": str(share.id),
        "task_id": task_id,
        "task_title": task.title,
        "shared_with": user_email,
        "permission": permission,
        "message": f"Task '{task.title}' shared with {user_email} ({permission} access)",
    }


# Register the tool
tool_registry.register(
    name="share_task",
    description="Share a task with another user by their email address. Use 'view' permission for read-only access, 'edit' for full access.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to share",
            },
            "user_email": {
                "type": "string",
                "description": "Email address of the user to share with",
            },
            "permission": {
                "type": "string",
                "enum": ["view", "edit"],
                "description": "Permission level: 'view' for read-only, 'edit' for full access. Default is 'view'.",
            },
        },
        "required": ["task_id", "user_email"],
    },
    handler=share_task_handler,
)
