---
name: pytest-suite-generator
description: |
  Auto-generate pytest test cases for backend APIs, services, and utilities.
  This skill should be used when users need to create comprehensive test suites for Python applications,
  particularly for API endpoints, service layer functions, model methods, and utility functions.
---

# Pytest Suite Generator

Auto-generate pytest test cases for backend APIs, services, and utilities.

## When to Use
- User asks to "write tests" or "create test suite"
- User mentions "pytest", "unit tests", or "test coverage"
- User needs tests for API endpoints, services, or utilities
- User wants to improve test coverage for existing codebase

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, testing patterns, framework (FastAPI/Django/Flask), models, services |
| **Conversation** | User's specific requirements, target modules to test, preferred testing patterns |
| **Skill References** | Pytest best practices, fixtures, parametrization, mocking strategies, AAA pattern |
| **User Guidelines** | Project-specific conventions, team standards, existing test organization |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

## Procedure

1. **Identify test type**: Unit, integration, or functional
2. **Create test structure**: Arrange-Act-Assert pattern
3. **Add fixtures**: Setup/teardown for test data
4. **Mock dependencies**: External APIs, databases, services
5. **Assert outcomes**: Status codes, data, exceptions

## Test Templates

### API Endpoint Tests
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUserAPI:
    """Test user management endpoints"""

    def test_create_user_success(self, db_session):
        """Test successful user creation"""
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }

        # Act
        response = client.post("/api/users", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert "password" not in data
        assert "id" in data

    def test_create_user_duplicate_email(self, db_session, existing_user):
        """Test user creation with duplicate email fails"""
        payload = {
            "email": existing_user.email,
            "password": "Pass123!",
            "name": "Duplicate"
        }

        response = client.post("/api/users", json=payload)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_get_user_by_id(self, db_session, existing_user):
        """Test retrieving user by ID"""
        response = client.get(f"/api/users/{existing_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == existing_user.id
        assert data["email"] == existing_user.email

    def test_get_user_not_found(self, db_session):
        """Test 404 for non-existent user"""
        response = client.get("/api/users/99999")

        assert response.status_code == 404

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "@example.com",
        "test@",
        ""
    ])
    def test_create_user_invalid_email(self, invalid_email):
        """Test validation for invalid email formats"""
        payload = {
            "email": invalid_email,
            "password": "Pass123!",
            "name": "Test"
        }

        response = client.post("/api/users", json=payload)

        assert response.status_code == 422
```

### Service Layer Tests
```python
# tests/test_services.py
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.models import User

class TestUserService:
    """Test business logic layer"""

    @pytest.fixture
    def user_service(self, mock_db):
        return UserService(db=mock_db)

    def test_create_user(self, user_service, mock_db):
        """Test user creation service"""
        # Arrange
        user_data = {
            "email": "new@example.com",
            "password": "Pass123!",
            "name": "New User"
        }

        # Act
        user = user_service.create_user(**user_data)

        # Assert
        assert user.email == user_data["email"]
        assert user.hashed_password != user_data["password"]
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_authenticate_user_success(self, user_service, mock_user):
        """Test successful authentication"""
        mock_user.verify_password.return_value = True

        result = user_service.authenticate(
            email="test@example.com",
            password="correctpass"
        )

        assert result == mock_user

    def test_authenticate_user_wrong_password(self, user_service, mock_user):
        """Test authentication with wrong password"""
        mock_user.verify_password.return_value = False

        result = user_service.authenticate(
            email="test@example.com",
            password="wrongpass"
        )

        assert result is None
```

### Model Tests
```python
# tests/test_models.py
import pytest
from app.models import User, Post

class TestUserModel:
    """Test User model methods"""

    def test_password_hashing(self):
        """Test password is hashed, not stored plain"""
        user = User(email="test@example.com")
        plain_password = "MySecurePass123!"

        user.set_password(plain_password)

        assert user.hashed_password != plain_password
        assert user.verify_password(plain_password) is True
        assert user.verify_password("wrongpass") is False

    def test_user_repr(self):
        """Test string representation"""
        user = User(id=1, email="test@example.com")

        assert "test@example.com" in repr(user)

    def test_user_relationships(self, db_session):
        """Test user-post relationship"""
        user = User(email="author@example.com")
        post = Post(title="Test Post", content="Content", author=user)

        db_session.add_all([user, post])
        db_session.commit()

        assert len(user.posts) == 1
        assert user.posts[0].title == "Test Post"
```

### Utility Function Tests
```python
# tests/test_utils.py
import pytest
from datetime import datetime, timedelta
from app.utils import (
    validate_email,
    generate_token,
    parse_date,
    calculate_age
)

class TestValidation:
    """Test validation utilities"""

    @pytest.mark.parametrize("valid_email", [
        "user@example.com",
        "test.user@domain.co.uk",
        "name+tag@site.com"
    ])
    def test_validate_email_valid(self, valid_email):
        assert validate_email(valid_email) is True

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "@example.com",
        "test@",
        "test space@example.com"
    ])
    def test_validate_email_invalid(self, invalid_email):
        assert validate_email(invalid_email) is False

class TestTokens:
    """Test token generation"""

    def test_generate_token_unique(self):
        """Test tokens are unique"""
        token1 = generate_token()
        token2 = generate_token()

        assert token1 != token2
        assert len(token1) == 32

    def test_generate_token_with_prefix(self):
        """Test token with custom prefix"""
        token = generate_token(prefix="usr")

        assert token.startswith("usr_")
```

## Pytest Configuration
```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    """Create database session for each test"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def existing_user(db_session):
    """Create test user"""
    from app.models import User
    user = User(
        email="existing@example.com",
        name="Existing User"
    )
    user.set_password("Pass123!")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def mock_db():
    """Mock database session"""
    from unittest.mock import Mock
    return Mock()

@pytest.fixture
def mock_user():
    """Mock user object"""
    from unittest.mock import Mock
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    return user
```

## Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run tests matching pattern
pytest -k "test_user"

# Run with verbose output
pytest -v

# Run failed tests only
pytest --lf
```

## Best Practices
1. **AAA Pattern**: Arrange-Act-Assert structure
2. **One assertion**: Test one thing per test when possible
3. **Descriptive names**: Clear test function names
4. **Parameterize**: Use @pytest.mark.parametrize for multiple inputs
5. **Fixtures**: Reuse setup code with fixtures
6. **Mock external**: Mock APIs, databases, time
7. **Cleanup**: Rollback database changes after tests
8. **Fast tests**: Unit tests should be quick