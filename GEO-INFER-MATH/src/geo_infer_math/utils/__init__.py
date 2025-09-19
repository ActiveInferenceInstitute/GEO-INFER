"""
Utility functions and tools for mathematical operations in geospatial context.

This package provides helper functions, data conversion tools, and other utilities
that support the core mathematical operations and models.
"""

# Import available utilities
try:
    from geo_infer_math.utils.validation import *
    _validation_available = True
except ImportError:
    _validation_available = False

try:
    from geo_infer_math.utils.conversion import *
    _conversion_available = True
except ImportError:
    _conversion_available = False

try:
    from geo_infer_math.utils.constants import *
    _constants_available = True
except ImportError:
    _constants_available = False

try:
    from geo_infer_math.utils.decorators import *
    _decorators_available = True
except ImportError:
    _decorators_available = False

try:
    from geo_infer_math.utils.parallel import *
    _parallel_available = True
except ImportError:
    _parallel_available = False

# Build __all__ list based on available modules
__all__ = []

if _validation_available:
    __all__.extend([
        "validate_coordinates", "validate_matrix", "validate_weights_matrix",
        "validate_values_array", "validate_bounds", "validate_function_input",
        "validate_spatial_autocorrelation_params", "validate_interpolation_params",
        "validate_clustering_params", "validate_tensor_data"
    ])

if _conversion_available:
    __all__.extend([
        "degrees_to_radians", "radians_to_degrees", "celsius_to_fahrenheit",
        "fahrenheit_to_celsius", "kelvin_to_celsius", "celsius_to_kelvin",
        "meters_to_feet", "feet_to_meters", "meters_to_miles", "miles_to_meters",
        "meters_to_kilometers", "kilometers_to_meters", "square_meters_to_square_feet",
        "square_feet_to_square_meters", "square_meters_to_acres", "acres_to_square_meters",
        "square_meters_to_hectares", "hectares_to_square_meters", "cartesian_to_polar",
        "polar_to_cartesian", "spherical_to_cartesian", "cartesian_to_spherical",
        "normalize_array", "standardize_array", "convert_data_types",
        "format_coordinate_string", "parse_coordinate_string"
    ])

if _constants_available:
    __all__.extend([
        "EARTH_RADIUS_EQUATORIAL", "EARTH_RADIUS_POLAR", "EARTH_RADIUS_MEAN",
        "EARTH_FLATTENING", "EARTH_ECCENTRICITY", "EARTH_GRAVITY_EQUATORIAL",
        "EARTH_GRAVITY_POLES", "EARTH_GRAVITY_MEAN", "PI", "EULER_GAMMA",
        "GOLDEN_RATIO", "DEFAULT_SPATIAL_WEIGHTS_K", "DEFAULT_VARIANCE_THRESHOLD",
        "DEFAULT_CONVERGENCE_TOLERANCE", "DEFAULT_MAX_ITERATIONS", "DEFAULT_IDW_POWER",
        "DEFAULT_KRIGING_RANGE", "DEFAULT_KRIGING_SILL", "DEFAULT_KRIGING_NUGGET",
        "DEFAULT_CONFIDENCE_LEVEL", "DEFAULT_SIGNIFICANCE_LEVEL", "DEFAULT_Z_SCORE_THRESHOLD",
        "WGS84_EPSG_CODE", "WEB_MERCATOR_EPSG_CODE", "UTM_ZONE_WIDTH_DEGREES",
        "UTM_CENTRAL_MERIDIAN_OFFSET", "SECOND", "MINUTE", "HOUR", "DAY", "WEEK",
        "MONTH", "YEAR", "METER_TO_FEET", "FEET_TO_METER", "METER_TO_YARD",
        "YARD_TO_METER", "METER_TO_MILE", "MILE_TO_METER", "METER_TO_KILOMETER",
        "KILOMETER_TO_METER", "METER_TO_NAUTICAL_MILE", "NAUTICAL_MILE_TO_METER",
        "SQUARE_METER_TO_SQUARE_FEET", "SQUARE_FEET_TO_SQUARE_METER",
        "SQUARE_METER_TO_ACRE", "ACRE_TO_SQUARE_METER", "SQUARE_METER_TO_HECTARE",
        "HECTARE_TO_SQUARE_METER", "CELSIUS_TO_FAHRENHEIT_OFFSET",
        "CELSIUS_TO_FAHRENHEIT_FACTOR", "CONSTANTS", "get_constant", "list_constants"
    ])

if _decorators_available:
    __all__.extend([
        "memoize", "memoize_with_expiry", "validate_input", "log_execution",
        "time_execution", "requires_positive_values", "requires_finite_values",
        "handle_exceptions", "deprecated", "requires_numpy_arrays", "cache_results",
        "validate_output", "retry_on_failure"
    ])

if _parallel_available:
    __all__.extend([
        "parallel_compute", "parallel_map", "parallel_matrix_operation",
        "parallel_matrix_multiply", "parallel_distance_matrix",
        "parallel_spatial_interpolation", "parallel_statistical_analysis",
        "get_optimal_worker_count", "parallel_file_processing",
        "memory_efficient_parallel", "DEFAULT_NUM_WORKERS", "MAX_CHUNK_SIZE"
    ])
