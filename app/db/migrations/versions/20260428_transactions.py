"""add transactions table and admin permission

Revision ID: 20260428_transactions
Revises: 20260428_packages_stripe
Create Date: 2026-04-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260428_transactions"
down_revision: Union[str, None] = "20260428_packages_stripe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("package_purchase_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="usd"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("provider", sa.String(length=32), nullable=False, server_default="stripe"),
        sa.Column("provider_session_id", sa.String(length=255), nullable=True),
        sa.Column("provider_payment_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["package_purchase_id"], ["package_purchases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"], unique=False)
    op.create_index(
        "ix_transactions_package_purchase_id",
        "transactions",
        ["package_purchase_id"],
        unique=False,
    )
    op.create_index("ix_transactions_status", "transactions", ["status"], unique=False)
    op.create_index(
        "ix_transactions_provider_session_id",
        "transactions",
        ["provider_session_id"],
        unique=False,
    )
    op.create_index(
        "ix_transactions_provider_payment_id",
        "transactions",
        ["provider_payment_id"],
        unique=False,
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO permissions (name, module, description)
            SELECT :name, :module, :description
            WHERE NOT EXISTS (
                SELECT 1 FROM permissions WHERE name = :name
            )
            """
        ),
        {
            "name": "manage_transactions",
            "module": "admin",
            "description": "Manage transactions",
        },
    )
    conn.execute(
        sa.text(
            """
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM roles r
            JOIN permissions p ON p.name = :permission_name
            WHERE r.name = 'ADMIN'
              AND NOT EXISTS (
                SELECT 1
                FROM role_permissions rp
                WHERE rp.role_id = r.id AND rp.permission_id = p.id
              )
            """
        ),
        {"permission_name": "manage_transactions"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE rp
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE p.name = 'manage_transactions'
            """
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE name = 'manage_transactions'"))

    op.drop_index("ix_transactions_provider_payment_id", table_name="transactions")
    op.drop_index("ix_transactions_provider_session_id", table_name="transactions")
    op.drop_index("ix_transactions_status", table_name="transactions")
    op.drop_index("ix_transactions_package_purchase_id", table_name="transactions")
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_table("transactions")
