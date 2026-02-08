"""FastAPI application entry point for Phase 5 - Event-Driven Backend."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from src.auth import verify_token_from_header
from src.chatkit_server import get_chatkit_server
from src.config import get_settings
from src.database import close_db, init_db
from src.events.publisher import get_event_publisher
from src.events.scheduler import get_job_scheduler
from src.events.schemas import ReminderEvent
from src.events.topics import Topics
from src.middleware import RateLimitMiddleware
from src.services.scheduler import scheduler_service

# Import MCP tools to register them (Phase 3)
import src.mcp.tools  # noqa: F401

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    await init_db()
    logger.info("Dapr integration: %s", "ENABLED" if settings.dapr_enabled else "DISABLED")
    # Start background scheduler for email reminders (optional - requires SendGrid)
    try:
        await scheduler_service.start()
    except Exception as e:
        print(f"Scheduler not started (email reminders disabled): {e}")
    yield
    # Shutdown
    await scheduler_service.stop()
    await get_event_publisher().close()
    await get_job_scheduler().close()
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Todo API - Phase 5",
    description="Phase 5 Todo Application - Event-Driven CRUD + AI Chatbot + Dapr + Kafka",
    version="5.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware (Phase 3)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_requests)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "5.0.0", "service": "backend"}


# --- Dapr Integration Endpoints (Phase 5) ---


@app.post("/api/jobs/trigger", tags=["dapr"])
async def handle_job_trigger(request: Request) -> dict:
    """Dapr Jobs API callback - fires when a scheduled job triggers.

    Used for exact-time reminders: publishes reminder event to Kafka via Dapr Pub/Sub.
    """
    job_data = await request.json()
    logger.info("Dapr job triggered: %s", job_data)

    data = job_data.get("data", {})
    if data.get("type") == "reminder":
        # Publish reminder event to Kafka via Dapr Pub/Sub
        publisher = get_event_publisher()
        reminder = ReminderEvent(
            task_id=data["task_id"],
            title=data.get("title", ""),
            due_at=data.get("due_at", ""),
            remind_at=data.get("remind_at", ""),
            user_id=data["user_id"],
        )
        await publisher.publish(Topics.REMINDERS, reminder.model_dump())
        logger.info("Reminder event published for task %s", data["task_id"])

    return {"status": "SUCCESS"}


@app.get("/dapr/subscribe", tags=["dapr"])
async def dapr_subscribe() -> list:
    """Dapr subscription endpoint - tells Dapr which topics this app subscribes to.

    The backend does not subscribe to topics (it only publishes).
    Consumer services (notification, recurring, audit) have their own subscriptions.
    """
    return []


# Import and include routers
# Phase 2 CRUD routers
from src.api import (
    activities_router,
    auth_router,
    chat_router,  # Phase 3
    comments_router,
    preferences_router,
    projects_router,
    shares_router,
    tasks_router,
    users_router,
)

# Phase 2 CRUD endpoints
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(shares_router, prefix="/api/tasks", tags=["shares"])
app.include_router(comments_router, prefix="/api", tags=["comments"])
app.include_router(activities_router, prefix="/api/activities", tags=["activities"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(preferences_router, prefix="/api/preferences", tags=["preferences"])

# Phase 3 AI Chat endpoints
app.include_router(chat_router, prefix="/api", tags=["chat"])


# ChatKit endpoint using the ChatKit Python SDK (Phase 3)
@app.post("/chatkit", tags=["chatkit"])
async def chatkit_endpoint(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """ChatKit-compatible endpoint using the ChatKit Python SDK.

    This endpoint processes requests from the ChatKit frontend and returns
    responses in the ChatKit protocol format (Server-Sent Events for streaming).
    """
    # Extract user_id from authorization header
    user_id = "anonymous"
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
        try:
            user_uuid = verify_token_from_header(token)
            user_id = str(user_uuid)
        except Exception:
            pass

    # Get the ChatKit server
    chatkit_server = get_chatkit_server()

    # Process the request with context containing user_id
    body = await request.body()
    context = {"user_id": user_id}

    try:
        result = await chatkit_server.process(body, context=context)

        # Check if result is a streaming response
        if hasattr(result, "__aiter__"):
            return StreamingResponse(result, media_type="text/event-stream")
        else:
            # Return JSON response
            return Response(content=result.json, media_type="application/json")
    except Exception as e:
        logger.error(f"ChatKit endpoint error: {e}")
        return Response(
            content='{"error": "Internal server error"}',
            media_type="application/json",
            status_code=500,
        )


@app.options("/chatkit")
async def chatkit_options():
    """Handle CORS preflight for ChatKit endpoint."""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )
