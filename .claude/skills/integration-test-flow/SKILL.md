---
name: integration-test-flow
description: |
  Create end-to-end user journey tests that span multiple endpoints. Use when users need full workflow testing.
---

# Integration Test Flow

Create end-to-end user journey tests that span multiple endpoints.

## When to Use
- User asks for "end-to-end tests" or "integration tests"
- User needs to test complete user journeys
- User wants multi-step workflow validation

## Procedure
1. **Define journey**: Map user workflow steps
2. **Setup state**: Create necessary test data
3. **Execute flow**: Call multiple endpoints in sequence
4. **Maintain context**: Pass tokens, IDs between steps
5. **Verify outcome**: Check final state matches expected

## User Journey Tests

### User Registration Flow
```python
# tests/integration/test_user_journey.py
import pytest
from fastapi.testclient import TestClient

class TestUserRegistrationJourney:
    """Complete user registration and setup flow"""

    def test_new_user_onboarding(self, client: TestClient, db_session):
        """Test: Register → Verify Email → Complete Profile → First Action"""

        # Step 1: Register new user
        register_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User"
        }
        response = client.post("/api/register", json=register_data)
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Step 2: Login
        login_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Get profile (should be incomplete)
        response = client.get("/api/profile", headers=headers)
        assert response.status_code == 200
        assert response.json()["profile_complete"] is False

        # Step 4: Complete profile
        profile_data = {
            "bio": "Software developer",
            "location": "San Francisco",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        response = client.put("/api/profile", json=profile_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["profile_complete"] is True

        # Step 5: Create first post
        post_data = {
            "title": "My First Post",
            "content": "Hello World!"
        }
        response = client.post("/api/posts", json=post_data, headers=headers)
        assert response.status_code == 201
        post_id = response.json()["id"]

        # Step 6: Verify post appears in user's feed
        response = client.get("/api/posts", headers=headers)
        assert response.status_code == 200
        posts = response.json()
        assert any(p["id"] == post_id for p in posts)
```

### E-Commerce Purchase Flow
```python
class TestPurchaseJourney:
    """Complete shopping and checkout flow"""

    def test_complete_purchase_flow(self, client, db_session):
        """Test: Browse → Add to Cart → Checkout → Payment → Confirmation"""

        # Setup: Login
        token = self._login(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Browse products
        response = client.get("/api/products?category=electronics")
        assert response.status_code == 200
        products = response.json()
        product_id = products[0]["id"]

        # Step 2: Get product details
        response = client.get(f"/api/products/{product_id}")
        assert response.status_code == 200
        product = response.json()

        # Step 3: Add to cart
        cart_item = {
            "product_id": product_id,
            "quantity": 2
        }
        response = client.post("/api/cart", json=cart_item, headers=headers)
        assert response.status_code == 201

        # Step 4: View cart
        response = client.get("/api/cart", headers=headers)
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) == 1
        assert cart["total"] == product["price"] * 2

        # Step 5: Add shipping address
        address = {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102"
        }
        response = client.post("/api/addresses", json=address, headers=headers)
        assert response.status_code == 201
        address_id = response.json()["id"]

        # Step 6: Create order
        order_data = {
            "shipping_address_id": address_id,
            "payment_method": "credit_card"
        }
        response = client.post("/api/orders", json=order_data, headers=headers)
        assert response.status_code == 201
        order = response.json()
        order_id = order["id"]
        assert order["status"] == "pending"

        # Step 7: Process payment
        payment_data = {
            "order_id": order_id,
            "card_number": "4242424242424242",
            "exp_month": "12",
            "exp_year": "2025",
            "cvc": "123"
        }
        response = client.post("/api/payments", json=payment_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Step 8: Verify order status updated
        response = client.get(f"/api/orders/{order_id}", headers=headers)
        assert response.status_code == 200
        order = response.json()
        assert order["status"] == "confirmed"

        # Step 9: Verify cart is cleared
        response = client.get("/api/cart", headers=headers)
        cart = response.json()
        assert len(cart["items"]) == 0

        # Step 10: Get order confirmation
        response = client.get(f"/api/orders/{order_id}/confirmation", headers=headers)
        assert response.status_code == 200
        confirmation = response.json()
        assert "order_number" in confirmation
        assert "tracking_number" in confirmation

    def _login(self, client):
        """Helper to login and get token"""
        response = client.post("/api/login", json={
            "email": "test@example.com",
            "password": "Pass123!"
        })
        return response.json()["token"]
```

