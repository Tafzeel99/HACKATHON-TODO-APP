"""Dapr Jobs API integration for scheduling exact-time reminders."""

import logging

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class DaprJobScheduler:
    """Schedule reminders using Dapr Jobs API for exact-time callbacks."""

    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = settings.dapr_enabled
        self.dapr_url = f"http://localhost:{settings.dapr_http_port}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def schedule_reminder(
        self, task_id: str, remind_at: str, user_id: str, title: str
    ) -> None:
        """Schedule a reminder job that fires at the exact remind_at time.

        Args:
            task_id: Task ID to remind about
            remind_at: ISO datetime string for when to fire
            user_id: User who owns the task
            title: Task title for the notification
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping reminder schedule for task %s", task_id)
            return

        job_name = f"reminder-task-{task_id}"
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        payload = {
            "dueTime": remind_at,
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "title": title,
                "type": "reminder",
            },
        }

        try:
            client = await self._get_client()
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info("Scheduled reminder for task %s at %s", task_id, remind_at)
        except Exception as e:
            logger.error("Failed to schedule reminder for task %s: %s", task_id, str(e))

    async def cancel_reminder(self, task_id: str) -> None:
        """Cancel a previously scheduled reminder job."""
        if not self.enabled:
            return

        job_name = f"reminder-task-{task_id}"
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        try:
            client = await self._get_client()
            response = await client.delete(url)
            if response.status_code != 404:
                response.raise_for_status()
            logger.info("Cancelled reminder for task %s", task_id)
        except Exception as e:
            logger.error("Failed to cancel reminder for task %s: %s", task_id, str(e))

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
_scheduler: DaprJobScheduler | None = None


def get_job_scheduler() -> DaprJobScheduler:
    """Get the singleton job scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = DaprJobScheduler()
    return _scheduler
