"""bookings and booking_requests + manage_bookings permission

Revision ID: 20260502_bookings
Revises: 20260502_services
Create Date: 2026-05-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260502_bookings"
down_revision: Union[str, None] = "20260502_services"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("subcategory_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("is_broadcast", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("total_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accepted_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pending_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("auto_closed_count", sa.Integer(), nullable=False, server_default="0"),
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
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subcategory_id"], ["subcategories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"], unique=False)
    op.create_index("ix_bookings_category_id", "bookings", ["category_id"], unique=False)
    op.create_index("ix_bookings_subcategory_id", "bookings", ["subcategory_id"], unique=False)
    op.create_index("ix_bookings_service_id", "bookings", ["service_id"], unique=False)
    op.create_index("ix_bookings_is_broadcast", "bookings", ["is_broadcast"], unique=False)
    op.create_index("ix_bookings_status", "bookings", ["status"], unique=False)

    op.create_table(
        "booking_requests",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "booking_id",
            "provider_id",
            name="uq_booking_requests_booking_provider",
        ),
    )
    op.create_index(
        "ix_booking_requests_booking_id", "booking_requests", ["booking_id"], unique=False
    )
    op.create_index(
        "ix_booking_requests_provider_id", "booking_requests", ["provider_id"], unique=False
    )
    op.create_index("ix_booking_requests_status", "booking_requests", ["status"], unique=False)

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
            "name": "manage_bookings",
            "module": "admin",
            "description": "View and manage bookings",
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
        {"permission_name": "manage_bookings"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE rp
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE p.name = 'manage_bookings'
            """
        )
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE name = 'manage_bookings'"))

    op.drop_index("ix_booking_requests_status", table_name="booking_requests")
    op.drop_index("ix_booking_requests_provider_id", table_name="booking_requests")
    op.drop_index("ix_booking_requests_booking_id", table_name="booking_requests")
    op.drop_table("booking_requests")

    op.drop_index("ix_bookings_status", table_name="bookings")
    op.drop_index("ix_bookings_is_broadcast", table_name="bookings")
    op.drop_index("ix_bookings_service_id", table_name="bookings")
    op.drop_index("ix_bookings_subcategory_id", table_name="bookings")
    op.drop_index("ix_bookings_category_id", table_name="bookings")
    op.drop_index("ix_bookings_user_id", table_name="bookings")
    op.drop_table("bookings")
