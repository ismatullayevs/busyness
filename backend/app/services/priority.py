from datetime import datetime, timezone

from app.models.task import Task


def update_task_impact(task: Task) -> float:
    """
    Update and return the current impact for a task.

    Calculates: new_impact = current_impact + (hours_since_last_update * not_doing_hourly_rate)
    Updates the task's impact and last_updated fields.
    Returns the priority score (impact with deadline multiplier applied).

    The impact is clamped between 0 and 10.
    """
    now = datetime.now(timezone.utc)

    # Calculate hours since last update
    last_updated = task.last_updated
    if last_updated.tzinfo is None:
        # Handle naive datetime from database
        last_updated = last_updated.replace(tzinfo=timezone.utc)

    hours_since_update = (now - last_updated).total_seconds() / 3600

    # Update impact based on time elapsed
    new_impact = task.impact + (hours_since_update * task.not_doing_hourly_rate)

    # Clamp between 0 and 10
    new_impact = max(0.0, min(10.0, new_impact))

    # Update task fields
    task.impact = new_impact
    task.last_updated = now

    return calculate_priority_score(task)


def calculate_priority_score(task: Task) -> float:
    """
    Calculate priority score from impact and effort, applying deadline multiplier if applicable.

    Priority = (impact / effort) * (1 + 1/days_before_deadline) if deadline exists
    Otherwise: priority = impact / effort
    """
    # Prevent division by zero
    effort = max(0.1, task.effort)
    base_priority = task.impact / effort

    if task.deadline:
        now = datetime.now(timezone.utc)
        deadline = task.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        days_until_deadline = (deadline - now).total_seconds() / 86400
        # Ensure minimum of 0.1 days to prevent division by zero/negative
        days_until_deadline = max(0.1, days_until_deadline)
        base_priority *= 1 + (1 / days_until_deadline)

    # Clamp between 0 and 10
    return max(0.0, min(10.0, base_priority))


def apply_activity_to_impact(task: Task, duration_minutes: int) -> None:
    """
    Apply activity (time spent doing the task) to adjust impact.

    Two modes:
    1. If impact_set_to is set: directly set impact to that value
    2. Else if doing_hourly_rate is set: impact -= (hours_spent * doing_hourly_rate)

    Also updates last_updated to current time.
    """
    now = datetime.now(timezone.utc)

    # First, update impact based on time since last update (time not doing)
    last_updated = task.last_updated
    if last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)

    hours_since_update = (now - last_updated).total_seconds() / 3600
    task.impact += hours_since_update * task.not_doing_hourly_rate

    # Apply the completion behavior
    if task.impact_set_to is not None:
        # Mode 1: Set impact to fixed value
        task.impact = task.impact_set_to
    elif task.doing_hourly_rate is not None:
        # Mode 2: Reduce impact based on hours spent
        hours_spent = duration_minutes / 60
        task.impact -= hours_spent * task.doing_hourly_rate

    # Clamp between 0 and 10
    task.impact = max(0.0, min(10.0, task.impact))

    # Update last_updated
    task.last_updated = now

