"""
GEO-INFER-MATH

A comprehensive mathematical library for geospatial data analysis and inference.
This module provides specialized mathematical tools, models, and algorithms that
are optimized for processing and analyzing geographical and spatial data.

Key components:
- Spatial statistics and probability distributions
- Geospatial optimization algorithms
- Spatial interpolation and extrapolation methods
- Vector and raster math operations
- Coordinate transformations and projections
- Geometric operations and calculations
- Tensor operations for multi-dimensional geospatial data
"""

# Import available core modules with explicit imports
from geo_infer_math.core.spatial_statistics import (
    SpatialDescriptiveStats,
    MoranI,
    getis_ord_g,
    ripley_k,
    semivariogram,
    spatial_descriptive_statistics,
    spatial_entropy,
    local_indicators_spatial_association,
)

from geo_infer_math.core.interpolation import (
    InterpolationConfig,
    SpatialInterpolator,
    IDWInterpolator,
    KrigingInterpolator,
    RBFInterpolator,
    LinearInterpolator,
    CubicInterpolator,
    InterpolationManager,
    create_interpolation_manager,
    interpolate_spatial_data,
    create_interpolation_grid,
)

from geo_infer_math.core.optimization import (
    OptimizationConfig,
    Optimizer,
    GradientDescentOptimizer,
    GeneticAlgorithmOptimizer,
    ScipyOptimizer,
    MultiObjectiveOptimizer,
    OptimizationManager,
    create_optimization_manager,
    optimize_function,
    compare_optimization_methods,
)

from geo_infer_math.core.geometry import (
    Point,
    LineString,
    Polygon,
    haversine_distance,
    vincenty_distance,
    bearing,
    destination_point,
    point_in_polygon,
    buffer_point,
    line_intersection,
    polygon_area_spherical,
)

# Try to import newly implemented modules
_available_core = []
_available_models = []

try:
    from geo_infer_math.core.numerical_methods import (
        InterpolationResult,
        OptimizationResult,
        ODEsolution,
        SpatialInterpolator as NumericalSpatialInterpolator,
        SpatialOptimizer as NumericalSpatialOptimizer,
        ODESolver,
        PDEsolver,
        numerical_integration,
        find_root,
        minimize_scalar_function,
    )
    _available_core.append("numerical_methods")
except ImportError:
    pass

try:
    from geo_infer_math.core.linalg_tensor import (
        TensorData,
        MatrixOperations,
        TensorOperations,
        SpatialLinearAlgebra,
    )
    _available_core.append("linalg_tensor")
except ImportError:
    pass

try:
    from geo_infer_math.core.transforms import (
        CRSDefinition,
        CoordinateTransformer,
        geographic_to_projected,
        projected_to_geographic,
        utm_zone_from_lon_lat,
        utm_central_meridian,
        datum_transformation,
        affine_transformation,
        rotation_matrix_2d,
        rotation_matrix_3d,
    )
    _available_core.append("transforms")
except ImportError:
    pass

try:
    from geo_infer_math.core.graph_theory import (
        GraphNode,
        GraphEdge,
        SpatialGraph,
        NetworkFlow,
    )
    _available_core.append("graph_theory")
except ImportError:
    pass

# Try to import model modules
# Note: These modules may not have __all__ defined, so we import the modules themselves
try:
    from geo_infer_math import models.regression as regression_module
    _available_models.append("regression")
except ImportError:
    regression_module = None

try:
    from geo_infer_math import models.clustering as clustering_module
    _available_models.append("clustering")
except ImportError:
    clustering_module = None

# Build __all__ list
__all__ = [
    # Spatial statistics
    "SpatialDescriptiveStats",
    "MoranI",
    "getis_ord_g",
    "ripley_k",
    "semivariogram",
    "spatial_descriptive_statistics",
    "spatial_entropy",
    "local_indicators_spatial_association",
    # Interpolation
    "InterpolationConfig",
    "SpatialInterpolator",
    "IDWInterpolator",
    "KrigingInterpolator",
    "RBFInterpolator",
    "LinearInterpolator",
    "CubicInterpolator",
    "InterpolationManager",
    "create_interpolation_manager",
    "interpolate_spatial_data",
    "create_interpolation_grid",
    # Optimization
    "OptimizationConfig",
    "Optimizer",
    "GradientDescentOptimizer",
    "GeneticAlgorithmOptimizer",
    "ScipyOptimizer",
    "MultiObjectiveOptimizer",
    "OptimizationManager",
    "create_optimization_manager",
    "optimize_function",
    "compare_optimization_methods",
    # Geometry
    "Point",
    "LineString",
    "Polygon",
    "haversine_distance",
    "vincenty_distance",
    "bearing",
    "destination_point",
    "point_in_polygon",
    "buffer_point",
    "line_intersection",
    "polygon_area_spherical",
]
