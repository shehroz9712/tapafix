"""services table and manage_services permission

Revision ID: 20260502_services
Revises: 20260428_email_verification_otps
Create Date: 2026-05-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260502_services"
down_revision: Union[str, None] = "20260428_email_verification_otps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("service_kind", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_services_service_kind", "services", ["service_kind"], unique=False)
    op.create_index("ix_services_user_id", "services", ["user_id"], unique=False)

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
            "name": "manage_services",
            "module": "admin",
            "description": "Manage services",
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
        {"permission_name": "manage_services"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE rp
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE p.name = 'manage_services'
            """
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE name = 'manage_services'"))

    op.drop_index("ix_services_user_id", table_name="services")
    op.drop_index("ix_services_service_kind", table_name="services")
    op.drop_table("services")
