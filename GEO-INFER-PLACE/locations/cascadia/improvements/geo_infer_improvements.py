"""
GeoInfer Improvements Module

This module analyzes agricultural improvement data within an H3 grid.
"""
import logging
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from .data_sources import CascadianImprovementsDataSources
from geo_infer_space.utils.h3_utils import h3_to_geo_boundary

logger = logging.getLogger(__name__)

class GeoInferImprovements:
    """Processes and analyzes improvements data within an H3 grid."""

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.improvements_data_source = CascadianImprovementsDataSources()
        logger.info(f"Initialized GeoInferImprovements with resolution {resolution}")

    def run_analysis(self, target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Spatially joins building footprint data with H3 hexagons and calculates metrics.
        This is the main entry point for the module.
        """
        logger.info(f"Starting improvements analysis for {len(target_hexagons)} hexagons.")
        
        # 1. Fetch building footprint data
        improvements_gdf = self.improvements_data_source.fetch_all_improvements_data(target_hexagons=target_hexagons)
        if improvements_gdf.empty:
            logger.warning("No improvements data found. Aborting analysis.")
            return {}

        # 2. Create a GeoDataFrame for the target hexagons
        hex_geometries = [Polygon(h3_to_geo_boundary(h)) for h in target_hexagons]
        hex_gdf = gpd.GeoDataFrame(
            {'hex_id': target_hexagons}, 
            geometry=hex_geometries, 
            crs="EPSG:4326"
        )
        
        # 3. Ensure CRS alignment
        improvements_gdf = improvements_gdf.to_crs(hex_gdf.crs)

        # 4. Perform the spatial join
        logger.info("Performing spatial join between hexagons and building footprints...")
        # Use 'intersects' as buildings can span multiple hexagons
        joined_gdf = gpd.sjoin(hex_gdf, improvements_gdf, how="inner", predicate="intersects")
        
        if joined_gdf.empty:
            logger.warning("Spatial join resulted in no matches between hexagons and improvements data.")
            return {}

        # 5. Aggregate results and calculate metrics
        imp_val_col = 'improvement_value'
        land_val_col = 'land_value'

        logger.info("Aggregating improvements results per hexagon...")
        h3_improvements = {}
        for hex_id, group in joined_gdf.groupby('hex_id'):
            total_imp_value = group[imp_val_col].sum()
            total_land_value = group[land_val_col].sum()
            
            # Improvement-to-Land Value Ratio
            imp_to_land_ratio = (total_imp_value / total_land_value) if total_land_value > 0 else 0

            # Calculate a modernization score based on value ratio
            # This is a heuristic: very high or low ratios could be interesting
            modernization_score = 1 - abs(imp_to_land_ratio - 0.5) * 2
            
            h3_improvements[hex_id] = {
                'total_improvement_value': total_imp_value,
                'total_land_value': total_land_value,
                'improvement_to_land_value_ratio': imp_to_land_ratio,
                'number_of_improvements': len(group),
                'modernization_score': max(0, modernization_score) # Ensure score is not negative
            }

        logger.info(f"Completed improvements analysis. Processed {len(h3_improvements)} hexagons.")
        return h3_improvements 