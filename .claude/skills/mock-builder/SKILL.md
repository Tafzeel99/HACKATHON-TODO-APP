---
name: mock-builder
description: |
  Create mocks for external dependencies like APIs, databases, JWT tokens. Use when users need to isolate code from external systems.
---

# Mock Builder

Create mocks for external dependencies like APIs, databases, JWT tokens.

## When to Use
- User asks to "mock" dependencies or "isolate tests"
- User needs to test without external services
- User wants to simulate API responses or database calls

## Procedure
1. **Identify dependencies**: APIs, database, auth, email, etc.
2. **Create mocks**: Use unittest.mock or pytest-mock
3. **Configure behavior**: Return values, exceptions, side effects
4. **Verify calls**: Assert mock was called correctly
5. **Patch imports**: Replace real implementations

## Basic Mocking

### Mock Objects
```python
from unittest.mock import Mock, MagicMock, patch

# Simple mock
mock_db = Mock()
mock_db.query.return_value = [{"id": 1, "name": "Test"}]
result = mock_db.query()  # Returns mocked data

# Mock with attributes
mock_user = Mock()
mock_user.id = 1
mock_user.email = "test@example.com"
mock_user.is_active = True

# Mock methods
mock_service = Mock()
mock_service.create_user.return_value = {"id": 1, "email": "test@example.com"}
mock_service.delete_user.return_value = True

# Verify calls
mock_service.create_user(email="test@example.com")
mock_service.create_user.assert_called_once()
mock_service.create_user.assert_called_with(email="test@example.com")
```

### Mocking Database
```python
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    db.query = Mock()
    return db

@pytest.fixture
def mock_user_repo(mock_db):
    """Mock user repository"""
    repo = Mock()
    repo.get_by_id = Mock(return_value=None)
    repo.get_by_email = Mock(return_value=None)
    repo.create = Mock()
    repo.update = Mock()
    repo.delete = Mock()
    return repo

def test_create_user_service(mock_user_repo):
    """Test service with mocked repository"""
    from app.services import UserService

    # Setup
    service = UserService(repo=mock_user_repo)
    mock_user_repo.create.return_value = User(id=1, email="test@example.com")

    # Act
    user = service.create_user(email="test@example.com", password="pass")

    # Assert
    mock_user_repo.create.assert_called_once()
    assert user.email == "test@example.com"
```

### Mocking External APIs
```python
from unittest.mock import patch, Mock
import requests

@patch('requests.get')
def test_fetch_external_data(mock_get):
    """Mock external API call"""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"id": 1, "name": "Item 1"}]
    }
    mock_get.return_value = mock_response

    # Call function that uses requests
    from app.services import fetch_items
    items = fetch_items()

    # Assert
    assert len(items) == 1
    assert items[0]["name"] == "Item 1"
    mock_get.assert_called_once_with(
        "https://api.example.com/items",
        headers={"Authorization": "Bearer token"}
    )

@patch('requests.post')
def test_api_error_handling(mock_post):
    """Mock API error"""
    mock_post.side_effect = requests.exceptions.ConnectionError()

    from app.services import send_notification

    with pytest.raises(Exception):
        send_notification("test@example.com", "message")
```

### Mocking JWT/Authentication
```python
from unittest.mock import patch, Mock
import jwt

@pytest.fixture
def mock_jwt_token():
    """Mock JWT token"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

@patch('app.auth.decode_token')
def test_protected_endpoint(mock_decode, client):
    """Mock JWT decode"""
    mock_decode.return_value = {
        "user_id": 1,
        "email": "test@example.com",
        "exp": 9999999999
    }

    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer fake_token"}
    )

    assert response.status_code == 200
    mock_decode.assert_called_once()

@pytest.fixture
def mock_auth_service():
    """Mock authentication service"""
    service = Mock()
    service.create_token.return_value = "mock_token_12345"
    service.verify_token.return_value = {"user_id": 1}
    service.hash_password.return_value = "hashed_password"
    service.verify_password.return_value = True
    return service
```

### Mocking Email Service
```python
from unittest.mock import patch, Mock

@patch('app.email.send_email')
def test_user_registration_sends_email(mock_send_email):
    """Mock email sending"""
    from app.services import register_user

    user = register_user(
        email="new@example.com",
        password="pass123"
    )

    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args
    assert call_args[0][0] == "new@example.com"
    assert "Welcome" in call_args[0][1]  # Subject

@pytest.fixture
def mock_email_client():
    """Mock email client"""
    client = Mock()
    client.send = Mock(return_value={"status": "sent", "id": "msg_123"})
    client.send.side_effect = None  # No exceptions
    return client

def test_email_failure_handling(mock_email_client):
    """Test email sending failure"""
    mock_email_client.send.side_effect = Exception("SMTP error")

    from app.services import notify_user

    # Should handle error gracefully
    result = notify_user(email="test@example.com", message="Hello")
    assert result is False
```

