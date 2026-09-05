"""Tests for geo_infer_sec.utils.geospatial_utils (physical-security helper)."""

import math
import unittest

from shapely.geometry import Point

from geo_infer_sec.utils.geospatial_utils import GeoSpatialUtils


class TestCreateCircle(unittest.TestCase):
    def test_radius_is_metrically_accurate(self):
        circle = GeoSpatialUtils().create_circle(Point(-118.24, 34.05), 1000.0)
        center = Point(-118.24, 34.05)
        for vertex in circle.exterior.coords:
            lat1, lon1 = math.radians(34.05), math.radians(-118.24)
            lat2, lon2 = math.radians(vertex[1]), math.radians(vertex[0])
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            )
            distance = 2 * 6_371_000 * math.asin(math.sqrt(a))
            self.assertAlmostEqual(distance, 1000.0, delta=5.0)

    def test_validates_inputs(self):
        utils = GeoSpatialUtils()
        with self.assertRaises(ValueError):
            utils.create_circle(Point(0, 0), 0)
        with self.assertRaises(ValueError):
            utils.create_circle(Point(0, 0), 100.0, num_points=2)
