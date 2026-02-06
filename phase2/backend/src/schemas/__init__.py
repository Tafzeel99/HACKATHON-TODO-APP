"""Pydantic schemas package."""

from src.schemas.activity import ActivityListResponse, ActivityResponse
from src.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)
from src.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectReorder,
    ProjectResponse,
    ProjectUpdate,
)
from src.schemas.task import (
    BulkArchive,
    TagsResponse,
    TaskCreate,
    TaskListResponse,
    TaskReorder,
    TaskResponse,
    TaskUpdate,
)
from src.schemas.task_share import (
    TaskShareCreate,
    TaskShareListResponse,
    TaskShareResponse,
    TaskShareUpdate,
)
from src.schemas.user import AuthResponse, TokenResponse, UserCreate, UserLogin, UserResponse
from src.schemas.user_preferences import (
    UserPreferencesDefault,
    UserPreferencesResponse,
    UserPreferencesUpdate,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "AuthResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TagsResponse",
    "TaskReorder",
    "BulkArchive",
    "TaskShareCreate",
    "TaskShareUpdate",
    "TaskShareResponse",
    "TaskShareListResponse",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentListResponse",
    "ActivityResponse",
    "ActivityListResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectReorder",
    "ProjectResponse",
    "ProjectListResponse",
    "UserPreferencesUpdate",
    "UserPreferencesResponse",
    "UserPreferencesDefault",
]
