# SQLModel Patterns Guide

This guide covers common patterns and best practices for using SQLModel in FastAPI applications.

## Model Definition Patterns

### Basic Model
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)
```

### Model with Relationships
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    headquarters: str

    heroes: List["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    team: Optional[Team] = Relationship(back_populates="heroes")
```

## CRUD Operation Patterns

### Create Pattern
```python
def create_item(item: ItemCreate, session: Session):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
```

### Read All Pattern
```python
def read_items(session: Session, offset: int = 0, limit: int = 100):
    items = session.exec(
        select(Item)
        .offset(offset)
        .limit(limit)
    ).all()
    return items
```

### Read Single Pattern
```python
def read_item_by_id(item_id: int, session: Session):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### Update Pattern
```python
def update_item(item_id: int, item_update: ItemUpdate, session: Session):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item
```

### Delete Pattern
```python
def delete_item(item_id: int, session: Session):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    session.delete(item)
    session.commit()
    return {"message": "Item deleted successfully"}
```

## Validation Patterns

### Custom Validators
```python
from pydantic import validator

class Item(SQLModel, table=True):
    name: str
    price: float

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

### Field Constraints
```python
from sqlmodel import Field
from typing import Optional

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    tax: Optional[float] = Field(default=None, gt=0)
```

## Session Management Patterns

### Session Dependency
```python
from sqlmodel import Session, create_engine
from contextlib import contextmanager

engine = create_engine("sqlite:///database.db")

def get_session():
    with Session(engine) as session:
        yield session
```

### Transaction Management
```python
def create_item_with_transaction(item: ItemCreate, session: Session):
    try:
        db_item = Item.model_validate(item)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
    except Exception as e:
        session.rollback()
        raise e
```

## Query Optimization Patterns

### Joins
```python
from sqlmodel import select

def get_items_with_details(session: Session):
    statement = select(Item).join(Category)
    items = session.exec(statement).all()
    return items
```

### Advanced Filtering
```python
def get_filtered_items(
    session: Session,
    name_contains: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    statement = select(Item)

    if name_contains:
        statement = statement.where(Item.name.contains(name_contains))
    if min_price is not None:
        statement = statement.where(Item.price >= min_price)
    if max_price is not None:
        statement = statement.where(Item.price <= max_price)

    items = session.exec(statement).all()
    return items
```