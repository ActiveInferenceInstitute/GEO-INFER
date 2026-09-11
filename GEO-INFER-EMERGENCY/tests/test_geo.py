"""Tests for shared geodesic helpers."""

import pytest

from geo_infer_emergency.core.geo import haversine_distance_km


class TestHaversineDistanceKm:
    """GS-155: missing coordinates must raise, not map to (0, 0)."""

    def test_missing_lon_raises(self) -> None:
        """A point missing 'lon' raises ValueError naming the keys."""
        with pytest.raises(ValueError, match="missing coordinate key"):
            haversine_distance_km({"lat": 45.5}, {"lat": 45.6, "lon": -122.6})

    def test_missing_lat_raises(self) -> None:
        """A point missing 'lat' raises ValueError naming the keys."""
        with pytest.raises(ValueError, match="missing coordinate key"):
            haversine_distance_km({"lat": 45.5, "lon": -122.6}, {"lon": -122.6})

    def test_error_lists_found_keys(self) -> None:
        """The error message lists the keys actually present."""
        with pytest.raises(ValueError, match="'lat'"):
            haversine_distance_km({"lat": 45.5}, {"lat": 45.6, "lon": -122.6})

    def test_complete_points_return_smoke_value(self) -> None:
        """SKILL smoke command value: ~11.119 km between the two points."""
        distance = haversine_distance_km(
            {"lat": 45.5, "lon": -122.6}, {"lat": 45.6, "lon": -122.6}
        )
        assert round(distance, 3) == 11.119

    def test_identical_points_return_zero(self) -> None:
        """Identical complete points yield zero distance."""
        point = {"lat": 45.5, "lon": -122.6}
        assert haversine_distance_km(point, point) == 0.0
