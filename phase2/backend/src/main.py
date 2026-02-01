"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import close_db, init_db
from src.services.scheduler import scheduler_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    await init_db()
    # Start background scheduler for email reminders (optional - requires SendGrid)
    try:
        await scheduler_service.start()
    except Exception as e:
        print(f"Scheduler not started (email reminders disabled): {e}")
    yield
    # Shutdown
    await scheduler_service.stop()
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Phase II Todo Full-Stack Web Application API",
    version="2.0.0",
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


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


# Import and include routers
from src.api import (
    activities_router,
    auth_router,
    comments_router,
    preferences_router,
    projects_router,
    shares_router,
    tasks_router,
    users_router,
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(shares_router, prefix="/api/tasks", tags=["shares"])
app.include_router(comments_router, prefix="/api", tags=["comments"])
app.include_router(activities_router, prefix="/api/activities", tags=["activities"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(preferences_router, prefix="/api/preferences", tags=["preferences"])
