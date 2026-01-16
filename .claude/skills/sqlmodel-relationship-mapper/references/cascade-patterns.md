# Cascade Operation Patterns

Best practices and patterns for handling cascade operations in SQLModel relationships.

## Cascade Options Overview

### CASCADE
Automatically delete related records when the parent is deleted.

```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # When user is deleted, all posts are also deleted
    posts: List["Post"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )

class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    user: Optional[User] = Relationship(back_populates="posts")
```

### SET NULL
Set foreign key to NULL when parent is deleted.

```python
class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    category_id: Optional[int] = Field(
        foreign_key="category.id",
        ondelete="SET NULL",
        index=True
    )

    category: Optional[Category] = Relationship()
```

### RESTRICT
Prevent deletion of parent if related records exist.

```python
class Department(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

class Employee(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    department_id: int = Field(
        foreign_key="department.id",
        ondelete="RESTRICT"  # Prevent deleting department if employees exist
    )

    department: Optional[Department] = Relationship()
```

### NO ACTION
Default behavior - raise an error if related records exist.

```python
class Author(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author_id: int = Field(
        foreign_key="author.id",
        ondelete="NO ACTION"  # Same as RESTRICT in most databases
    )

    author: Optional[Author] = Relationship()
```

## Cascade Configuration Patterns

### All Cascade Options
```python
class Parent(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    children: List["Child"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",  # All operations cascade
            "passive_deletes": True  # Let database handle deletes
        }
    )

class Child(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    parent_id: int = Field(foreign_key="parent.id", ondelete="CASCADE")

    parent: Optional[Parent] = Relationship(back_populates="children")
```

### Specific Cascade Operations
```python
class Organization(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # Only cascade merges and saves, not deletes
    departments: List["Department"] = Relationship(
        back_populates="organization",
        sa_relationship_kwargs={
            "cascade": "save-update, merge, refresh-expire"  # Only these operations
        }
    )

class Department(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    org_id: int = Field(foreign_key="organization.id")

    organization: Optional[Organization] = Relationship(back_populates="departments")
```

## Common Cascade Scenarios

### Blog Post with Comments
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str

    posts: List["Post"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )

class Post(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    author: Optional[User] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )

class Comment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    post_id: int = Field(foreign_key="post.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", ondelete="SET NULL")

    post: Optional[Post] = Relationship(back_populates="comments")
    author: Optional[User] = Relationship()
```

### E-commerce with Orders and Items
```python
class Customer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

    orders: List["Order"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={
            "cascade": "save-update, merge"  # Only save/merge, not delete
        }
    )

class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_date: datetime = Field(default_factory=datetime.utcnow)
    customer_id: int = Field(foreign_key="customer.id", ondelete="CASCADE")

    customer: Optional[Customer] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )

class OrderItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    quantity: int
    price: float
    order_id: int = Field(foreign_key="order.id", ondelete="CASCADE")
    product_id: int = Field(foreign_key="product.id", ondelete="RESTRICT")

    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship()
```

## Multi-Tenant Cascade Patterns

### Tenant-Aware Cascades
```python
class TenantScopedModel(SQLModel, table=True):
    __abstract__ = True
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)

class Project(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str

    tasks: List["Task"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )

class Task(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE")
    title: str

    project: Optional[Project] = Relationship(back_populates="tasks")
```

## Performance Considerations

### Large Dataset Cascades
For large datasets, consider batch processing:

```python
def delete_user_with_posts_batch(user_id: int, session, batch_size: int = 1000):
    # Delete related records in batches to avoid locking issues
    while True:
        # Delete a batch of posts
        stmt = (
            delete(Post)
            .where(Post.user_id == user_id)
            .limit(batch_size)
        )
        result = session.exec(stmt)
        session.commit()

        if result.rowcount < batch_size:
            break  # No more posts to delete

    # Now safely delete the user
    user = session.get(User, user_id)
    session.delete(user)
    session.commit()
```

### Soft Delete Pattern
Instead of cascading physical deletes, consider soft deletes:

```python
class SoftDeleteMixin:
    deleted_at: Optional[datetime] = Field(default=None, index=True)

class User(SoftDeleteMixin, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    posts: List["Post"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={
            "cascade": "save-update, merge"  # Only cascade updates, not deletes
        }
    )

class Post(SoftDeleteMixin, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    user_id: int = Field(foreign_key="user.id")

    author: Optional[User] = Relationship(back_populates="posts")

# Custom delete function that cascades soft deletes
def soft_delete_user(user_id: int, session):
    # Soft delete the user
    user = session.get(User, user_id)
    user.deleted_at = datetime.utcnow()

    # Cascade soft delete to posts
    stmt = (
        update(Post)
        .where(Post.user_id == user_id)
        .values(deleted_at=datetime.utcnow())
    )
    session.exec(stmt)
    session.commit()
```

## Error Handling

### Handling Cascade Failures
```python
from sqlalchemy.exc import IntegrityError

def safe_delete_with_cascade(parent_id: int, session):
    try:
        parent = session.get(Parent, parent_id)
        session.delete(parent)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        # Handle specific cascade constraint violations
        if "foreign key constraint" in str(e):
            raise ValueError("Cannot delete parent: child records exist")
        raise
```

These patterns provide a comprehensive guide to implementing cascade operations in SQLModel relationships while considering performance, data integrity, and multi-tenant requirements.