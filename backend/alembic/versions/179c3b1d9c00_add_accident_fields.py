"""add accident fields

Revision ID: 179c3b1d9c00
Revises: a054a5b9362d
Create Date: 2026-06-07 16:56:12.176393
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "179c3b1d9c00"
down_revision: Union[str, Sequence[str], None] = "a054a5b9362d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "accidents",
        sa.Column(
            "accident_subtype",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "accidents",
        sa.Column(
            "road_condition",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "accidents",
        sa.Column(
            "ist_sonstige",
            sa.Integer(),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        "accidents",
        "ist_sonstige"
    )

    op.drop_column(
        "accidents",
        "road_condition"
    )

    op.drop_column(
        "accidents",
        "accident_subtype"
    )
