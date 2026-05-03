from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    sender_id: int
    sender_role: str
    message_text: str | None
    media_url: str | None
    media_type: str | None
    is_request: bool
    created_at: dt.datetime | None = None
    time_ago: str = ""


class ChatMessageSummary(BaseModel):
    message_text: str | None = None
    media_url: str | None = None
    media_type: str | None = None
    created_at: dt.datetime | None = None
    time_ago: str = ""


class ChatListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    other_user_id: int
    other_role: str
    unread_count: int = 0
    updated_at: dt.datetime | None = None
    last_message: ChatMessageSummary | None = None


class ChatCreatedEnvelope(BaseModel):
    chat_id: int
    message: ChatMessageOut


class ChatStatusOut(BaseModel):
    chat_id: int
    status: str


class ChatMessagesPage(BaseModel):
    chat_id: int
    status: str
    messages: list[ChatMessageOut]
