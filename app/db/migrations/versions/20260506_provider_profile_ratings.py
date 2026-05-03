"""Provider profile average_rating and rating_count for worker listings.

Revision ID: 20260506_provider_ratings
Revises: 20260505_user_profile
Create Date: 2026-05-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260506_provider_ratings"
down_revision: Union[str, None] = "20260505_user_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "provider_profiles",
        sa.Column(
            "average_rating",
            sa.Numeric(3, 2),
            nullable=False,
            server_default="0.00",
        ),
    )
    op.add_column(
        "provider_profiles",
        sa.Column(
            "rating_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("provider_profiles", "rating_count")
    op.drop_column("provider_profiles", "average_rating")
