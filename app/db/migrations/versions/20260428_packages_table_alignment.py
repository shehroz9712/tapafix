"""align packages schema with requested columns

Revision ID: 20260428_packages_alignment
Revises: 20260428_transactions
Create Date: 2026-04-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260428_packages_alignment"
down_revision: Union[str, None] = "20260428_transactions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    return {col["name"] for col in inspector.get_columns(table_name)}


def upgrade() -> None:
    package_cols = _column_names("packages")
    with op.batch_alter_table("packages") as batch:
        if "sort" not in package_cols:
            batch.add_column(sa.Column("sort", sa.SmallInteger(), nullable=False, server_default="0"))
        if "image" not in package_cols:
            batch.add_column(sa.Column("image", sa.String(length=255), nullable=True))
        if "price" not in package_cols:
            batch.add_column(sa.Column("price", sa.Numeric(8, 2), nullable=False, server_default="0"))
        if "duration" not in package_cols:
            batch.add_column(sa.Column("duration", sa.Integer(), nullable=False, server_default="1"))
        if "payment_interval" not in package_cols:
            batch.add_column(sa.Column("payment_interval", sa.String(length=50), nullable=True))
        if "currency" not in package_cols:
            batch.add_column(sa.Column("currency", sa.String(length=10), nullable=False, server_default="usd"))
        if "services" not in package_cols:
            batch.add_column(sa.Column("services", sa.Integer(), nullable=True))

    package_cols = _column_names("packages")
    if "monthly_price" in package_cols:
        op.execute(sa.text("UPDATE packages SET price = monthly_price WHERE price = 0"))
        op.execute(
            sa.text(
                "UPDATE packages SET payment_interval = 'monthly' "
                "WHERE payment_interval IS NULL OR payment_interval = ''"
            )
        )
        with op.batch_alter_table("packages") as batch:
            batch.drop_column("monthly_price")
    if "yearly_price" in package_cols:
        with op.batch_alter_table("packages") as batch:
            batch.drop_column("yearly_price")
    if "is_active" in package_cols:
        with op.batch_alter_table("packages") as batch:
            batch.drop_column("is_active")

    with op.batch_alter_table("packages") as batch:
        batch.alter_column("name", type_=sa.String(length=100), existing_type=sa.String(length=120))
    idx_names = {idx["name"] for idx in sa.inspect(op.get_bind()).get_indexes("packages")}
    if "ix_packages_is_active" in idx_names:
        op.drop_index("ix_packages_is_active", table_name="packages")
    if "ix_packages_sort" not in idx_names:
        op.create_index("ix_packages_sort", "packages", ["sort"], unique=False)

    purchase_cols = _column_names("package_purchases")
    with op.batch_alter_table("package_purchases") as batch:
        if "payment_interval" not in purchase_cols:
            batch.add_column(sa.Column("payment_interval", sa.String(length=50), nullable=True))
    purchase_cols = _column_names("package_purchases")
    if "billing_cycle" in purchase_cols:
        op.execute(
            sa.text(
                "UPDATE package_purchases SET payment_interval = billing_cycle "
                "WHERE payment_interval IS NULL OR payment_interval = ''"
            )
        )
        with op.batch_alter_table("package_purchases") as batch:
            batch.drop_column("billing_cycle")


def downgrade() -> None:
    package_cols = _column_names("packages")
    with op.batch_alter_table("packages") as batch:
        if "is_active" not in package_cols:
            batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        if "monthly_price" not in package_cols:
            batch.add_column(sa.Column("monthly_price", sa.Float(), nullable=False, server_default="0"))
        if "yearly_price" not in package_cols:
            batch.add_column(sa.Column("yearly_price", sa.Float(), nullable=False, server_default="0"))
    package_cols = _column_names("packages")
    if "price" in package_cols:
        op.execute(sa.text("UPDATE packages SET monthly_price = price, yearly_price = price"))
    with op.batch_alter_table("packages") as batch:
        if "services" in package_cols:
            batch.drop_column("services")
        if "currency" in package_cols:
            batch.drop_column("currency")
        if "payment_interval" in package_cols:
            batch.drop_column("payment_interval")
        if "duration" in package_cols:
            batch.drop_column("duration")
        if "price" in package_cols:
            batch.drop_column("price")
        if "image" in package_cols:
            batch.drop_column("image")
        if "sort" in package_cols:
            batch.drop_column("sort")
        batch.alter_column("name", type_=sa.String(length=120), existing_type=sa.String(length=100))

    idx_names = {idx["name"] for idx in sa.inspect(op.get_bind()).get_indexes("packages")}
    if "ix_packages_sort" in idx_names:
        op.drop_index("ix_packages_sort", table_name="packages")
    if "ix_packages_is_active" not in idx_names:
        op.create_index("ix_packages_is_active", "packages", ["is_active"], unique=False)

    purchase_cols = _column_names("package_purchases")
    with op.batch_alter_table("package_purchases") as batch:
        if "billing_cycle" not in purchase_cols:
            batch.add_column(
                sa.Column(
                    "billing_cycle",
                    sa.Enum("monthly", "yearly", name="package_billing_cycle_enum"),
                    nullable=False,
                    server_default="monthly",
                )
            )
    purchase_cols = _column_names("package_purchases")
    if "payment_interval" in purchase_cols:
        op.execute(
            sa.text(
                "UPDATE package_purchases SET billing_cycle = COALESCE(payment_interval, 'monthly')"
            )
        )
        with op.batch_alter_table("package_purchases") as batch:
            batch.drop_column("payment_interval")
