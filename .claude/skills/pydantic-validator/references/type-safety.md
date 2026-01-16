# Pydantic Type Safety Guide

This guide covers all type safety patterns and techniques in Pydantic for ensuring consistency between frontend TypeScript and backend Python.

## Type Hints and Generics

### Basic Type Safety
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from datetime import datetime

class User(BaseModel):
    # Basic types
    id: int
    name: str
    email: str
    is_active: bool

    # Optional types
    bio: Optional[str] = None
    age: Optional[int] = None

    # Union types
    contact: Union[str, int]  # Can be either string or integer

    # Literal types
    role: Literal['admin', 'user', 'moderator']

    # Complex types
    created_at: datetime
    tags: List[str]
```

### Generic Models
```python
from typing import Generic, TypeVar, List

T = TypeVar('T')

class ApiResponse(Generic[T], BaseModel):
    """Generic response wrapper that preserves type information"""
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    errors: List[str] = []

# Usage examples
user_response: ApiResponse[User] = ApiResponse(
    success=True,
    data=User(id=1, name="John", email="john@example.com", role="user")
)

users_response: ApiResponse[List[User]] = ApiResponse(
    success=True,
    data=[
        User(id=1, name="John", email="john@example.com", role="user"),
        User(id=2, name="Jane", email="jane@example.com", role="admin")
    ]
)
```

## Type Validation and Coercion

### Type Coercion Behavior
```python
class FlexibleTypes(BaseModel):
    # Pydantic will attempt to coerce compatible types
    id: int          # "123" -> 123
    name: str        # 123 -> "123"
    is_active: bool  # "true" -> True, 1 -> True, "yes" -> True
    score: float     # 10 -> 10.0, "10.5" -> 10.5

# This works due to type coercion
data = {
    'id': '123',           # string -> int
    'name': 456,           # int -> string
    'is_active': 'true',   # string -> bool
    'score': '95.5'        # string -> float
}
model = FlexibleTypes(**data)
print(model)  # All values properly coerced
```

### Strict Type Validation
```python
from pydantic import ConfigDict

class StrictTypes(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        strict=True  # Disables type coercion
    )

# This would raise a ValidationError in strict mode
try:
    StrictTypes(id='123', name=456)  # Won't coerce types
except Exception as e:
    print(f"Strict validation error: {e}")
```

## Type Consistency Between Frontend and Backend

### API Schema Generation
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Task description", max_length=1000)
    completed: bool = Field(default=False, description="Whether the task is completed")

class TaskResponse(TaskCreate):
    id: int = Field(..., description="Task ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")

# This schema can be used to generate TypeScript types
schema = TaskResponse.model_json_schema()
print(schema)  # JSON schema that matches TypeScript interface
```

### TypeScript Interface Generation Example
```typescript
// Generated from Pydantic model
interface TaskCreate {
  title: string;
  description?: string | null;
  completed: boolean;
}

interface TaskResponse extends TaskCreate {
  id: number;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

interface ApiResponse<T> {
  success: boolean;
  data?: T | null;
  message?: string | null;
  errors: string[];
}
```

## Advanced Type Safety

### Custom Type Annotations
```python
from typing_extensions import Annotated
from annotated_types import Gt, Lt, MinLen, MaxLen

# Define reusable type annotations
PositiveInt = Annotated[int, Gt(0)]
NonEmptyString = Annotated[str, MinLen(1)]
EmailString = Annotated[str, MinLen(5), str]  # Additional validation would be needed

class Product(BaseModel):
    id: PositiveInt
    name: NonEmptyString = Field(max_length=200)
    price: Annotated[float, Gt(0), Lt(10000)]
    description: Optional[NonEmptyString] = Field(None, max_length=1000)

# These types can be reused across multiple models
class OrderItem(BaseModel):
    product_id: PositiveInt
    quantity: PositiveInt
    unit_price: Annotated[float, Gt(0)]
```

### Discriminated Unions (Tagged Unions)
```python
from typing import Literal, Union
from pydantic import BaseModel, Field, Tag, Discriminator

class Cat(BaseModel):
    pet_type: Literal['cat']
    name: str
    color: str

class Dog(BaseModel):
    pet_type: Literal['dog']
    name: str
    breed: str

class Pet(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator='pet_type')

# This creates a discriminated union that maintains type safety
cat_pet = Pet(pet=Cat(pet_type='cat', name='Fluffy', color='white'))
dog_pet = Pet(pet=Dog(pet_type='dog', name='Buddy', breed='Golden Retriever'))
```

## Type Safety with Nested Models

### Nested Model Validation
```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class UserWithAddress(BaseModel):
    id: int
    name: str
    address: Address  # Nested model maintains type safety

# Validation happens at all levels
user = UserWithAddress(
    id=1,
    name="John Doe",
    address=Address(
        street="123 Main St",
        city="Anytown",
        country="USA",
        postal_code="12345"
    )
)
```

