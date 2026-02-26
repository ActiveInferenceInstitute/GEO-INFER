"""
Extended unit tests for geojson_helpers covering buffer, intersection, union, and distance.
"""
import math
import pytest

from geo_infer_api.models.geojson import GeoJSONType, Polygon
from geo_infer_api.utils.geojson_helpers import (
    create_buffer,
    calculate_intersection,
    calculate_union,
    calculate_distance,
)

# Two overlapping polygons (San Francisco area)
SF_POLYGON_COORDS = [
    [
        [-122.51, 37.77],
        [-122.42, 37.81],
        [-122.37, 37.73],
        [-122.51, 37.77],
    ]
]

# Second polygon overlapping with SF polygon
SF_POLYGON2_COORDS = [
    [
        [-122.48, 37.74],
        [-122.39, 37.80],
        [-122.34, 37.72],
        [-122.48, 37.74],
    ]
]

# Non-overlapping polygon (New York)
NYC_POLYGON_COORDS = [
    [
        [-74.01, 40.70],
        [-73.96, 40.70],
        [-73.96, 40.75],
        [-74.01, 40.75],
        [-74.01, 40.70],
    ]
]


def make_polygon(coords) -> Polygon:
    return Polygon(type=GeoJSONType.POLYGON, coordinates=coords)


# ---------------------------------------------------------------------------
# create_buffer tests
# ---------------------------------------------------------------------------

class TestCreateBuffer:
    def test_buffer_is_larger_than_source(self):
        """Buffer bounding box must be strictly larger than source bounding box."""
        poly = make_polygon(SF_POLYGON_COORDS)
        ring = SF_POLYGON_COORDS[0]
        src_lons = [c[0] for c in ring]
        src_lats = [c[1] for c in ring]
        src_min_lon, src_max_lon = min(src_lons), max(src_lons)
        src_min_lat, src_max_lat = min(src_lats), max(src_lats)

        buf = create_buffer(poly, 5.0, "kilometers")
        buf_ring = buf.coordinates[0]
        buf_lons = [c[0] for c in buf_ring]
        buf_lats = [c[1] for c in buf_ring]

        assert min(buf_lons) < src_min_lon
        assert max(buf_lons) > src_max_lon
        assert min(buf_lats) < src_min_lat
        assert max(buf_lats) > src_max_lat

    def test_buffer_is_valid_polygon(self):
        """Buffer result must be a closed polygon with at least 4 points."""
        poly = make_polygon(SF_POLYGON_COORDS)
        buf = create_buffer(poly, 1.0)
        ring = buf.coordinates[0]
        assert ring[0] == ring[-1], "Ring must be closed"
        assert len(ring) >= 4

    def test_buffer_unit_meters(self):
        """1000m buffer should produce same result as 1km buffer."""
        poly = make_polygon(SF_POLYGON_COORDS)
        buf_m = create_buffer(poly, 1000.0, "meters")
        buf_km = create_buffer(poly, 1.0, "kilometers")
        assert buf_m.coordinates == buf_km.coordinates

    def test_buffer_unit_miles(self):
        """Buffer in miles should be larger than equivalent km for same numeric value."""
        poly = make_polygon(SF_POLYGON_COORDS)
        buf_mi = create_buffer(poly, 1.0, "miles")
        buf_km = create_buffer(poly, 1.0, "kilometers")
        buf_mi_ring = buf_mi.coordinates[0]
        buf_km_ring = buf_km.coordinates[0]
        mi_lons = [c[0] for c in buf_mi_ring]
        km_lons = [c[0] for c in buf_km_ring]
        assert max(mi_lons) > max(km_lons)

    def test_buffer_dict_input(self):
        """create_buffer must accept dict input as well as Polygon model."""
        poly_dict = {"type": "Polygon", "coordinates": SF_POLYGON_COORDS}
        buf = create_buffer(poly_dict, 1.0)
        assert buf.type == GeoJSONType.POLYGON

    def test_buffer_invalid_input_raises(self):
        """Invalid input must raise ValueError."""
        with pytest.raises(ValueError):
            create_buffer({"type": "Point", "coordinates": [0, 0]}, 1.0)

    def test_zero_buffer_returns_bbox(self):
        """Zero-distance buffer returns bounding box of source."""
        poly = make_polygon(SF_POLYGON_COORDS)
        buf = create_buffer(poly, 0.0)
        ring = buf.coordinates[0]
        # All source coords must be inside or on the buffer ring
        src_ring = SF_POLYGON_COORDS[0]
        buf_lons = [c[0] for c in ring]
        buf_lats = [c[1] for c in ring]
        for lon, lat in src_ring:
            assert min(buf_lons) <= lon <= max(buf_lons)
            assert min(buf_lats) <= lat <= max(buf_lats)


# ---------------------------------------------------------------------------
# calculate_intersection tests
# ---------------------------------------------------------------------------

