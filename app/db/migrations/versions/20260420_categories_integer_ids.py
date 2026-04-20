"""categories/subcategories: integer primary keys (replace UUID)

Revision ID: 20260420_categories_int
Revises: 20260417_login_as_enum
Create Date: 2026-04-20

Drops and recreates category tables. Existing rows in these tables are removed.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_categories_int"
down_revision: Union[str, None] = "20260417_login_as_enum"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("uq_subcategories_category_name", table_name="subcategories")
    op.drop_index("ix_subcategories_is_active", table_name="subcategories")
    op.drop_index("ix_subcategories_category_id", table_name="subcategories")
    op.drop_table("subcategories")

    op.drop_index("ix_categories_is_active", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    op.create_index("ix_categories_is_active", "categories", ["is_active"], unique=False)

    op.create_table(
        "subcategories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_subcategories_category_id", "subcategories", ["category_id"], unique=False)
    op.create_index("ix_subcategories_is_active", "subcategories", ["is_active"], unique=False)
    op.create_index(
        "uq_subcategories_category_name",
        "subcategories",
        ["category_id", "name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_subcategories_category_name", table_name="subcategories")
    op.drop_index("ix_subcategories_is_active", table_name="subcategories")
    op.drop_index("ix_subcategories_category_id", table_name="subcategories")
    op.drop_table("subcategories")

    op.drop_index("ix_categories_is_active", table_name="categories")
    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_table("categories")

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    op.create_index("ix_categories_is_active", "categories", ["is_active"], unique=False)

    op.create_table(
        "subcategories",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("category_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_subcategories_category_id", "subcategories", ["category_id"], unique=False)
    op.create_index("ix_subcategories_is_active", "subcategories", ["is_active"], unique=False)
    op.create_index(
        "uq_subcategories_category_name",
        "subcategories",
        ["category_id", "name"],
        unique=True,
    )
