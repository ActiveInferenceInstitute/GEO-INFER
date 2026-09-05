"""
Core mathematical components for geospatial analysis.

This package provides fundamental mathematical operations and algorithms
that serve as building blocks for more complex geospatial analysis.
"""

# Import available modules
from geo_infer_math.core.spatial_statistics import *
from geo_infer_math.core.interpolation import *
from geo_infer_math.core.optimization import *
from geo_infer_math.core.geometry import *

# Import newly implemented modules
try:
    from geo_infer_math.core.numerical_methods import (
        InterpolationResult as InterpolationResult,
        OptimizationResult as OptimizationResult,
        ODEsolution as ODEsolution,
        SpatialOptimizer as SpatialOptimizer,
        ODESolver as ODESolver,
        PDEsolver as PDEsolver,
        numerical_integration as numerical_integration,
        find_root as find_root,
        minimize_scalar_function as minimize_scalar_function,
    )
    _numerical_methods_available = True
except ImportError:
    _numerical_methods_available = False

try:
    from geo_infer_math.core.linalg_tensor import *
    _linalg_tensor_available = True
except ImportError:
    _linalg_tensor_available = False

try:
    from geo_infer_math.core.transforms import *
    _transforms_available = True
except ImportError:
    _transforms_available = False

try:
    from geo_infer_math.core.graph_theory import *
    _graph_theory_available = True
except ImportError:
    _graph_theory_available = False

try:
    from geo_infer_math.core.integration import *
    _integration_available = True
except ImportError:
    _integration_available = False

try:
    from geo_infer_math.core.gpu_acceleration import *
    _gpu_acceleration_available = True
except ImportError:
    _gpu_acceleration_available = False

try:
    from geo_infer_math.core.symbolic_math import *
    _symbolic_math_available = True
except ImportError:
    _symbolic_math_available = False

try:
    from geo_infer_math.core.information_theory import (
        shannon_entropy as shannon_entropy,
        renyi_entropy as renyi_entropy,
        tsallis_entropy as tsallis_entropy,
        spatial_entropy as info_spatial_entropy,  # noqa: F401 -- legacy renamed re-export; redundant alias would shadow spatial_statistics.spatial_entropy
        mutual_information as mutual_information,
        kl_divergence as kl_divergence,
        conditional_entropy as conditional_entropy,
        joint_entropy as joint_entropy,
        EntropyCalculator as EntropyCalculator,
        MutualInformationCalculator as MutualInformationCalculator,
        KLDivergenceCalculator as KLDivergenceCalculator,
    )
    _information_theory_available = True
except ImportError:
    _information_theory_available = False

try:
    from geo_infer_math.core.theorem_proving import *
    _theorem_proving_available = True
except ImportError:
    _theorem_proving_available = False

# Build __all__ list based on available modules
__all__ = [
    "spatial_statistics",
    "interpolation",
    "optimization",
    "geometry"
]

if _numerical_methods_available:
    __all__.append("numerical_methods")

if _linalg_tensor_available:
    __all__.append("linalg_tensor")

if _transforms_available:
    __all__.append("transforms")

if _graph_theory_available:
    __all__.append("graph_theory")

if _integration_available:
    __all__.append("integration")

if _gpu_acceleration_available:
    __all__.append("gpu_acceleration")

if _symbolic_math_available:
    __all__.append("symbolic_math")

if _information_theory_available:
    __all__.append("information_theory")

if _theorem_proving_available:
    __all__.append("theorem_proving")