### Content Management Flow
```python
class TestBlogWorkflow:
    """Blog post creation to publication workflow"""

    def test_blog_post_lifecycle(self, client, db_session):
        """Test: Draft → Edit → Review → Publish → Update → Archive"""

        # Login as author
        author_token = self._login(client, "author@example.com")
        author_headers = {"Authorization": f"Bearer {author_token}"}

        # Step 1: Create draft post
        draft = {
            "title": "My Blog Post",
            "content": "Initial content",
            "status": "draft"
        }
        response = client.post("/api/posts", json=draft, headers=author_headers)
        assert response.status_code == 201
        post_id = response.json()["id"]

        # Step 2: Update draft multiple times
        for i in range(3):
            update = {
                "content": f"Updated content version {i+1}"
            }
            response = client.patch(
                f"/api/posts/{post_id}",
                json=update,
                headers=author_headers
            )
            assert response.status_code == 200

        # Step 3: Submit for review
        response = client.post(
            f"/api/posts/{post_id}/submit",
            headers=author_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "pending_review"

        # Step 4: Login as editor
        editor_token = self._login(client, "editor@example.com")
        editor_headers = {"Authorization": f"Bearer {editor_token}"}

        # Step 5: Editor reviews and requests changes
        review = {
            "action": "request_changes",
            "comments": "Please add more details"
        }
        response = client.post(
            f"/api/posts/{post_id}/review",
            json=review,
            headers=editor_headers
        )
        assert response.status_code == 200

        # Step 6: Author makes changes and resubmits
        update = {
            "content": "Updated with more details"
        }
        response = client.patch(
            f"/api/posts/{post_id}",
            json=update,
            headers=author_headers
        )
        response = client.post(
            f"/api/posts/{post_id}/submit",
            headers=author_headers
        )

        # Step 7: Editor approves
        review = {
            "action": "approve"
        }
        response = client.post(
            f"/api/posts/{post_id}/review",
            json=review,
            headers=editor_headers
        )
        assert response.status_code == 200

        # Step 8: Publish post
        response = client.post(
            f"/api/posts/{post_id}/publish",
            headers=author_headers
        )
        assert response.status_code == 200
        post = response.json()
        assert post["status"] == "published"
        assert post["published_at"] is not None

        # Step 9: Verify post appears publicly
        response = client.get("/api/posts/public")
        public_posts = response.json()
        assert any(p["id"] == post_id for p in public_posts)

        # Step 10: Update published post
        update = {
            "content": "Updated published content"
        }
        response = client.patch(
            f"/api/posts/{post_id}",
            json=update,
            headers=author_headers
        )
        assert response.status_code == 200

        # Step 11: Archive post
        response = client.post(
            f"/api/posts/{post_id}/archive",
            headers=author_headers
        )
        assert response.status_code == 200

        # Step 12: Verify not in public feed
        response = client.get("/api/posts/public")
        public_posts = response.json()
        assert not any(p["id"] == post_id for p in public_posts)
```

### Multi-User Collaboration
```python
class TestCollaborationFlow:
    """Test multi-user interaction workflows"""

    def test_team_project_workflow(self, client, db_session):
        """Test: Create Project → Invite → Collaborate → Complete"""

        # Owner creates project
        owner_token = self._login(client, "owner@example.com")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        project = {
            "name": "New Project",
            "description": "Team project"
        }
        response = client.post("/api/projects", json=project, headers=owner_headers)
        project_id = response.json()["id"]

        # Owner invites team member
        invite = {
            "email": "member@example.com",
            "role": "contributor"
        }
        response = client.post(
            f"/api/projects/{project_id}/invites",
            json=invite,
            headers=owner_headers
        )
        invite_token = response.json()["token"]

        # Member accepts invite
        member_token = self._login(client, "member@example.com")
        member_headers = {"Authorization": f"Bearer {member_token}"}

        response = client.post(
            f"/api/invites/{invite_token}/accept",
            headers=member_headers
        )
        assert response.status_code == 200

        # Member creates task
        task = {
            "title": "Implement feature",
            "description": "Add new feature"
        }
        response = client.post(
            f"/api/projects/{project_id}/tasks",
            json=task,
            headers=member_headers
        )
        task_id = response.json()["id"]

        # Owner assigns task
        response = client.patch(
            f"/api/tasks/{task_id}",
            json={"assigned_to": "member@example.com"},
            headers=owner_headers
        )

        # Member completes task
        response = client.post(
            f"/api/tasks/{task_id}/complete",
            headers=member_headers
        )

        # Owner reviews and approves
        response = client.post(
            f"/api/tasks/{task_id}/approve",
            headers=owner_headers
        )

        # Verify project progress
        response = client.get(
            f"/api/projects/{project_id}/stats",
            headers=owner_headers
        )
        stats = response.json()
        assert stats["completed_tasks"] == 1
```

## Test Fixtures for Flows

```python
# conftest.py
@pytest.fixture
def authenticated_client(client, db_session):
    """Client with authentication"""
    # Create and login user
    user = UserFactory.create(email="test@example.com")
    user.set_password("Pass123!")
    db_session.add(user)
    db_session.commit()

    response = client.post("/api/login", json={
        "email": "test@example.com",
        "password": "Pass123!"
    })
    token = response.json()["token"]

    # Add auth header to client
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture
def multi_user_setup(client, db_session):
    """Setup multiple users with different roles"""
    users = {
        "admin": UserFactory.create(email="admin@example.com", role="admin"),
        "user": UserFactory.create(email="user@example.com", role="user"),
        "moderator": UserFactory.create(email="mod@example.com", role="moderator")
    }

    for user in users.values():
        user.set_password("Pass123!")
        db_session.add(user)
    db_session.commit()

    # Login all users
    tokens = {}
    for role, user in users.items():
        response = client.post("/api/login", json={
            "email": user.email,
            "password": "Pass123!"
        })
        tokens[role] = response.json()["token"]

    return {
        "users": users,
        "tokens": tokens
    }
```

## Best Practices
1. **State management**: Maintain session context across requests
2. **Data isolation**: Clean up test data after each test
3. **Realistic flows**: Mirror actual user behavior
4. **Error handling**: Test failure scenarios in workflows
5. **Parallel execution**: Design tests to run independently
6. **Performance**: Measure execution time for slow tests
7. **Documentation**: Comment each step in the workflow

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing API endpoints, authentication methods, data models |
| **Conversation** | User's specific workflows, business requirements |
| **Skill References** | Standard integration testing patterns, FastAPI testing best practices |
| **User Guidelines** | Project-specific conventions, testing requirements |