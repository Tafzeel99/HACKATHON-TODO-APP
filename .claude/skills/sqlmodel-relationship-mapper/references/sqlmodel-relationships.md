# SQLModel Relationship Configuration Patterns

Advanced patterns and best practices for configuring relationships in SQLModel.

## Basic Relationship Types

### One-to-Many Relationships
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Parent(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # One parent has many children
    children: List["Child"] = Relationship(back_populates="parent")

class Child(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    parent_id: int = Field(foreign_key="parent.id", index=True)
    name: str

    # Many children belong to one parent
    parent: Optional[Parent] = Relationship(back_populates="children")
```

### Many-to-One Relationships
```python
class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    category_id: int = Field(foreign_key="category.id", index=True)

    # Many products belong to one category
    category: Optional[Category] = Relationship(back_populates="products")
```

### One-to-One Relationships
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # One user has one profile
    profile: Optional["UserProfile"] = Relationship(back_populates="user")

class UserProfile(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    bio: str

    # One profile belongs to one user
    user: Optional[User] = Relationship(back_populates="profile")
```

## Advanced Relationship Configurations

### Relationship with Custom Join Conditions
```python
from sqlalchemy import and_

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # Custom join condition
    active_tasks: List["Task"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "primaryjoin": "and_(User.id==Task.user_id, Task.status=='active')"
        }
    )

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    status: str = Field(default="active")

    user: Optional[User] = Relationship(back_populates="active_tasks")
```

### Polymorphic Relationships
```python
from sqlalchemy.ext.declarative import declared_attr

class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    # Polymorphic association
    commentable_type: str
    commentable_id: int

    @declared_attr
    def commentable(cls):
        return Relationship(
            back_populates="comments",
            sa_relationship_kwargs={
                "primaryjoin": "and_("
                "Comment.commentable_id==foreign(cls.id), "
                "Comment.commentable_type==cls.__tablename__"
                ")"
            }
        )

class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str

    comments: List[Comment] = Relationship(back_populates="commentable")

class Article(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    headline: str

    comments: List[Comment] = Relationship(back_populates="commentable")
```

## Many-to-Many Relationships

### Standard Many-to-Many with Junction Table
```python
# Junction table
class StudentCourse(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)

class Student(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    courses: List["Course"] = Relationship(
        back_populates="students",
        link_model=StudentCourse
    )

class Course(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    students: List[Student] = Relationship(
        back_populates="courses",
        link_model=StudentCourse
    )
```

### Many-to-Many with Additional Data in Junction Table
```python
from datetime import datetime

class Enrollment(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    grade: Optional[str] = None

class Student(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    enrollments: List["Enrollment"] = Relationship(back_populates="student")
    courses: List["Course"] = Relationship(
        back_populates="students",
        link_model=Enrollment
    )

class Course(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    enrollments: List[Enrollment] = Relationship(back_populates="course")
    students: List[Student] = Relationship(
        back_populates="courses",
        link_model=Enrollment
    )
```

## Self-Referential Relationships

### Hierarchical Tree Structure
```python
class Node(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(foreign_key="node.id", index=True)

    # Children nodes
    children: List["Node"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "remote_side": "Node.id"
        }
    )

    # Parent node
    parent: Optional["Node"] = Relationship(back_populates="children")
```

### Adjacency List with Depth Tracking
```python
class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(foreign_key="category.id", index=True)
    depth: int = Field(default=0)

    children: List["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "remote_side": "Category.id"
        }
    )
    parent: Optional["Category"] = Relationship(back_populates="children")
```

## Relationship Loading Strategies

### Eager Loading Options
```python
from sqlalchemy.orm import selectinload, joinedload, lazyload

# SelectIN loading (separate query with IN clause)
def get_user_with_tasks_selectin(user_id: int, session):
    statement = (
        select(User)
        .options(selectinload(User.tasks))
        .where(User.id == user_id)
    )
    return session.exec(statement).first()

# Joined loading (single query with JOIN)
def get_user_with_tasks_joined(user_id: int, session):
    statement = (
        select(User)
        .options(joinedload(User.tasks))
        .where(User.id == user_id)
    )
    return session.exec(statement).first()

# Lazy loading (default - relationships loaded on access)
def get_user_lazy_loaded(user_id: int, session):
    user = session.get(User, user_id)
    # Tasks loaded when user.tasks is accessed
    return user
```

### Conditional Loading
```python
from sqlalchemy.orm import raiseload

# Prevent accidental loading (to catch N+1 queries)
def get_user_without_tasks(user_id: int, session):
    statement = (
        select(User)
        .options(raiseload(User.tasks))
        .where(User.id == user_id)
    )
    return session.exec(statement).first()
```

## Relationship Constraints and Validation

### Cascading Operations
```python
class Author(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # Cascade operations
    books: List["Book"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",  # Delete books when author is deleted
            "passive_deletes": True
        }
    )

class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(foreign_key="author.id", ondelete="CASCADE")

    author: Optional[Author] = Relationship(back_populates="books")
```

### Relationship Validation
```python
from pydantic import model_validator

class Team(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    players: List["Player"] = Relationship(back_populates="team")

class Player(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    team_id: int = Field(foreign_key="team.id", index=True)
    team: Optional[Team] = Relationship(back_populates="players")

    @model_validator(mode='after')
    def validate_team_size(self):
        # Note: This validation would need to happen at the database level
        # or in a separate validation function since we can't access the team's
        # current player count here
        return self
```

## Performance Considerations

### Avoiding N+1 Query Problems
```python
# Problem: N+1 query
def get_users_with_tasks_bad(session):
    users = session.exec(select(User)).all()
    for user in users:
        print(user.tasks)  # This causes N additional queries

# Solution: Use eager loading
def get_users_with_tasks_good(session):
    users = session.exec(
        select(User).options(selectinload(User.tasks))
    ).all()
    for user in users:
        print(user.tasks)  # No additional queries
```

### Batch Loading for Complex Relationships
```python
from sqlalchemy.orm import selectinload

def get_users_with_tasks_and_categories(session):
    statement = (
        select(User)
        .options(
            selectinload(User.tasks)
            .selectinload(Task.category)
        )
    )
    return session.exec(statement).all()
```

## Multi-Tenant Relationship Patterns

### Tenant-Isolated Relationships
```python
class TenantScopedModel(SQLModel, table=True):
    __abstract__ = True  # Base class, not a table

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Foreign key to user

class Project(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str

    tasks: List["Task"] = Relationship(back_populates="project")

class Task(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    title: str

    project: Optional[Project] = Relationship(back_populates="tasks")
```