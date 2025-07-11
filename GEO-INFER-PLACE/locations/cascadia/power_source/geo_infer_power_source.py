"""
GeoInfer Power Source Module

This module analyzes proximity and density of high-voltage transmission
lines within an H3 grid, using data from the HIFLD open data portal.
"""
import logging
from typing import Dict, List, Any
import geopandas as gpd
from shapely.geometry import Polygon

from .data_sources import CascadianPowerSourceDataSources
from geo_infer_space.utils.h3_utils import h3_to_geo_boundary

logger = logging.getLogger(__name__)

class GeoInferPowerSource:
    """Analyzes proximity to high-voltage power infrastructure."""

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.data_source = CascadianPowerSourceDataSources()
        logger.info(f"Initialized GeoInferPowerSource with resolution {self.resolution}")

    def run_analysis(self, target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calculates the density of transmission lines and average voltage
        for each H3 hexagon.

        Args:
            target_hexagons: A list of H3 hexagon IDs to analyze.

        Returns:
            A dictionary mapping H3 hexagons to their power source analysis.
        """
        logger.info(f"Starting power source analysis for {len(target_hexagons)} hexagons.")
        if not target_hexagons:
            return {}

        # 1. Fetch all power infrastructure data for the target area
        infra_data = self.data_source.fetch_power_infrastructure_features(target_hexagons)
        
        trans_lines_gdf = infra_data.get('transmission_lines')
        power_plants_gdf = infra_data.get('power_plants') # Available for future use

        if trans_lines_gdf is None or trans_lines_gdf.empty:
            logger.warning("No transmission line data found for the target area. Aborting analysis.")
            return {hex_id: {'transmission_line_km': 0, 'avg_voltage_kv': 0} for hex_id in target_hexagons}

        # 2. Create a GeoDataFrame for the target hexagons
        hex_geometries = [Polygon(h3_to_geo_boundary(h)) for h in target_hexagons]
        hex_gdf = gpd.GeoDataFrame(
            {'hex_id': target_hexagons}, 
            geometry=hex_geometries, 
            crs="EPSG:4326"
        )

        # 3. Ensure CRS alignment
        trans_lines_gdf = trans_lines_gdf.to_crs(hex_gdf.crs)

        # 4. Perform a spatial join (intersection)
        logger.info("Performing spatial join between hexagons and transmission lines...")
        # An intersection is needed to clip lines to the hexagon boundaries
        joined_gdf = gpd.overlay(hex_gdf, trans_lines_gdf, how='intersection', keep_geom_type=False)

        if joined_gdf.empty:
            logger.warning("Spatial join resulted in no matches. No hexagons contain transmission lines.")
            # Return a default "no grid" score for all hexagons
            return {hex_id: {'transmission_line_km': 0, 'avg_voltage_kv': 0} for hex_id in target_hexagons}

        # 5. Calculate metrics for each hexagon
        # Project to an equal-area projection to calculate length accurately
        joined_gdf_proj = joined_gdf.to_crs('EPSG:3310') # Albers Equal Area for North America
        joined_gdf_proj['line_length_km'] = joined_gdf_proj.geometry.length / 1000

        # The 'VOLTAGE' column might be named differently, we'll need to be robust.
        # Based on HIFLD data, it's typically 'VOLTAGE'.
        voltage_col = 'VOLTAGE'
        if voltage_col not in joined_gdf_proj.columns:
            logger.warning(f"'{voltage_col}' column not found in data. Voltage analysis will be skipped.")
            voltage_col = None

        h3_power = {}
        for hex_id, group in joined_gdf_proj.groupby('hex_id'):
            total_length_km = group['line_length_km'].sum()
            
            avg_voltage = 0
            if voltage_col:
                # Weighted average of voltage by line length
                avg_voltage = (group[voltage_col] * group['line_length_km']).sum() / total_length_km if total_length_km > 0 else 0

            h3_power[hex_id] = {
                'transmission_line_km': round(total_length_km, 2),
                'avg_voltage_kv': round(avg_voltage, 2)
            }
            
        # Add hexagons that had no intersecting lines with default zero values
        for hex_id in target_hexagons:
            if hex_id not in h3_power:
                h3_power[hex_id] = {'transmission_line_km': 0, 'avg_voltage_kv': 0}

        logger.info(f"Completed power source analysis for {len(target_hexagons)} hexagons.")
        return h3_power 