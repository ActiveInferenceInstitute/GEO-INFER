"""
Advanced H3 Hexagonal Grid System for GEO-INFER-SPACE.

This module provides comprehensive H3 hexagonal grid operations with v4 API compliance,
advanced analytics, visualizations, and real-world spatial analysis capabilities.
Based on Uber's H3 system for efficient geospatial indexing and analysis.

References:
- H3 Documentation: https://h3geo.org/
- H3 Python Library: https://github.com/uber/h3-py
- HDWallet H3 Integration: https://hdwallet.readthedocs.io/en/v3.4.0/
"""

from .core import (
    H3Grid,
    H3Cell,
    H3Analytics,
    H3Visualizer,
    H3Validator
)

from .operations import (
    # Core operations
    coordinate_to_cell,
    cell_to_coordinates,
    cell_to_boundary,
    cells_to_geojson,
    
    # Grid operations
    grid_disk,
    grid_ring,
    grid_distance,
    grid_path,
    
    # Hierarchy operations
    cell_to_parent,
    cell_to_children,
    compact_cells,
    uncompact_cells,
    
    # Area operations
    polygon_to_cells,
    cells_to_polygon,
    cell_area,
    cells_area,
    
    # Analysis operations
    neighbor_cells,
    cell_resolution,
    is_valid_cell,
    are_neighbor_cells,
    
    # Advanced operations
    cells_intersection,
    cells_union,
    cells_difference,
    grid_statistics
)

from .analytics import (
    H3SpatialAnalyzer,
    H3ClusterAnalyzer,
    H3DensityAnalyzer,
    H3NetworkAnalyzer,
    H3TemporalAnalyzer
)

# ML Integration and Advanced Methods
try:
    from .ml_integration import (
        H3MLFeatureEngine, H3DisasterResponse, H3PerformanceOptimizer
    )
    ML_INTEGRATION_AVAILABLE = True
except ImportError:
    ML_INTEGRATION_AVAILABLE = False
    logger.warning("ML integration methods not available")

from .visualization import (
    H3MapVisualizer,
    H3StaticVisualizer,
    H3InteractiveVisualizer,
    H3AnimationVisualizer
)

from .datasets import (
    H3Dataset,
    H3DataLoader,
    H3DataExporter,
    create_sample_datasets
)

from .utils import (
    H3Utils,
    H3Converter,
    H3Optimizer,
    H3Cache
)

__all__ = [
    # Core classes
    'H3Grid',
    'H3Cell', 
    'H3Analytics',
    'H3Visualizer',
    'H3Validator',
    
    # Core operations
    'coordinate_to_cell',
    'cell_to_coordinates',
    'cell_to_boundary',
    'cells_to_geojson',
    
    # Grid operations
    'grid_disk',
    'grid_ring',
    'grid_distance',
    'grid_path',
    
    # Hierarchy operations
    'cell_to_parent',
    'cell_to_children',
    'compact_cells',
    'uncompact_cells',
    
    # Area operations
    'polygon_to_cells',
    'cells_to_polygon',
    'cell_area',
    'cells_area',
    
    # Analysis operations
    'neighbor_cells',
    'cell_resolution',
    'is_valid_cell',
    'are_neighbor_cells',
    
    # Advanced operations
    'cells_intersection',
    'cells_union',
    'cells_difference',
    'grid_statistics',
    
    # Analytics
    'H3SpatialAnalyzer',
    'H3ClusterAnalyzer', 
    'H3DensityAnalyzer',
    'H3NetworkAnalyzer',
    'H3TemporalAnalyzer',
    
    # ML Integration (if available)
    'H3MLFeatureEngine',
    'H3DisasterResponse', 
    'H3PerformanceOptimizer',
    
    # Visualization
    'H3MapVisualizer',
    'H3StaticVisualizer',
    'H3InteractiveVisualizer',
    'H3AnimationVisualizer',
    
    # Data handling
    'H3Dataset',
    'H3DataLoader',
    'H3DataExporter',
    'create_sample_datasets',
    
    # Utilities
    'H3Utils',
    'H3Converter',
    'H3Optimizer',
    'H3Cache'
]

# Version and metadata
__version__ = "1.0.0"
__h3_version__ = "4.0+"
__author__ = "GEO-INFER Team"
__description__ = "Advanced H3 hexagonal grid system with comprehensive analytics and visualization"
