"""Event Pydantic models for Kafka/Dapr Pub/Sub."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TaskEvent(BaseModel):
    """Event published when a task CRUD operation occurs."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # "created", "updated", "completed", "deleted"
    task_id: str
    task_data: dict
    user_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ReminderEvent(BaseModel):
    """Event published when a reminder should fire."""

    task_id: str
    title: str
    due_at: str
    remind_at: str
    user_id: str
