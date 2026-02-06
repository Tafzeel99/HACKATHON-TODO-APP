"""Pytest configuration and fixtures for backend tests."""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.config import get_settings
from src.database import get_session
from src.main import app
from src.models import Task, User

settings = get_settings()

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

# Create test session factory
test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with test_session_maker() as session:
        yield session

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP test client."""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> uuid.UUID:
    """Generate a test user ID."""
    return uuid.uuid4()


@pytest.fixture
def test_user_data() -> dict:
    """Generate test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
    }


@pytest.fixture
def create_test_token(test_user_id: uuid.UUID) -> str:
    """Create a valid JWT token for testing."""
    expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)
    payload = {
        "sub": str(test_user_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.better_auth_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture
def auth_headers(create_test_token: str) -> dict[str, str]:
    """Create authorization headers with a valid token."""
    return {"Authorization": f"Bearer {create_test_token}"}


@pytest.fixture
async def test_user(test_session: AsyncSession, test_user_id: uuid.UUID, test_user_data: dict) -> dict:
    """Create a test user in the database and return as dict."""
    import bcrypt as bcrypt_lib

    hashed = bcrypt_lib.hashpw(
        test_user_data["password"].encode("utf-8"), bcrypt_lib.gensalt()
    ).decode("utf-8")

    user = User(
        id=test_user_id,
        email=test_user_data["email"],
        hashed_password=hashed,
        name=test_user_data["name"],
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "password": test_user_data["password"],  # Keep raw password for signin tests
    }


@pytest.fixture
async def test_task(test_session: AsyncSession, test_user: dict, test_user_id: uuid.UUID) -> dict:
    """Create a test task in the database and return as dict."""
    task = Task(
        user_id=test_user_id,
        title="Test Task",
        description="This is a test task",
        completed=False,
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "user_id": str(task.user_id),
    }


@pytest.fixture
async def test_tasks(test_session: AsyncSession, test_user: dict, test_user_id: uuid.UUID) -> list[dict]:
    """Create multiple test tasks in the database and return as dicts."""
    tasks = [
        Task(user_id=test_user_id, title="Task 1", completed=False),
        Task(user_id=test_user_id, title="Task 2", completed=True),
        Task(user_id=test_user_id, title="Task 3", completed=False),
        Task(user_id=test_user_id, title="Alpha Task", completed=True),
        Task(user_id=test_user_id, title="Zeta Task", completed=False),
    ]
    for task in tasks:
        test_session.add(task)
    await test_session.commit()
    result = []
    for task in tasks:
        await test_session.refresh(task)
        result.append({
            "id": str(task.id),
            "title": task.title,
            "completed": task.completed,
            "user_id": str(task.user_id),
        })
    return result
