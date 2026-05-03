from __future__ import annotations

import math
from typing import Any

from sqlalchemy import Float, cast, func

def haversine_distance_km_sql(
    lat_col: Any,
    lon_col: Any,
    search_lat: float,
    search_lon: float,
) -> Any:
    """SQL expression for great-circle distance in km (WGS84 mean radius)."""
    lat1 = cast(lat_col, Float)
    lon1 = cast(lon_col, Float)
    lat2 = float(search_lat)
    lon2 = float(search_lon)

    dlat = func.radians(lat1 - lat2) / 2
    dlon = func.radians(lon1 - lon2) / 2
    a = func.pow(func.sin(dlat), 2) + func.cos(func.radians(lat1)) * func.cos(
        func.radians(lat2)
    ) * func.pow(func.sin(dlon), 2)
    c = 2 * func.asin(func.sqrt(func.least(1.0, a)))
    return 6371.0 * c


def haversine_between_sql(lat1_col: Any, lon1_col: Any, lat2_col: Any, lon2_col: Any) -> Any:
    """Great-circle distance in km between two WGS84 points given as SQL columns (degrees)."""
    lat1 = cast(lat1_col, Float)
    lon1 = cast(lon1_col, Float)
    lat2 = cast(lat2_col, Float)
    lon2 = cast(lon2_col, Float)
    dlat = func.radians(lat2 - lat1) / 2
    dlon = func.radians(lon2 - lon1) / 2
    a = func.pow(func.sin(dlat), 2) + func.cos(func.radians(lat1)) * func.cos(
        func.radians(lat2)
    ) * func.pow(func.sin(dlon), 2)
    c = 2 * func.asin(func.sqrt(func.least(1.0, a)))
    return 6371.0 * c


def haversine_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """Great-circle distance in km (float coordinates, degrees)."""
    r = 6371.0
    p1 = math.radians(a_lat)
    p2 = math.radians(b_lat)
    dlat = math.radians(b_lat - a_lat)
    dlon = math.radians(b_lon - a_lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(h)))
