"""Rate limiting middleware for Phase 3 API."""

import time
from collections import defaultdict
from typing import Dict

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static assets
        if request.url.path in ["/health", "/docs", "/redoc"] or request.url.path.startswith("/static"):
            return await call_next(request)

        # For chat endpoints, extract user_id from path
        user_id = None
        if "/chat" in request.url.path:
            # Extract user_id from path like /api/{user_id}/chat
            path_parts = request.url.path.split("/")
            for i, part in enumerate(path_parts):
                if part == "chat" and i > 0:
                    # The user_id should be the part before "chat"
                    user_id = path_parts[i - 1]
                    break

        if not user_id:
            # If we can't extract user_id from path, try to get it from headers
            user_id = request.headers.get("user-id") or request.headers.get("x-user-id")

        if user_id:
            current_time = time.time()

            # Clean old requests (older than 1 minute)
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if current_time - req_time < 60
            ]

            # Check if user has exceeded rate limit
            if len(self.requests[user_id]) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limited",
                        "message": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
                    },
                )

            # Record this request
            self.requests[user_id].append(current_time)

        response = await call_next(request)
        return response