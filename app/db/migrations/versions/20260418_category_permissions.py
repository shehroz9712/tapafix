"""add category/subcategory admin permissions

Revision ID: 20260418_category_permissions
Revises: 20260417_categories
Create Date: 2026-04-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260418_category_permissions"
down_revision: Union[str, None] = "20260417_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
            "name": "manage_categories",
            "module": "admin",
            "description": "Manage categories",
        },
    )
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
            "name": "manage_subcategories",
            "module": "admin",
            "description": "Manage subcategories",
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
        {"permission_name": "manage_categories"},
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
        {"permission_name": "manage_subcategories"},
    )


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            DELETE rp
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE p.name IN ('manage_categories', 'manage_subcategories')
            """
        )
    )
    conn.execute(
        sa.text(
            "DELETE FROM permissions WHERE name IN ('manage_categories', 'manage_subcategories')"
        )
    )
