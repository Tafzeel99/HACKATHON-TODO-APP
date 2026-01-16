"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import close_db, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
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
from src.api import auth_router, tasks_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
