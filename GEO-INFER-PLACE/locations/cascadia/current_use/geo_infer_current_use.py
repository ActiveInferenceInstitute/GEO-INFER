"""
GeoInferCurrentUse: Current Agricultural Use Analysis Module

Real-time agricultural land use classification and crop production analysis
with H3 spatial indexing and multi-temporal analysis capabilities.
"""

import logging
from typing import Dict, List, Any, Tuple
import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import Polygon
from collections import Counter

from .data_sources import CascadianCurrentUseDataSources
from utils_h3 import h3_to_geo_boundary

logger = logging.getLogger(__name__)

class GeoInferCurrentUse:
    def __init__(self, resolution: int):
        self.resolution = resolution
        self.data_source = CascadianCurrentUseDataSources()
        logger.info(f"Initialized GeoInferCurrentUse with resolution {resolution}")

    def run_analysis(self, target_hexagons: List[str], year: int = 2023) -> Dict[str, Dict[str, Any]]:
        """
        Generate H3-indexed current agricultural use classification from NASS CDL data.
        This is the main entry point for the module.
        
        Args:
            target_hexagons: A list of H3 hexagon IDs to analyze.
            year: The year for which to analyze data.
            
        Returns:
            A dictionary mapping H3 hexagon IDs to their current use analysis.
        """
        if not target_hexagons:
            logger.warning("No target hexagons provided for current use analysis.")
            return {}
            
        logger.info(f"Starting current use analysis for {len(target_hexagons)} hexagons for the year {year}.")
        
        # Data source now fetches and processes data for all hexagons in batches
        hex_crop_data = self.data_source.fetch_nass_cdl_data_for_hexagons(year, target_hexagons)
        
        if not hex_crop_data:
            logger.error(f"Could not retrieve any CDL data for year {year} and the given area. Aborting.")
            return {}

        h3_current_use = {}

        for h3_index, crop_percentages in hex_crop_data.items():
            try:
                if not crop_percentages:
                    continue

                # Sort by percentage to find the primary crop
                crop_percentages.sort(key=lambda x: x[1], reverse=True)
                primary_crop_code = crop_percentages[0][0]
                primary_crop_coverage = crop_percentages[0][1]
                
                primary_crop_info = self.data_source.get_crop_classification(primary_crop_code)
                
                h3_current_use[h3_index] = {
                    'primary_crop_code': int(primary_crop_code),
                    'primary_crop_name': primary_crop_info.name if primary_crop_info else 'Unknown',
                    'primary_crop_category': primary_crop_info.crop_category if primary_crop_info else 'Unknown',
                    'primary_crop_coverage': round(primary_crop_coverage, 3),
                    'crop_diversity': len(crop_percentages),
                    'is_mock_data': False, # This logic is now handled inside data source, assume real if returned
                    'intensity_score': self._calculate_intensity(crop_percentages)
                }
            except Exception as e:
                logger.error(f"An unexpected error occurred for hexagon {h3_index}: {e}", exc_info=True)
                continue
        
        logger.info(f"Completed current use analysis. Processed {len(h3_current_use)} of {len(target_hexagons)} hexagons.")
        return h3_current_use

    def _calculate_intensity(self, crop_percentages: List[Tuple[int, float]]) -> float:
        """
        Calculate an agricultural intensity score (0-1) based on crop types and their coverage.
        """
        if not crop_percentages:
            return 0.0
            
        total_value = 0
        for code, percentage in crop_percentages:
            info = self.data_source.get_crop_classification(code)
            if info:
                # Weight value by percentage of coverage
                total_value += info.value_per_acre * (percentage / 100.0)

        # Normalize by a reasonable maximum value to get a 0-1 score
        # Using $2000/acre as a high-end benchmark for this simple model
        max_possible_value = 2000
        intensity = total_value / max_possible_value if max_possible_value > 0 else 0
        return round(min(1.0, intensity), 3) 