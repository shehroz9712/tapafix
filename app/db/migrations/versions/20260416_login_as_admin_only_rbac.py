"""login_as + admin-only role_id; drop USER/VENDOR roles

Revision ID: 20260416_login_as
Revises: 20260415_social
Create Date: 2026-04-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260416_login_as"
down_revision: Union[str, None] = "20260415_social"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("login_as", sa.String(length=16), nullable=False, server_default="user"),
    )

    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE users u
        JOIN roles r ON u.role_id = r.id
        SET u.login_as = CASE r.name
            WHEN 'ADMIN' THEN 'admin'
            WHEN 'VENDOR' THEN 'provider'
            ELSE 'user'
        END
    """))

    conn.execute(sa.text("UPDATE users SET role_id = NULL WHERE login_as <> 'admin'"))
    op.alter_column("users", "role_id", existing_type=sa.Integer(), nullable=True)

    conn.execute(sa.text("""
        DELETE rp FROM role_permissions rp
        JOIN roles r ON rp.role_id = r.id
        WHERE r.name IN ('USER', 'VENDOR')
    """))
    conn.execute(sa.text("DELETE FROM roles WHERE name IN ('USER', 'VENDOR')"))


def downgrade() -> None:
    pass
