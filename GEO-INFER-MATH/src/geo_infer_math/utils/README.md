# utils
 ## Overview
 This directory contains utils components. It includes 7 Python modules. ## Components
 ### cachin
g
.py Caching Utilities for Expensive Computations **Classes**: `ComputationCache` **Functions**: `cache_result`, `_create_cache_key`, `decorator`, `serialize_arg`, `wrapper` ### constant
s
.py Constants Module **Functions**: `get_constant`, `list_constants` ### conversio
n
.py Conversion Utilities Module **Functions**: `degrees_to_radians`, `radians_to_degrees`, `celsius_to_fahrenheit`, `fahrenheit_to_celsius`, `kelvin_to_celsius`, `celsius_to_kelvin`, `meters_to_feet`, `feet_to_meters`, `meters_to_miles`, `miles_to_meters`, `meters_to_kilometers`, `kilometers_to_meters`, `square_meters_to_square_feet`, `square_feet_to_square_meters`, `square_meters_to_acres`, `acres_to_square_meters`, `square_meters_to_hectares`, `hectares_to_square_meters`, `cartesian_to_polar`, `polar_to_cartesian`, `spherical_to_cartesian`, `cartesian_to_spherical`, `normalize_array`, `standardize_array`, `convert_data_types`, `format_coordinate_string`, `parse_coordinate_string`, `decimal_to_dms`, `decimal_to_dm` ### decorator
s
.py Decorators Module **Functions**: `memoize`, `memoize_with_expiry`, `validate_input`, `log_execution`, `time_execution`, `requires_positive_values`, `requires_finite_values`, `handle_exceptions`, `deprecated`, `requires_numpy_arrays`, `cache_results`, `validate_output`, `retry_on_failure`, `memoized_func`, `decorator`, `decorator`, `decorator`, `timed_func`, `decorator`, `decorator`, `decorator`, `decorator`, `decorator`, `decorator`, `decorator`, `decorator`, `memoized_func`, `clear_cache`, `cache_info`, `validated_func`, `logged_func`, `validated_func`, `validated_func`, `exception_handled_func`, `deprecated_func`, `array_func`, `cached_func`, `clear_cache`, `get_cache_size`, `validated_output_func`, `retry_func` ### exception
s
.py Custom Exceptions for GEO-INFER-MATH **Classes**: `MathError`, `NumericalError`, `ConvergenceError`, `SingularMatrixError`, `TheoremProvingError`, `ProofVerificationError`, `InformationTheoryError`, `InvalidDistributionError`, `SpatialError`, `CoordinateError`, `GeometryError` ### paralle
l
.py Parallel Processing Module **Functions**: `parallel_compute`, `_calculate_optimal_chunk_size`, `_create_memory_aware_chunks`, `parallel_map`, `parallel_matrix_operation`, `parallel_matrix_multiply`, `parallel_distance_matrix`, `parallel_spatial_interpolation`, `parallel_statistical_analysis`, `get_optimal_worker_count`, `parallel_file_processing`, `memory_efficient_parallel`, `multiply_chunk`, `distance_chunk`, `interpolate_chunk`, `analyze_chunk`, `process_batch` ### validatio
n
.py Validation Utilities **Functions**: `validate_probabilities`, `validate_coordinates`, `validate_numerical`, `validate_shape`, `validate_range`, `wrapper`, `wrapper`, `wrapper`, `decorator`, `decorator`, `wrapper`, `wrapper` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 