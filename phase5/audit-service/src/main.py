"""Audit Service - Consumes all task events and stores activity history."""

import json
import logging
import sys

import uvicorn
from fastapi import FastAPI, Request

from src.config import get_settings
from src.handlers.task_event import handle_task_event

settings = get_settings()


# Structured JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": settings.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_entry)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=settings.log_level, handlers=[handler])
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audit Service",
    description="Consumes task events from Kafka via Dapr and stores activity history",
    version="5.0.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "service": "audit-service"}


@app.get("/dapr/subscribe", tags=["dapr"])
async def dapr_subscribe() -> list:
    """Dapr subscription configuration - subscribes to task-events topic."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/api/task-events",
        }
    ]


@app.post("/api/task-events", tags=["events"])
async def receive_task_event(request: Request) -> dict:
    """Receive task events from Dapr Pub/Sub and store as activity."""
    try:
        cloud_event = await request.json()
        data = cloud_event.get("data", cloud_event)
        logger.info("Received task event: %s", data.get("event_type", "unknown"))
        result = await handle_task_event(
            data=data,
            dapr_http_port=settings.dapr_http_port,
            backend_app_id=settings.backend_app_id,
        )
        return result
    except Exception as e:
        logger.error("Error processing task event: %s", str(e))
        return {"status": "SUCCESS"}  # ACK to Dapr to prevent redelivery


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.app_port, reload=False)
