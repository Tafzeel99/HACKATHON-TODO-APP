---
name: fixture-creator
description: |
  Generate test data fixtures and database seeders. Use when users need sample data for testing,
  Postman collections, or curl commands for testing REST endpoints.
---

# Fixture Creator

Generate test data fixtures and database seeders.

## When to Use
- User asks for "test data", "fixtures", or "seed data"
- User needs sample data for testing
- User wants to populate test database

## Procedure
1. **Define models**: Identify entities (users, posts, orders)
2. **Create factory**: Generate random realistic data
3. **Build fixtures**: Predefined test scenarios
4. **Seed database**: Insert data for testing
5. **Cleanup**: Teardown after tests

## Pytest Fixtures

### Basic Fixtures
```python
# conftest.py
import pytest
from datetime import datetime, timedelta
from app.models import User, Post, Comment
from app.database import SessionLocal

@pytest.fixture
def db_session():
    """Database session for tests"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def user(db_session):
    """Single test user"""
    user = User(
        email="test@example.com",
        name="Test User",
        is_active=True,
        created_at=datetime.utcnow()
    )
    user.set_password("Pass123!")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    """Admin user fixture"""
    admin = User(
        email="admin@example.com",
        name="Admin User",
        is_active=True,
        is_admin=True
    )
    admin.set_password("AdminPass123!")
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def users(db_session):
    """Multiple test users"""
    users = []
    for i in range(5):
        user = User(
            email=f"user{i}@example.com",
            name=f"User {i}",
            is_active=True
        )
        user.set_password("Pass123!")
        users.append(user)

    db_session.add_all(users)
    db_session.commit()
    return users

@pytest.fixture
def post(db_session, user):
    """Single post fixture"""
    post = Post(
        title="Test Post",
        content="This is test content",
        author_id=user.id,
        published=True,
        created_at=datetime.utcnow()
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post

@pytest.fixture
def posts(db_session, user):
    """Multiple posts"""
    posts = []
    for i in range(10):
        post = Post(
            title=f"Post {i}",
            content=f"Content {i}",
            author_id=user.id,
            published=i % 2 == 0,
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        posts.append(post)

    db_session.add_all(posts)
    db_session.commit()
    return posts
```

### Factory Pattern
```python
# factories.py
from datetime import datetime, timedelta
import random
from faker import Faker
from app.models import User, Post, Comment, Order

fake = Faker()

class UserFactory:
    """Factory for creating users"""

    @staticmethod
    def create(**kwargs):
        defaults = {
            "email": fake.email(),
            "name": fake.name(),
            "bio": fake.text(max_nb_chars=200),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        defaults.update(kwargs)

        user = User(**defaults)
        if "password" not in kwargs:
            user.set_password("DefaultPass123!")
        return user

    @staticmethod
    def create_batch(count=10, **kwargs):
        return [UserFactory.create(**kwargs) for _ in range(count)]

class PostFactory:
    """Factory for creating posts"""

    @staticmethod
    def create(author=None, **kwargs):
        defaults = {
            "title": fake.sentence(),
            "content": fake.text(max_nb_chars=1000),
            "published": random.choice([True, False]),
            "views": random.randint(0, 1000),
            "created_at": fake.date_time_between(start_date="-30d")
        }

        if author:
            defaults["author_id"] = author.id

        defaults.update(kwargs)
        return Post(**defaults)

    @staticmethod
    def create_batch(count=10, author=None, **kwargs):
        return [PostFactory.create(author, **kwargs) for _ in range(count)]

class CommentFactory:
    """Factory for creating comments"""

    @staticmethod
    def create(post=None, author=None, **kwargs):
        defaults = {
            "content": fake.text(max_nb_chars=200),
            "created_at": fake.date_time_between(start_date="-7d")
        }

        if post:
            defaults["post_id"] = post.id
        if author:
            defaults["author_id"] = author.id

        defaults.update(kwargs)
        return Comment(**defaults)

# Usage in tests
@pytest.fixture
def random_users(db_session):
    users = UserFactory.create_batch(10)
    db_session.add_all(users)
    db_session.commit()
    return users

@pytest.fixture
def blog_with_comments(db_session):
    author = UserFactory.create(name="Blog Author")
    post = PostFactory.create(author=author, published=True)
    comments = [
        CommentFactory.create(post=post, author=author)
        for _ in range(5)
    ]

    db_session.add(author)
    db_session.add(post)
    db_session.add_all(comments)
    db_session.commit()

    return {"author": author, "post": post, "comments": comments}
```

