"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestSignup:
    """Test cases for signup endpoint."""

    async def test_signup_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["name"] == "New User"
        assert "id" in data["user"]

    async def test_signup_duplicate_email(self, client: AsyncClient, test_user: dict):
        """Test signup with existing email fails."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": test_user["email"],
                "password": "anotherpassword123",
                "name": "Another User",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_signup_invalid_email(self, client: AsyncClient):
        """Test signup with invalid email format fails."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "securepassword123",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    async def test_signup_short_password(self, client: AsyncClient):
        """Test signup with short password fails."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short",
                "name": "Test User",
            },
        )
        assert response.status_code == 422

    async def test_signup_missing_fields(self, client: AsyncClient):
        """Test signup with missing required fields fails."""
        response = await client.post(
            "/api/auth/signup",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422


class TestSignin:
    """Test cases for signin endpoint."""

    async def test_signin_success(self, client: AsyncClient, test_user: dict):
        """Test successful login."""
        response = await client.post(
            "/api/auth/signin",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user["email"]

    async def test_signin_wrong_password(self, client: AsyncClient, test_user: dict):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/auth/signin",
            json={
                "email": test_user["email"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_signin_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email fails."""
        response = await client.post(
            "/api/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword123",
            },
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_signin_missing_fields(self, client: AsyncClient):
        """Test login with missing fields fails."""
        response = await client.post(
            "/api/auth/signin",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422


class TestSignout:
    """Test cases for signout endpoint."""

    async def test_signout_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful logout."""
        response = await client.post(
            "/api/auth/signout",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully signed out"

    async def test_signout_without_auth(self, client: AsyncClient):
        """Test logout without authentication fails."""
        response = await client.post("/api/auth/signout")
        assert response.status_code == 401


class TestAuthenticatedUser:
    """Test cases for authenticated user endpoint."""

    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict, test_user: dict):
        """Test getting current authenticated user."""
        response = await client.get(
            "/api/auth/me",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert "id" in data

    async def test_get_current_user_without_auth(self, client: AsyncClient):
        """Test getting current user without authentication fails."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token fails."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401
