"""Tests for task endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateTask:
    """Test cases for task creation endpoint."""

    async def test_create_task_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful task creation."""
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={
                "title": "Test Task",
                "description": "Test description",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test description"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_task_minimal(self, client: AsyncClient, auth_headers: dict):
        """Test task creation with only required fields."""
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Minimal Task"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["completed"] is False

    async def test_create_task_without_auth(self, client: AsyncClient):
        """Test task creation without authentication fails."""
        response = await client.post(
            "/api/tasks",
            json={"title": "Test Task"},
        )
        assert response.status_code == 401

    async def test_create_task_empty_title(self, client: AsyncClient, auth_headers: dict):
        """Test task creation with empty title fails."""
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": ""},
        )
        assert response.status_code == 422

    async def test_create_task_missing_title(self, client: AsyncClient, auth_headers: dict):
        """Test task creation without title fails."""
        response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"description": "Only description"},
        )
        assert response.status_code == 422


class TestListTasks:
    """Test cases for task listing endpoint."""

    async def test_list_tasks_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing tasks when none exist."""
        response = await client.get(
            "/api/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0

    async def test_list_tasks_with_data(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test listing tasks returns created tasks."""
        response = await client.get(
            "/api/tasks",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) >= 1
        assert data["total"] >= 1

        # Find the test task in the list
        task_ids = [t["id"] for t in data["tasks"]]
        assert test_task["id"] in task_ids

    async def test_list_tasks_without_auth(self, client: AsyncClient):
        """Test listing tasks without authentication fails."""
        response = await client.get("/api/tasks")
        assert response.status_code == 401

    async def test_list_tasks_filter_completed(self, client: AsyncClient, auth_headers: dict):
        """Test filtering tasks by completion status."""
        # Create a completed task
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Completed Task"},
        )

        # Filter for pending tasks
        response = await client.get(
            "/api/tasks?status=pending",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["completed"] is False

    async def test_list_tasks_sort_by_created(self, client: AsyncClient, auth_headers: dict):
        """Test sorting tasks by creation date."""
        # Create multiple tasks
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Task A"},
        )
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Task B"},
        )

        # Get tasks sorted by created_at descending (newest first)
        response = await client.get(
            "/api/tasks?sort=created&order=desc",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        if len(data["tasks"]) >= 2:
            # Verify descending order
            for i in range(len(data["tasks"]) - 1):
                assert data["tasks"][i]["created_at"] >= data["tasks"][i + 1]["created_at"]

    async def test_list_tasks_sort_by_title(self, client: AsyncClient, auth_headers: dict):
        """Test sorting tasks by title."""
        # Create multiple tasks with different titles
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Zebra Task"},
        )
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Apple Task"},
        )
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Mango Task"},
        )

        # Get tasks sorted by title ascending
        response = await client.get(
            "/api/tasks?sort=title&order=asc",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        if len(data["tasks"]) >= 3:
            titles = [task["title"] for task in data["tasks"]]
            # Should be in alphabetical order
            assert titles == sorted(titles)

    async def test_list_tasks_filter_completed_only(self, client: AsyncClient, auth_headers: dict):
        """Test filtering to show only completed tasks."""
        # Create one completed task and one pending task
        response1 = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Pending Task"},
        )
        response2 = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Completed Task"},
        )

        # Mark one task as completed
        task_id = response2.json()["id"]
        await client.patch(
            f"/api/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        # Get only completed tasks
        response = await client.get(
            "/api/tasks?status=completed",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify all returned tasks are completed
        for task in data["tasks"]:
            assert task["completed"] is True

    async def test_list_tasks_filter_pending_only(self, client: AsyncClient, auth_headers: dict):
        """Test filtering to show only pending tasks."""
        # Create one completed task and one pending task
        response1 = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Pending Task"},
        )
        task1_id = response1.json()["id"]

        response2 = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Another Pending Task"},
        )

        # Mark one task as completed
        await client.patch(
            f"/api/tasks/{task1_id}/complete",
            headers=auth_headers,
        )

        # Get only pending tasks
        response = await client.get(
            "/api/tasks?status=pending",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify all returned tasks are pending
        for task in data["tasks"]:
            assert task["completed"] is False

    async def test_list_tasks_combined_filter_and_sort(self, client: AsyncClient, auth_headers: dict):
        """Test combining filtering and sorting."""
        # Create multiple tasks with different statuses
        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Z Completed Task"},
        )
        z_task_id = (await client.get("/api/tasks", headers=auth_headers)).json()["tasks"][0]["id"]

        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "A Pending Task"},
        )

        await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "M Pending Task"},
        )

        # Mark the first task as completed
        await client.patch(
            f"/api/tasks/{z_task_id}/complete",
            headers=auth_headers,
        )

        # Get pending tasks sorted by title ascending
        response = await client.get(
            "/api/tasks?status=pending&sort=title&order=asc",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Should only have pending tasks, sorted by title
        if len(data["tasks"]) >= 2:
            titles = [task["title"] for task in data["tasks"]]
            assert titles == sorted(titles)
            for task in data["tasks"]:
                assert task["completed"] is False


class TestGetTask:
    """Test cases for getting a single task."""

    async def test_get_task_success(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test getting a task by ID."""
        response = await client.get(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task["id"]
        assert data["title"] == test_task["title"]

    async def test_get_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent task returns 404."""
        response = await client.get(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_get_task_without_auth(self, client: AsyncClient, test_task: dict):
        """Test getting task without authentication fails."""
        response = await client.get(f"/api/tasks/{test_task['id']}")
        assert response.status_code == 401


class TestUpdateTask:
    """Test cases for updating tasks."""

    async def test_update_task_title(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test updating task title."""
        response = await client.put(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers,
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["id"] == test_task["id"]

    async def test_update_task_description(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test updating task description."""
        response = await client.put(
            f"/api/tasks/{test_task['id']}",
            headers=auth_headers,
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    async def test_update_task_completed(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test marking task as completed via toggle endpoint."""
        response = await client.patch(
            f"/api/tasks/{test_task['id']}/complete",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_update_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent task returns 404."""
        response = await client.put(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
            json={"title": "New Title"},
        )
        assert response.status_code == 404

    async def test_update_task_without_auth(self, client: AsyncClient, test_task: dict):
        """Test updating task without authentication fails."""
        response = await client.put(
            f"/api/tasks/{test_task['id']}",
            json={"title": "New Title"},
        )
        assert response.status_code == 401


class TestDeleteTask:
    """Test cases for deleting tasks."""

    async def test_delete_task_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful task deletion."""
        # Create a task to delete
        create_response = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"title": "Task to Delete"},
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = await client.delete(
            f"/api/tasks/{task_id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(
            f"/api/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent task returns 404."""
        response = await client.delete(
            "/api/tasks/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_delete_task_without_auth(self, client: AsyncClient, test_task: dict):
        """Test deleting task without authentication fails."""
        response = await client.delete(f"/api/tasks/{test_task['id']}")
        assert response.status_code == 401


class TestToggleTaskComplete:
    """Test cases for toggling task completion."""

    async def test_toggle_incomplete_to_complete(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test toggling incomplete task to complete."""
        response = await client.patch(
            f"/api/tasks/{test_task['id']}/complete",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    async def test_toggle_complete_to_incomplete(self, client: AsyncClient, auth_headers: dict, test_task: dict):
        """Test toggling complete task back to incomplete."""
        # First toggle to complete
        await client.patch(
            f"/api/tasks/{test_task['id']}/complete",
            headers=auth_headers,
        )

        # Toggle back to incomplete
        response = await client.patch(
            f"/api/tasks/{test_task['id']}/complete",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False

    async def test_toggle_task_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test toggling non-existent task returns 404."""
        response = await client.patch(
            "/api/tasks/00000000-0000-0000-0000-000000000000/complete",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_toggle_task_without_auth(self, client: AsyncClient, test_task: dict):
        """Test toggling task without authentication fails."""
        response = await client.patch(f"/api/tasks/{test_task['id']}/complete")
        assert response.status_code == 401
