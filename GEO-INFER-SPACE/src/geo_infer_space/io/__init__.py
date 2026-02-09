"""
I/O module for GEO-INFER-SPACE geospatial data handling.

This module provides comprehensive input/output capabilities for various
geospatial data formats including vector, raster, and point cloud data.
"""

import logging

logger = logging.getLogger(__name__)

# Vector I/O (always available)
from .vector_io import (
    VectorReader,
    VectorWriter,
    read_vector_file,
    write_vector_file,
    supported_vector_formats
)

__all__ = [
    # Vector I/O
    'VectorReader',
    'VectorWriter',
    'read_vector_file',
    'write_vector_file',
    'supported_vector_formats',
]

# Raster I/O (requires rasterio)
try:
    from .raster_io import (
        RasterReader,
        RasterWriter,
        read_raster_file,
        write_raster_file,
        supported_raster_formats
    )
    __all__.extend([
        'RasterReader',
        'RasterWriter',
        'read_raster_file',
        'write_raster_file',
        'supported_raster_formats',
    ])
except ImportError:
    logger.debug("Raster I/O not available (rasterio not installed)")

# Point cloud I/O (basic always available, LAS/LAZ requires laspy)
try:
    from .point_cloud_io import (
        PointCloudReader,
        PointCloudWriter,
        read_point_cloud_file,
        write_point_cloud_file,
        supported_point_cloud_formats
    )
    __all__.extend([
        'PointCloudReader',
        'PointCloudWriter',
        'read_point_cloud_file',
        'write_point_cloud_file',
        'supported_point_cloud_formats',
    ])
except ImportError:
    logger.debug("Point cloud I/O not available")

# Format handlers
try:
    from .format_handlers import (
        FormatHandler,
        GeoJSONHandler,
        ShapefileHandler,
        GeoTIFFHandler,
        COGHandler,
        LASHandler,
        NetCDFHandler
    )
    __all__.extend([
        'FormatHandler',
        'GeoJSONHandler',
        'ShapefileHandler',
        'GeoTIFFHandler',
        'COGHandler',
        'LASHandler',
        'NetCDFHandler',
    ])
except ImportError:
    logger.debug("Format handlers not fully available")
