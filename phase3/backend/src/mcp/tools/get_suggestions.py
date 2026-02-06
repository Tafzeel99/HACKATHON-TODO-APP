"""MCP tool for getting smart task suggestions.

Enhanced with time estimation, conflict detection, workload analysis, and habit tracking.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.server import tool_registry
from src.services.suggestions import get_suggestion_service


async def get_suggestions_handler(
    user_id: str,
    session: AsyncSession,
    suggestion_type: str = "focus",
    task_title: str | None = None,
    task_description: str | None = None,
    due_date: str | None = None,
) -> dict[str, Any]:
    """Get smart suggestions for tasks.

    Args:
        user_id: Owner user ID
        session: Database session
        suggestion_type: Type of suggestion (focus, priority, similar, time_estimate, conflict, workload, habit, all)
        task_title: Task title for priority, similar, or time_estimate suggestions
        task_description: Task description for enhanced suggestions
        due_date: Due date (ISO format) for conflict detection

    Returns:
        Dict with suggestions
    """
    from src.mcp.tools.add_task import Task

    suggestion_service = get_suggestion_service()

    if suggestion_type == "focus":
        # Get user's pending tasks for focus suggestions
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.completed == False,
        ).order_by(Task.due_date.asc().nulls_last(), Task.priority.desc())

        result = await session.execute(query)
        tasks = result.scalars().all()

        task_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "completed": t.completed,
            }
            for t in tasks
        ]

        suggestion = suggestion_service.suggest_focus_tasks(task_dicts)

        return {
            "type": "focus",
            "message": suggestion.message,
            "confidence": suggestion.confidence,
            "focus_tasks": [
                {"id": t.get("id"), "title": t.get("title")}
                for t in (suggestion.data or {}).get("focus_tasks", [])
            ],
            "overdue_count": suggestion.data.get("overdue_count", 0) if suggestion.data else 0,
            "due_today_count": suggestion.data.get("due_today_count", 0) if suggestion.data else 0,
        }

    elif suggestion_type == "priority" and task_title:
        suggestion = suggestion_service.suggest_priority(task_title)
        return {
            "type": "priority",
            "message": suggestion.message,
            "suggested_priority": suggestion.data.get("suggested_priority") if suggestion.data else "medium",
            "confidence": suggestion.confidence,
        }

    elif suggestion_type == "similar" and task_title:
        # Get user's existing tasks for comparison
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.completed == False,
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        task_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "completed": t.completed,
            }
            for t in tasks
        ]

        suggestion = suggestion_service.suggest_similar_tasks(task_title, task_dicts)
        return {
            "type": "similar",
            "message": suggestion.message,
            "similar_tasks": [
                {"id": t.get("id"), "title": t.get("title")}
                for t in (suggestion.data or {}).get("similar_tasks", [])
            ],
            "confidence": suggestion.confidence,
        }

    elif suggestion_type == "time_estimate" and task_title:
        # Get completed tasks for time estimation
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.completed == True,
        ).order_by(Task.updated_at.desc()).limit(100)

        result = await session.execute(query)
        completed_tasks = result.scalars().all()

        task_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "completed": t.completed,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in completed_tasks
        ]

        suggestion = suggestion_service.estimate_time(task_title, task_dicts)
        return {
            "type": "time_estimate",
            "message": suggestion.message,
            "estimated_hours": suggestion.data.get("estimated_hours") if suggestion.data else None,
            "based_on_count": suggestion.data.get("based_on_count", 0) if suggestion.data else 0,
            "category": suggestion.data.get("category") if suggestion.data else "unknown",
            "confidence": suggestion.confidence,
        }

    elif suggestion_type == "conflict" and due_date:
        # Parse due date
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            return {
                "type": "error",
                "message": f"Invalid due_date format: {due_date}. Use ISO format.",
            }

        # Get existing tasks
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.completed == False,
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        task_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "completed": t.completed,
            }
            for t in tasks
        ]

        suggestion = suggestion_service.detect_scheduling_conflicts(parsed_due_date, task_dicts)
        return {
            "type": "conflict",
            "message": suggestion.message,
            "has_conflict": suggestion.data.get("conflict_date") is not None if suggestion.data else False,
            "existing_task_count": suggestion.data.get("existing_task_count", 0) if suggestion.data else 0,
            "estimated_hours": suggestion.data.get("estimated_hours", 0) if suggestion.data else 0,
            "alternative_dates": suggestion.data.get("alternative_dates", []) if suggestion.data else [],
            "confidence": suggestion.confidence,
        }

    elif suggestion_type == "workload":
        # Get all pending tasks for workload analysis
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.completed == False,
        )
        result = await session.execute(query)
        tasks = result.scalars().all()

        task_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "completed": t.completed,
            }
            for t in tasks
        ]

        suggestion = suggestion_service.analyze_workload(task_dicts)
        return {
            "type": "workload",
            "message": suggestion.message,
            "overloaded_days": suggestion.data.get("overloaded_days", []) if suggestion.data else [],
            "total_upcoming": suggestion.data.get("total_upcoming", 0) if suggestion.data else 0,
            "avg_per_day": suggestion.data.get("avg_per_day", 0) if suggestion.data else 0,
            "confidence": suggestion.confidence,
        }

    elif suggestion_type == "habit":
        # Get completed tasks for habit tracking
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
            Task.completed == True,
        ).order_by(Task.updated_at.desc()).limit(200)

        result = await session.execute(query)
        completed_tasks = result.scalars().all()

        task_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "completed": t.completed,
                "completed_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in completed_tasks
        ]

        suggestion = suggestion_service.track_habits(task_dicts)
        return {
            "type": "habit",
            "message": suggestion.message,
            "habits": suggestion.data.get("habits", []) if suggestion.data else [],
            "strongest_habit": suggestion.data.get("strongest_habit") if suggestion.data else None,
            "total_analyzed": suggestion.data.get("total_analyzed", 0) if suggestion.data else 0,
            "confidence": suggestion.confidence,
        }

    elif suggestion_type == "all" and task_title:
        # Get all tasks for comprehensive suggestions
        query = select(Task).where(
            Task.user_id == uuid.UUID(user_id),
        )
        result = await session.execute(query)
        all_tasks = result.scalars().all()

        existing_tasks = [
            {
                "id": str(t.id),
                "title": t.title,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "completed": t.completed,
            }
            for t in all_tasks if not t.completed
        ]

        completed_tasks = [
            {
                "id": str(t.id),
                "title": t.title,
                "completed": t.completed,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in all_tasks if t.completed
        ]

        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError:
                pass

        suggestions = suggestion_service.get_all_suggestions(
            task_title=task_title,
            task_description=task_description,
            due_date=parsed_due_date,
            existing_tasks=existing_tasks,
            completed_tasks=completed_tasks,
        )

        return {
            "type": "all",
            "suggestions": [
                {
                    "type": s.suggestion_type,
                    "message": s.message,
                    "confidence": s.confidence,
                    "data": s.data,
                }
                for s in suggestions
            ],
            "count": len(suggestions),
        }

    else:
        return {
            "type": "error",
            "message": f"Invalid suggestion type '{suggestion_type}' or missing required parameters. "
                       f"Types: focus, priority, similar, time_estimate, conflict, workload, habit, all. "
                       f"Some types require task_title or due_date.",
        }


# Register the tool
tool_registry.register(
    name="get_suggestions",
    description="""Get smart task suggestions with AI-powered insights.

Types available:
- 'focus': Suggest what to work on today (overdue, due today, high priority)
- 'priority': Suggest priority for a new task based on keywords
- 'similar': Find similar existing tasks to avoid duplicates
- 'time_estimate': Estimate how long a task will take based on history
- 'conflict': Detect scheduling conflicts for a given due date
- 'workload': Analyze workload distribution over the next 7 days
- 'habit': Track completion patterns and habits
- 'all': Get all suggestions at once for a task
""",
    parameters={
        "type": "object",
        "properties": {
            "suggestion_type": {
                "type": "string",
                "enum": ["focus", "priority", "similar", "time_estimate", "conflict", "workload", "habit", "all"],
                "description": "Type of suggestion to request",
            },
            "task_title": {
                "type": "string",
                "description": "Task title (required for priority, similar, time_estimate, all)",
            },
            "task_description": {
                "type": "string",
                "description": "Task description (optional, enhances suggestions)",
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO format (required for conflict detection)",
            },
        },
        "required": ["suggestion_type"],
    },
    handler=get_suggestions_handler,
)
