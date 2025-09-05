"""
I/O module for GEO-INFER-SPACE geospatial data handling.

This module provides comprehensive input/output capabilities for various
geospatial data formats including vector, raster, and point cloud data.
"""

from .vector_io import (
    VectorReader,
    VectorWriter,
    read_vector_file,
    write_vector_file,
    supported_vector_formats
)

from .raster_io import (
    RasterReader,
    RasterWriter,
    read_raster_file,
    write_raster_file,
    supported_raster_formats
)

from .point_cloud_io import (
    PointCloudReader,
    PointCloudWriter,
    read_point_cloud_file,
    write_point_cloud_file,
    supported_point_cloud_formats
)

from .format_handlers import (
    FormatHandler,
    GeoJSONHandler,
    ShapefileHandler,
    GeoTIFFHandler,
    COGHandler,
    LASHandler,
    NetCDFHandler
)

__all__ = [
    # Vector I/O
    'VectorReader',
    'VectorWriter',
    'read_vector_file',
    'write_vector_file',
    'supported_vector_formats',
    
    # Raster I/O
    'RasterReader',
    'RasterWriter',
    'read_raster_file',
    'write_raster_file',
    'supported_raster_formats',
    
    # Point cloud I/O
    'PointCloudReader',
    'PointCloudWriter',
    'read_point_cloud_file',
    'write_point_cloud_file',
    'supported_point_cloud_formats',
    
    # Format handlers
    'FormatHandler',
    'GeoJSONHandler',
    'ShapefileHandler',
    'GeoTIFFHandler',
    'COGHandler',
    'LASHandler',
    'NetCDFHandler'
]
