# Pytest Mocking and Testing External Dependencies

## Mocking External Services
When testing code that depends on external services (APIs, databases, file systems), use mocking to isolate the functionality being tested.

### Mocking HTTP Requests
```python
import pytest
from unittest.mock import patch, Mock
import requests

def test_api_call_success():
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "success"}

    # Act & Assert
    with patch('requests.get', return_value=mock_response):
        result = make_external_api_call("https://api.example.com/data")
        assert result == {"result": "success"}

def test_api_call_failure():
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 404

    # Act & Assert
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(Exception):
            make_external_api_call("https://api.example.com/data")
```

### Mocking Database Calls
```python
import pytest
from unittest.mock import Mock

def test_user_creation_with_mocked_db(user_service, mock_db_session):
    # Arrange
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None

    # Act
    result = user_service.create_user(mock_db_session, "test@example.com", "password")

    # Assert
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    assert result.email == "test@example.com"
```

## Monkey Patching
Use pytest's monkeypatch fixture for simpler patching scenarios:

```python
def test_with_monkeypatch(monkeypatch):
    def mock_get_current_user():
        return {"id": 999, "email": "mocked@example.com"}

    monkeypatch.setattr("myapp.auth.get_current_user", mock_get_current_user)

    result = protected_function()
    assert result["user"]["id"] == 999
```

## Mocking Time Dependencies
```python
from unittest.mock import patch
from datetime import datetime

def test_timestamp_generation():
    fixed_time = datetime(2023, 1, 1, 12, 0, 0)

    with patch('myapp.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        result = generate_timestamp()
        assert result == fixed_time.isoformat()
```

## Testing Async Code
```python
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_function():
    # Arrange
    mock_result = {"data": "success"}
    mock_async_func = AsyncMock(return_value=mock_result)

    # Act
    result = await call_async_function(mock_async_func)

    # Assert
    assert result == mock_result
    mock_async_func.assert_called_once()
```

## Side Effects for Complex Mocking
```python
def test_function_with_exception_handling():
    # Arrange
    def side_effect():
        raise ConnectionError("Network error")

    # Act & Assert
    with patch('myapp.external_api.call', side_effect=side_effect):
        with pytest.raises(ConnectionError):
            call_function_that_handles_errors()
```