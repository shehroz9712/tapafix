from __future__ import annotations

import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.repositories.base import BaseRepository


def normalize_user_pair(a: int, b: int) -> tuple[int, int]:
    if a < b:
        return a, b
    return b, a


class ChatRepository(BaseRepository[Chat]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chat)

    async def get_by_user_pair(self, user_a: int, user_b: int) -> Chat | None:
        u1, u2 = normalize_user_pair(user_a, user_b)
        stmt = select(Chat).where(Chat.user_one_id == u1, Chat.user_two_id == u2)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[Chat]:
        stmt = (
            select(Chat)
            .where(
                or_(Chat.user_one_id == user_id, Chat.user_two_id == user_id),
            )
            .order_by(Chat.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatMessage)

    async def count_for_chat(self, chat_id: int) -> int:
        stmt = select(ChatMessage).where(ChatMessage.chat_id == chat_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_last_for_chat(self, chat_id: int) -> ChatMessage | None:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_chat(self, chat_id: int) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_unread_for_user(
        self,
        chat_id: int,
        *,
        current_user_id: int,
        last_read_at: datetime.datetime | None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(ChatMessage)
            .where(
                ChatMessage.chat_id == chat_id,
                ChatMessage.sender_id != current_user_id,
            )
        )
        if last_read_at is not None:
            stmt = stmt.where(ChatMessage.created_at > last_read_at)
        result = await self.session.execute(stmt)
        return int(result.scalar() or 0)
