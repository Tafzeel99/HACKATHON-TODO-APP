"""Handler for task.completed events - creates next occurrence for recurring tasks."""

import logging
from datetime import datetime, timedelta

import httpx
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

# Mapping of recurrence patterns to date deltas
RECURRENCE_DELTAS = {
    "daily": lambda dt: dt + timedelta(days=1),
    "weekly": lambda dt: dt + timedelta(days=7),
    "monthly": lambda dt: dt + relativedelta(months=1),
    "yearly": lambda dt: dt + relativedelta(years=1),
}


def _calculate_next_due_date(current_due_date: str | None, pattern: str) -> str:
    """Calculate the next due date based on the recurrence pattern.

    Args:
        current_due_date: The current due date as an ISO 8601 string, or None.
        pattern: The recurrence pattern (daily, weekly, monthly, yearly).

    Returns:
        The next due date as an ISO 8601 string.
    """
    if current_due_date:
        base_date = datetime.fromisoformat(
            current_due_date.replace("Z", "+00:00")
        )
    else:
        base_date = datetime.utcnow()

    delta_fn = RECURRENCE_DELTAS.get(pattern)
    if delta_fn is None:
        raise ValueError(f"Unsupported recurrence pattern: {pattern}")

    next_date = delta_fn(base_date)
    return next_date.isoformat()


def _is_past_recurrence_end(
    next_due_date: str, recurrence_end_date: str | None
) -> bool:
    """Check whether the next due date exceeds the recurrence end date.

    Args:
        next_due_date: The calculated next due date as an ISO 8601 string.
        recurrence_end_date: The recurrence end date as an ISO 8601 string, or None.

    Returns:
        True if the next due date is past the recurrence end date.
    """
    if not recurrence_end_date:
        return False

    end_date = datetime.fromisoformat(
        recurrence_end_date.replace("Z", "+00:00")
    )
    next_date = datetime.fromisoformat(
        next_due_date.replace("Z", "+00:00")
    )
    return next_date > end_date


async def handle_task_completed(
    data: dict,
    dapr_http_port: int,
    backend_app_id: str,
) -> dict:
    """Handle a task.completed event and create the next recurring occurrence.

    This function is invoked when a CloudEvent with task completion data arrives
    from the Dapr Pub/Sub subscription on the ``task-events`` topic.

    Args:
        data: The event payload containing event_type, task_id, task_data,
              user_id, and timestamp.
        dapr_http_port: The local Dapr HTTP sidecar port (default 3500).
        backend_app_id: The Dapr app-id of the backend service.

    Returns:
        A dict with a ``status`` key indicating the outcome:
        ``SUCCESS``, ``SKIP``, or ``ERROR``.
    """
    event_type = data.get("event_type")
    if event_type != "completed":
        logger.debug(
            "Skipping non-completion event: event_type=%s", event_type
        )
        return {"status": "SKIP"}

    task_data = data.get("task_data", {})
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    recurrence_pattern = task_data.get("recurrence_pattern")

    # Skip non-recurring tasks
    if not recurrence_pattern or recurrence_pattern == "none":
        logger.debug(
            "Skipping non-recurring task: task_id=%s, pattern=%s",
            task_id,
            recurrence_pattern,
        )
        return {"status": "SKIP"}

    logger.info(
        "Processing recurring task completion: task_id=%s, pattern=%s, user_id=%s",
        task_id,
        recurrence_pattern,
        user_id,
    )

    # Calculate next due date
    current_due_date = task_data.get("due_date")
    try:
        next_due_date = _calculate_next_due_date(current_due_date, recurrence_pattern)
    except ValueError as exc:
        logger.error("Failed to calculate next due date: %s", exc)
        return {"status": "ERROR", "detail": str(exc)}

    # Check if recurrence has ended
    recurrence_end_date = task_data.get("recurrence_end_date")
    if _is_past_recurrence_end(next_due_date, recurrence_end_date):
        logger.info(
            "Recurrence ended for task_id=%s: next_due=%s > end=%s",
            task_id,
            next_due_date,
            recurrence_end_date,
        )
        return {"status": "SKIP"}

    # Build the new task payload
    new_task_payload = {
        "title": task_data.get("title", "Untitled recurring task"),
        "description": task_data.get("description"),
        "priority": task_data.get("priority", "medium"),
        "tags": task_data.get("tags", []),
        "due_date": next_due_date,
        "recurrence_pattern": recurrence_pattern,
        "recurrence_end_date": recurrence_end_date,
        "parent_task_id": str(task_id) if task_id else None,
    }

    # Create the next task occurrence via Dapr Service Invocation
    invoke_url = (
        f"http://localhost:{dapr_http_port}/v1.0/invoke/"
        f"{backend_app_id}/method/api/tasks"
    )

    # NOTE: In production, service-to-service auth would use mTLS via Dapr
    # or a dedicated service account token. For the hackathon, we pass the
    # user_id header so the backend can identify which user owns the task.
    headers = {
        "Content-Type": "application/json",
        "x-user-id": str(user_id) if user_id else "",
    }

    logger.info(
        "Creating next occurrence via Dapr Service Invocation: url=%s, "
        "user_id=%s, next_due=%s",
        invoke_url,
        user_id,
        next_due_date,
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                invoke_url,
                json=new_task_payload,
                headers=headers,
            )
            response.raise_for_status()

        created_task = response.json()
        logger.info(
            "Successfully created next occurrence: new_task_id=%s, "
            "parent_task_id=%s, next_due=%s",
            created_task.get("id"),
            task_id,
            next_due_date,
        )
        return {"status": "SUCCESS", "new_task_id": created_task.get("id")}

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Backend returned error creating task: status=%s, body=%s",
            exc.response.status_code,
            exc.response.text,
        )
        return {
            "status": "ERROR",
            "detail": f"Backend error: {exc.response.status_code}",
        }
    except httpx.RequestError as exc:
        logger.error(
            "Failed to reach backend via Dapr Service Invocation: %s", exc
        )
        return {"status": "ERROR", "detail": f"Connection error: {exc}"}