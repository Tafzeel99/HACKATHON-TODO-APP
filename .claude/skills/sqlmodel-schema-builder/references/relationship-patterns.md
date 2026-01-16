# SQLModel Relationship Patterns Guide

This guide covers all relationship patterns and configurations in SQLModel.

## One-to-Many / Many-to-One Relationships

### Basic One-to-Many
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str

    # One-to-many: One user has many tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    user_id: str = Field(foreign_key="user.id", index=True)

    # Many-to-one: Many tasks belong to one user
    user: User = Relationship(back_populates="tasks")
```

### Cascade Operations
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str

    # Cascade delete: When user is deleted, all tasks are deleted
    tasks: List["Task"] = Relationship(
        back_populates="user",
        cascade_delete=True  # Note: This is SQLAlchemy's cascade option
    )

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    user_id: str = Field(foreign_key="user.id", ondelete="CASCADE")  # DB-level cascade
    user: User = Relationship(back_populates="tasks")
```

### Foreign Key Restrictions
```python
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", ondelete="RESTRICT")  # Prevent deletion if orders exist
    total_amount: float
    user: User = Relationship(back_populates="orders")
```

## Many-to-Many Relationships

### Using Association Table
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List

# Association table for many-to-many relationship
class UserGroup(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    group_id: int = Field(foreign_key="group.id", primary_key=True)

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    groups: List["Group"] = Relationship(
        back_populates="users",
        link_model=UserGroup
    )

class Group(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    users: List[User] = Relationship(
        back_populates="groups",
        link_model=UserGroup
    )
```

### Association Table with Additional Fields
```python
from datetime import datetime

class UserGroupMembership(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    group_id: int = Field(foreign_key="group.id", primary_key=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    role: str = Field(default="member")  # Additional field in association table

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    memberships: List["UserGroupMembership"] = Relationship(back_populates="user")
    groups: List["Group"] = Relationship(
        back_populates="users",
        link_model=UserGroupMembership
    )

class Group(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    memberships: List[UserGroupMembership] = Relationship(back_populates="group")
    users: List[User] = Relationship(
        back_populates="groups",
        link_model=UserGroupMembership
    )
```

## One-to-One Relationships

### Basic One-to-One
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    profile: "UserProfile" = Relationship(back_populates="user")

class UserProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", unique=True)  # Unique to enforce one-to-one
    bio: str | None = None
    avatar_url: str | None = None
    user: User = Relationship(back_populates="profile")
```

### Self-Referencing Relationships
```python
class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    parent_id: int | None = Field(default=None, foreign_key="category.id")

    # Self-referencing relationships
    parent: "Category" = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Category.id"
        },
        back_populates="children"
    )
    children: List["Category"] = Relationship(back_populates="parent")
```

## Advanced Relationship Configurations

### Lazy Loading Options
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    # Different loading strategies
    posts: List["Post"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={
            "lazy": "select"  # Default: load when accessed
        }
    )
    profile: "Profile" = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "joined"  # Load immediately with parent
        }
    )
```

### Relationship with Conditions
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str

    # Only active posts
    active_posts: List["Post"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={
            "primaryjoin": "and_(User.id==Post.author_id, Post.is_active==True)"
        }
    )

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: str = Field(foreign_key="user.id")
    is_active: bool = Field(default=True)
    author: User = Relationship(back_populates="active_posts")
```

## Working with Relationships

### Creating Related Objects
```python
# Creating objects with relationships
def create_user_with_profile(session: Session, email: str, bio: str):
    user = User(email=email)
    profile = UserProfile(bio=bio)
    user.profile = profile  # Set the relationship

    session.add(user)
    session.commit()
    return user

# Alternative: Set foreign key directly
def create_user_with_profile_alt(session: Session, email: str, bio: str):
    user = User(email=email)
    session.add(user)
    session.flush()  # Get the user ID

    profile = UserProfile(user_id=user.id, bio=bio)
    session.add(profile)
    session.commit()
    return user
```

### Querying with Relationships
```python
from sqlmodel import select

# Query user with all tasks
def get_user_with_tasks(session: Session, user_id: str):
    statement = select(User).where(User.id == user_id).join(Task)
    user = session.exec(statement).first()
    return user

# Query with eager loading
def get_user_with_eager_tasks(session: Session, user_id: str):
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    # Access tasks (loaded lazily) - triggers additional query
    _ = user.tasks  # This will trigger a query to load tasks
    return user
```

### Relationship Validation
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str

    _tasks: List["Task"] = []

    @property
    def tasks(self) -> List["Task"]:
        """Custom property to add validation or processing"""
        return self._tasks

    def add_task(self, task: "Task"):
        """Custom method to add task with validation"""
        if task.user_id != self.id:
            raise ValueError("Task user_id does not match user id")
        self._tasks.append(task)
```

## Circular Import Solutions

### Using String Annotations
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    posts: List["Post"] = Relationship(back_populates="author")  # String reference

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: str = Field(foreign_key="user.id")
    author: "User" = Relationship(back_populates="posts")  # String reference
```

### Forward References in Type Hints
```python
from __future__ import annotations  # At the top of the file

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    posts: List[Post] = Relationship(back_populates="author")  # No quotes needed

class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: str = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="posts")  # No quotes needed
```

## Relationship Best Practices

### Always Use Bidirectional Relationships
```python
# ✅ GOOD: Bidirectional
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tasks")

# ❌ AVOID: Unidirectional
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tasks: List["Task"] = Relationship()  # Missing back_populates

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    # Missing user relationship
```

### Proper Indexing for Performance
```python
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)  # Always index foreign keys
    product_id: int = Field(foreign_key="product.id", index=True)  # Always index foreign keys
```

### Choose Appropriate Loading Strategies
- Use `lazy="select"` (default) for relationships accessed infrequently
- Use `lazy="joined"` for relationships almost always needed
- Use `lazy="dynamic"` for large collections with custom queries