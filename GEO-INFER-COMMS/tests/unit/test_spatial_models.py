"""Tests for COMMS spatial data models."""

import pytest

from geo_infer_comms.models.spatial import (
    GeospatialPoint,
    SpatialIndex,
    buffer_point,
    calculate_distance,
    create_bounds_from_points,
    geojson_to_geospatial_point,
    geospatial_point_to_geojson,
)


class TestGeospatialPoint:
    def test_create_valid_point(self):
        pt = GeospatialPoint(longitude=-122.4, latitude=37.7)
        assert pt.longitude == -122.4
        assert pt.latitude == 37.7

    def test_create_point_with_altitude(self):
        pt = GeospatialPoint(longitude=0.0, latitude=0.0, altitude=100.0)
        assert pt.altitude == 100.0

    def test_invalid_latitude_raises(self):
        with pytest.raises(ValueError):
            GeospatialPoint(longitude=0.0, latitude=91.0)

    def test_invalid_longitude_raises(self):
        with pytest.raises(ValueError):
            GeospatialPoint(longitude=181.0, latitude=0.0)

    def test_to_dict(self):
        pt = GeospatialPoint(longitude=-122.4, latitude=37.7)
        d = pt.to_dict()
        assert d["longitude"] == -122.4
        assert d["latitude"] == 37.7

    def test_from_dict(self):
        data = {"longitude": 10.0, "latitude": 20.0}
        pt = GeospatialPoint.from_dict(data)
        assert pt.longitude == 10.0
        assert pt.latitude == 20.0

    def test_distance_to_same_point(self):
        pt = GeospatialPoint(longitude=0.0, latitude=0.0)
        assert pt.distance_to(pt) == 0.0

    def test_haversine_distance(self):
        ny = GeospatialPoint(longitude=-74.006, latitude=40.7128)
        la = GeospatialPoint(longitude=-118.2437, latitude=34.0522)
        dist = ny.distance_to(la)
        # NY to LA is roughly 3,940 km
        assert 3_500_000 < dist < 4_500_000

    def test_euclidean_distance(self):
        pt1 = GeospatialPoint(longitude=0.0, latitude=0.0)
        pt2 = GeospatialPoint(longitude=1.0, latitude=1.0)
        dist = pt1.distance_to(pt2, method="euclidean")
        assert dist > 0

    def test_unknown_method_raises(self):
        pt1 = GeospatialPoint(longitude=0.0, latitude=0.0)
        pt2 = GeospatialPoint(longitude=1.0, latitude=1.0)
        with pytest.raises(ValueError):
            pt1.distance_to(pt2, method="unknown")


class TestSpatialIndex:
    def test_create_index(self):
        idx = SpatialIndex()
        assert idx is not None

    def test_insert_and_index(self):
        idx = SpatialIndex()
        pt = GeospatialPoint(longitude=10.0, latitude=20.0)
        idx.insert(pt, "item-1")
        # SpatialIndex should be able to store items
        assert len(idx._index) > 0

    def test_clear(self):
        idx = SpatialIndex()
        pt = GeospatialPoint(longitude=10.0, latitude=20.0)
        idx.insert(pt, "item-1")
        idx.clear()
        assert len(idx._index) == 0


class TestSpatialHelperFunctions:
    def test_calculate_distance_matches_point_distance_to(self):
        ny = GeospatialPoint(longitude=-74.006, latitude=40.7128)
        la = GeospatialPoint(longitude=-118.2437, latitude=34.0522)
        assert calculate_distance(ny, la) == ny.distance_to(la)

    def test_create_bounds_envelopes_points(self):
        points = [
            GeospatialPoint(longitude=2.35, latitude=48.85),
            GeospatialPoint(longitude=13.4, latitude=52.52),
            GeospatialPoint(longitude=-0.12, latitude=51.5),
        ]
        bounds = create_bounds_from_points(points)
        assert bounds.min_longitude == -0.12
        assert bounds.max_longitude == 13.4
        assert bounds.min_latitude == 48.85
        assert bounds.max_latitude == 52.52

    def test_create_bounds_from_empty_list_raises(self):
        with pytest.raises(ValueError, match="empty point list"):
            create_bounds_from_points([])

    def test_buffer_at_equator_uses_flat_degree_conversion(self):
        pt = GeospatialPoint(longitude=0.0, latitude=0.0)
        bounds = buffer_point(pt, 111_000)
        # Documented equator approximation: 1 degree ~= 111,000 m.
        assert bounds.max_longitude == pytest.approx(1.0)
        assert bounds.max_latitude == pytest.approx(1.0)
        assert bounds.min_longitude == pytest.approx(-1.0)
        assert bounds.min_latitude == pytest.approx(-1.0)

    def test_buffer_lon_delta_scales_with_latitude(self):
        equator = buffer_point(GeospatialPoint(longitude=0.0, latitude=0.0), 111_000)
        high_lat = buffer_point(GeospatialPoint(longitude=0.0, latitude=60.0), 111_000)
        # Same distance needs ~2x the longitude degrees at 60 degrees north,
        # where a longitude degree covers only cos(60) of the equator meterage.
        assert equator.max_longitude == pytest.approx(1.0)
        assert high_lat.max_longitude == pytest.approx(2.0)
        assert high_lat.min_longitude == pytest.approx(-2.0)
        # Latitude dimensions stay at the flat 111,000 m-per-degree conversion.
        assert high_lat.min_latitude == pytest.approx(59.0)
        assert high_lat.max_latitude == pytest.approx(61.0)

    def test_buffer_preserves_point_crs(self):
        pt = GeospatialPoint(longitude=0.0, latitude=0.0)
        assert buffer_point(pt, 1000).crs == pt.crs

    def test_geojson_point_round_trip(self):
        pt = GeospatialPoint(longitude=13.4050, latitude=52.5200, altitude=34.0)
        geojson = geospatial_point_to_geojson(pt)
        assert geojson == {
            "type": "Point",
            "coordinates": [13.4050, 52.5200, 34.0],
        }
        restored = geojson_to_geospatial_point(geojson)
        assert restored == pt

    def test_geojson_point_without_altitude_round_trips(self):
        geojson = {"type": "Point", "coordinates": [13.4050, 52.5200]}
        pt = geojson_to_geospatial_point(geojson)
        assert pt.altitude is None
        assert geospatial_point_to_geojson(pt)["coordinates"] == [13.4050, 52.5200]

    def test_non_point_geometry_rejected(self):
        line = {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}
        with pytest.raises(ValueError, match="must be a Point"):
            geojson_to_geospatial_point(line)

    def test_invalid_geojson_rejected(self):
        with pytest.raises(ValueError, match="Invalid GeoJSON"):
            geojson_to_geospatial_point({"type": "Point", "coordinates": "oops"})
