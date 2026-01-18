from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class TaskType(str, Enum):
    ENDING = "ending"
    ENDLESS = "endless"


class TaskLogCreate(BaseModel):
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes")


class TaskLogResponse(BaseModel):
    id: int
    task_id: int
    logged_at: datetime
    duration_minutes: int

    model_config = {"from_attributes": True}


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    task_type: TaskType = TaskType.ENDING
    impact: float = Field(default=5.0, ge=0.0, le=10.0)
    effort: float = Field(default=1.0, gt=0.0, le=1000.0, description="Hours to accomplish this task")
    not_doing_hourly_rate: float = Field(default=0.1, ge=0.0)
    # Two mutually exclusive options for what happens when task is done:
    doing_hourly_rate: float | None = Field(default=None, ge=0.0, description="Impact decrease per hour of doing")
    impact_set_to: float | None = Field(default=None, ge=0.0, le=10.0, description="Fixed value to set impact to when done")
    deadline: datetime | None = None

    @model_validator(mode="after")
    def validate_completion_behavior(self):
        """Ensure doing_hourly_rate and impact_set_to are mutually exclusive for endless tasks."""
        if self.task_type == TaskType.ENDLESS:
            # At least one should be set for endless tasks
            if self.doing_hourly_rate is None and self.impact_set_to is None:
                self.doing_hourly_rate = 0.1  # Default
        return self


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    impact: float | None = Field(default=None, ge=0.0, le=10.0)
    effort: float | None = Field(default=None, gt=0.0, le=1000.0)
    not_doing_hourly_rate: float | None = Field(default=None, ge=0.0)
    doing_hourly_rate: float | None = Field(default=None, ge=0.0)
    impact_set_to: float | None = Field(default=None, ge=0.0, le=10.0)
    deadline: datetime | None = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    last_updated: datetime
    completed_at: datetime | None = None
    priority_score: float = 0.0

    model_config = {"from_attributes": True}


class TaskWithLogsResponse(TaskResponse):
    logs: list[TaskLogResponse] = []