### Mocking Time/Datetime
```python
from unittest.mock import patch
from datetime import datetime

@patch('app.utils.datetime')
def test_with_fixed_time(mock_datetime):
    """Mock current time"""
    fixed_time = datetime(2024, 1, 15, 12, 0, 0)
    mock_datetime.now.return_value = fixed_time
    mock_datetime.utcnow.return_value = fixed_time

    from app.services import create_post
    post = create_post(title="Test", content="Content")

    assert post.created_at == fixed_time

import freezegun

@freezegun.freeze_time("2024-01-15 12:00:00")
def test_with_frozen_time():
    """Freeze time for test"""
    from app.services import is_expired

    # Time is frozen at 2024-01-15 12:00:00
    assert not is_expired(datetime(2024, 1, 16))
    assert is_expired(datetime(2024, 1, 14))
```

### Mocking File Operations
```python
from unittest.mock import mock_open, patch

@patch("builtins.open", new_callable=mock_open, read_data="file content")
def test_read_file(mock_file):
    """Mock file reading"""
    from app.utils import process_file

    result = process_file("data.txt")

    mock_file.assert_called_once_with("data.txt", "r")
    assert "file content" in result

@patch("builtins.open", new_callable=mock_open)
def test_write_file(mock_file):
    """Mock file writing"""
    from app.utils import save_data

    save_data("output.txt", "test data")

    mock_file.assert_called_once_with("output.txt", "w")
    mock_file().write.assert_called_once_with("test data")
```

### Mocking Redis/Cache
```python
@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis = Mock()
    redis.get.return_value = None
    redis.set.return_value = True
    redis.delete.return_value = True
    redis.exists.return_value = False
    return redis

def test_cache_hit(mock_redis):
    """Test with cached data"""
    mock_redis.get.return_value = b'{"id": 1, "name": "Cached"}'

    from app.services import get_user
    user = get_user(user_id=1, cache=mock_redis)

    mock_redis.get.assert_called_once_with("user:1")
    assert user["name"] == "Cached"

def test_cache_miss(mock_redis):
    """Test cache miss and set"""
    mock_redis.get.return_value = None

    from app.services import get_user
    user = get_user(user_id=1, cache=mock_redis)

    # Should fetch from DB and cache
    mock_redis.set.assert_called_once()
```

### Mocking S3/Cloud Storage
```python
@pytest.fixture
def mock_s3_client():
    """Mock AWS S3 client"""
    s3 = Mock()
    s3.upload_file.return_value = None
    s3.download_file.return_value = None
    s3.delete_object.return_value = {"DeleteMarker": True}
    s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/signed-url"
    return s3

def test_file_upload(mock_s3_client):
    """Test S3 file upload"""
    from app.services import upload_to_s3

    url = upload_to_s3(
        file_path="/tmp/test.pdf",
        bucket="my-bucket",
        s3_client=mock_s3_client
    )

    mock_s3_client.upload_file.assert_called_once()
    assert "s3.amazonaws.com" in url
```

## Advanced Mocking

### Pytest-Mock Plugin
```python
# Using pytest-mock (more Pythonic)
def test_with_mocker(mocker):
    """Use mocker fixture"""
    # Patch function
    mock_send = mocker.patch('app.email.send_email')
    mock_send.return_value = True

    # Spy on function (real call + tracking)
    spy = mocker.spy(MyClass, 'method')

    # Mock property
    mocker.patch.object(User, 'is_admin', return_value=True)
```

### Multiple Return Values
```python
def test_retry_logic():
    """Mock multiple return values"""
    mock_api = Mock()
    mock_api.fetch.side_effect = [
        Exception("Network error"),  # First call fails
        Exception("Timeout"),         # Second call fails
        {"data": "success"}           # Third call succeeds
    ]

    from app.services import fetch_with_retry
    result = fetch_with_retry(mock_api)

    assert mock_api.fetch.call_count == 3
    assert result["data"] == "success"
```

### Context Manager Mocks
```python
def test_database_transaction(mocker):
    """Mock context manager"""
    mock_session = mocker.MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    mocker.patch('app.database.get_session', return_value=mock_session)

    from app.services import create_user_transactional
    create_user_transactional(email="test@example.com")

    mock_session.commit.assert_called_once()
```

## Best Practices
1. **Use appropriate mock types**: Mock for simple objects, MagicMock for magic methods
2. **Mock at the right level**: Patch where object is used, not where it's defined
3. **Verify behavior**: Check that mocks were called with expected arguments
4. **Avoid over-mocking**: Only mock external dependencies, not your own logic
5. **Keep mocks simple**: Don't replicate complex logic in mocks
6. **Document expectations**: Make clear what the mock should return/handle

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing code structure, dependencies, testing framework |
| **Conversation** | User's specific dependencies to mock, testing requirements |
| **Skill References** | Standard mocking patterns, pytest-mock best practices |
| **User Guidelines** | Project-specific conventions, testing requirements |