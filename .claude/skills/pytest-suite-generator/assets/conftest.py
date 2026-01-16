"""Pytest Configuration and Fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app  # Adjust import based on your app structure


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for API tests."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    # Use an in-memory SQLite database for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    yield engine


@pytest.fixture
def db_session(db_engine, monkeypatch):
    """Create a database session for each test."""
    from app.database import Base  # Adjust import based on your app structure

    # Create tables
    Base.metadata.create_all(bind=db_engine)

    # Create session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # For SQLAlchemy, we'll use a manual rollback approach
    yield session

    # Cleanup
    session.close()


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for tests."""
    # Example: monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    yield monkeypatch


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )