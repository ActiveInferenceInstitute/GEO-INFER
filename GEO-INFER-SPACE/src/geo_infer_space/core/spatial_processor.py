"""Spatial processing module for geospatial operations."""

import logging
import geopandas as gpd
from typing import Union, Dict, Any
from shapely.geometry import Point, LineString, Polygon

logger = logging.getLogger(__name__)

class SpatialProcessor:
    """Spatial processing engine for geospatial operations."""
    
    def __init__(self):
        pass
    
    def buffer_analysis(self, gdf: gpd.GeoDataFrame, buffer_distance: float) -> gpd.GeoDataFrame:
        """Create buffers around geometries.
        
        Args:
            gdf: Input GeoDataFrame
            buffer_distance: Distance in units of the CRS
        
        Returns:
            GeoDataFrame with buffered geometries
        """
        if gdf.empty or 'geometry' not in gdf.columns:
            raise ValueError("Input GeoDataFrame is empty or missing geometry column")
        try:
            buffered = gdf.copy()
            buffered['geometry'] = gdf.geometry.buffer(buffer_distance)
            return buffered
        except Exception as e:
            logger.error(f"Buffer analysis failed: {e}")
            raise
    
    def proximity_analysis(self, gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Calculate proximity between two sets of features.
        
        Args:
            gdf1: First GeoDataFrame
            gdf2: Second GeoDataFrame
        
        Returns:
            Dictionary with min, max, mean distance
        """
        try:
            distances = []
            for geom1 in gdf1.geometry:
                min_dist = min(geom1.distance(geom2) for geom2 in gdf2.geometry)
                distances.append(min_dist)
            return {
                'min_distance': min(distances),
                'max_distance': max(distances),
                'mean_distance': sum(distances) / len(distances)
            }
        except Exception as e:
            logger.error(f"Proximity analysis failed: {e}")
            raise