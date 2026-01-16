# Pytest Patterns and Templates Reference

## AAA Pattern (Arrange-Act-Assert)
```python
def test_example():
    # Arrange - Set up test data and dependencies
    user_data = {"email": "test@example.com", "name": "Test User"}
    expected_result = "test@example.com"

    # Act - Execute the functionality being tested
    user = create_user(user_data)
    result = user.email

    # Assert - Verify the expected outcome
    assert result == expected_result
```

## Common Test Patterns

### API Endpoint Tests
```python
def test_endpoint_returns_correct_status(client):
    # Arrange
    url = "/api/users"
    payload = {"email": "test@example.com"}

    # Act
    response = client.post(url, json=payload)

    # Assert
    assert response.status_code == 201

def test_endpoint_returns_expected_data(client):
    # Arrange
    url = "/api/users/1"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "id" in data
```

### Service Layer Tests
```python
def test_service_creates_entity(service, mock_db):
    # Arrange
    user_data = {"email": "test@example.com"}

    # Act
    result = service.create_user(**user_data)

    # Assert
    assert result.email == user_data["email"]
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_service_handles_error_case(service):
    # Arrange
    invalid_data = {"email": "invalid-email"}

    # Act & Assert
    with pytest.raises(ValueError):
        service.create_user(**invalid_data)
```

### Model Tests
```python
def test_model_property_computes_correctly(model_instance):
    # Arrange
    model_instance.value1 = 5
    model_instance.value2 = 10

    # Act
    result = model_instance.computed_property

    # Assert
    assert result == 15

def test_model_validation_fails_on_invalid_data():
    # Act & Assert
    with pytest.raises(ValidationError):
        MyModel(invalid_field="wrong_value")
```

## Parametrization Examples
```python
@pytest.mark.parametrize("input_value,expected", [
    ("lowercase", "LOWERCASE"),
    ("UPPERCASE", "UPPERCASE"),
    ("MixedCase", "MIXEDCASE"),
    ("", ""),
])
def test_string_conversion(input_value, expected):
    result = convert_to_uppercase(input_value)
    assert result == expected

@pytest.mark.parametrize("email,is_valid", [
    ("valid@example.com", True),
    ("invalid-email", False),
    ("", False),
    ("test@", False),
])
def test_email_validation(email, is_valid):
    result = validate_email(email)
    assert result is is_valid
```

## Fixture Patterns
```python
@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def authenticated_client(client, sample_user):
    """Client with authentication headers."""
    token = generate_token(sample_user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    return client

@pytest.fixture(scope="session")
def database_engine():
    """Session-scoped database engine for all tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```