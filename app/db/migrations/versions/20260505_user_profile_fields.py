"""User profile: first_name, last_name, country, latitude, longitude

Revision ID: 20260505_user_profile
Revises: 20260504_users_email_unique
Create Date: 2026-05-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260505_user_profile"
down_revision: Union[str, None] = "20260504_users_email_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("first_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("country", sa.String(length=120), nullable=True))
    op.add_column("users", sa.Column("latitude", sa.Numeric(10, 7), nullable=True))
    op.add_column("users", sa.Column("longitude", sa.Numeric(10, 7), nullable=True))

    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET first_name = name WHERE first_name IS NULL"))
    conn.execute(sa.text("UPDATE users SET last_name = '' WHERE last_name IS NULL"))

    op.alter_column("users", "first_name", nullable=False)
    op.alter_column("users", "last_name", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "longitude")
    op.drop_column("users", "latitude")
    op.drop_column("users", "country")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