### Scenario Fixtures
```python
# test_fixtures.py

@pytest.fixture
def complete_blog_scenario(db_session):
    """Complete blog with authors, posts, comments"""
    # Create 3 authors
    authors = []
    for i in range(3):
        author = UserFactory.create(name=f"Author {i}")
        authors.append(author)

    # Each author creates 3 posts
    posts = []
    for author in authors:
        for j in range(3):
            post = PostFactory.create(
                author=author,
                published=True,
                title=f"Post by {author.name} #{j}"
            )
            posts.append(post)

    # Add comments to each post
    commenters = UserFactory.create_batch(5)
    for post in posts:
        for commenter in random.sample(commenters, 3):
            comment = CommentFactory.create(
                post=post,
                author=commenter
            )

    db_session.add_all(authors + posts + commenters)
    db_session.commit()

    return {
        "authors": authors,
        "posts": posts,
        "commenters": commenters
    }

@pytest.fixture
def ecommerce_scenario(db_session):
    """E-commerce with products, orders, customers"""
    # Customers
    customers = UserFactory.create_batch(10)

    # Products
    products = []
    for i in range(20):
        product = Product(
            name=fake.word(),
            price=round(random.uniform(10, 1000), 2),
            stock=random.randint(0, 100),
            category=random.choice(["Electronics", "Books", "Clothing"])
        )
        products.append(product)

    # Orders
    orders = []
    for customer in customers:
        for _ in range(random.randint(1, 5)):
            order = Order(
                customer_id=customer.id,
                total=0,
                status=random.choice(["pending", "shipped", "delivered"]),
                created_at=fake.date_time_between(start_date="-90d")
            )

            # Order items
            selected_products = random.sample(products, random.randint(1, 5))
            for product in selected_products:
                item = OrderItem(
                    order=order,
                    product=product,
                    quantity=random.randint(1, 3),
                    price=product.price
                )
                order.items.append(item)

            order.total = sum(item.price * item.quantity for item in order.items)
            orders.append(order)

    db_session.add_all(customers + products + orders)
    db_session.commit()

    return {
        "customers": customers,
        "products": products,
        "orders": orders
    }
```

## JSON Fixtures
```python
# fixtures/users.json
[
  {
    "email": "john@example.com",
    "name": "John Doe",
    "role": "admin",
    "is_active": true
  },
  {
    "email": "jane@example.com",
    "name": "Jane Smith",
    "role": "user",
    "is_active": true
  }
]

# Load JSON fixtures
import json
from pathlib import Path

@pytest.fixture
def json_users(db_session):
    """Load users from JSON file"""
    fixture_path = Path(__file__).parent / "fixtures" / "users.json"
    with open(fixture_path) as f:
        data = json.load(f)

    users = []
    for user_data in data:
        user = User(**user_data)
        user.set_password("DefaultPass123!")
        users.append(user)

    db_session.add_all(users)
    db_session.commit()
    return users
```

## Database Seeder
```python
# seed.py
from app.database import SessionLocal
from factories import UserFactory, PostFactory, CommentFactory

def seed_database():
    """Populate database with test data"""
    db = SessionLocal()

    try:
        # Create users
        print("Creating users...")
        users = UserFactory.create_batch(50)
        db.add_all(users)
        db.commit()

        # Create posts
        print("Creating posts...")
        posts = []
        for user in users[:20]:  # First 20 users create posts
            user_posts = PostFactory.create_batch(
                random.randint(1, 10),
                author=user
            )
            posts.extend(user_posts)

        db.add_all(posts)
        db.commit()

        # Create comments
        print("Creating comments...")
        comments = []
        for post in posts:
            commenters = random.sample(users, random.randint(0, 10))
            for commenter in commenters:
                comment = CommentFactory.create(
                    post=post,
                    author=commenter
                )
                comments.append(comment)

        db.add_all(comments)
        db.commit()

        print(f"✓ Created {len(users)} users")
        print(f"✓ Created {len(posts)} posts")
        print(f"✓ Created {len(comments)} comments")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
```

## Parametrized Fixtures
```python
@pytest.fixture(params=[
    {"role": "admin", "permissions": ["read", "write", "delete"]},
    {"role": "editor", "permissions": ["read", "write"]},
    {"role": "viewer", "permissions": ["read"]}
])
def user_with_role(request, db_session):
    """Test with different user roles"""
    user = UserFactory.create(
        role=request.param["role"],
        permissions=request.param["permissions"]
    )
    db_session.add(user)
    db_session.commit()
    return user

# This test runs 3 times, once for each param
def test_permissions(user_with_role):
    assert user_with_role.role in ["admin", "editor", "viewer"]
```

## Best Practices
1. **Use factories**: Generate realistic data with Faker
2. **Keep fixtures simple**: Focus on test requirements
3. **Use parametrized fixtures**: Test multiple scenarios efficiently
4. **Clean up after tests**: Ensure database isolation
5. **Organize by domain**: Group related fixtures together
6. **Document fixture dependencies**: Make relationships clear

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing models, database schema, testing framework |
| **Conversation** | User's specific entities, testing requirements, data needs |
| **Skill References** | Standard fixture patterns, factory patterns, pytest best practices |
| **User Guidelines** | Project-specific conventions, security requirements |