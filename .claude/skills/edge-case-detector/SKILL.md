---
name: edge-case-detector
description: |
  Generate boundary value and error condition tests. Use when users need comprehensive edge case coverage.
---

# Edge Case Detector

Generate boundary value and error condition tests.

## When to Use
- User asks for "edge cases" or "boundary tests"
- User needs error condition testing
- User wants comprehensive test coverage

## Procedure
1. **Identify boundaries**: Min/max values, limits
2. **Null/empty cases**: Missing data, empty strings
3. **Invalid inputs**: Wrong types, formats
4. **Error conditions**: Exceptions, failures
5. **Race conditions**: Concurrent access

## Boundary Value Testing

### Numeric Boundaries
```python
import pytest

class TestNumericBoundaries:
    """Test boundary values for numeric inputs"""

    @pytest.mark.parametrize("age,valid", [
        (-1, False),      # Below minimum
        (0, True),        # Minimum
        (1, True),        # Just above minimum
        (17, True),       # Just below threshold
        (18, True),       # Threshold
        (19, True),       # Just above threshold
        (120, True),      # Maximum
        (121, False),     # Above maximum
    ])
    def test_age_validation(self, age, valid):
        """Test age boundaries"""
        if valid:
            assert validate_age(age) is True
        else:
            with pytest.raises(ValidationError):
                validate_age(age)

    @pytest.mark.parametrize("price", [
        0.00,             # Free
        0.01,             # Minimum paid
        99.99,            # Normal
        9999.99,          # Maximum
        10000.00,         # Above max (should fail)
    ])
    def test_price_boundaries(self, price):
        """Test price boundaries"""
        if price <= 9999.99:
            assert validate_price(price)
        else:
            with pytest.raises(ValidationError):
                validate_price(price)
```

### String Length Boundaries
```python
class TestStringBoundaries:
    """Test string length limits"""

    def test_username_empty(self):
        """Empty username should fail"""
        with pytest.raises(ValidationError):
            create_user(username="")

    def test_username_minimum(self):
        """Minimum length username"""
        user = create_user(username="ab")  # Min: 2 chars
        assert user.username == "ab"

    def test_username_maximum(self):
        """Maximum length username"""
        username = "a" * 50  # Max: 50 chars
        user = create_user(username=username)
        assert len(user.username) == 50

    def test_username_exceeds_maximum(self):
        """Username exceeding max should fail"""
        username = "a" * 51
        with pytest.raises(ValidationError):
            create_user(username=username)

    @pytest.mark.parametrize("bio", [
        None,                    # Null
        "",                      # Empty
        "Short",                 # Valid short
        "x" * 500,              # Max length
        "x" * 501,              # Exceeds max
    ])
    def test_bio_boundaries(self, bio):
        """Test bio field boundaries"""
        if bio is None or len(bio) <= 500:
            user = create_user(bio=bio)
            assert user.bio == (bio or "")
        else:
            with pytest.raises(ValidationError):
                create_user(bio=bio)
```

### Date/Time Boundaries
```python
from datetime import datetime, timedelta

class TestDateBoundaries:
    """Test date/time edge cases"""

    def test_past_date(self):
        """Dates in the past should fail"""
        past = datetime.now() - timedelta(days=1)
        with pytest.raises(ValidationError):
            schedule_event(date=past)

    def test_today(self):
        """Today's date should be valid"""
        today = datetime.now()
        event = schedule_event(date=today)
        assert event.date == today

    def test_far_future(self):
        """Very far future dates"""
        far_future = datetime.now() + timedelta(days=365 * 10)
        with pytest.raises(ValidationError):
            schedule_event(date=far_future)

    def test_leap_year(self):
        """Test Feb 29 on leap year"""
        leap_date = datetime(2024, 2, 29)
        event = schedule_event(date=leap_date)
        assert event.date.day == 29

    def test_timezone_boundaries(self):
        """Test UTC midnight boundaries"""
        midnight_utc = datetime(2024, 1, 1, 0, 0, 0)
        event = schedule_event(date=midnight_utc)
        assert event.date.hour == 0
```

