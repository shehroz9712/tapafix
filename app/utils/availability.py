from __future__ import annotations

import datetime as dt
from typing import Any

# English weekday names, matching ``datetime.strftime("%A")`` in locale C / UTC.
_DAY_ALIASES = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}


def _normalize_day(name: str) -> str | None:
    key = (name or "").strip().lower()
    return _DAY_ALIASES.get(key)


def _parse_hhmm(value: str) -> dt.time | None:
    if not isinstance(value, str):
        return None
    parts = value.strip().split(":")
    if len(parts) != 2:
        return None
    try:
        h, m = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if not (0 <= h <= 23 and 0 <= m <= 59):
        return None
    return dt.time(h, m)


def is_within_availability(
    available_days: list[dict[str, Any]] | None,
    *,
    when: dt.datetime | None = None,
) -> bool:
    """Return True if ``when`` falls on a configured day between start/end (inclusive).

    ``when`` should be timezone-aware (recommended: UTC). ``available_days`` entries
    use keys ``day``, ``start_time``, ``end_time`` with ``HH:MM`` 24-hour times.
    """
    if not available_days:
        return False
    now = when or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    weekday = now.strftime("%A")
    tnow = now.timetz().replace(tzinfo=None) if now.tzinfo else now.time()

    for raw in available_days:
        if not isinstance(raw, dict):
            continue
        day = _normalize_day(str(raw.get("day", "")))
        if day != weekday:
            continue
        start = _parse_hhmm(str(raw.get("start_time", "")))
        end = _parse_hhmm(str(raw.get("end_time", "")))
        if start is None or end is None:
            continue
        if start <= end:
            if start <= tnow <= end:
                return True
        else:
            # overnight window (e.g. 22:00–06:00)
            if tnow >= start or tnow <= end:
                return True
    return False


def is_listing_complete_for_public(profile: Any) -> bool:
    """Minimum data required before geo + schedule visibility rules apply."""
    if not bool(getattr(profile, "is_listing_verified", False)):
        return False
    if profile.latitude is None or profile.longitude is None:
        return False
    if profile.service_radius_km is None or float(profile.service_radius_km) <= 0:
        return False
    cats = profile.category_ids or []
    if not isinstance(cats, list) or len(cats) == 0:
        return False
    days = profile.available_days or []
    if not isinstance(days, list) or len(days) == 0:
        return False
    return True
