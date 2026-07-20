"""
Utility functions and tools for mathematical operations in geospatial context.

This package provides helper functions, data conversion tools, and other utilities
that support the core mathematical operations and models.
"""

# This package initializer intentionally re-exports the public utility surface.
# ruff: noqa: F401

# Import new utility modules
try:
    from geo_infer_math.utils.caching import (
        cache_result,
        ComputationCache,
    )

    _caching_available = True
except ImportError:
    _caching_available = False

try:
    from geo_infer_math.utils.exceptions import (
        MathError,
        NumericalError as NewNumericalError,
        ConvergenceError as NewConvergenceError,
        SingularMatrixError,
        TheoremProvingError,
        ProofVerificationError,
        InformationTheoryError,
        InvalidDistributionError,
        SpatialError,
        CoordinateError,
        GeometryError,
    )

    _exceptions_available = True
except ImportError:
    _exceptions_available = False

# Import available utilities
try:
    from geo_infer_math.utils import validation

    _validation_available = True
except ImportError:
    _validation_available = False

try:
    from geo_infer_math.utils import conversion

    _conversion_available = True
except ImportError:
    _conversion_available = False

try:
    from geo_infer_math.utils import constants

    _constants_available = True
except ImportError:
    _constants_available = False

try:
    from geo_infer_math.utils import decorators

    _decorators_available = True
except ImportError:
    _decorators_available = False

try:
    from geo_infer_math.utils import parallel

    _parallel_available = True
except ImportError:
    _parallel_available = False

# Build __all__ list based on available modules
__all__ = []

# Add new utility exports
if _caching_available:
    __all__.extend(["cache_result", "ComputationCache"])

if _exceptions_available:
    __all__.extend(
        [
            "MathError",
            "NewNumericalError",
            "NewConvergenceError",
            "SingularMatrixError",
            "TheoremProvingError",
            "ProofVerificationError",
            "InformationTheoryError",
            "InvalidDistributionError",
            "SpatialError",
            "CoordinateError",
            "GeometryError",
        ]
    )

# Try to import new validation functions
try:
    from geo_infer_math.utils.validation import (
        validate_probabilities,
        validate_coordinates as validate_coordinates_new,
        validate_numerical,
        validate_shape,
        validate_range,
    )

    __all__.extend(
        [
            "validate_probabilities",
            "validate_coordinates_new",
            "validate_numerical",
            "validate_shape",
            "validate_range",
        ]
    )
except ImportError:
    pass

# Import functions from available modules
if _validation_available:
    from geo_infer_math.utils.validation import (
        validate_coordinates,
        validate_matrix,
        validate_weights_matrix,
        validate_values_array,
        validate_bounds,
        validate_function_input,
        validate_spatial_autocorrelation_params,
        validate_interpolation_params,
        validate_clustering_params,
        validate_tensor_data,
    )

    __all__.extend(
        [
            "validate_coordinates",
            "validate_matrix",
            "validate_weights_matrix",
            "validate_values_array",
            "validate_bounds",
            "validate_function_input",
            "validate_spatial_autocorrelation_params",
            "validate_interpolation_params",
            "validate_clustering_params",
            "validate_tensor_data",
        ]
    )

