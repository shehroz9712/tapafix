from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.exceptions import BadRequestError


_SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")


def _ext_from_filename(name: str) -> str:
    suffix = Path(name).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    return ""


def infer_media_category(content_type: str | None) -> str | None:
    if not content_type:
        return None
    ct = content_type.split(";")[0].strip().lower()
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("video/"):
        return "video"
    return "file"


def _category_from_extension(name: str) -> str | None:
    ext = Path(name).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
        return "image"
    if ext in {".mp4", ".webm", ".mov", ".mkv"}:
        return "video"
    if ext in {".pdf", ".zip", ".doc", ".docx", ".txt"}:
        return "file"
    return None


async def save_chat_upload(file: UploadFile) -> tuple[str, str]:
    """Persist upload under uploads/chat; return (public path, media_type category)."""
    content_type = file.content_type
    category = infer_media_category(content_type)
    if category is None:
        category = _category_from_extension(file.filename or "")
    if category is None:
        raise BadRequestError("Unsupported media type")

    raw = file.filename or "upload"
    ext = _ext_from_filename(raw)
    if not ext:
        if category == "image":
            ext = ".jpg"
        elif category == "video":
            ext = ".mp4"
        else:
            ext = ".bin"

    safe_stub = _SAFE_NAME.sub("-", Path(raw).stem)[:40] or "file"
    name = f"{uuid.uuid4().hex}_{safe_stub}{ext}"

    base = Path(settings.UPLOAD_BASE_DIR)
    chat_dir = base / "chat"
    chat_dir.mkdir(parents=True, exist_ok=True)

    dest = chat_dir / name
    size = 0
    chunk_size = 1024 * 1024
    with dest.open("wb") as out:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.CHAT_UPLOAD_MAX_BYTES:
                dest.unlink(missing_ok=True)
                raise BadRequestError("File too large")
            out.write(chunk)

    public_path = f"{settings.PUBLIC_MEDIA_URL_PREFIX}/chat/{name}"
    return public_path, category
