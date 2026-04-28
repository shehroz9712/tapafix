"""add email verification fields to users

Revision ID: 20260428_email_verification_otps
Revises: 20260428_packages_alignment
Create Date: 2026-04-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260428_email_verification_otps"
down_revision: Union[str, None] = "20260428_packages_alignment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("email_verification_otp", sa.String(length=6), nullable=True))
        batch.add_column(
            sa.Column("email_verification_otp_expires_at", sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("email_verification_otp_expires_at")
        batch.drop_column("email_verification_otp")
