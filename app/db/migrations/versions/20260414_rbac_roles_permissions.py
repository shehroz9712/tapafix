"""RBAC: roles, permissions, user.role_id

Revision ID: 20260414_rbac
Revises: 20260413_0001
Create Date: 2026-04-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260414_rbac"
down_revision: Union[str, None] = "20260413_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISSIONS = [
    ("login", "auth", "Authenticate"),
    ("register", "auth", "Register account"),
    ("create_booking", "booking", "Create booking"),
    ("view_booking", "booking", "View booking"),
    ("cancel_booking", "booking", "Cancel booking"),
    ("send_message", "chat", "Send chat message"),
    ("manage_users", "admin", "List and manage users"),
    ("manage_packages", "admin", "Manage packages"),
    ("manage_roles", "admin", "Manage roles and permissions"),
    ("accept_job", "vendor", "Accept a job"),
    ("bid_job", "vendor", "Place a bid on a job"),
]


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("allows_self_registration", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"], unique=True)
    op.create_index("ix_permissions_module", "permissions", ["module"], unique=False)

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    conn = op.get_bind()
    conn.execute(sa.text("INSERT INTO roles (name, description, allows_self_registration) VALUES ('ADMIN','System administrator', false)"))
    conn.execute(sa.text("INSERT INTO roles (name, description, allows_self_registration) VALUES ('USER','Customer', true)"))
    conn.execute(sa.text("INSERT INTO roles (name, description, allows_self_registration) VALUES ('VENDOR','Handyman / vendor', true)"))

    for pname, module, desc in PERMISSIONS:
        conn.execute(
            sa.text("INSERT INTO permissions (name, module, description) VALUES (:name, :module, :desc)"),
            {"name": pname, "module": module, "desc": desc},
        )

    conn.execute(sa.text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON 1=1 WHERE r.name='ADMIN'
    """))

    conn.execute(sa.text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON p.name IN
        ('login','register','create_booking','view_booking','cancel_booking','send_message')
        WHERE r.name='USER'
    """))

    conn.execute(sa.text("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id FROM roles r JOIN permissions p ON p.name IN
        ('login','register','create_booking','view_booking','cancel_booking','accept_job','bid_job','send_message')
        WHERE r.name='VENDOR'
    """))

    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_users_role_id_roles", "users", "roles", ["role_id"], ["id"], ondelete="RESTRICT")

    conn.execute(sa.text("""
        UPDATE users u
        JOIN roles r ON r.name = u.role
        SET u.role_id = r.id
    """))
    conn.execute(sa.text("""
        UPDATE users u
        JOIN roles r ON r.name = 'USER'
        SET u.role_id = r.id
        WHERE u.role_id IS NULL
    """))

    op.alter_column("users", "role_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=16), nullable=True, server_default="USER"))
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE users u
        JOIN roles r ON r.id = u.role_id
        SET u.role = r.name
    """))
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
    op.drop_table("role_permissions")
    op.drop_index("ix_permissions_module", table_name="permissions")
    op.drop_index("ix_permissions_name", table_name="permissions")
    op.drop_table("permissions")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
