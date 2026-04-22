from __future__ import annotations

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
