"""Recurring Task Service - FastAPI application entry point.

This microservice subscribes to the ``task-events`` Kafka topic via Dapr
Pub/Sub and automatically creates the next occurrence when a recurring task
is marked as completed.
"""

import json
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, Response

from src.config import get_settings
from src.handlers.task_completed import handle_task_completed

settings = get_settings()


# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------

class JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "service": settings.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


def _configure_logging() -> None:
    """Set up structured JSON logging on stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level.upper())

    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


_configure_logging()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    logger.info(
        "Starting %s on port %s", settings.service_name, settings.app_port
    )
    yield
    logger.info("Shutting down %s", settings.service_name)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Recurring Task Service",
    description=(
        "Subscribes to task.completed events via Dapr Pub/Sub and "
        "creates the next occurrence for recurring tasks."
    ),
    version="5.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return {"status": "healthy", "service": settings.service_name}


# ---------------------------------------------------------------------------
# Dapr subscription configuration
# ---------------------------------------------------------------------------

@app.get("/dapr/subscribe", tags=["dapr"])
async def dapr_subscribe() -> list[dict]:
    """Return Dapr subscription configuration.

    Dapr calls this endpoint on startup to discover which topics this
    service wants to subscribe to and on which route to receive events.
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/api/task-events",
        }
    ]
    logger.info("Dapr subscription config requested: %s", subscriptions)
    return subscriptions


# ---------------------------------------------------------------------------
# Dapr Pub/Sub event handler
# ---------------------------------------------------------------------------

@app.post("/api/task-events", tags=["events"])
async def receive_task_event(request: Request) -> Response:
    """Receive a CloudEvent from Dapr Pub/Sub on the ``task-events`` topic.

    Dapr delivers messages as CloudEvents. The ``data`` field contains the
    application-level event payload published by the backend service.

    The handler filters for ``task.completed`` events where the task has a
    recurrence pattern, then creates the next occurrence via Dapr Service
    Invocation to the backend.
    """
    try:
        cloud_event = await request.json()
    except Exception:
        logger.error("Failed to parse incoming CloudEvent body")
        return Response(
            content=json.dumps({"status": "DROP"}),
            media_type="application/json",
            status_code=200,
        )

    event_data = cloud_event.get("data", {})
    event_id = cloud_event.get("id", "unknown")

    logger.info(
        "Received CloudEvent: id=%s, type=%s, event_type=%s",
        event_id,
        cloud_event.get("type"),
        event_data.get("event_type"),
    )

    result = await handle_task_completed(
        data=event_data,
        dapr_http_port=settings.dapr_http_port,
        backend_app_id=settings.backend_app_id,
    )

    logger.info(
        "Event processing result: id=%s, status=%s",
        event_id,
        result.get("status"),
    )

    # Return SUCCESS to Dapr so it does not redeliver the message.
    # Even if we SKIP or ERROR, we acknowledge receipt to avoid infinite
    # redelivery. Errors are logged for operational visibility.
    return Response(
        content=json.dumps({"status": "SUCCESS"}),
        media_type="application/json",
        status_code=200,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=False,
    )