if _conversion_available:
    from geo_infer_math.utils.conversion import (
        degrees_to_radians,
        radians_to_degrees,
        celsius_to_fahrenheit,
        fahrenheit_to_celsius,
        kelvin_to_celsius,
        celsius_to_kelvin,
        meters_to_feet,
        feet_to_meters,
        meters_to_miles,
        miles_to_meters,
        meters_to_kilometers,
        kilometers_to_meters,
        square_meters_to_square_feet,
        square_feet_to_square_meters,
        square_meters_to_acres,
        acres_to_square_meters,
        square_meters_to_hectares,
        hectares_to_square_meters,
        cartesian_to_polar,
        polar_to_cartesian,
        spherical_to_cartesian,
        cartesian_to_spherical,
        normalize_array,
        standardize_array,
        convert_data_types,
        format_coordinate_string,
        parse_coordinate_string,
    )

    __all__.extend(
        [
            "degrees_to_radians",
            "radians_to_degrees",
            "celsius_to_fahrenheit",
            "fahrenheit_to_celsius",
            "kelvin_to_celsius",
            "celsius_to_kelvin",
            "meters_to_feet",
            "feet_to_meters",
            "meters_to_miles",
            "miles_to_meters",
            "meters_to_kilometers",
            "kilometers_to_meters",
            "square_meters_to_square_feet",
            "square_feet_to_square_meters",
            "square_meters_to_acres",
            "acres_to_square_meters",
            "square_meters_to_hectares",
            "hectares_to_square_meters",
            "cartesian_to_polar",
            "polar_to_cartesian",
            "spherical_to_cartesian",
            "cartesian_to_spherical",
            "normalize_array",
            "standardize_array",
            "convert_data_types",
            "format_coordinate_string",
            "parse_coordinate_string",
        ]
    )

if _constants_available:
    from geo_infer_math.utils.constants import (
        EARTH_RADIUS_EQUATORIAL,
        EARTH_RADIUS_POLAR,
        EARTH_RADIUS_MEAN,
        EARTH_FLATTENING,
        EARTH_ECCENTRICITY,
        EARTH_GRAVITY_EQUATORIAL,
        EARTH_GRAVITY_POLES,
        EARTH_GRAVITY_MEAN,
        PI,
        EULER_GAMMA,
        GOLDEN_RATIO,
        DEFAULT_SPATIAL_WEIGHTS_K,
        DEFAULT_VARIANCE_THRESHOLD,
        DEFAULT_CONVERGENCE_TOLERANCE,
        DEFAULT_MAX_ITERATIONS,
        DEFAULT_IDW_POWER,
        DEFAULT_KRIGING_RANGE,
        DEFAULT_KRIGING_SILL,
        DEFAULT_KRIGING_NUGGET,
        DEFAULT_CONFIDENCE_LEVEL,
        DEFAULT_SIGNIFICANCE_LEVEL,
        DEFAULT_Z_SCORE_THRESHOLD,
        WGS84_EPSG_CODE,
        WEB_MERCATOR_EPSG_CODE,
        UTM_ZONE_WIDTH_DEGREES,
        UTM_CENTRAL_MERIDIAN_OFFSET,
        SECOND,
        MINUTE,
        HOUR,
        DAY,
        WEEK,
        MONTH,
        YEAR,
        METER_TO_FEET,
        FEET_TO_METER,
        METER_TO_YARD,
        YARD_TO_METER,
        METER_TO_MILE,
        MILE_TO_METER,
        METER_TO_KILOMETER,
        KILOMETER_TO_METER,
        METER_TO_NAUTICAL_MILE,
        NAUTICAL_MILE_TO_METER,
        SQUARE_METER_TO_SQUARE_FEET,
        SQUARE_FEET_TO_SQUARE_METER,
        SQUARE_METER_TO_ACRE,
        ACRE_TO_SQUARE_METER,
        SQUARE_METER_TO_HECTARE,
        HECTARE_TO_SQUARE_METER,
        CELSIUS_TO_FAHRENHEIT_OFFSET,
        CELSIUS_TO_FAHRENHEIT_FACTOR,
        CONSTANTS,
        get_constant,
        list_constants,
    )

    __all__.extend(
        [
            "EARTH_RADIUS_EQUATORIAL",
            "EARTH_RADIUS_POLAR",
            "EARTH_RADIUS_MEAN",
            "EARTH_FLATTENING",
            "EARTH_ECCENTRICITY",
            "EARTH_GRAVITY_EQUATORIAL",
            "EARTH_GRAVITY_POLES",
            "EARTH_GRAVITY_MEAN",
            "PI",
            "EULER_GAMMA",
            "GOLDEN_RATIO",
            "DEFAULT_SPATIAL_WEIGHTS_K",
            "DEFAULT_VARIANCE_THRESHOLD",
            "DEFAULT_CONVERGENCE_TOLERANCE",
            "DEFAULT_MAX_ITERATIONS",
            "DEFAULT_IDW_POWER",
            "DEFAULT_KRIGING_RANGE",
            "DEFAULT_KRIGING_SILL",
            "DEFAULT_KRIGING_NUGGET",
            "DEFAULT_CONFIDENCE_LEVEL",
            "DEFAULT_SIGNIFICANCE_LEVEL",
            "DEFAULT_Z_SCORE_THRESHOLD",
            "WGS84_EPSG_CODE",
            "WEB_MERCATOR_EPSG_CODE",
            "UTM_ZONE_WIDTH_DEGREES",
            "UTM_CENTRAL_MERIDIAN_OFFSET",
            "SECOND",
            "MINUTE",
            "HOUR",
            "DAY",
            "WEEK",
            "MONTH",
            "YEAR",
            "METER_TO_FEET",
            "FEET_TO_METER",
            "METER_TO_YARD",
            "YARD_TO_METER",
            "METER_TO_MILE",
            "MILE_TO_METER",
            "METER_TO_KILOMETER",
            "KILOMETER_TO_METER",
            "METER_TO_NAUTICAL_MILE",
            "NAUTICAL_MILE_TO_METER",
            "SQUARE_METER_TO_SQUARE_FEET",
            "SQUARE_FEET_TO_SQUARE_METER",
            "SQUARE_METER_TO_ACRE",
            "ACRE_TO_SQUARE_METER",
            "SQUARE_METER_TO_HECTARE",
            "HECTARE_TO_SQUARE_METER",
            "CELSIUS_TO_FAHRENHEIT_OFFSET",
            "CELSIUS_TO_FAHRENHEIT_FACTOR",
            "CONSTANTS",
            "get_constant",
            "list_constants",
        ]
    )

