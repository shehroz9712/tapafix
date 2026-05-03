"""Booking cancellation reason, note, timestamp.

Revision ID: 20260508_booking_cancellation
Revises: 20260507_booking_schedule
Create Date: 2026-05-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260508_booking_cancellation"
down_revision: Union[str, None] = "20260507_booking_schedule"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column("cancellation_reason_type", sa.String(length=64), nullable=True),
    )
    op.add_column("bookings", sa.Column("cancellation_note", sa.Text(), nullable=True))
    op.add_column(
        "bookings",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bookings", "cancelled_at")
    op.drop_column("bookings", "cancellation_note")
    op.drop_column("bookings", "cancellation_reason_type")
