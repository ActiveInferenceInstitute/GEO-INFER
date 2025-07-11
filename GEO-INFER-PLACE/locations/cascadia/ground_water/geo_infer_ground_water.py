
import logging
from typing import Dict, List, Any, Tuple
import geopandas as gpd
from shapely.geometry import Polygon
from .data_sources import CascadianGroundWaterDataSources
from utils_h3 import h3_to_geo_boundary

logger = logging.getLogger(__name__)

class GeoInferGroundWater:
    """
    Analyzes groundwater availability by fetching real well data from the USGS
    for a given set of H3 hexagons.
    """

    def __init__(self, resolution: int):
        self.resolution = resolution
        self.data_source = CascadianGroundWaterDataSources()
        logger.info(f"Initialized GeoInferGroundWater with resolution {self.resolution}")

    def run_analysis(self, target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Performs groundwater analysis by querying the USGS NWIS for wells within
        the target hexagons.

        Args:
            target_hexagons: A list of H3 hexagon IDs to analyze.

        Returns:
            A dictionary mapping H3 hexagon IDs to their groundwater analysis.
        """
        logger.info(f"Starting groundwater analysis for {len(target_hexagons)} hexagons.")
        if not target_hexagons:
            return {}

        # The data source now handles batching and bounding box calculation
        wells_gdf = self.data_source.fetch_groundwater_data(target_hexagons)

        if wells_gdf.empty:
            logger.warning("No groundwater wells found in the entire analysis area. Returning empty results.")
            return {}

        # Spatially index the wells for efficient lookups
        wells_sindex = wells_gdf.sindex

        results = {}
        for h3_index in target_hexagons:
            try:
                hex_poly = Polygon(h3_to_geo_boundary(h3_index))
                
                # Find wells that intersect with the hexagon's bounding box first
                possible_matches_index = list(wells_sindex.intersection(hex_poly.bounds))
                possible_matches = wells_gdf.iloc[possible_matches_index]
                
                # Perform precise intersection check
                precise_matches = possible_matches[possible_matches.intersects(hex_poly)]

                well_count = len(precise_matches)
                if well_count > 0:
                    # Score is a simple heuristic: 1.0 if any wells exist.
                    # A more complex score could be based on well depth, yield, etc.
                    score = 1.0
                    results[h3_index] = {
                        'has_ground_water': True,
                        'groundwater_well_count': well_count,
                        'groundwater_availability_score': score
                    }
                else:
                     results[h3_index] = {
                        'has_ground_water': False,
                        'groundwater_well_count': 0,
                        'groundwater_availability_score': 0.0
                    }
            except Exception as e:
                logger.error(f"Failed to process hexagon {h3_index} for groundwater analysis: {e}", exc_info=True)
                continue

        logger.info(f"Completed groundwater analysis. Found data for {len(results)} hexagons.")
        return results 