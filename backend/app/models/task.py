from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskType(str, PyEnum):
    ENDING = "ending"
    ENDLESS = "endless"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), nullable=False, default=TaskType.ENDING
    )

    # User ownership
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)  # Nullable for migration
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    # Current impact value (0-10), updated on each fetch and activity log
    impact: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)

    # Effort in hours to accomplish this task
    effort: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Impact increase per hour of not doing the task
    not_doing_hourly_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.1
    )

    # Impact decrease per hour of doing the task (only for endless tasks, mutually exclusive with impact_set_to)
    doing_hourly_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Fixed value to set impact to when task is done (alternative to doing_hourly_rate)
    impact_set_to: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Optional deadline
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    # last_updated tracks when impact was last recalculated
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Completion timestamp (only for ending tasks)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationship to task logs
    logs: Mapped[list["TaskLog"]] = relationship(
        "TaskLog", back_populates="task", cascade="all, delete-orphan"
    )

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None


class TaskLog(Base):
    """Tracks time spent on endless tasks."""

    __tablename__ = "task_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    duration_minutes: Mapped[int] = mapped_column(nullable=False)

    # Relationship back to task
    task: Mapped["Task"] = relationship("Task", back_populates="logs")
