"""add packages and package purchases with admin permission

Revision ID: 20260428_packages_stripe
Revises: 20260422_listing_verified
Create Date: 2026-04-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260428_packages_stripe"
down_revision: Union[str, None] = "20260422_listing_verified"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "packages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sort", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("image", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Numeric(8, 2), nullable=False, server_default="0"),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("payment_interval", sa.String(length=50), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="usd"),
        sa.Column("services", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_packages_name", "packages", ["name"], unique=True)
    op.create_index("ix_packages_sort", "packages", ["sort"], unique=False)

    op.create_table(
        "package_purchases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("payment_interval", sa.String(length=50), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="usd"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("stripe_checkout_session_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_package_purchases_user_id", "package_purchases", ["user_id"], unique=False)
    op.create_index("ix_package_purchases_package_id", "package_purchases", ["package_id"], unique=False)
    op.create_index("ix_package_purchases_status", "package_purchases", ["status"], unique=False)
    op.create_index(
        "ix_package_purchases_checkout_session",
        "package_purchases",
        ["stripe_checkout_session_id"],
        unique=True,
    )
    op.create_index(
        "ix_package_purchases_payment_intent",
        "package_purchases",
        ["stripe_payment_intent_id"],
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
            "name": "manage_packages",
            "module": "admin",
            "description": "Manage packages",
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
        {"permission_name": "manage_packages"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE rp
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE p.name = 'manage_packages'
            """
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE name = 'manage_packages'"))

    op.drop_index("ix_package_purchases_payment_intent", table_name="package_purchases")
    op.drop_index("ix_package_purchases_checkout_session", table_name="package_purchases")
    op.drop_index("ix_package_purchases_status", table_name="package_purchases")
    op.drop_index("ix_package_purchases_package_id", table_name="package_purchases")
    op.drop_index("ix_package_purchases_user_id", table_name="package_purchases")
    op.drop_table("package_purchases")

    op.drop_index("ix_packages_sort", table_name="packages")
    op.drop_index("ix_packages_name", table_name="packages")
    op.drop_table("packages")
