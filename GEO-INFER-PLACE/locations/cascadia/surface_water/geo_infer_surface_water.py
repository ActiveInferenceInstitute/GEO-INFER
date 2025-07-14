"""
GeoInfer Surface Water Module

This module analyzes surface water resources (lakes, rivers, etc.) within
an H3 grid by using data from the USGS National Hydrography Dataset.
"""
import logging
from typing import Dict, List, Any, Tuple
import geopandas as gpd
from shapely.geometry import Polygon, box

from .data_sources import CascadianSurfaceWaterDataSources
from geo_infer_space.utils.h3_utils import cell_to_latlng_boundary

logger = logging.getLogger(__name__)

class GeoInferSurfaceWater:
    """
    Analyzes surface water features by quantifying the area of water bodies
    and the length of flowlines within H3 hexagons.
    """

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.data_source = CascadianSurfaceWaterDataSources()
        logger.info(f"Initialized GeoInferSurfaceWater with resolution {self.resolution}")

    def _get_analysis_bbox(self, target_hexagons: List[str]) -> Tuple[float, float, float, float]:
        """Calculates the total bounding box for a list of H3 hexagons."""
        polygons = [Polygon(cell_to_latlng_boundary(h)) for h in target_hexagons]
        min_lons, min_lats, max_lons, max_lats = [], [], [], []
        for p in polygons:
            min_lon, min_lat, max_lon, max_lat = p.bounds
            min_lons.append(min_lon)
            min_lats.append(min_lat)
            max_lons.append(max_lon)
            max_lats.append(max_lat)
        return (min(min_lons), min(min_lats), max(max_lons), max(max_lats))

    def run_analysis(self, target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calculates the area of water bodies and length of flowlines for each hexagon.
        """
        logger.info(f"Starting surface water analysis for {len(target_hexagons)} hexagons.")
        
        # 1. Get the bounding box for all hexagons
        analysis_bbox = self._get_analysis_bbox(target_hexagons)

        # 2. Fetch all surface water features from NHD
        nhd_data = self.data_source.fetch_surface_water_features(analysis_bbox)
        flowlines_gdf = nhd_data.get('flowlines')
        waterbodies_gdf = nhd_data.get('waterbodies')

        if flowlines_gdf.empty and waterbodies_gdf.empty:
            logger.warning("No surface water features found in the target area.")
            return {hex_id: {'water_body_area_sqkm': 0, 'flowline_length_km': 0} for hex_id in target_hexagons}

        # 3. Create a GeoDataFrame for the target hexagons
        hex_geometries = [Polygon(cell_to_latlng_boundary(h)) for h in target_hexagons]
        hex_gdf = gpd.GeoDataFrame(
            {'hex_id': target_hexagons}, 
            geometry=hex_geometries, 
            crs="EPSG:4326"
        )
        
        # 4. Initialize results
        results = {hex_id: {'water_body_area_sqkm': 0, 'flowline_length_km': 0} for hex_id in target_hexagons}
        
        # 5. Analyze water bodies (polygons)
        if not waterbodies_gdf.empty:
            waterbodies_gdf = waterbodies_gdf.to_crs(hex_gdf.crs)
            logger.info("Intersecting hexagons with water bodies...")
            intersected_wb = gpd.overlay(hex_gdf, waterbodies_gdf, how='intersection')
            
            if not intersected_wb.empty:
                # Project to an equal-area projection for accurate area calculation
                intersected_wb_proj = intersected_wb.to_crs('EPSG:3310')
                intersected_wb_proj['area_sqkm'] = intersected_wb_proj.geometry.area / 1_000_000
                
                area_by_hex = intersected_wb_proj.groupby('hex_id')['area_sqkm'].sum()
                for hex_id, area in area_by_hex.items():
                    results[hex_id]['water_body_area_sqkm'] = round(area, 4)

        # 6. Analyze flowlines (linestrings)
        if not flowlines_gdf.empty:
            flowlines_gdf = flowlines_gdf.to_crs(hex_gdf.crs)
            logger.info("Intersecting hexagons with flowlines...")
            intersected_fl = gpd.overlay(hex_gdf, flowlines_gdf, how='intersection', keep_geom_type=False)
            
            if not intersected_fl.empty:
                # Project to an equal-area projection for accurate length calculation
                intersected_fl_proj = intersected_fl.to_crs('EPSG:3310')
                intersected_fl_proj['length_km'] = intersected_fl_proj.geometry.length / 1000

                length_by_hex = intersected_fl_proj.groupby('hex_id')['length_km'].sum()
                for hex_id, length in length_by_hex.items():
                    results[hex_id]['flowline_length_km'] = round(length, 4)

        logger.info(f"Completed surface water analysis for {len(target_hexagons)} hexagons.")
        return results 