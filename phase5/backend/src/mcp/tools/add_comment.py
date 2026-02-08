"""MCP tool for adding comments to tasks."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, SQLModel

from src.mcp.server import tool_registry
from src.models.comment import Comment


async def add_comment_handler(
    user_id: str,
    session: AsyncSession,
    task_id: str,
    content: str,
    parent_id: str | None = None,
) -> dict[str, Any]:
    """Add a comment to a task.

    Args:
        user_id: Commenting user ID
        session: Database session
        task_id: ID of the task to comment on
        content: Comment content
        parent_id: Optional parent comment ID for replies

    Returns:
        Dict with comment details
    """
    from src.models.task import Task
    from src.models.task_share import TaskShare

    # Validate content
    if not content or not content.strip():
        return {"error": "Comment content cannot be empty"}

    content = content.strip()[:2000]  # Limit to 2000 chars

    # Find the task
    task = await session.get(Task, uuid.UUID(task_id))
    if not task:
        return {"error": "Task not found", "task_id": task_id}

    # Check if user has access (owner or shared with)
    has_access = str(task.user_id) == user_id
    if not has_access:
        # Check if task is shared with user
        share_query = select(TaskShare).where(
            TaskShare.task_id == task.id,
            TaskShare.shared_with_id == uuid.UUID(user_id),
        )
        share_result = await session.execute(share_query)
        share = share_result.scalar_one_or_none()
        has_access = share is not None

    if not has_access:
        return {"error": "You don't have access to comment on this task"}

    # Validate parent comment if provided
    if parent_id:
        parent_comment = await session.get(Comment, uuid.UUID(parent_id))
        if not parent_comment or str(parent_comment.task_id) != task_id:
            return {"error": "Parent comment not found", "parent_id": parent_id}

    # Create comment
    comment = Comment(
        task_id=task.id,
        user_id=uuid.UUID(user_id),
        parent_id=uuid.UUID(parent_id) if parent_id else None,
        content=content,
    )
    session.add(comment)
    await session.flush()

    return {
        "status": "created",
        "comment_id": str(comment.id),
        "task_id": task_id,
        "task_title": task.title,
        "content": content[:100] + ("..." if len(content) > 100 else ""),
        "is_reply": parent_id is not None,
        "message": f"Comment added to task '{task.title}'",
    }


# Register the tool
tool_registry.register(
    name="add_comment",
    description="Add a comment to a task. Use this for discussions, notes, or updates on a task.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to comment on",
            },
            "content": {
                "type": "string",
                "description": "The comment content (max 2000 characters)",
            },
            "parent_id": {
                "type": "string",
                "description": "Optional parent comment ID if this is a reply to another comment",
            },
        },
        "required": ["task_id", "content"],
    },
    handler=add_comment_handler,
)
