from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.v1.deps.auth import get_current_user
from app.api.v1.deps.controllers import get_chat_controller
from app.controllers.chat_controller import ChatController
from app.models.user import User

router = APIRouter(tags=["chat"])


@router.post("/send", status_code=201)
async def chat_send_request(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ChatController, Depends(get_chat_controller)],
    receiver_id: int = Form(..., ge=1),
    message_text: str | None = Form(None),
    media_file: UploadFile | None = File(None),
):
    return await controller.send_request(
        current_user,
        receiver_id=receiver_id,
        message_text=message_text,
        media_file=media_file,
    )


@router.get("/list")
async def chat_list(
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ChatController, Depends(get_chat_controller)],
):
    return await controller.list_chats(current_user)


@router.post("/{chat_id}/accept")
async def chat_accept(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ChatController, Depends(get_chat_controller)],
):
    return await controller.accept(current_user, chat_id)


@router.post("/{chat_id}/reject")
async def chat_reject(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ChatController, Depends(get_chat_controller)],
):
    return await controller.reject(current_user, chat_id)


@router.post("/{chat_id}/message", status_code=201)
async def chat_send_message(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ChatController, Depends(get_chat_controller)],
    message_text: str | None = Form(None),
    media_file: UploadFile | None = File(None),
):
    return await controller.send_message(
        current_user,
        chat_id,
        message_text=message_text,
        media_file=media_file,
    )


@router.get("/{chat_id}/messages")
async def chat_messages(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    controller: Annotated[ChatController, Depends(get_chat_controller)],
):
    return await controller.list_messages(current_user, chat_id)
