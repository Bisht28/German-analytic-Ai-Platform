"""add accident composite index

Revision ID: fda9b75d3d48
Revises: 179c3b1d9c00
Create Date: 2026-06-07 17:06:18.054394
"""

from typing import Sequence, Union

from alembic import op


revision: str = "fda9b75d3d48"
down_revision: Union[str, Sequence[str], None] = "179c3b1d9c00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_index(
        "ix_accidents_year_region",
        "accidents",
        ["year", "region_id"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_accidents_year_region",
        table_name="accidents"
    )