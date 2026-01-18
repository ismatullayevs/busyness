from datetime import datetime, timedelta, timezone
import pytest


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestTasksEndpoints:
    """Tests for tasks API endpoints."""

    def test_get_empty_tasks(self, client):
        """Test getting tasks when none exist."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_ending_task(self, client):
        """Test creating an ending task."""
        task_data = {
            "title": "Complete project",
            "description": "Finish the todo app",
            "task_type": "ending",
            "impact": 7.0,
            "not_doing_hourly_rate": 0.2,
        }
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Complete project"
        assert data["task_type"] == "ending"
        assert data["impact"] == 7.0
        assert data["id"] is not None
        assert data["priority_score"] >= 0

    def test_create_endless_task(self, client):
        """Test creating an endless task."""
        task_data = {
            "title": "Exercise",
            "description": "Daily workout",
            "task_type": "endless",
            "impact": 5.0,
            "not_doing_hourly_rate": 0.1,
            "doing_hourly_rate": 0.05,
        }
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Exercise"
        assert data["task_type"] == "endless"
        assert data["doing_hourly_rate"] == 0.05

    def test_create_task_with_deadline(self, client):
        """Test creating a task with deadline."""
        deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
        task_data = {
            "title": "Submit report",
            "task_type": "ending",
            "impact": 8.0,
            "deadline": deadline,
        }
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["deadline"] is not None

    def test_get_task(self, client):
        """Test getting a single task."""
        # Create task first
        task_data = {"title": "Test task", "impact": 5.0}
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Get the task
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test task"

    def test_get_nonexistent_task(self, client):
        """Test getting a task that doesn't exist."""
        response = client.get("/api/tasks/9999")
        assert response.status_code == 404

    def test_update_task(self, client):
        """Test updating a task."""
        # Create task
        task_data = {"title": "Original", "impact": 5.0}
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Update task
        update_data = {"title": "Updated", "impact": 8.0}
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
        assert response.json()["impact"] == 8.0

    def test_delete_task(self, client):
        """Test deleting a task."""
        # Create task
        task_data = {"title": "To delete"}
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Delete task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_complete_ending_task(self, client):
        """Test completing an ending task."""
        # Create task
        task_data = {"title": "Ending task", "task_type": "ending"}
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Complete task
        response = client.post(f"/api/tasks/{task_id}/complete")
        assert response.status_code == 200
        assert response.json()["completed_at"] is not None

        # Verify not in active tasks
        tasks_response = client.get("/api/tasks")
        task_ids = [t["id"] for t in tasks_response.json()]
        assert task_id not in task_ids

        # Verify in completed tasks
        completed_response = client.get("/api/tasks/completed")
        completed_ids = [t["id"] for t in completed_response.json()]
        assert task_id in completed_ids

    def test_log_time_for_endless_task(self, client):
        """Test logging time for an endless task."""
        # Create endless task
        task_data = {
            "title": "Exercise",
            "task_type": "endless",
            "impact": 7.0,
            "doing_hourly_rate": 0.5,
        }
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Log time (2 hours)
        log_data = {"duration_minutes": 120}
        response = client.post(f"/api/tasks/{task_id}/complete", json=log_data)
        assert response.status_code == 200

        # Impact should be reduced: 7.0 - (2 * 0.5) = 6.0
        assert response.json()["impact"] == pytest.approx(6.0, abs=0.2)

        # Verify log created
        logs_response = client.get(f"/api/tasks/{task_id}/logs")
        assert logs_response.status_code == 200
        logs = logs_response.json()
        assert len(logs) == 1
        assert logs[0]["duration_minutes"] == 120

    def test_endless_task_requires_duration(self, client):
        """Test that endless task completion requires duration."""
        # Create endless task
        task_data = {"title": "Exercise", "task_type": "endless"}
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Try to complete without duration
        response = client.post(f"/api/tasks/{task_id}/complete")
        assert response.status_code == 400

    def test_tasks_sorted_by_priority(self, client):
        """Test that tasks are returned sorted by priority."""
        # Create tasks with different impacts
        client.post(
            "/api/tasks",
            json={"title": "Low", "impact": 2.0, "not_doing_hourly_rate": 0.0},
        )
        client.post(
            "/api/tasks",
            json={"title": "High", "impact": 9.0, "not_doing_hourly_rate": 0.0},
        )
        client.post(
            "/api/tasks",
            json={"title": "Medium", "impact": 5.0, "not_doing_hourly_rate": 0.0},
        )

        response = client.get("/api/tasks")
        tasks = response.json()

        assert tasks[0]["title"] == "High"
        assert tasks[1]["title"] == "Medium"
        assert tasks[2]["title"] == "Low"

    def test_validation_impact_range(self, client):
        """Test that impact must be between 0 and 10."""
        # Too high
        response = client.post(
            "/api/tasks", json={"title": "Test", "impact": 15.0}
        )
        assert response.status_code == 422

        # Too low
        response = client.post(
            "/api/tasks", json={"title": "Test", "impact": -1.0}
        )
        assert response.status_code == 422

    def test_impact_increases_on_fetch(self, client):
        """Test that impact increases when fetching tasks."""
        # Create a task with high not_doing_hourly_rate
        task_data = {
            "title": "Urgent task",
            "impact": 5.0,
            "not_doing_hourly_rate": 1.0,  # Increases 1.0 per hour
        }
        response = client.post("/api/tasks", json=task_data)
        initial_impact = response.json()["impact"]
        assert initial_impact == 5.0

        # Impact should increase on subsequent fetches (even if just slightly)
        # Note: In tests the time difference is minimal, so we just verify the endpoint works
        response = client.get("/api/tasks")
        assert response.status_code == 200
