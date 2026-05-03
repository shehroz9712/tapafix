"""chats and chat_messages

Revision ID: 20260503_chat
Revises: 20260502_bookings
Create Date: 2026-05-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260503_chat"
down_revision: Union[str, None] = "20260502_bookings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("user_one_id", sa.Integer(), nullable=False),
        sa.Column("user_two_id", sa.Integer(), nullable=False),
        sa.Column("user_one_role", sa.String(length=32), nullable=False),
        sa.Column("user_two_role", sa.String(length=32), nullable=False),
        sa.Column("requester_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("user_one_last_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_two_last_read_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["user_one_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_two_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_one_id", "user_two_id", name="uq_chats_user_pair"),
    )
    op.create_index("ix_chats_user_one_id", "chats", ["user_one_id"], unique=False)
    op.create_index("ix_chats_user_two_id", "chats", ["user_two_id"], unique=False)
    op.create_index("ix_chats_requester_id", "chats", ["requester_id"], unique=False)
    op.create_index("ix_chats_status", "chats", ["status"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("sender_role", sa.String(length=32), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=True),
        sa.Column("media_url", sa.String(length=1024), nullable=True),
        sa.Column("media_type", sa.String(length=32), nullable=True),
        sa.Column("is_request", sa.Boolean(), nullable=False, server_default=sa.text("0")),
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
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_messages_chat_id", "chat_messages", ["chat_id"], unique=False)
    op.create_index("ix_chat_messages_sender_id", "chat_messages", ["sender_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_chat_messages_sender_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_chat_id", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index("ix_chats_status", table_name="chats")
    op.drop_index("ix_chats_requester_id", table_name="chats")
    op.drop_index("ix_chats_user_two_id", table_name="chats")
    op.drop_index("ix_chats_user_one_id", table_name="chats")
    op.drop_table("chats")