### List of Nested Models
```python
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    customer_id: int
    items: List[OrderItem]  # List maintains type safety
    total_amount: float

# Type safety is maintained even with complex nested structures
order = Order(
    id=1,
    customer_id=123,
    items=[
        OrderItem(product_id=1, quantity=2, price=19.99),
        OrderItem(product_id=2, quantity=1, price=29.99)
    ],
    total_amount=69.97
)
```

## Type Safety for API Responses

### Generic Response Models
```python
from typing import Generic, TypeVar, List, Optional, Union

T = TypeVar('T')
TData = TypeVar('TData')
TParams = TypeVar('TParams')

class SuccessResponse(Generic[T], BaseModel):
    """Generic success response with type safety"""
    success: Literal[True] = True
    data: T
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response structure"""
    success: Literal[False] = False
    message: str
    error_code: Optional[str] = None

class PaginatedResponse(Generic[T], BaseModel):
    """Paginated response with type safety"""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_more: bool

# Usage examples
user_response: SuccessResponse[User] = SuccessResponse(
    data=User(id=1, name="John", email="john@example.com", role="user")
)

users_page: PaginatedResponse[User] = PaginatedResponse(
    items=[User(id=1, name="John", email="john@example.com", role="user")],
    total=100,
    page=1,
    page_size=10,
    has_more=True
)
```

## Type Safety with Configurations

### Model Configuration for Type Safety
```python
from pydantic import ConfigDict, BaseModel

class ConfigurableModel(BaseModel):
    name: str
    value: int

    model_config = ConfigDict(
        # Prevent extra fields from being accepted
        extra='forbid',

        # Allow population by field name or alias
        populate_by_name=True,

        # Use strict type checking
        strict=False,  # Set to True for strict mode

        # Coerce dates from strings
        arbitrary_types_allowed=False,

        # Validate default values
        validate_default=True,

        # Validate assignment after initialization
        validate_assignment=True,

        # Use aliases in JSON
        json_by_alias=True,
    )
```

## Type Safety Testing

### Type Checking with mypy
```python
# Example of how mypy verifies type safety
from typing import cast

def process_user(user: User) -> str:
    return user.name.upper()

# mypy will catch type mismatches
user = User(id=1, name="John", email="john@example.com", role="user")
result: str = process_user(user)  # ✓ Correct type

# This would be caught by mypy:
# result: int = process_user(user)  # ✗ Type mismatch error
```

### Runtime Type Validation Tests
```python
import pytest
from pydantic import ValidationError

def test_type_coercion():
    """Test that type coercion works as expected"""
    # String to int coercion
    model = FlexibleTypes(id='123', name='test', is_active='true', score=95.5)
    assert model.id == 123
    assert model.is_active is True

def test_strict_types():
    """Test that strict types prevent coercion"""
    with pytest.raises(ValidationError):
        StrictTypes(id='123', name=456)  # Would fail in strict mode

def test_nested_validation():
    """Test that nested models validate properly"""
    # Valid nested structure
    user = UserWithAddress(
        id=1,
        name="John",
        address=Address(street="123 St", city="City", country="US", postal_code="12345")
    )
    assert user.address.city == "City"

    # Invalid nested structure should raise error
    with pytest.raises(ValidationError):
        UserWithAddress(
            id=1,
            name="John",
            address={}  # Missing required fields
        )
```

## Type Safety Best Practices

### 1. Use Specific Types
```python
# ❌ Avoid generic types when possible
class BadExample(BaseModel):
    data: dict  # Too generic
    items: list  # Too generic

# ✅ Use specific types
class GoodExample(BaseModel):
    user_data: Dict[str, Any]  # More specific
    items: List[OrderItem]     # Even better: specific model type
```

### 2. Leverage TypeVar for Generics
```python
# ✅ Properly typed generic functions
def create_response[T](data: T) -> SuccessResponse[T]:
    return SuccessResponse(data=data)

user_resp = create_response(user)  # Type safety maintained
```

### 3. Use Field for Documentation
```python
class WellDocumented(BaseModel):
    # Field provides both validation and documentation
    id: int = Field(..., description="Unique identifier for the resource")
    name: str = Field(..., min_length=1, max_length=100, description="Resource name")
```

### 4. Validate Assignment
```python
class SafeAssignment(BaseModel):
    name: str
    age: int

    model_config = ConfigDict(validate_assignment=True)

# This will validate the assignment at runtime
model = SafeAssignment(name="John", age=30)
# model.age = "thirty"  # Would raise ValidationError
```

These patterns ensure robust type safety and consistency between frontend and backend systems.