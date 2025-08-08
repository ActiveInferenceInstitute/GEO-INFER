"""
GeoInfer Surface Water Module

This module analyzes surface water resources (lakes, rivers, etc.) within
an H3 grid by using data from the USGS National Hydrography Dataset.
"""
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from .data_sources import CascadianSurfaceWaterDataSources
from geo_infer_space.utils.h3_utils import cell_to_latlng_boundary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geo_infer_place.core.unified_backend import CascadianAgriculturalH3Backend

logger = logging.getLogger(__name__)

class GeoInferSurfaceWater:
    """
    Analyzes surface water features by quantifying the area of water bodies
    and the length of flowlines within H3 hexagons.
    """

    module_name: str = "surface_water"

    def __init__(self, backend: "CascadianAgriculturalH3Backend"):
        self.backend = backend
        self.resolution = getattr(backend, "h3_resolution", 8)
        self.target_hexagons = list(getattr(backend, "target_hexagons", []))
        self.data_source = CascadianSurfaceWaterDataSources()
        # Will be injected
        self.data_manager = None  # type: ignore[attr-defined]
        self.h3_fusion = None  # type: ignore[attr-defined]
        logger.info(f"Initialized GeoInferSurfaceWater with resolution {self.resolution}")

    def acquire_raw_data(self) -> Path:
        """Acquire and cache raw NHD flowlines/waterbodies for target area."""
        if not hasattr(self, "data_manager") or self.data_manager is None:
            raw_out = Path("output/data/raw_surface_water_data.geojson")
        else:
            paths = self.data_manager.get_data_structure(self.module_name)  # type: ignore[union-attr]
            raw_out = paths['raw_data']

        if raw_out.exists():
            return raw_out

        bbox = self._get_analysis_bbox(self.target_hexagons)
        nhd = self.data_source.fetch_surface_water_features(bbox)
        waterbodies = nhd.get('waterbodies') or gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        flowlines = nhd.get('flowlines') or gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")

        frames = []
        if not waterbodies.empty:
            waterbodies['layer'] = 'waterbodies'
            frames.append(waterbodies)
        if not flowlines.empty:
            # Buffer lines to narrow polygons for H3 polygon processing
            try:
                fproj = flowlines.to_crs('EPSG:3310')
                fproj['geometry'] = fproj.buffer(10)  # ~10m buffer
                flowlines = fproj.to_crs('EPSG:4326')
            except Exception:
                pass
            flowlines['layer'] = 'flowlines'
            frames.append(flowlines)
        gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True)) if frames else gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
        raw_out.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_file(raw_out, driver='GeoJSON')
        return raw_out

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

    def run_final_analysis(self, h3_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize H3-indexed water features into per-hex metrics if provided as features."""
        results: Dict[str, Any] = {}
        for hex_id, items in h3_data.items():
            try:
                df = pd.DataFrame(items) if isinstance(items, list) else pd.DataFrame()
                wb = int((df.get('layer') == 'waterbodies').sum()) if not df.empty else 0
                fl = int((df.get('layer') == 'flowlines').sum()) if not df.empty else 0
                results[hex_id] = {
                    'has_water': wb > 0 or fl > 0,
                    'waterbody_feature_count': wb,
                    'flowline_feature_count': fl
                }
            except Exception:
                results[hex_id] = {
                    'has_water': False,
                    'waterbody_feature_count': 0,
                    'flowline_feature_count': 0
                }
        return results