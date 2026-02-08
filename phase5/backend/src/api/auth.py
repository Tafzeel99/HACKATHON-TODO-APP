"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.api.deps import CurrentUser, DbSession
from src.schemas import AuthResponse, UserCreate, UserLogin, UserResponse
from src.services import AuthService

router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
)
async def signup(
    data: UserCreate,
    session: DbSession,
) -> AuthResponse:
    """Create a new user account.

    - **email**: Valid email address (unique)
    - **password**: Password (min 8 characters)
    - **name**: Optional display name
    """
    auth_service = AuthService(session)

    # Check if email already exists
    existing_user = await auth_service.get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        auth_response = await auth_service.signup_with_token(data)
        return auth_response
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )


@router.post(
    "/signin",
    response_model=AuthResponse,
    summary="Authenticate user and get JWT token",
)
async def signin(
    data: UserLogin,
    session: DbSession,
) -> AuthResponse:
    """Authenticate a user and return a JWT access token.

    - **email**: User's email address
    - **password**: User's password
    """
    auth_service = AuthService(session)

    auth_response = await auth_service.signin(data.email, data.password)

    if not auth_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return auth_response


@router.post(
    "/signout",
    status_code=status.HTTP_200_OK,
    summary="Invalidate current session",
)
async def signout(
    current_user: CurrentUser,
) -> dict:
    """Sign out the current user.

    Note: Since we use stateless JWT tokens, this endpoint simply
    acknowledges the signout. The client should discard the token.
    """
    # In a stateless JWT system, we don't need to do anything server-side
    # The client is responsible for discarding the token
    return {"message": "Successfully signed out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_current_user_info(
    current_user: CurrentUser,
    session: DbSession,
) -> UserResponse:
    """Get the currently authenticated user's information."""
    auth_service = AuthService(session)
    user = await auth_service.get_user_by_id(current_user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
    )
