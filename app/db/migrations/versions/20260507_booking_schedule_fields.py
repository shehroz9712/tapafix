"""Booking scheduled date, time range, optional note.

Revision ID: 20260507_booking_schedule
Revises: 20260506_provider_ratings
Create Date: 2026-05-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260507_booking_schedule"
down_revision: Union[str, None] = "20260506_provider_ratings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("scheduled_date", sa.Date(), nullable=True))
    op.add_column(
        "bookings",
        sa.Column("start_time", sa.String(length=5), nullable=True),
    )
    op.add_column(
        "bookings",
        sa.Column("end_time", sa.String(length=5), nullable=True),
    )
    op.add_column("bookings", sa.Column("note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("bookings", "note")
    op.drop_column("bookings", "end_time")
    op.drop_column("bookings", "start_time")
    op.drop_column("bookings", "scheduled_date")
