"""provider_profiles: listing, geo, documents, weekly availability (JSON)

Revision ID: 20260421_provider_profiles
Revises: 20260420_categories_int
Create Date: 2026-04-21

Geo filtering uses haversine in application SQL against latitude/longitude.
For heavier workloads on PostgreSQL, consider PostGIS (ST_DWithin, GiST) and
replace the float columns with a geography/geometry column.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260421_provider_profiles"
down_revision: Union[str, None] = "20260420_categories_int"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "provider_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("category_ids", sa.JSON(), nullable=False),
        sa.Column("subcategory_ids", sa.JSON(), nullable=False),
        sa.Column("years_of_experience", sa.Integer(), nullable=True),
        sa.Column("price_per_job", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_per_hour", sa.Numeric(12, 2), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("service_radius_km", sa.Numeric(10, 3), nullable=True),
        sa.Column("cnic_front", sa.Text(), nullable=True),
        sa.Column("cnic_back", sa.Text(), nullable=True),
        sa.Column("certificates", sa.JSON(), nullable=False),
        sa.Column("available_days", sa.JSON(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_provider_profiles_user_id"),
    )
    op.create_index("ix_provider_profiles_email", "provider_profiles", ["email"], unique=False)
    op.create_index("ix_provider_profiles_city", "provider_profiles", ["city"], unique=False)
    op.create_index(
        "ix_provider_profiles_lat_lng",
        "provider_profiles",
        ["latitude", "longitude"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_provider_profiles_lat_lng", table_name="provider_profiles")
    op.drop_index("ix_provider_profiles_city", table_name="provider_profiles")
    op.drop_index("ix_provider_profiles_email", table_name="provider_profiles")
    op.drop_table("provider_profiles")
