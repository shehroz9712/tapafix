from __future__ import annotations

from typing import Any


def request_validation_loc_to_field(loc: tuple[Any, ...] | list[Any]) -> str:
    """Turn Pydantic / FastAPI ``loc`` into a stable dot path for form field mapping."""
    parts: list[str] = []
    for x in loc:
        if x == "body":
            continue
        if isinstance(x, int):
            parts.append(str(x))
        elif isinstance(x, str):
            if x in ("__root__", ""):
                continue
            parts.append(x)
        else:
            parts.append(str(x))
    return ".".join(parts) if parts else "_root"


def _clean_validation_message(msg: str) -> str:
    """Drop Pydantic's generic wrappers so clients can show concise text per field."""
    for prefix in ("Value error, ", "Assertion failed, "):
        if msg.startswith(prefix):
            return msg[len(prefix) :]
    return msg


def format_request_validation_errors(raw_errors: list[dict[str, Any]]) -> dict[str, Any]:
    """Group FastAPI ``RequestValidationError`` entries by API field name."""
    fields: dict[str, list[str]] = {}
    for err in raw_errors:
        loc = err.get("loc") or ()
        if not isinstance(loc, (tuple, list)):
            loc = (str(loc),)
        field = request_validation_loc_to_field(tuple(loc))
        msg = _clean_validation_message(str(err.get("msg", "Invalid value")))
        fields.setdefault(field, []).append(msg)
    return {"fields": fields}
