"""Normalize users.email to lowercase and enforce unique index on email.

Keeps existing ix_users_email_lower (LOWER(email)) from 20260415; adds column-level
ix_users_email so the same address cannot be stored twice (after normalization).

Revision ID: 20260504_users_email_unique
Revises: 20260503_chat
Create Date: 2026-05-04
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260504_users_email_unique"
down_revision: Union[str, None] = "20260503_chat"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE users SET email = LOWER(TRIM(email))"))
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
