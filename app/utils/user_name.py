from __future__ import annotations


def display_name_from_parts(first_name: str, last_name: str) -> str:
    return f"{(first_name or '').strip()} {(last_name or '').strip()}".strip()[:200] or "User"


def split_display_name(full: str | None) -> tuple[str, str]:
    """Split a single display string into first/last (last may be empty)."""
    parts = (full or "").strip().split(None, 1)
    if not parts:
        return "User", ""
    if len(parts) == 1:
        return parts[0][:100], ""
    return parts[0][:100], parts[1][:100]
