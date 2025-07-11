import unittest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from geo_infer_space.core.spatial_processor import SpatialProcessor

class TestSpatialProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = SpatialProcessor()
        self.gdf = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)])
        self.gdf2 = gpd.GeoDataFrame(geometry=[Polygon([(0,0), (2,0), (2,2), (0,2)])])

    def test_buffer_analysis(self):
        buffered = self.processor.buffer_analysis(self.gdf, 1.0)
        self.assertEqual(len(buffered), 2)
        self.assertGreater(buffered.geometry.area.mean(), 0)

    def test_proximity_analysis(self):
        proximity = self.processor.proximity_analysis(self.gdf, self.gdf2)
        self.assertIn('min_distance', proximity)
        self.assertEqual(proximity['min_distance'], 0) 