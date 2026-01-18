from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task, TaskLog, TaskType
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithLogsResponse,
    TaskLogCreate,
    TaskLogResponse,
)
from app.services.priority import update_task_impact, apply_activity_to_impact, calculate_priority_score
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def task_to_response(task: Task) -> dict:
    """Convert a task model to response dict with priority score."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "impact": task.impact,
        "effort": task.effort,
        "not_doing_hourly_rate": task.not_doing_hourly_rate,
        "doing_hourly_rate": task.doing_hourly_rate,
        "impact_set_to": task.impact_set_to,
        "deadline": task.deadline,
        "created_at": task.created_at,
        "last_updated": task.last_updated,
        "completed_at": task.completed_at,
        "priority_score": calculate_priority_score(task),
    }


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active tasks for current user sorted by priority score."""
    tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id)
        .filter(Task.completed_at.is_(None))
        .all()
    )

    # Update impact for each task and collect responses
    task_responses = []
    for task in tasks:
        update_task_impact(task)
        task_responses.append(task_to_response(task))

    # Commit the impact updates
    db.commit()

    # Sort by priority score
    task_responses.sort(key=lambda t: t["priority_score"], reverse=True)

    return task_responses


@router.get("/completed", response_model=list[TaskResponse])
def get_completed_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all completed ending tasks for current user."""
    tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id)
        .filter(Task.completed_at.is_not(None))
        .order_by(Task.completed_at.desc())
        .all()
    )
    return [task_to_response(task) for task in tasks]


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task for current user."""
    # Set default doing_hourly_rate for endless tasks if neither completion mode is set
    doing_rate = task_data.doing_hourly_rate
    impact_set_to = task_data.impact_set_to
    if task_data.task_type == TaskType.ENDLESS and doing_rate is None and impact_set_to is None:
        doing_rate = 0.1

    task = Task(
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        impact=task_data.impact,
        effort=task_data.effort,
        not_doing_hourly_rate=task_data.not_doing_hourly_rate,
        doing_hourly_rate=doing_rate,
        impact_set_to=impact_set_to,
        deadline=task_data.deadline,
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task_to_response(task)


@router.get("/{task_id}", response_model=TaskWithLogsResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a task by ID with its logs."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update impact if task is not completed
    if not task.completed_at:
        update_task_impact(task)
        db.commit()

    logs = list(task.logs)
    response = task_to_response(task)
    response["logs"] = [
        {
            "id": log.id,
            "task_id": log.task_id,
            "logged_at": log.logged_at,
            "duration_minutes": log.duration_minutes,
        }
        for log in logs
    ]
    return response


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task_to_response(task)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    log_data: TaskLogCreate | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a task or log time."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.task_type == TaskType.ENDING:
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
    else:
        if not log_data:
            raise HTTPException(
                status_code=400,
                detail="duration_minutes is required for endless tasks",
            )

        apply_activity_to_impact(task, log_data.duration_minutes)

        log = TaskLog(task_id=task.id, duration_minutes=log_data.duration_minutes)
        db.add(log)
        db.commit()
        db.refresh(task)

    return task_to_response(task)


@router.get("/{task_id}/logs", response_model=list[TaskLogResponse])
def get_task_logs(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all time logs for a task."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    logs = db.query(TaskLog).filter(TaskLog.task_id == task_id).order_by(TaskLog.logged_at.desc()).all()
    return logs
