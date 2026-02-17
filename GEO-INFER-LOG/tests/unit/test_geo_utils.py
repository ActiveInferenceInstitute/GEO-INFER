"""Tests for geo utility module."""

import pytest
from geo_infer_log.utils.geo import (
    haversine_distance,
    get_bbox,
    coords_to_geojson,
    calculate_route_distance,
    get_centroid,
)


class TestHaversineDistance:
    """Tests for haversine distance calculation."""

    def test_same_point_returns_zero(self) -> None:
        d = haversine_distance((0.0, 0.0), (0.0, 0.0))
        assert abs(d) < 0.01

    def test_positive_distance(self) -> None:
        d = haversine_distance((0.0, 0.0), (1.0, 1.0))
        assert d > 0

    def test_known_distance(self) -> None:
        # New York (lon, lat) to Los Angeles (lon, lat) approx 3944 km
        nyc = (-74.006, 40.7128)
        lax = (-118.2437, 34.0522)
        d = haversine_distance(nyc, lax)
        assert 3900 < d < 4000

    def test_symmetric(self) -> None:
        a = (-73.9857, 40.7484)
        b = (2.3522, 48.8566)
        assert abs(haversine_distance(a, b) - haversine_distance(b, a)) < 0.01


class TestGetBbox:
    """Tests for bounding box calculation."""

    def test_single_point(self) -> None:
        bbox = get_bbox([(10.0, 20.0)])
        assert bbox[0] == 10.0  # min lon
        assert bbox[1] == 20.0  # min lat

    def test_with_buffer(self) -> None:
        bbox = get_bbox([(10.0, 20.0)], buffer=1.0)
        assert bbox[0] < 10.0
        assert bbox[1] < 20.0


class TestCoordsToGeojson:
    """Tests for coordinate-to-GeoJSON conversion."""

    def test_linestring(self) -> None:
        geojson = coords_to_geojson([(0, 0), (1, 1), (2, 2)])
        assert geojson["type"] == "Feature"
        assert geojson["geometry"]["type"] == "LineString"

    def test_point(self) -> None:
        geojson = coords_to_geojson([(5, 10)], geometry_type="Point")
        assert geojson["geometry"]["type"] == "Point"


class TestRouteDistance:
    """Tests for route distance calculation."""

    def test_empty_returns_zero(self) -> None:
        d = calculate_route_distance([])
        assert d == 0.0

    def test_single_point_returns_zero(self) -> None:
        d = calculate_route_distance([(0.0, 0.0)])
        assert d == 0.0

    def test_round_trip_distance(self) -> None:
        coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
        d = calculate_route_distance(coords)
        assert d > 0


class TestGetCentroid:
    """Tests for centroid calculation."""

    def test_single_point(self) -> None:
        c = get_centroid([(5.0, 10.0)])
        assert abs(c[0] - 5.0) < 0.01
        assert abs(c[1] - 10.0) < 0.01

    def test_symmetric_points(self) -> None:
        c = get_centroid([(0, 0), (2, 0), (0, 2), (2, 2)])
        assert abs(c[0] - 1.0) < 0.01
        assert abs(c[1] - 1.0) < 0.01