## Null/Empty Cases

### Null Value Testing
```python
class TestNullValues:
    """Test null/None handling"""

    def test_required_field_null(self):
        """Required field as null should fail"""
        with pytest.raises(ValidationError):
            create_user(email=None)

    def test_optional_field_null(self):
        """Optional field as null should succeed"""
        user = create_user(bio=None)
        assert user.bio is None

    def test_null_in_list(self):
        """Null values in list"""
        tags = ["tag1", None, "tag3"]
        with pytest.raises(ValidationError):
            create_post(tags=tags)

    @pytest.mark.parametrize("value", [
        None,
        "",
        "   ",    # Whitespace only
        "\n\t",   # Newlines/tabs
    ])
    def test_empty_values(self, value):
        """Test various empty values"""
        with pytest.raises(ValidationError):
            create_user(name=value)
```

### Empty Collection Cases
```python
class TestEmptyCollections:
    """Test empty lists, dicts, sets"""

    def test_empty_list(self):
        """Empty list handling"""
        result = process_items([])
        assert result == []

    def test_empty_dict(self):
        """Empty dictionary"""
        result = process_data({})
        assert result == {}

    def test_list_with_empty_strings(self):
        """List containing empty strings"""
        items = ["valid", "", "also_valid"]
        cleaned = clean_items(items)
        assert cleaned == ["valid", "also_valid"]

    def test_nested_empty_collections(self):
        """Nested empty structures"""
        data = {"users": [], "posts": {}}
        result = process_nested(data)
        assert result["users"] == []
```

## Invalid Input Testing

### Type Errors
```python
class TestTypeErrors:
    """Test invalid types"""

    @pytest.mark.parametrize("invalid_email", [
        123,              # Integer
        12.34,            # Float
        True,             # Boolean
        [],               # List
        {},               # Dict
        None,             # None
    ])
    def test_email_wrong_type(self, invalid_email):
        """Email must be string"""
        with pytest.raises(TypeError):
            create_user(email=invalid_email)

    def test_age_as_string(self):
        """Age as string should fail"""
        with pytest.raises(TypeError):
            create_user(age="twenty")

    def test_price_as_string(self):
        """Price as string"""
        # Should accept "10.99" and convert
        product = create_product(price="10.99")
        assert product.price == 10.99
```

### Format Validation
```python
class TestFormatValidation:
    """Test format/pattern validation"""

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com",
        "user@example",
    ])
    def test_invalid_email_formats(self, invalid_email):
        """Invalid email formats"""
        with pytest.raises(ValidationError):
            create_user(email=invalid_email)

    @pytest.mark.parametrize("invalid_phone", [
        "123",              # Too short
        "abcdefghij",       # Letters
        "123-456-789X",     # Invalid char
        "+1234567890123",   # Too long
    ])
    def test_invalid_phone_formats(self, invalid_phone):
        """Invalid phone formats"""
        with pytest.raises(ValidationError):
            create_user(phone=invalid_phone)

    @pytest.mark.parametrize("invalid_url", [
        "not a url",
        "htp://example.com",    # Typo in protocol
        "ftp://example.com",    # Wrong protocol
        "//example.com",        # Missing protocol
    ])
    def test_invalid_url_formats(self, invalid_url):
        """Invalid URL formats"""
        with pytest.raises(ValidationError):
            create_post(url=invalid_url)
```

## Race Conditions & Concurrency

### Concurrent Access
```python
import threading
from concurrent.futures import ThreadPoolExecutor

class TestConcurrency:
    """Test concurrent access edge cases"""

    def test_concurrent_user_creation(self):
        """Multiple threads creating same user"""
        email = "test@example.com"
        results = []

        def create():
            try:
                user = create_user(email=email)
                results.append(("success", user))
            except Exception as e:
                results.append(("error", str(e)))

        # Attempt to create same user simultaneously
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create) for _ in range(5)]
            [f.result() for f in futures]

        # Only one should succeed
        successes = [r for r in results if r[0] == "success"]
        assert len(successes) == 1

    def test_concurrent_balance_update(self):
        """Test race condition in balance updates"""
        user = create_user(balance=100)

        def deduct():
            update_balance(user.id, -10)

        # 10 concurrent deductions
        with ThreadPoolExecutor(max_workers=10) as executor:
            [executor.submit(deduct) for _ in range(10)]

        user.refresh()
        assert user.balance == 0  # Should be 0, not negative
```

