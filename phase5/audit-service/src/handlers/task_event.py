"""Handler for task events received from the Kafka task-events topic.

Stores each task event as an activity log entry in the backend service
via Dapr Service Invocation.
"""

import logging

import httpx

logger = logging.getLogger(__name__)


async def handle_task_event(
    data: dict,
    dapr_http_port: int,
    backend_app_id: str,
) -> dict:
    """Process a task event and store it as an activity log entry.

    Extracts the event details from the payload and forwards them to the
    backend's activity endpoint via Dapr Service Invocation. If the
    service invocation fails, the error is logged but the event is still
    acknowledged (fire-and-forget semantics) so that Dapr does not
    redeliver the message.

    Args:
        data: The event payload containing event_type, task_id, user_id,
              task_data, and timestamp fields.
        dapr_http_port: The local Dapr HTTP sidecar port (default 3500).
        backend_app_id: The Dapr app-id of the backend service.

    Returns:
        A dict with ``{"status": "SUCCESS"}`` indicating the event was
        processed without error.
    """
    event_type = data.get("event_type")
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    task_data = data.get("task_data", {})
    timestamp = data.get("timestamp")

    logger.info(
        "AUDIT: %s on task %s by user %s",
        event_type,
        task_id,
        user_id,
    )

    logger.debug(
        "Audit event details - event_type: %s, task_id: %s, user_id: %s, "
        "timestamp: %s, task_data: %s",
        event_type,
        task_id,
        user_id,
        timestamp,
        task_data,
    )

    # Build the activity payload to store via the backend
    activity_payload = {
        "task_id": task_id,
        "action_type": event_type,
        "details": task_data,
    }

    # Store activity via Dapr Service Invocation (fire-and-forget)
    invoke_url = (
        f"http://localhost:{dapr_http_port}/v1.0/invoke/"
        f"{backend_app_id}/method/api/activities"
    )

    headers = {
        "Content-Type": "application/json",
        "x-user-id": str(user_id) if user_id else "",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                invoke_url,
                json=activity_payload,
                headers=headers,
            )
            response.raise_for_status()

        logger.info(
            "Activity stored successfully for task %s (event: %s)",
            task_id,
            event_type,
        )

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Backend returned error storing activity: status=%s, body=%s",
            exc.response.status_code,
            exc.response.text,
        )

    except httpx.RequestError as exc:
        logger.error(
            "Failed to reach backend via Dapr Service Invocation: %s",
            exc,
        )

    return {"status": "SUCCESS"}