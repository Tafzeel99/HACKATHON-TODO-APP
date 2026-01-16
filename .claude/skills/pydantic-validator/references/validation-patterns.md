# Pydantic Validation Patterns Guide

This guide covers all validation patterns and techniques in Pydantic.

## Field Validation

### Basic Field Constraints
```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    # String constraints
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')

    # Numeric constraints
    age: int = Field(..., ge=0, le=150)  # greater than or equal, less than or equal
    score: float = Field(default=0.0, ge=0.0, le=100.0)

    # Optional field with constraints
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
```

### Using Annotated Types
```python
from typing_extensions import Annotated
from annotated_types import Gt, Lt, MinLen, MaxLen

class Product(BaseModel):
    name: Annotated[str, MinLen(1), MaxLen(100)]
    price: Annotated[float, Gt(0)]  # Greater than 0
    quantity: Annotated[int, Gt(-1), Lt(1000)]  # Between -1 and 1000
```

## Field Validators

### Single Field Validator
```python
from pydantic import BaseModel, field_validator
from typing import Any

class User(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Email must contain @ symbol')
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### Multiple Field Validator
```python
class Transaction(BaseModel):
    amount: float
    fee: float

    @field_validator('amount', 'fee')
    @classmethod
    def validate_positive_values(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Value must be positive')
        return v
```

### Validation Modes
```python
class DataProcessor(BaseModel):
    raw_input: str
    processed: str = None

    # 'before' mode - runs before type coercion
    @field_validator('processed', mode='before')
    @classmethod
    def preprocess_raw(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    # 'after' mode - runs after type coercion (default)
    @field_validator('processed', mode='after')
    @classmethod
    def validate_processed(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('Processed value too short')
        return v

    # 'plain' mode - replaces type coercion entirely
    @field_validator('raw_input', mode='plain')
    @classmethod
    def validate_raw_input(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError('Input must be string')
        return v.strip()
```

## Model Validators

### Cross-Field Validation
```python
from datetime import datetime

class Booking(BaseModel):
    start_date: datetime
    end_date: datetime
    notify_days_before: int = Field(default=1, ge=0)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError('End date must be after start date')

        notification_date = self.start_date - timedelta(days=self.notify_days_before)
        if notification_date < datetime.now():
            raise ValueError('Notification date is in the past')

        return self
```

### Conditional Validation
```python
class Payment(BaseModel):
    payment_type: str  # 'credit_card', 'paypal', 'bank_transfer'
    card_number: str = None
    paypal_email: str = None
    bank_account: str = None

    @model_validator(mode='after')
    def validate_payment_details(self):
        if self.payment_type == 'credit_card':
            if not self.card_number or len(self.card_number) != 16:
                raise ValueError('Valid card number required for credit card payments')
        elif self.payment_type == 'paypal':
            if not self.paypal_email or '@' not in self.paypal_email:
                raise ValueError('Valid PayPal email required')
        elif self.payment_type == 'bank_transfer':
            if not self.bank_account:
                raise ValueError('Bank account details required for bank transfer')
        else:
            raise ValueError('Invalid payment type')

        return self
```

## Custom Error Handling

### Using PydanticCustomError
```python
from pydantic_core import PydanticCustomError

class Product(BaseModel):
    name: str
    price: float
    category: str

    @field_validator('price')
    @classmethod
    def validate_price_range(cls, v: float) -> float:
        if v <= 0:
            raise PydanticCustomError(
                'invalid_price',
                'Price must be positive, got {price}',
                {'price': v}
            )
        if v > 10000:
            raise PydanticCustomError(
                'price_too_high',
                'Price {price} exceeds maximum allowed ({max_price})',
                {'price': v, 'max_price': 10000}
            )
        return v
```

### Custom Error Message Formatting
```python
CUSTOM_ERROR_MESSAGES = {
    'price_range_error': 'The price {value} is not within the allowed range ({min_val}-{max_val})',
    'invalid_format': 'The value {input_value} does not match the expected format',
}

def format_validation_error(error_type: str, **context) -> str:
    """Helper function to format custom error messages"""
    template = CUSTOM_ERROR_MESSAGES.get(error_type, 'Validation failed')
    return template.format(**context)
```

## Advanced Validation Techniques

### Using PlainValidator for Complex Validation
```python
from typing import Annotated
from pydantic import PlainValidator

def validate_id_or_email(value: str) -> str:
    """Validate that input is either a valid ID (numeric) or email"""
    if value.isdigit():
        # It's an ID
        if int(value) <= 0:
            raise ValueError('ID must be positive')
    elif '@' in value and '.' in value:
        # It's an email
        if len(value) < 5:
            raise ValueError('Email too short')
    else:
        raise ValueError('Must be a valid ID or email')

    return value

UserIdOrEmail = Annotated[str, PlainValidator(validate_id_or_email)]

class LookupRequest(BaseModel):
    identifier: UserIdOrEmail
```

### Using WrapValidator for Complex Logic
```python
from pydantic import WrapValidator
from typing import Callable, Any

def conditional_validator(
    v: Any,
    handler: Callable[[Any], Any],
    info
) -> Any:
    """Validate differently based on other field values"""
    # First, let the normal validation happen
    validated_value = handler(v)

    # Then apply conditional validation
    # Note: This would need access to the full model context
    # which is more complex to implement

    return validated_value

ConditionalField = Annotated[str, WrapValidator(conditional_validator)]
```

## Validation Performance Tips

### Efficient Validation Patterns
```python
class EfficientModel(BaseModel):
    # Use built-in constraints when possible (faster than custom validators)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)

    # For complex validation, use early returns to avoid unnecessary computation
    @field_validator('complex_field')
    @classmethod
    def validate_complex_field(cls, v: str) -> str:
        if not v:  # Early return for empty values
            return v

        if len(v) > 1000:  # Early return for obviously invalid
            raise ValueError('Field too long')

        # Only do expensive validation for values that pass initial checks
        if expensive_validation_check(v):
            return v
        raise ValueError('Failed complex validation')
```

### Caching Validated Values
```python
from functools import lru_cache

class CachedValidationModel(BaseModel):
    url: str

    @field_validator('url')
    @classmethod
    def validate_and_normalize_url(cls, v: str) -> str:
        # Use lru_cache for expensive validation operations
        return cls._cached_url_validation(v)

    @staticmethod
    @lru_cache(maxsize=1000)
    def _cached_url_validation(url: str) -> str:
        # Expensive URL validation that benefits from caching
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        # Additional validation logic...
        return url
```

## Validation Testing

### Unit Testing Validators
```python
import pytest
from pydantic import ValidationError

def test_email_validation():
    # Valid email should pass
    user = User(email="test@example.com", password="StrongPass123")
    assert user.email == "test@example.com"

    # Invalid email should raise ValidationError
    with pytest.raises(ValidationError):
        User(email="invalid-email", password="StrongPass123")

    # Empty email should raise ValidationError
    with pytest.raises(ValidationError):
        User(email="", password="StrongPass123")

def test_cross_field_validation():
    # Valid date range should pass
    booking = Booking(
        start_date=datetime(2023, 12, 1),
        end_date=datetime(2023, 12, 5)
    )
    assert booking.start_date < booking.end_date

    # Invalid date range should raise ValidationError
    with pytest.raises(ValidationError):
        Booking(
            start_date=datetime(2023, 12, 5),
            end_date=datetime(2023, 12, 1)
        )
```

These patterns ensure robust, efficient, and maintainable validation in your Pydantic models.