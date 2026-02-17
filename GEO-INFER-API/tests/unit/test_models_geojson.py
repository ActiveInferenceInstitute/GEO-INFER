"""Tests for GeoJSON Pydantic models."""

import pytest
from pydantic import ValidationError
from geo_infer_api.models.geojson import (
    GeoJSONType,
    Point,
    LineString,
    Polygon,
    Feature,
    FeatureCollection,
    PolygonFeature,
    PolygonFeatureCollection,
)


class TestPoint:
    def test_valid_point(self):
        p = Point(coordinates=(-73.9857, 40.7484))
        assert p.type == GeoJSONType.POINT
        assert p.coordinates == (-73.9857, 40.7484)

    def test_invalid_longitude(self):
        with pytest.raises(ValidationError):
            Point(coordinates=(200.0, 40.0))

    def test_invalid_latitude(self):
        with pytest.raises(ValidationError):
            Point(coordinates=(0.0, 100.0))


class TestLineString:
    def test_valid_linestring(self):
        ls = LineString(coordinates=[(-73.9, 40.7), (-74.0, 40.8)])
        assert ls.type == GeoJSONType.LINE_STRING
        assert len(ls.coordinates) == 2

    def test_too_few_points(self):
        with pytest.raises(ValidationError):
            LineString(coordinates=[(-73.9, 40.7)])


class TestPolygon:
    def test_valid_polygon(self):
        ring = [(0, 0), (1, 0), (1, 1), (0, 0)]
        p = Polygon(coordinates=[ring])
        assert p.type == GeoJSONType.POLYGON

    def test_unclosed_ring(self):
        with pytest.raises(ValidationError):
            Polygon(coordinates=[[(0, 0), (1, 0), (1, 1), (0, 1)]])

    def test_too_few_coords(self):
        with pytest.raises(ValidationError):
            Polygon(coordinates=[[(0, 0), (1, 0), (0, 0)]])


class TestFeature:
    def test_feature_with_properties(self):
        f = Feature(properties={"name": "test"}, id="f1")
        assert f.type == GeoJSONType.FEATURE
        assert f.properties["name"] == "test"

    def test_feature_no_geometry(self):
        f = Feature()
        assert f.geometry is None


class TestPolygonFeature:
    def test_polygon_feature(self):
        ring = [(0, 0), (1, 0), (1, 1), (0, 0)]
        pf = PolygonFeature(
            geometry=Polygon(coordinates=[ring]),
            properties={"area": 0.5},
            id="pf1",
        )
        assert pf.geometry.type == GeoJSONType.POLYGON
        assert pf.id == "pf1"


class TestFeatureCollection:
    def test_collection(self):
        fc = FeatureCollection(features=[
            Feature(properties={"a": 1}),
            Feature(properties={"b": 2}),
        ])
        assert len(fc.features) == 2


class TestPolygonFeatureCollection:
    def test_polygon_collection(self):
        ring = [(0, 0), (1, 0), (1, 1), (0, 0)]
        pfc = PolygonFeatureCollection(features=[
            PolygonFeature(geometry=Polygon(coordinates=[ring]), properties={}, id="p1"),
        ])
        assert len(pfc.features) == 1
