"""
Advanced spatial analytics module for GEO-INFER-SPACE.

This module provides comprehensive spatial analysis capabilities including:
- Vector operations (overlay, buffer, proximity)
- Raster analysis (terrain, map algebra, focal statistics)
- Network analysis (routing, service areas)
- Geostatistics (interpolation, clustering, hotspot detection)
- Point cloud processing
"""

from .vector import (
    buffer_and_intersect,
    overlay_analysis,
    proximity_analysis,
    spatial_join_analysis,
    geometric_calculations,
    topology_operations
)

from .raster import (
    terrain_analysis,
    map_algebra,
    focal_statistics,
    zonal_statistics,
    raster_overlay,
    image_processing
)

from .network import (
    shortest_path,
    service_area,
    network_connectivity,
    routing_analysis,
    accessibility_analysis
)

from .geostatistics import (
    spatial_interpolation,
    clustering_analysis,
    hotspot_detection,
    spatial_autocorrelation,
    variogram_analysis
)

from .point_cloud import (
    point_cloud_filtering,
    feature_extraction,
    classification,
    surface_generation
)

__all__ = [
    # Vector operations
    'buffer_and_intersect',
    'overlay_analysis', 
    'proximity_analysis',
    'spatial_join_analysis',
    'geometric_calculations',
    'topology_operations',
    
    # Raster operations
    'terrain_analysis',
    'map_algebra',
    'focal_statistics',
    'zonal_statistics',
    'raster_overlay',
    'image_processing',
    
    # Network analysis
    'shortest_path',
    'service_area',
    'network_connectivity',
    'routing_analysis',
    'accessibility_analysis',
    
    # Geostatistics
    'spatial_interpolation',
    'clustering_analysis',
    'hotspot_detection',
    'spatial_autocorrelation',
    'variogram_analysis',
    
    # Point cloud
    'point_cloud_filtering',
    'feature_extraction',
    'classification',
    'surface_generation'
]
