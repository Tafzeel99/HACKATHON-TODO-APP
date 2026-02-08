"""Handler for reminder events received from the Kafka reminders topic."""

import logging

logger = logging.getLogger(__name__)


def handle_reminder(data: dict) -> dict:
    """Process a reminder event and log the notification.

    Extracts task details from the event payload and emits a structured
    log line that downstream systems (or operators) can consume.

    Args:
        data: Reminder event payload containing task_id, title, user_id,
              due_at, and remind_at fields.

    Returns:
        A dict with ``{"status": "SUCCESS"}`` indicating the event was
        processed without error.
    """
    task_id = data.get("task_id")
    title = data.get("title")
    user_id = data.get("user_id")
    due_at = data.get("due_at")
    remind_at = data.get("remind_at")

    logger.info(
        "REMINDER: Task '%s' (ID: %s) is due at %s for user %s",
        title,
        task_id,
        due_at,
        user_id,
    )

    logger.debug(
        "Reminder details - remind_at: %s, due_at: %s, task_id: %s, user_id: %s",
        remind_at,
        due_at,
        task_id,
        user_id,
    )

    return {"status": "SUCCESS"}
