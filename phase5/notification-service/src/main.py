"""FastAPI application entry point for the Notification Service.

This lightweight microservice subscribes to the 'reminders' Kafka topic
via Dapr Pub/Sub and logs notifications when reminder events arrive.
"""

import logging
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.handlers.reminder import handle_reminder

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
settings = get_settings()


def _configure_logging() -> None:
    """Set up structured JSON-style logging to stdout."""
    log_format = (
        '{"timestamp":"%(asctime)s",'
        '"level":"%(levelname)s",'
        '"service":"%(name)s",'
        '"message":"%(message)s"}'
    )
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )


_configure_logging()
logger = logging.getLogger(settings.service_name)

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Notification Service",
    description="Phase 5 Notification Service - Dapr Pub/Sub consumer for reminder events",
    version="5.0.0",
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Liveness / readiness probe used by Kubernetes and the Dockerfile HEALTHCHECK."""
    return {"status": "healthy", "service": settings.service_name}


# ---------------------------------------------------------------------------
# Dapr subscription configuration
# ---------------------------------------------------------------------------
@app.get("/dapr/subscribe", tags=["dapr"])
async def dapr_subscribe() -> list[dict]:
    """Tell the Dapr sidecar which topics this service subscribes to.

    Dapr calls this endpoint on startup to discover programmatic
    subscriptions. We subscribe to the ``reminders`` topic on the
    ``kafka-pubsub`` component and route incoming messages to
    ``POST /api/reminders``.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/api/reminders",
        }
    ]


# ---------------------------------------------------------------------------
# Reminder event consumer endpoint
# ---------------------------------------------------------------------------
@app.post("/api/reminders", tags=["reminders"])
async def receive_reminder(request: Request) -> JSONResponse:
    """Receive a CloudEvent from Dapr Pub/Sub for the reminders topic.

    Dapr wraps the original event payload inside a CloudEvent envelope.
    This endpoint extracts the ``data`` field and delegates processing
    to :func:`src.handlers.reminder.handle_reminder`.
    """
    cloud_event = await request.json()
    logger.info("Received CloudEvent on reminders topic: id=%s", cloud_event.get("id"))

    data = cloud_event.get("data", {})
    result = handle_reminder(data)

    return JSONResponse(content=result)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=False,
    )