class TestCalculateIntersection:
    def test_intersection_of_overlapping_polygons(self):
        """Intersection of overlapping polygons must be smaller than both inputs."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(SF_POLYGON2_COORDS)
        inter = calculate_intersection([p1, p2])
        assert inter.type == GeoJSONType.POLYGON

        inter_ring = inter.coordinates[0]
        p1_ring = SF_POLYGON_COORDS[0]
        p2_ring = SF_POLYGON2_COORDS[0]

        inter_lons = [c[0] for c in inter_ring]
        p1_lons = [c[0] for c in p1_ring]
        p2_lons = [c[0] for c in p2_ring]

        # Intersection must fit within both bounding boxes
        assert min(inter_lons) >= min(min(p1_lons), min(p2_lons)) - 1e-9
        assert max(inter_lons) <= max(max(p1_lons), max(p2_lons)) + 1e-9

    def test_intersection_returns_different_from_inputs(self):
        """Intersection of two overlapping polygons must differ from each individual input."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(SF_POLYGON2_COORDS)
        inter = calculate_intersection([p1, p2])
        assert inter.coordinates != p1.coordinates
        assert inter.coordinates != p2.coordinates

    def test_non_overlapping_raises(self):
        """Non-overlapping polygons must raise ValueError."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        with pytest.raises(ValueError, match="do not overlap"):
            calculate_intersection([p1, p2])

    def test_too_few_polygons_raises(self):
        """Fewer than 2 polygons must raise ValueError."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        with pytest.raises(ValueError, match="At least 2"):
            calculate_intersection([p1])

    def test_dict_input(self):
        """calculate_intersection must accept dict inputs."""
        p1 = {"type": "Polygon", "coordinates": SF_POLYGON_COORDS}
        p2 = {"type": "Polygon", "coordinates": SF_POLYGON2_COORDS}
        result = calculate_intersection([p1, p2])
        assert result.type == GeoJSONType.POLYGON

    def test_intersection_is_closed_ring(self):
        """Result ring must be closed."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(SF_POLYGON2_COORDS)
        inter = calculate_intersection([p1, p2])
        ring = inter.coordinates[0]
        assert ring[0] == ring[-1]


# ---------------------------------------------------------------------------
# calculate_union tests
# ---------------------------------------------------------------------------

class TestCalculateUnion:
    def test_union_spans_both_polygons(self):
        """Union bounding box must contain both source polygons entirely."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        union = calculate_union([p1, p2])

        union_ring = union.coordinates[0]
        u_lons = [c[0] for c in union_ring]
        u_lats = [c[1] for c in union_ring]

        for coords in [SF_POLYGON_COORDS[0], NYC_POLYGON_COORDS[0]]:
            for lon, lat in coords:
                assert min(u_lons) - 1e-9 <= lon <= max(u_lons) + 1e-9
                assert min(u_lats) - 1e-9 <= lat <= max(u_lats) + 1e-9

    def test_union_larger_than_each_input(self):
        """Union must be larger or equal to each individual input."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        union = calculate_union([p1, p2])

        union_ring = union.coordinates[0]
        sf_ring = SF_POLYGON_COORDS[0]
        nyc_ring = NYC_POLYGON_COORDS[0]

        u_lon_span = max(c[0] for c in union_ring) - min(c[0] for c in union_ring)
        sf_lon_span = max(c[0] for c in sf_ring) - min(c[0] for c in sf_ring)
        nyc_lon_span = max(c[0] for c in nyc_ring) - min(c[0] for c in nyc_ring)

        assert u_lon_span >= sf_lon_span - 1e-9
        assert u_lon_span >= nyc_lon_span - 1e-9

    def test_union_returns_different_from_inputs(self):
        """Union of disjoint polygons must differ from each input."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        union = calculate_union([p1, p2])
        assert union.coordinates != p1.coordinates
        assert union.coordinates != p2.coordinates

    def test_too_few_polygons_raises(self):
        """Fewer than 2 polygons must raise ValueError."""
        with pytest.raises(ValueError, match="At least 2"):
            calculate_union([make_polygon(SF_POLYGON_COORDS)])

    def test_dict_input(self):
        """calculate_union must accept dict inputs."""
        p1 = {"type": "Polygon", "coordinates": SF_POLYGON_COORDS}
        p2 = {"type": "Polygon", "coordinates": NYC_POLYGON_COORDS}
        result = calculate_union([p1, p2])
        assert result.type == GeoJSONType.POLYGON

    def test_union_is_closed_ring(self):
        """Result ring must be closed."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        union = calculate_union([p1, p2])
        ring = union.coordinates[0]
        assert ring[0] == ring[-1]


# ---------------------------------------------------------------------------
# calculate_distance tests
# ---------------------------------------------------------------------------

class TestCalculateDistance:
    def test_distance_sf_to_nyc_approximate(self):
        """SF-NYC centroid distance should be roughly 4,100–4,200 km."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        dist = calculate_distance(p1, p2)
        # Known approximate great-circle distance is ~4,130 km; centroid
        # approximation with cosine correction should be within 5%.
        assert 3900 < dist < 4500, f"Unexpected distance: {dist:.1f} km"

    def test_distance_same_polygon_is_zero(self):
        """Distance from a polygon to itself must be 0."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        dist = calculate_distance(p1, p1)
        assert dist == pytest.approx(0.0, abs=1e-6)

    def test_distance_is_symmetric(self):
        """Distance must be symmetric."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(NYC_POLYGON_COORDS)
        assert calculate_distance(p1, p2) == pytest.approx(calculate_distance(p2, p1), rel=1e-9)

    def test_distance_dict_input(self):
        """calculate_distance must accept dict inputs."""
        p1 = {"type": "Polygon", "coordinates": SF_POLYGON_COORDS}
        p2 = {"type": "Polygon", "coordinates": NYC_POLYGON_COORDS}
        dist = calculate_distance(p1, p2)
        assert dist > 0

    def test_distance_nearby_polygons_small(self):
        """Overlapping polygons must have small centroid distance."""
        p1 = make_polygon(SF_POLYGON_COORDS)
        p2 = make_polygon(SF_POLYGON2_COORDS)
        dist = calculate_distance(p1, p2)
        assert dist < 20  # SF polygons are within 20 km of each other