### Deadlock Scenarios
```python
class TestDeadlocks:
    """Test potential deadlock scenarios"""

    def test_circular_dependency(self):
        """Test circular resource acquisition"""
        user1 = create_user()
        user2 = create_user()

        def transfer_1_to_2():
            with db.transaction():
                lock_account(user1.id)
                lock_account(user2.id)
                transfer(user1, user2, 10)

        def transfer_2_to_1():
            with db.transaction():
                lock_account(user2.id)
                lock_account(user1.id)
                transfer(user2, user1, 10)

        # Should not deadlock
        with ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(transfer_1_to_2)
            f2 = executor.submit(transfer_2_to_1)

            # Should complete without timeout
            f1.result(timeout=5)
            f2.result(timeout=5)
```

## Special Character Testing

### SQL Injection Attempts
```python
class TestSecurityEdgeCases:
    """Test security edge cases"""

    @pytest.mark.parametrize("malicious_input", [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--",
    ])
    def test_sql_injection_attempts(self, malicious_input):
        """Test SQL injection protection"""
        # Should not raise SQL error, should be escaped
        user = create_user(name=malicious_input)
        assert user.name == malicious_input

    @pytest.mark.parametrize("xss_input", [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
    ])
    def test_xss_attempts(self, xss_input):
        """Test XSS protection"""
        user = create_user(bio=xss_input)
        # Should be escaped in output
        assert "<script>" not in user.bio_html
```

### Unicode & Encoding
```python
class TestUnicodeEdgeCases:
    """Test unicode and encoding edge cases"""

    @pytest.mark.parametrize("unicode_text", [
        "Hello 世界",           # Chinese
        "مرحبا",                # Arabic
        "Привет",               # Russian
        "🎉🎊🎈",               # Emoji
        "café",                 # Accented
        "\u200b",               # Zero-width space
    ])
    def test_unicode_handling(self, unicode_text):
        """Test unicode character handling"""
        user = create_user(name=unicode_text)
        assert user.name == unicode_text

    def test_emoji_in_text(self):
        """Test emoji handling"""
        text = "Hello 👋 World 🌍"
        post = create_post(content=text)
        assert post.content == text
```

## Error Recovery

### Partial Failure Handling
```python
class TestPartialFailures:
    """Test partial failure scenarios"""

    def test_batch_insert_partial_failure(self):
        """Some items valid, some invalid"""
        users = [
            {"email": "valid1@example.com"},
            {"email": "invalid"},  # Invalid email
            {"email": "valid2@example.com"},
        ]

        result = batch_create_users(users)

        assert result["success"] == 2
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    def test_transaction_rollback(self):
        """Test rollback on error"""
        initial_count = User.query.count()

        with pytest.raises(Exception):
            with db.transaction():
                create_user(email="test1@example.com")
                create_user(email="test2@example.com")
                raise Exception("Forced error")

        # Count should be unchanged
        assert User.query.count() == initial_count
```

## Best Practices
1. **Test boundaries**: Min, max, just inside, just outside
2. **Null cases**: Test None, empty string, whitespace
3. **Invalid types**: Wrong data types for parameters
4. **Format validation**: Invalid formats, patterns
5. **Concurrent access**: Race conditions, deadlocks
6. **Security**: SQL injection, XSS attempts
7. **Unicode**: International characters, emoji
8. **Error recovery**: Partial failures, rollbacks

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing validation logic, data models, error handling |
| **Conversation** | User's specific edge cases, business rules, constraints |
| **Skill References** | Standard edge case testing patterns, boundary value analysis |
| **User Guidelines** | Project-specific validation rules, security requirements |