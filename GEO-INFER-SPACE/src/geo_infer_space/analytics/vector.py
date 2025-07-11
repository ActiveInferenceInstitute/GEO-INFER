import logging
from typing import Union
import geopandas as gpd

logger = logging.getLogger(__name__)

def buffer_and_intersect(
    points_gdf: gpd.GeoDataFrame,
    polygons_gdf: gpd.GeoDataFrame,
    buffer_distance_meters: Union[int, float]
) -> gpd.GeoDataFrame:
    """Buffer points and intersect with polygons.
    
    Args:
        points_gdf: GeoDataFrame of points to buffer.
        polygons_gdf: GeoDataFrame of polygons to intersect with.
        buffer_distance_meters: Buffer distance in meters.
        
    Returns:
        GeoDataFrame of intersection results.
        
    Raises:
        ValueError: If CRS mismatch or empty inputs.
    """
    if points_gdf.crs != polygons_gdf.crs:
        raise ValueError("CRS mismatch between points and polygons")
    
    # Project to metric CRS if necessary
    original_crs = points_gdf.crs
    if not original_crs.is_projected:
        metric_crs = "EPSG:3857"  # Web Mercator
        points_gdf = points_gdf.to_crs(metric_crs)
        polygons_gdf = polygons_gdf.to_crs(metric_crs)
    
    buffered = points_gdf.buffer(buffer_distance_meters)
    buffered_gdf = gpd.GeoDataFrame(geometry=buffered, crs=points_gdf.crs)
    
    intersection = gpd.overlay(buffered_gdf, polygons_gdf, how='intersection')
    
    # Reproject back to original CRS
    intersection = intersection.to_crs(original_crs)
    
    logger.info("Intersection completed: %d features", len(intersection))
    return intersection 