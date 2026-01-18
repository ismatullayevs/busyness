"""Refactor base_impact to impact

Revision ID: 002
Revises: 001
Create Date: 2026-01-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename base_impact to impact
    op.alter_column("tasks", "base_impact", new_column_name="impact")

    # Rename updated_at to last_updated
    op.alter_column("tasks", "updated_at", new_column_name="last_updated")


def downgrade() -> None:
    # Rename impact back to base_impact
    op.alter_column("tasks", "impact", new_column_name="base_impact")

    # Rename last_updated back to updated_at
    op.alter_column("tasks", "last_updated", new_column_name="updated_at")
