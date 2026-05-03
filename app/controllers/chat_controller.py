from __future__ import annotations

from fastapi import UploadFile
from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.services.chat_service import ChatService


class ChatController(BaseController):
    def __init__(self, service: ChatService):
        self._service = service

    async def send_request(
        self,
        user: User,
        *,
        receiver_id: int,
        message_text: str | None,
        media_file: UploadFile | None,
    ) -> JSONResponse:
        payload = await self._service.send_initial_request(
            user,
            receiver_id=receiver_id,
            message_text=message_text,
            media_file=media_file,
        )
        return self.respond_success(payload.model_dump(), "Chat request sent", 201)

    async def send_message(
        self,
        user: User,
        chat_id: int,
        *,
        message_text: str | None,
        media_file: UploadFile | None,
    ) -> JSONResponse:
        msg = await self._service.send_message_active(
            user,
            chat_id,
            message_text=message_text,
            media_file=media_file,
        )
        return self.respond_success(msg.model_dump(), "Message sent", 201)

    async def accept(self, user: User, chat_id: int) -> JSONResponse:
        chat = await self._service.accept_chat(user, chat_id)
        return self.respond_success(
            {"chat_id": chat.id, "status": chat.status},
            "Chat accepted",
        )

    async def reject(self, user: User, chat_id: int) -> JSONResponse:
        chat = await self._service.reject_chat(user, chat_id)
        return self.respond_success(
            {"chat_id": chat.id, "status": chat.status},
            "Chat rejected",
        )

    async def list_chats(self, user: User) -> JSONResponse:
        rows = await self._service.list_chats(user)
        data = [r.model_dump() for r in rows]
        return self.respond_success(data, "Chats retrieved")

    async def list_messages(self, user: User, chat_id: int) -> JSONResponse:
        page = await self._service.list_messages(user, chat_id)
        return self.respond_success(page.model_dump(), "Messages retrieved")
