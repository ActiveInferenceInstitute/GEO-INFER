"""Shared geodesic helpers.

Single owner for geo distance calculations used across the emergency
management core (resource travel-time estimation, SAR pattern metrics).
"""
import math
from typing import Dict

# Mean Earth radius in kilometres (spherical approximation).
EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(
    point_a: Dict[str, float],
    point_b: Dict[str, float]
) -> float:
    """
    Great-circle distance between two points in kilometres.

    Args:
        point_a: {"lat": float, "lon": float} in decimal degrees
        point_b: {"lat": float, "lon": float} in decimal degrees

    Returns:
        Distance in kilometres (Haversine formula, spherical Earth).
    """
    lat1 = math.radians(point_a.get("lat", 0.0))
    lon1 = math.radians(point_a.get("lon", 0.0))
    lat2 = math.radians(point_b.get("lat", 0.0))
    lon2 = math.radians(point_b.get("lon", 0.0))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS_KM * c
