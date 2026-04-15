"""Social OAuth fields on users

Revision ID: 20260415_social
Revises: 20260414_rbac
Create Date: 2026-04-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260415_social"
down_revision: Union[str, None] = "20260414_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "provider",
            sa.String(length=32),
            nullable=False,
            server_default="email",
        ),
    )
    op.add_column(
        "users",
        sa.Column("provider_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("avatar_url", sa.String(length=2048), nullable=True),
    )

    op.execute("UPDATE users SET provider = 'email' WHERE provider IS NULL")

    op.drop_index("ix_users_email", table_name="users")

    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute(
            "CREATE UNIQUE INDEX ix_users_email_lower ON users (lower(email))"
        )
        op.execute(
            "CREATE UNIQUE INDEX uq_users_provider_provider_id ON users (provider, provider_id) "
            "WHERE provider_id IS NOT NULL"
        )
    else:
        op.execute(
            "CREATE UNIQUE INDEX ix_users_email_lower ON users ((LOWER(email)))"
        )
        op.execute(
            """
            ALTER TABLE users ADD COLUMN oauth_provider_pair VARCHAR(512)
            GENERATED ALWAYS AS (
              CASE WHEN provider_id IS NULL THEN NULL
              ELSE CONCAT(provider, ':', provider_id) END
            ) STORED
            """
        )
        op.create_index(
            "uq_users_oauth_provider_pair",
            "users",
            ["oauth_provider_pair"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute("DROP INDEX IF EXISTS uq_users_provider_provider_id")
    else:
        op.drop_index("uq_users_oauth_provider_pair", table_name="users")
        op.execute("ALTER TABLE users DROP COLUMN oauth_provider_pair")

    if dialect == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_users_email_lower")
    else:
        op.drop_index("ix_users_email_lower", table_name="users")

    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.drop_column("users", "avatar_url")
    op.drop_column("users", "provider_id")
    op.drop_column("users", "provider")
