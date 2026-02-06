"""MCP tool for task analytics and productivity statistics."""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry
from src.models.task import Task


async def get_analytics_handler(
    user_id: str,
    session: AsyncSession,
) -> dict[str, Any]:
    """Get productivity analytics for the user's tasks.

    Args:
        user_id: Owner user ID
        session: Database session

    Returns:
        Dict with comprehensive task statistics
    """
    user_uuid = uuid.UUID(user_id)
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    # Calculate week boundaries (Monday to Sunday)
    days_since_monday = now.weekday()
    week_start = (now - timedelta(days=days_since_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_end = week_start + timedelta(days=7)

    # Get all user tasks
    all_tasks_result = await session.execute(
        select(Task).where(Task.user_id == user_uuid)
    )
    all_tasks = all_tasks_result.scalars().all()

    # Calculate statistics
    total_tasks = len(all_tasks)
    completed_count = sum(1 for t in all_tasks if t.completed)
    pending_count = total_tasks - completed_count

    # Overdue tasks (past due date, not completed)
    overdue_count = sum(
        1 for t in all_tasks
        if t.due_date and t.due_date < now and not t.completed
    )

    # Tasks due today
    due_today_count = sum(
        1 for t in all_tasks
        if t.due_date and today_start <= t.due_date < today_end and not t.completed
    )

    # Tasks due this week
    due_this_week_count = sum(
        1 for t in all_tasks
        if t.due_date and week_start <= t.due_date < week_end and not t.completed
    )

    # Completed this week
    completed_this_week = sum(
        1 for t in all_tasks
        if t.completed and t.updated_at and week_start <= t.updated_at < week_end
    )

    # Completion rate
    completion_rate = (
        round((completed_count / total_tasks) * 100, 1)
        if total_tasks > 0 else 0.0
    )

    # Tasks by priority
    tasks_by_priority = {
        "high": sum(1 for t in all_tasks if t.priority == "high" and not t.completed),
        "medium": sum(1 for t in all_tasks if t.priority == "medium" and not t.completed),
        "low": sum(1 for t in all_tasks if t.priority == "low" and not t.completed),
    }

    # High priority pending
    high_priority_pending = tasks_by_priority["high"]

    # Get overdue task titles (for summary)
    overdue_tasks = [
        {"id": str(t.id), "title": t.title, "due_date": t.due_date.isoformat()}
        for t in all_tasks
        if t.due_date and t.due_date < now and not t.completed
    ][:5]  # Limit to 5

    # Get tasks due today titles
    due_today_tasks = [
        {"id": str(t.id), "title": t.title, "priority": t.priority}
        for t in all_tasks
        if t.due_date and today_start <= t.due_date < today_end and not t.completed
    ][:5]  # Limit to 5

    return {
        "summary": {
            "total_tasks": total_tasks,
            "completed_count": completed_count,
            "pending_count": pending_count,
            "completion_rate": completion_rate,
        },
        "urgency": {
            "overdue_count": overdue_count,
            "due_today_count": due_today_count,
            "due_this_week_count": due_this_week_count,
            "high_priority_pending": high_priority_pending,
        },
        "productivity": {
            "completed_this_week": completed_this_week,
        },
        "by_priority": tasks_by_priority,
        "details": {
            "overdue_tasks": overdue_tasks,
            "due_today_tasks": due_today_tasks,
        },
        "message": (
            f"You have {total_tasks} total tasks. "
            f"{completed_count} completed ({completion_rate}% completion rate). "
            f"{pending_count} pending. "
            f"{overdue_count} overdue. "
            f"{due_today_count} due today. "
            f"{high_priority_pending} high priority tasks pending."
        ),
    }


# Register the tool
tool_registry.register(
    name="get_analytics",
    description="Get productivity statistics and analytics about user's tasks. Use when user asks about progress, productivity, stats, summary, 'how am I doing?', or 'summarize my day/week'.",
    parameters={
        "type": "object",
        "properties": {},
    },
    handler=get_analytics_handler,
)
