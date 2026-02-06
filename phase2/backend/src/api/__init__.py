"""API routes package."""

from src.api.activities import router as activities_router
from src.api.auth import router as auth_router
from src.api.comments import router as comments_router
from src.api.preferences import router as preferences_router
from src.api.projects import router as projects_router
from src.api.shares import router as shares_router
from src.api.tasks import router as tasks_router
from src.api.users import router as users_router

__all__ = [
    "auth_router",
    "tasks_router",
    "shares_router",
    "comments_router",
    "activities_router",
    "users_router",
    "projects_router",
    "preferences_router",
]
