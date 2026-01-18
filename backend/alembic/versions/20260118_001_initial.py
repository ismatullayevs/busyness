"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-01-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "task_type",
            sa.Enum("ENDING", "ENDLESS", name="tasktype"),
            nullable=False,
        ),
        sa.Column("base_impact", sa.Float(), nullable=False),
        sa.Column("not_doing_hourly_rate", sa.Float(), nullable=False),
        sa.Column("doing_hourly_rate", sa.Float(), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)

    # Create task_logs table
    op.create_table(
        "task_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("logged_at", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_logs_id"), "task_logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_task_logs_id"), table_name="task_logs")
    op.drop_table("task_logs")
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.execute("DROP TYPE IF EXISTS tasktype")
