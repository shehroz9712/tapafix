from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.repositories.chat_repository import ChatMessageRepository, ChatRepository, normalize_user_pair
from app.repositories.user_repository import UserRepository
from app.schemas.chat import (
    ChatCreatedEnvelope,
    ChatListItemOut,
    ChatMessageOut,
    ChatMessageSummary,
    ChatMessagesPage,
)
from app.utils.chat_media import save_chat_upload
from app.utils.time_ago import format_time_ago

STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_REJECTED = "rejected"
STATUS_BLOCKED = "blocked"


def _role_str(user: User) -> str:
    la = user.login_as
    if hasattr(la, "value"):
        return str(la.value).lower()
    return str(la).lower()


def _peer_user_id(chat: Chat, uid: int) -> int:
    return chat.user_two_id if uid == chat.user_one_id else chat.user_one_id


def _request_receiver_id(chat: Chat) -> int:
    return _peer_user_id(chat, chat.requester_id)


def _role_for_user(chat: Chat, uid: int) -> str:
    return chat.user_one_role if uid == chat.user_one_id else chat.user_two_role


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.chats = ChatRepository(session)
        self.messages = ChatMessageRepository(session)
        self.users = UserRepository(session)

    def _serialize_message(self, row: ChatMessage) -> dict[str, Any]:
        created = row.created_at
        data = ChatMessageOut.model_validate(row).model_dump()
        data["time_ago"] = format_time_ago(created)
        return data

    def _touch_chat(self, chat: Chat) -> None:
        chat.updated_at = dt.datetime.now(dt.timezone.utc)

    async def _persist_media(self, file: UploadFile | None) -> tuple[str | None, str | None]:
        if file is None:
            return None, None
        url, category = await save_chat_upload(file)
        return url, category

    async def send_initial_request(
        self,
        sender: User,
        *,
        receiver_id: int,
        message_text: str | None,
        media_file: UploadFile | None,
    ) -> ChatCreatedEnvelope:
        if receiver_id == sender.id:
            raise BadRequestError("Cannot message yourself")
        receiver = await self.users.get_by_id(receiver_id)
        if not receiver or not receiver.is_active:
            raise BadRequestError("Recipient not found")

        text = (message_text or "").strip() or None
        media_url: str | None = None
        media_type: str | None = None
        if media_file is not None and media_file.filename:
            media_url, media_type = await self._persist_media(media_file)
        if not text and not media_url:
            raise BadRequestError("Provide message text and/or a media file")

        u1, u2 = normalize_user_pair(sender.id, receiver.id)
        existing = await self.chats.get_by_user_pair(sender.id, receiver.id)
        if existing:
            if existing.status == STATUS_PENDING:
                raise BadRequestError("Chat request already pending")
            if existing.status == STATUS_ACTIVE:
                raise BadRequestError("Chat already active; use POST /chat/{chat_id}/message")
            if existing.status in (STATUS_REJECTED, STATUS_BLOCKED):
                raise BadRequestError("Chat is closed for this conversation")
            raise BadRequestError("Cannot open a new chat with this user")

        rs, rr = _role_str(sender), _role_str(receiver)
        role_u1 = rs if u1 == sender.id else rr
        role_u2 = rr if u2 == receiver.id else rs
        try:
            chat = await self.chats.create(
                obj_in={
                    "user_one_id": u1,
                    "user_two_id": u2,
                    "user_one_role": role_u1,
                    "user_two_role": role_u2,
                    "requester_id": sender.id,
                    "status": STATUS_PENDING,
                }
            )
            await self.session.flush()
            msg = await self.messages.create(
                obj_in={
                    "chat_id": chat.id,
                    "sender_id": sender.id,
                    "sender_role": _role_str(sender),
                    "message_text": text,
                    "media_url": media_url,
                    "media_type": media_type,
                    "is_request": True,
                }
            )
            self._touch_chat(chat)
            await self.session.commit()
            await self.session.refresh(chat)
            await self.session.refresh(msg)
        except IntegrityError:
            await self.session.rollback()
            raise BadRequestError("Could not create chat")

        out_msg = ChatMessageOut(**self._serialize_message(msg))
        return ChatCreatedEnvelope(chat_id=chat.id, message=out_msg)

    async def send_message_active(
        self,
        sender: User,
        chat_id: int,
        *,
        message_text: str | None,
        media_file: UploadFile | None,
    ) -> ChatMessageOut:
        chat = await self.chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found")
        if sender.id not in (chat.user_one_id, chat.user_two_id):
            raise ForbiddenError("Not a participant")
        if chat.status != STATUS_ACTIVE:
            raise BadRequestError("Chat is not active")

        text = (message_text or "").strip() or None
        media_url: str | None = None
        media_type: str | None = None
        if media_file is not None and media_file.filename:
            media_url, media_type = await self._persist_media(media_file)
        if not text and not media_url:
            raise BadRequestError("Provide message text and/or a media file")

        try:
            msg = await self.messages.create(
                obj_in={
                    "chat_id": chat.id,
                    "sender_id": sender.id,
                    "sender_role": _role_str(sender),
                    "message_text": text,
                    "media_url": media_url,
                    "media_type": media_type,
                    "is_request": False,
                }
            )
            self._touch_chat(chat)
            await self.session.commit()
            await self.session.refresh(msg)
        except IntegrityError:
            await self.session.rollback()
            raise BadRequestError("Could not send message")

        return ChatMessageOut(**self._serialize_message(msg))

    async def accept_chat(self, user: User, chat_id: int) -> Chat:
        chat = await self.chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found")
        if user.id not in (chat.user_one_id, chat.user_two_id):
            raise ForbiddenError("Not a participant")
        if chat.status != STATUS_PENDING:
            raise BadRequestError("Chat is not pending")
        if user.id != _request_receiver_id(chat):
            raise ForbiddenError("Only the recipient can accept")

        chat.status = STATUS_ACTIVE
        self._touch_chat(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def reject_chat(self, user: User, chat_id: int) -> Chat:
        chat = await self.chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found")
        if user.id not in (chat.user_one_id, chat.user_two_id):
            raise ForbiddenError("Not a participant")
        if chat.status != STATUS_PENDING:
            raise BadRequestError("Chat is not pending")
        if user.id != _request_receiver_id(chat):
            raise ForbiddenError("Only the recipient can reject")

        chat.status = STATUS_REJECTED
        self._touch_chat(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    def _last_read_for_user(self, chat: Chat, user_id: int) -> dt.datetime | None:
        if user_id == chat.user_one_id:
            return chat.user_one_last_read_at
        return chat.user_two_last_read_at

    def _set_last_read_for_user(self, chat: Chat, user_id: int, when: dt.datetime) -> None:
        if user_id == chat.user_one_id:
            chat.user_one_last_read_at = when
        else:
            chat.user_two_last_read_at = when

    async def list_chats(self, user: User) -> list[ChatListItemOut]:
        rows = await self.chats.list_for_user(user.id)
        out: list[ChatListItemOut] = []
        for chat in rows:
            other_id = _peer_user_id(chat, user.id)
            other_role = _role_for_user(chat, other_id)
            last = await self.messages.get_last_for_chat(chat.id)
            last_summary = None
            if last:
                last_summary = ChatMessageSummary(
                    message_text=last.message_text,
                    media_url=last.media_url,
                    media_type=last.media_type,
                    created_at=last.created_at,
                    time_ago=format_time_ago(last.created_at),
                )
            lr = self._last_read_for_user(chat, user.id)
            unread = await self.messages.count_unread_for_user(
                chat.id,
                current_user_id=user.id,
                last_read_at=lr,
            )
            out.append(
                ChatListItemOut(
                    id=chat.id,
                    status=chat.status,
                    other_user_id=other_id,
                    other_role=other_role,
                    unread_count=unread,
                    updated_at=chat.updated_at,
                    last_message=last_summary,
                )
            )
        return out

    async def list_messages(self, user: User, chat_id: int) -> ChatMessagesPage:
        chat = await self.chats.get_by_id(chat_id)
        if not chat:
            raise NotFoundError("Chat not found")
        if user.id not in (chat.user_one_id, chat.user_two_id):
            raise ForbiddenError("Not a participant")

        msgs = await self.messages.list_for_chat(chat_id)
        now = dt.datetime.now(dt.timezone.utc)
        self._set_last_read_for_user(chat, user.id, now)
        self._touch_chat(chat)
        await self.session.commit()
        await self.session.refresh(chat)

        payload = [ChatMessageOut(**self._serialize_message(m)) for m in msgs]
        return ChatMessagesPage(chat_id=chat.id, status=chat.status, messages=payload)
