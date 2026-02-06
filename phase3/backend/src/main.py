"""FastAPI application entry point for Phase 3 AI Chatbot."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from src.auth import verify_token_from_header
from src.chatkit_server import get_chatkit_server
from src.config import get_settings
from src.db import close_db, init_db
from src.middleware import RateLimitMiddleware

# Import MCP tools to register them
import src.mcp.tools  # noqa: F401

settings = get_settings()
logger = logging.getLogger(__name__)


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
    title="Todo AI Chatbot API",
    description="Phase III Todo AI Chatbot with OpenAI Agents SDK and MCP",
    version="3.0.0",
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

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": "3.0.0"}


# Import and include routers
from src.api import chat_router

app.include_router(chat_router, prefix="/api", tags=["chat"])


# ChatKit endpoint using the ChatKit Python SDK
@app.post("/chatkit", tags=["chatkit"])
async def chatkit_endpoint(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """ChatKit-compatible endpoint using the ChatKit Python SDK.

    This endpoint processes requests from the ChatKit frontend and returns
    responses in the ChatKit protocol format (Server-Sent Events for streaming).
    """
    # Extract and verify user_id from authorization header (REQUIRED)
    if not authorization or not authorization.startswith("Bearer "):
        logger.error("❌ No authorization header provided")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid JWT token."
        )

    token = authorization.removeprefix("Bearer ")
    try:
        user_uuid = verify_token_from_header(token)
        user_id = str(user_uuid)
        logger.info(f"✅ Token verified successfully, user_id: {user_id[:8]}...")
    except Exception as e:
        logger.error(f"❌ Token verification failed: {e}")
        logger.error(f"   Token preview: {token[:20]}... (length: {len(token)})")
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token: {str(e)}"
        )

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
