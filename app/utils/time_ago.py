from __future__ import annotations

import datetime as dt


def format_time_ago(when: dt.datetime | None) -> str:
    """Human-readable relative time (UTC-aware safe)."""
    if when is None:
        return ""
    now = dt.datetime.now(dt.timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.timezone.utc)
    delta = now - when
    seconds = int(delta.total_seconds())
    if seconds < 0:
        seconds = 0
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        m = seconds // 60
        return f"{m} minute{'s' if m != 1 else ''} ago"
    if seconds < 86400:
        h = seconds // 3600
        return f"{h} hour{'s' if h != 1 else ''} ago"
    d = seconds // 86400
    if d < 14:
        return f"{d} day{'s' if d != 1 else ''} ago"
    return when.strftime("%Y-%m-%d %H:%M UTC")
