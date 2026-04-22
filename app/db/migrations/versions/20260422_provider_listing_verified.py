"""provider_profiles: admin listing verification flag

Revision ID: 20260422_listing_verified
Revises: 20260421_provider_profiles
Create Date: 2026-04-22

Until ``is_listing_verified`` is true (set by admin), the provider is not shown
in public search or GET /providers/{id}. Identity (name, email, phone) remains
on ``users``; provider_profiles still stores a denormalized copy refreshed
from the user row on each listing write.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260422_listing_verified"
down_revision: Union[str, None] = "20260421_provider_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "provider_profiles",
        sa.Column(
            "is_listing_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index(
        "ix_provider_profiles_listing_verified",
        "provider_profiles",
        ["is_listing_verified"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_provider_profiles_listing_verified", table_name="provider_profiles")
    op.drop_column("provider_profiles", "is_listing_verified")
