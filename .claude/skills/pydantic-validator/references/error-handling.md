# Pydantic Error Handling Guide

This guide covers all error handling patterns and techniques in Pydantic.

## Built-in Validation Errors

### Common Error Types
```python
from pydantic import BaseModel, Field, ValidationError
from pydantic_core import PydanticCustomError
import pytest

class ExampleModel(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$')

# Common errors that can occur:
try:
    ExampleModel(name="", age=-5, email="invalid-email")
except ValidationError as e:
    # Access error details
    errors = e.errors()
    for error in errors:
        print(f"Field: {error['loc']}")           # Field location (e.g., ('name',))
        print(f"Message: {error['msg']}")         # Error message
        print(f"Type: {error['type']}")           # Error type (e.g., 'string_too_short')
        print(f"Input: {error['input']}")         # The input value that caused the error
```

### Error Context
```python
# Error context contains additional information for custom error types
try:
    ExampleModel(name="", age=-5, email="invalid-email")
except ValidationError as e:
    for error in e.errors():
        context = error.get('ctx')  # Additional context for the error
        if context:
            print(f"Context: {context}")
```

## Custom Error Messages

### Using PydanticCustomError
```python
class Product(BaseModel):
    name: str
    price: float = Field(gt=0)
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

### Custom Error Message Templates
```python
ERROR_TEMPLATES = {
    'negative_value': 'Value cannot be negative, got {value}',
    'out_of_range': 'Value {value} is not in range [{min_val}, {max_val}]',
    'invalid_format': 'Value {input_value} does not match required format',
    'too_long': 'Value too long: {length} characters, maximum {max_length}',
    'too_short': 'Value too short: {length} characters, minimum {min_length}',
}

class CustomErrorModel(BaseModel):
    value: float = Field(gt=0, lt=100)

    @field_validator('value')
    @classmethod
    def validate_value_range(cls, v: float) -> float:
        if v < 0:
            raise PydanticCustomError(
                'negative_value',
                ERROR_TEMPLATES['negative_value'],
                {'value': v}
            )
        if v > 100:
            raise PydanticCustomError(
                'out_of_range',
                ERROR_TEMPLATES['out_of_range'],
                {'value': v, 'min_val': 0, 'max_val': 100}
            )
        return v
```

## Error Formatting and Conversion

### Converting Errors to Custom Format
```python
from pydantic_core import ErrorDetails

def format_validation_errors(
    e: ValidationError,
    custom_messages: dict[str, str] = None
) -> list[dict]:
    """
    Convert Pydantic ValidationError to custom format
    """
    if custom_messages is None:
        custom_messages = {}

    formatted_errors = []
    for error in e.errors():
        # Use custom message if available
        custom_msg = custom_messages.get(error['type'])
        if custom_msg:
            ctx = error.get('ctx', {})
            error['msg'] = custom_msg.format(**ctx) if ctx else custom_msg

        # Format error for API response
        formatted_error = {
            'field': error['loc'][-1] if error['loc'] else 'unknown',
            'message': error['msg'],
            'type': error['type'],
            'input': error.get('input'),
            'path': list(error['loc']) if error['loc'] else []
        }
        formatted_errors.append(formatted_error)

    return formatted_errors

# Usage example
try:
    CustomErrorModel(value=-5)
except ValidationError as e:
    api_errors = format_validation_errors(
        e,
        custom_messages={
            'negative_value': 'The value must be positive',
            'out_of_range': 'The value is out of allowed range [0, 100]'
        }
    )
    print(api_errors)
```

### Pretty Error Display
```python
def pretty_print_errors(validation_error: ValidationError):
    """
    Print validation errors in a user-friendly format
    """
    print("Validation Errors:")
    print("-" * 50)

    for i, error in enumerate(validation_error.errors(), 1):
        field_path = " -> ".join(str(loc) for loc in error['loc']) if error['loc'] else "root"
        print(f"{i}. Field: {field_path}")
        print(f"   Message: {error['msg']}")
        print(f"   Type: {error['type']}")
        print(f"   Input: {error.get('input', 'N/A')}")

        if error.get('ctx'):
            print(f"   Context: {error['ctx']}")
        print()
```

## Error Handling in APIs

### FastAPI Integration
```python
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """
    Handle validation errors in FastAPI
    """
    errors = format_validation_errors(exc)
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }
    )

@app.post("/api/products")
async def create_product(product: Product):
    # If validation fails, the exception handler above will be called
    return {"success": True, "data": product}
```

### Error Response Models
```python
from typing import List, Optional

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[dict] = []
    request_id: Optional[str] = None

class SuccessResponse[T](BaseModel):
    success: bool = True
    data: T
    message: Optional[str] = None
    request_id: Optional[str] = None

