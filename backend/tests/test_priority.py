from datetime import datetime, timedelta, timezone
import pytest

from app.models.task import Task, TaskLog, TaskType
from app.services.priority import update_task_impact, apply_activity_to_impact, calculate_priority_score


class TestPriorityCalculation:
    """Tests for the priority calculation service."""

    def test_task_base_priority(self):
        """Test that task starts with its initial impact/effort ratio."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDING,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.0,
            created_at=now,
            last_updated=now,
        )
        score = calculate_priority_score(task)
        # priority = impact / effort = 5.0 / 1.0 = 5.0
        assert score == pytest.approx(5.0, abs=0.1)

    def test_effort_affects_priority(self):
        """Test that higher effort reduces priority score."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDING,
            impact=10.0,
            effort=2.0,
            not_doing_hourly_rate=0.0,
            created_at=now,
            last_updated=now,
        )
        score = calculate_priority_score(task)
        # priority = impact / effort = 10.0 / 2.0 = 5.0
        assert score == pytest.approx(5.0, abs=0.1)

    def test_update_impact_increases_over_time(self):
        """Test that impact increases based on time since last update."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDING,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.2,
            created_at=now - timedelta(hours=20),
            last_updated=now - timedelta(hours=10),
        )
        update_task_impact(task)
        # Should be 5.0 + (10 * 0.2) = 7.0
        assert task.impact == pytest.approx(7.0, abs=0.1)

    def test_priority_capped_at_10(self):
        """Test that impact is capped at 10."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDING,
            impact=8.0,
            effort=1.0,
            not_doing_hourly_rate=0.5,
            created_at=now - timedelta(hours=100),
            last_updated=now - timedelta(hours=100),
        )
        update_task_impact(task)
        assert task.impact == 10.0

    def test_priority_floored_at_0(self):
        """Test that impact is floored at 0."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDLESS,
            impact=1.0,
            effort=1.0,
            not_doing_hourly_rate=0.0,
            doing_hourly_rate=1.0,
            created_at=now - timedelta(hours=1),
            last_updated=now,
        )
        # Apply activity to reduce impact below 0
        apply_activity_to_impact(task, duration_minutes=600)  # 10 hours
        assert task.impact == 0.0

    def test_deadline_increases_priority(self):
        """Test that deadline multiplier increases priority score."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDING,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.0,
            deadline=now + timedelta(days=1),
            created_at=now,
            last_updated=now,
        )
        score = calculate_priority_score(task)
        # Should be (5.0/1.0) * (1 + 1/1) = 10.0
        assert score == pytest.approx(10.0, abs=0.5)

    def test_deadline_closer_higher_priority(self):
        """Test that closer deadlines have higher priority."""
        now = datetime.now(timezone.utc)
        task_soon = Task(
            id=1,
            title="Task 1",
            task_type=TaskType.ENDING,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.0,
            deadline=now + timedelta(days=1),
            created_at=now,
            last_updated=now,
        )
        task_later = Task(
            id=2,
            title="Task 2",
            task_type=TaskType.ENDING,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.0,
            deadline=now + timedelta(days=7),
            created_at=now,
            last_updated=now,
        )
        score_soon = calculate_priority_score(task_soon)
        score_later = calculate_priority_score(task_later)
        assert score_soon > score_later

    def test_apply_activity_reduces_impact(self):
        """Test that logging activity reduces impact for endless tasks."""
        now = datetime.now(timezone.utc)
        task = Task(
            id=1,
            title="Exercise",
            task_type=TaskType.ENDLESS,
            impact=7.0,
            effort=1.0,
            not_doing_hourly_rate=0.1,
            doing_hourly_rate=0.5,
            created_at=now - timedelta(days=30),
            last_updated=now,
        )
        # Log 2 hours of activity
        apply_activity_to_impact(task, duration_minutes=120)
        # Should be 7.0 - (2 * 0.5) = 6.0
        assert task.impact == pytest.approx(6.0, abs=0.1)

    def test_apply_activity_updates_last_updated(self):
        """Test that applying activity updates last_updated timestamp."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(hours=5)
        task = Task(
            id=1,
            title="Exercise",
            task_type=TaskType.ENDLESS,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.1,
            doing_hourly_rate=0.5,
            created_at=old_time,
            last_updated=old_time,
        )
        apply_activity_to_impact(task, duration_minutes=60)
        # last_updated should be close to now
        assert (datetime.now(timezone.utc) - task.last_updated).total_seconds() < 2

    def test_update_impact_also_updates_last_updated(self):
        """Test that update_task_impact updates last_updated timestamp."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(hours=5)
        task = Task(
            id=1,
            title="Test Task",
            task_type=TaskType.ENDING,
            impact=5.0,
            effort=1.0,
            not_doing_hourly_rate=0.1,
            created_at=old_time,
            last_updated=old_time,
        )
        update_task_impact(task)
        # last_updated should be close to now
        assert (datetime.now(timezone.utc) - task.last_updated).total_seconds() < 2
