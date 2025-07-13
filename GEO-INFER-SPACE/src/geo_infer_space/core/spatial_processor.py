"""Spatial processing module for geospatial operations."""

import logging
import geopandas as gpd
from typing import Union, Dict, Any
from shapely.geometry import Point, LineString, Polygon
import pandas as pd

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

    def perform_multi_overlay(self, spatial_datasets: Dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
        """
        Perform multi-layer spatial overlay on multiple GeoDataFrames.
        
        Args:
            spatial_datasets: Dictionary of dataset names to GeoDataFrames
        
        Returns:
            Single GeoDataFrame with overlaid geometries and attributes
        """
        if not spatial_datasets:
            raise ValueError("No spatial datasets provided")
        
        # Get the first dataset as base
        base_name = list(spatial_datasets.keys())[0]
        base_gdf = spatial_datasets[base_name].copy()
        
        # Add domain identifier
        base_gdf['domain'] = base_name
        
        # Overlay with other datasets
        for name, gdf in spatial_datasets.items():
            if name == base_name:
                continue
            
            # Ensure same CRS
            if gdf.crs != base_gdf.crs:
                gdf = gdf.to_crs(base_gdf.crs)
            
            # Add domain identifier
            gdf = gdf.copy()
            gdf['domain'] = name
            
            # Concatenate
            base_gdf = gpd.GeoDataFrame(pd.concat([base_gdf, gdf], ignore_index=True), crs=base_gdf.crs)
        
        return base_gdf

    def calculate_spatial_correlation(self, gdf: gpd.GeoDataFrame) -> Dict[str, float]:
        """
        Calculate spatial correlation metrics for a GeoDataFrame.
        
        Args:
            gdf: Input GeoDataFrame
        
        Returns:
            Dictionary with correlation metrics
        """
        try:
            # Simple spatial autocorrelation using nearest neighbors
            if len(gdf) < 2:
                return {'spatial_correlation': 0.0}
            
            # Calculate distances between all points
            coords = [(geom.x, geom.y) for geom in gdf.geometry if hasattr(geom, 'x') and hasattr(geom, 'y')]
            if len(coords) < 2:
                return {'spatial_correlation': 0.0}
            
            # Simple correlation based on distance
            distances = []
            for i in range(len(coords)):
                for j in range(i+1, len(coords)):
                    dist = ((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)**0.5
                    distances.append(dist)
            
            if distances:
                return {'spatial_correlation': 1.0 / (1.0 + sum(distances) / len(distances))}
            else:
                return {'spatial_correlation': 0.0}
        except Exception as e:
            logger.error(f"Spatial correlation calculation failed: {e}")
            return {'spatial_correlation': 0.0}