def create_error_response(message: str, errors: List[dict] = None, request_id: str = None):
    return ErrorResponse(
        message=message,
        errors=errors or [],
        request_id=request_id
    )
```

## Advanced Error Handling

### Validation Error Recovery
```python
class RecoverableModel(BaseModel):
    email: str
    age: int

    @field_validator('email')
    @classmethod
    def validate_email_with_recovery(cls, v: str) -> str:
        if '@' not in v:
            # Attempt recovery by adding default domain
            if v and '.' in v:
                recovered_email = f"{v}@example.com"
                return recovered_email
            else:
                raise ValueError('Invalid email format')
        return v

# Example usage
try:
    model = RecoverableModel(email="user.domain.com", age=25)
    print(f"Recovered email: {model.email}")  # user.domain.com@example.com
except ValidationError as e:
    print(f"Could not recover: {e}")
```

### Validation with Logging
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LoggedValidationModel(BaseModel):
    sensitive_data: str
    public_data: str

    @field_validator('sensitive_data')
    @classmethod
    def validate_sensitive_data(cls, v: str) -> str:
        if len(v) < 8:
            # Log the validation failure without exposing sensitive data
            logger.warning(f"Sensitive data validation failed: length {len(v)} < 8")
            raise ValueError('Sensitive data too short')

        # Log successful validation without the actual data
        logger.info(f"Sensitive data validated successfully: length {len(v)}")
        return v
```

## Error Localization

### Multi-language Error Messages
```python
from typing import Dict, Any

class LocalizedErrorsModel(BaseModel):
    name: str
    email: str

    def translate_error(self, error: dict, locale: str = 'en') -> dict:
        """Translate error messages to different languages"""
        translations = {
            'en': {
                'string_too_short': 'String is too short',
                'value_error': 'Invalid value provided',
                'field_required': 'This field is required'
            },
            'es': {
                'string_too_short': 'La cadena es demasiado corta',
                'value_error': 'Valor inválido proporcionado',
                'field_required': 'Este campo es obligatorio'
            }
        }

        trans_map = translations.get(locale, translations['en'])
        error_type = error['type']

        translated_msg = trans_map.get(error_type, error['msg'])
        error['msg'] = translated_msg

        return error

    def localized_errors(self, locale: str = 'en') -> list[dict]:
        """Get errors with localized messages"""
        try:
            self.model_validate(self.model_dump())
            return []
        except ValidationError as e:
            return [self.translate_error(err, locale) for err in e.errors()]
```

## Error Testing

### Testing Error Cases
```python
import pytest

def test_custom_error_messages():
    """Test that custom error messages are properly formatted"""
    with pytest.raises(ValidationError) as exc_info:
        Product(name="Test", price=-10, category="electronics")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert 'Price must be positive' in error['msg']
    assert error['ctx']['price'] == -10

def test_error_formatting():
    """Test error formatting function"""
    with pytest.raises(ValidationError) as exc_info:
        CustomErrorModel(value=150)

    formatted = format_validation_errors(
        exc_info.value,
        custom_messages={'out_of_range': 'Value out of range [0, 100]'}
    )

    assert len(formatted) == 1
    assert formatted[0]['message'] == 'Value out of range [0, 100]'

def test_api_error_handling():
    """Test API error response format"""
    with pytest.raises(ValidationError) as exc_info:
        Product(name="Test", price=-10, category="electronics")

    formatted_errors = format_validation_errors(exc_info.value)
    error = formatted_errors[0]

    # Check that the error has the expected structure
    assert 'field' in error
    assert 'message' in error
    assert 'type' in error
    assert 'input' in error
    assert 'path' in error
```

## Error Performance Considerations

### Efficient Error Handling
```python
from functools import lru_cache

class EfficientErrorModel(BaseModel):
    complex_field: str

    @field_validator('complex_field')
    @classmethod
    def validate_complex_field(cls, v: str) -> str:
        # Use early returns to avoid expensive validation when possible
        if not v:
            raise ValueError('Field cannot be empty')

        if len(v) > 10000:  # Avoid expensive validation on huge inputs
            raise ValueError('Field too large')

        # Perform expensive validation only on reasonable inputs
        if not cls._expensive_validation(v):
            raise ValueError('Complex validation failed')

        return v

    @staticmethod
    @lru_cache(maxsize=1000)
    def _expensive_validation(value: str) -> bool:
        """Cached expensive validation logic"""
        # Complex validation that benefits from caching
        return len(set(value)) > 5  # Example: must have more than 5 unique characters
```

These error handling patterns ensure robust, informative, and user-friendly error reporting in your Pydantic models.