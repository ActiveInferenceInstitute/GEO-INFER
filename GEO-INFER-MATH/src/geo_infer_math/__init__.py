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
    GearysC,
    GetisOrd,
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

# Track available optional modules
_available_core = []
_available_models = []

# Try to import model modules
# Note: These modules may not have __all__ defined, so we import the modules themselves
from geo_infer_math.models import regression as regression_module

_available_models.append("regression")

from geo_infer_math.models import clustering as clustering_module

_available_models.append("clustering")

# Try to import information theory
try:
    from geo_infer_math.core.information_theory import (
        shannon_entropy,
        renyi_entropy,
        tsallis_entropy,
        spatial_entropy as info_spatial_entropy,
        mutual_information,
        kl_divergence,
        EntropyCalculator,
        MutualInformationCalculator,
        KLDivergenceCalculator,
    )

    _available_core.append("information_theory")
except ImportError:
    pass

# Try to import theorem proving
try:
    from geo_infer_math.core.theorem_proving import (
        TheoremProver,
        ProofResult,
        create_prover,
        TheoremDatabase,
    )

    _available_core.append("theorem_proving")
except ImportError:
    pass

# Try to import convenience APIs
try:
    from geo_infer_math.api.convenience import (
        ActiveInferenceConvenience,
        BayesianConvenience,
        AIConvenience,
        InformationTheoryConvenience,
        SpatialConvenience,
        IntegrationConvenience,
    )

    _convenience_available = True
except ImportError:
    _convenience_available = False

# Try to import integration modules
try:
    from geo_infer_math.integration.ai import (
        AIGradientHelpers,
        SpatialLossFunctions,
        OptimizationBridges,
    )
    from geo_infer_math.integration.act import (
        FreeEnergyCalculator,
        VariationalInferenceHelpers,
        BeliefUpdating,
    )
    from geo_infer_math.integration.bayes import (
        PosteriorHelpers,
        PriorBuilders,
        MCMCHelpers,
    )

    _integration_available = True
except ImportError:
    _integration_available = False

# Build __all__ list
__all__ = [
    # Spatial statistics
    "SpatialDescriptiveStats",
    "MoranI",
    "GearysC",
    "GetisOrd",
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

# Add information theory exports if available
if "information_theory" in _available_core:
    __all__.extend(
        [
            "shannon_entropy",
            "renyi_entropy",
            "tsallis_entropy",
            "info_spatial_entropy",
            "mutual_information",
            "kl_divergence",
            "EntropyCalculator",
            "MutualInformationCalculator",
            "KLDivergenceCalculator",
        ]
    )

# Add theorem proving exports if available
if "theorem_proving" in _available_core:
    __all__.extend(
        [
            "TheoremProver",
            "ProofResult",
            "create_prover",
            "TheoremDatabase",
        ]
    )

# Add convenience API exports if available
if _convenience_available:
    __all__.extend(
        [
            "ActiveInferenceConvenience",
            "BayesianConvenience",
            "AIConvenience",
            "InformationTheoryConvenience",
            "SpatialConvenience",
            "IntegrationConvenience",
        ]
    )

# Add integration exports if available
if _integration_available:
    __all__.extend(
        [
            "AIGradientHelpers",
            "SpatialLossFunctions",
            "OptimizationBridges",
            "FreeEnergyCalculator",
            "VariationalInferenceHelpers",
            "BeliefUpdating",
            "PosteriorHelpers",
            "PriorBuilders",
            "MCMCHelpers",
        ]
    )

# Version information
__version__ = "0.2.0"
__author__ = "GEO-INFER Development Team"
__email__ = "geo-infer@activeinference.institute"
