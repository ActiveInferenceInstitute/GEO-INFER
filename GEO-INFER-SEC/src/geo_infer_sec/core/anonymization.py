"""
Geospatial data anonymization techniques.

This module provides implementation of various anonymization techniques
for geospatial data to protect privacy while maintaining utility.
"""

from typing import Union, Dict, List, Tuple, Optional, Any
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import pandas as pd
import h3
from pyproj import Transformer


class GeospatialAnonymizer:
    """
    Provides methods for anonymizing geospatial data while preserving utility.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the anonymizer.

        Args:
            seed: Random seed for reproducibility of anonymization operations.
        """
        self.rng = np.random.RandomState(seed)
    
    def location_perturbation(
        self, 
        gdf: gpd.GeoDataFrame, 
        epsilon: float = 100.0, 
        geometry_col: str = "geometry"
    ) -> gpd.GeoDataFrame:
        """
        Apply random perturbation to point locations.
        
        Args:
            gdf: GeoDataFrame with point geometries to anonymize
            epsilon: Maximum displacement distance in meters
            geometry_col: Name of the geometry column

        Returns:
            GeoDataFrame with perturbed geometries
        """
        if not all(isinstance(geom, Point) for geom in gdf[geometry_col]):
            raise ValueError("All geometries must be Point objects")
        
        result = gdf.copy()
        for idx, row in result.iterrows():
            point = row[geometry_col]
            # Generate random angle and distance
            angle = self.rng.uniform(0, 2 * np.pi)
            distance = self.rng.uniform(0, epsilon)
            
            # Calculate displacement in degrees (approximate)
            # 111,000 meters ≈ 1 degree of latitude
            lat_shift = distance * np.cos(angle) / 111000
            # 111,000 * cos(latitude) meters ≈ 1 degree of longitude
            lon_shift = distance * np.sin(angle) / (111000 * np.cos(np.radians(point.y)))
            
            # Create new point
            new_point = Point(point.x + lon_shift, point.y + lat_shift)
            result.loc[idx, geometry_col] = new_point
            
        return result
    
    def spatial_k_anonymity(
        self, 
        gdf: gpd.GeoDataFrame, 
        k: int = 5, 
        h3_resolution: int = 9, 
        geometry_col: str = "geometry"
    ) -> gpd.GeoDataFrame:
        """
        Apply spatial k-anonymity by aggregating points into H3 cells.
        
        Args:
            gdf: GeoDataFrame with point geometries to anonymize
            k: Minimum number of points required in each H3 cell
            h3_resolution: H3 grid resolution (0-15, where higher is more precise)
            geometry_col: Name of the geometry column
            
        Returns:
            GeoDataFrame with k-anonymized data
        """
        if not all(isinstance(geom, Point) for geom in gdf[geometry_col]):
            raise ValueError("All geometries must be Point objects")
        
        result = gdf.copy()
        
        # Add H3 cell IDs
        result["h3_cell"] = result.apply(
            lambda row: h3.geo_to_h3(row[geometry_col].y, row[geometry_col].x, h3_resolution), 
            axis=1
        )
        
        # Count records per cell
        cell_counts = result["h3_cell"].value_counts()
        
        # Identify cells with fewer than k points
        small_cells = cell_counts[cell_counts < k].index.tolist()
        
        # For cells with fewer than k points, merge with neighboring cells
        for small_cell in small_cells:
            # Get neighboring cells
            neighbors = h3.k_ring(small_cell, 1)
            
            # Find a neighbor with enough points or that would have enough when combined
            for neighbor in neighbors:
                if neighbor in cell_counts and cell_counts[neighbor] >= k - cell_counts[small_cell]:
                    # Reassign points from small cell to neighbor
                    result.loc[result["h3_cell"] == small_cell, "h3_cell"] = neighbor
                    break
        
        # Replace coordinates with cell centroids
        for cell_id in result["h3_cell"].unique():
            cell_center = h3.h3_to_geo(cell_id)
            result.loc[result["h3_cell"] == cell_id, geometry_col] = Point(cell_center[1], cell_center[0])
            
        # Drop H3 cell column
        result = result.drop(columns=["h3_cell"])
        
        return result
    
    def geographic_masking(
        self, 
        gdf: gpd.GeoDataFrame, 
        attribute_cols: List[str] = None, 
        admin_boundaries: gpd.GeoDataFrame = None,
        admin_id_col: str = "admin_id",
        geometry_col: str = "geometry"
    ) -> gpd.GeoDataFrame:
        """
        Apply geographic masking by aggregating data to administrative boundaries.
        
        Args:
            gdf: GeoDataFrame with point geometries to anonymize
            attribute_cols: List of columns with attributes to aggregate
            admin_boundaries: GeoDataFrame with administrative boundaries
            admin_id_col: Column name for administrative area identifier
            geometry_col: Name of the geometry column
            
        Returns:
            GeoDataFrame with geographically masked data
        """
        if attribute_cols is None or admin_boundaries is None:
            raise ValueError("attribute_cols and admin_boundaries must be provided")
        
        # Spatial join to determine which admin area each point belongs to
        joined = gpd.sjoin(gdf, admin_boundaries, how="inner", predicate="within")
        
        # Aggregate data by admin area
        aggregated = {}
        
        for col in attribute_cols:
            # Determine appropriate aggregation function
            if pd.api.types.is_numeric_dtype(gdf[col]):
                aggregated[col] = joined.groupby(f"index_right")[col].mean()
            else:
                aggregated[col] = joined.groupby(f"index_right")[col].agg(
                    lambda x: x.value_counts().index[0] if len(x) > 0 else None
                )
                
        # Create aggregated GeoDataFrame
        agg_df = pd.DataFrame(aggregated)
        agg_df = agg_df.reset_index()
        
        # Get admin area geometries
        agg_gdf = admin_boundaries.loc[agg_df["index_right"]].copy()
        
        # Join aggregated attributes
        for col in attribute_cols:
            agg_gdf[col] = agg_df[col].values
            
        return agg_gdf 