"""Add impact_set_to field

Revision ID: 004
Revises: 003
Create Date: 2026-01-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add impact_set_to column (nullable, alternative to doing_hourly_rate)
    op.add_column(
        "tasks",
        sa.Column("impact_set_to", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tasks", "impact_set_to")
