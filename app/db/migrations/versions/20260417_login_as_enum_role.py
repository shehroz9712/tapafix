"""Make users.login_as an enum role

Revision ID: 20260417_login_as_enum
Revises: 20260416_login_as
Create Date: 2026-04-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260417_login_as_enum"
down_revision: Union[str, None] = "20260418_category_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

account_role_enum = sa.Enum("user", "provider", "admin", name="account_role_enum")


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE users SET login_as = 'user' WHERE login_as NOT IN ('user','provider','admin')"
    ))
    op.alter_column(
        "users",
        "login_as",
        existing_type=sa.String(length=16),
        type_=account_role_enum,
        existing_nullable=False,
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "login_as",
        existing_type=account_role_enum,
        type_=sa.String(length=16),
        existing_nullable=False,
        nullable=False,
    )
