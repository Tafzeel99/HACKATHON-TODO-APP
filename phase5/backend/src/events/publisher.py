"""Dapr Pub/Sub event publisher - publishes events via Dapr sidecar HTTP API."""

import logging

import httpx

from src.config import get_settings
from src.events.schemas import TaskEvent
from src.events.topics import Topics

logger = logging.getLogger(__name__)

PUBSUB_NAME = "kafka-pubsub"


class DaprEventPublisher:
    """Publishes events to Kafka via Dapr sidecar Pub/Sub API.

    Fire-and-forget: if Dapr is unavailable, logs error but never fails the caller.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = settings.dapr_enabled
        self.dapr_url = f"http://localhost:{settings.dapr_http_port}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=5.0)
        return self._client

    async def publish(self, topic: str, data: dict) -> None:
        """Publish an event to a Kafka topic via Dapr Pub/Sub.

        Args:
            topic: Kafka topic name (e.g., Topics.TASK_EVENTS)
            data: Event payload dict
        """
        if not self.enabled:
            logger.debug("Dapr disabled, skipping event publish to %s", topic)
            return

        url = f"{self.dapr_url}/v1.0/publish/{PUBSUB_NAME}/{topic}"
        try:
            client = await self._get_client()
            response = await client.post(url, json=data)
            response.raise_for_status()
            logger.info("Published event to %s: %s", topic, data.get("event_type", "unknown"))
        except Exception as e:
            logger.error("Failed to publish event to %s: %s", topic, str(e))

    async def publish_task_event(
        self,
        event_type: str,
        task_id: str,
        task_data: dict,
        user_id: str,
    ) -> None:
        """Publish a task event (created/updated/completed/deleted)."""
        event = TaskEvent(
            event_type=event_type,
            task_id=task_id,
            task_data=task_data,
            user_id=user_id,
        )
        await self.publish(Topics.TASK_EVENTS, event.model_dump())

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
_publisher: DaprEventPublisher | None = None


def get_event_publisher() -> DaprEventPublisher:
    """Get the singleton event publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = DaprEventPublisher()
    return _publisher
