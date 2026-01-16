"""Authentication service layer."""

import uuid
from datetime import datetime, timedelta

from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.models import User
from src.schemas import AuthResponse, TokenResponse, UserCreate, UserResponse

settings = get_settings()


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Get a user by ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, data: UserCreate) -> User:
        """Create a new user account."""
        # Hash the password
        hashed_password = bcrypt.hash(data.password)

        # Create user
        user = User(
            email=data.email,
            hashed_password=hashed_password,
            name=data.name,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: uuid.UUID) -> TokenResponse:
        """Create a JWT access token for a user."""
        expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)
        expires_in = settings.jwt_expiration_days * 24 * 60 * 60  # seconds

        payload = {
            "sub": str(user_id),
            "exp": expire,
        }

        access_token = jwt.encode(
            payload,
            settings.better_auth_secret,
            algorithm=settings.jwt_algorithm,
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    async def signup(self, data: UserCreate) -> UserResponse:
        """Sign up a new user."""
        user = await self.create_user(data)
        return UserResponse.model_validate(user)

    async def signup_with_token(self, data: UserCreate) -> AuthResponse:
        """Sign up a new user and return auth response with token."""
        user = await self.create_user(data)
        token = self.create_access_token(user.id)

        return AuthResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
        )

    async def signin(self, email: str, password: str) -> AuthResponse | None:
        """Sign in a user and return auth response with token."""
        user = await self.get_user_by_email(email)

        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        token = self.create_access_token(user.id)

        return AuthResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in,
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
        )