if _decorators_available:
    from geo_infer_math.utils.decorators import (
        memoize,
        memoize_with_expiry,
        validate_input,
        log_execution,
        time_execution,
        requires_positive_values,
        requires_finite_values,
        handle_exceptions,
        requires_numpy_arrays,
        cache_results,
        validate_output,
        retry_on_failure,
    )

    __all__.extend(
        [
            "memoize",
            "memoize_with_expiry",
            "validate_input",
            "log_execution",
            "time_execution",
            "requires_positive_values",
            "requires_finite_values",
            "handle_exceptions",
            "requires_numpy_arrays",
            "cache_results",
            "validate_output",
            "retry_on_failure",
        ]
    )

# Import error handling classes and decorators from their owning modules.
from geo_infer_math.utils.exceptions import (
    GeoInferMathError,
    ValidationError,
    NumericalError,
    ConvergenceError,
    MemoryError,
)
from geo_infer_math.utils.validation import (
    handle_validation_errors,
    handle_numerical_errors,
)

__all__.extend(
    [
        "GeoInferMathError",
        "ValidationError",
        "NumericalError",
        "ConvergenceError",
        "MemoryError",
        "handle_validation_errors",
        "handle_numerical_errors",
    ]
)

if _parallel_available:
    from geo_infer_math.utils.parallel import (
        parallel_compute,
        parallel_map,
        parallel_matrix_operation,
        parallel_matrix_multiply,
        parallel_distance_matrix,
        parallel_spatial_interpolation,
        parallel_statistical_analysis,
        get_optimal_worker_count,
        parallel_file_processing,
        memory_efficient_parallel,
        DEFAULT_NUM_WORKERS,
        MAX_CHUNK_SIZE,
    )

    __all__.extend(
        [
            "parallel_compute",
            "parallel_map",
            "parallel_matrix_operation",
            "parallel_matrix_multiply",
            "parallel_distance_matrix",
            "parallel_spatial_interpolation",
            "parallel_statistical_analysis",
            "get_optimal_worker_count",
            "parallel_file_processing",
            "memory_efficient_parallel",
            "DEFAULT_NUM_WORKERS",
            "MAX_CHUNK_SIZE",
        ]
    )
