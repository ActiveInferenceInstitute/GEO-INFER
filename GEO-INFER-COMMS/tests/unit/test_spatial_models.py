"""Tests for COMMS spatial data models."""
import math
import pytest

from geo_infer_comms.models.spatial import (
    GeospatialPoint,
    SpatialIndex,
    CoordinateSystem,
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
