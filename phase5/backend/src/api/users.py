"""User API endpoints for collaboration features."""

import uuid

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DbSession
from src.models import User
from src.schemas.user import UserResponse

router = APIRouter()


class UserSearchResponse(BaseModel):
    """Schema for user search response."""

    users: list[UserResponse]
    total: int = Field(..., description="Total number of matching users")


@router.get(
    "/search",
    response_model=UserSearchResponse,
    summary="Search users",
)
async def search_users(
    current_user: CurrentUser,
    session: DbSession,
    q: str = Query(..., min_length=2, description="Search query (email or name)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
) -> UserSearchResponse:
    """Search for users by email or name.

    Useful for finding users to share tasks with.
    Excludes the current user from results.
    """
    search_pattern = f"%{q}%"

    query = (
        select(User)
        .where(
            User.id != current_user,
            or_(
                User.email.ilike(search_pattern),
                User.name.ilike(search_pattern),
            ),
        )
        .limit(limit)
    )

    result = await session.execute(query)
    users = result.scalars().all()

    return UserSearchResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=len(users),
    )
