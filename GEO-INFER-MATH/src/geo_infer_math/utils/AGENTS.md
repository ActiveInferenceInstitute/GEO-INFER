# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 12 classes and 106 functions.

## Classes
 and Functions

### ComputationCache
 Cache manager for expensive computations.

**Methods**:
- `get(key: str) -> Optional[Any]`: Get cached value.
- `set(key: str, value: Any)`: Set cached value.
- `clear()`: Clear all cached values.
- `info() -> dict`: Get cache information.

### MathError
 Base exception for mathematical operations.

### NumericalError
 Exception for numerical computation errors.

### ConvergenceError
 Exception for convergence failures in iterative methods.

### SingularMatrixError
 Exception for singular matrix operations.

### TheoremProvingError
 Exception for theorem proving errors.

### ProofVerificationError
 Exception for proof verification errors.

### InformationTheoryError
 Exception for information theory errors.

### InvalidDistributionError
 Exception for invalid probability distributions.

### SpatialError
 Exception for spatial operation errors.

### CoordinateError
 Exception for coordinate transformation errors.

### GeometryError
 Exception for geometric operation errors.

### cache_result
 `cache_result(maxsize: int, ttl: Optional[float])` Decorator to cache function results.

### decorator
 `decorator(func: Callable) -> Callable`

### serialize_arg
 `serialize_arg(arg)`

### wrapper
 `wrapper(*args, **kwargs)`

### get_constant
 `get_constant(category: str, name: str) -> Any` Get a constant value by category and name.

### list_constants
 `list_constants(category: Optional[str]) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]` List available constants.

### degrees_to_radians
 `degrees_to_radians(degrees: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert degrees to radians.

### radians_to_degrees
 `radians_to_degrees(radians: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert radians to degrees.

### celsius_to_fahrenheit
 `celsius_to_fahrenheit(celsius: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Celsius to Fahrenheit.

### fahrenheit_to_celsius
 `fahrenheit_to_celsius(fahrenheit: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Fahrenheit to Celsius.

### kelvin_to_celsius
 `kelvin_to_celsius(kelvin: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Kelvin to Celsius.

### celsius_to_kelvin
 `celsius_to_kelvin(celsius: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Celsius to Kelvin.

### meters_to_feet
 `meters_to_feet(meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert meters to feet.

### feet_to_meters
 `feet_to_meters(feet: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert feet to meters.

### meters_to_miles
 `meters_to_miles(meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert meters to miles.

### miles_to_meters
 `miles_to_meters(miles: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert miles to meters.

### meters_to_kilometers
 `meters_to_kilometers(meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert meters to kilometers.

### kilometers_to_meters
 `kilometers_to_meters(kilometers: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert kilometers to meters.

### square_meters_to_square_feet
 `square_meters_to_square_feet(sq_meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square meters to square feet.

### square_feet_to_square_meters
 `square_feet_to_square_meters(sq_feet: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square feet to square meters.

### square_meters_to_acres
 `square_meters_to_acres(sq_meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square meters to acres.

### acres_to_square_meters
 `acres_to_square_meters(acres: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert acres to square meters.

### square_meters_to_hectares
 `square_meters_to_hectares(sq_meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square meters to hectares.

### hectares_to_square_meters
 `hectares_to_square_meters(hectares: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert hectares to square meters.

### cartesian_to_polar
 `cartesian_to_polar(x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]` Convert Cartesian coordinates to polar coordinates.

### polar_to_cartesian
 `polar_to_cartesian(radius: Union[float, np.ndarray], angle: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]` Convert polar coordinates to Cartesian coordinates.

### spherical_to_cartesian
 `spherical_to_cartesian(radius: Union[float, np.ndarray], theta: Union[float, np.ndarray], phi: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray], Union[float, np.ndarray]]` Convert spherical coordinates to Cartesian coordinates.

### cartesian_to_spherical
 `cartesian_to_spherical(x: Union[float, np.ndarray], y: Union[float, np.ndarray], z: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray], Union[float, np.ndarray]]` Convert Cartesian coordinates to spherical coordinates.

### normalize_array
 `normalize_array(array: np.ndarray, method: str, feature_range: Tuple[float, float]) -> np.ndarray` Normalize array using specified method.

### standardize_array
 `standardize_array(array: np.ndarray, center: bool, scale: bool) -> np.ndarray` Standardize array (center and/or scale).

### convert_data_types
 `convert_data_types(data: Any, target_type: type) -> Any` Convert data to target type with appropriate handling.

### format_coordinate_string
 `format_coordinate_string(lat: float, lon: float, format_type: str) -> str` Format coordinates as a string.

### parse_coordinate_string
 `parse_coordinate_string(coord_string: str) -> Tuple[float, float]` Parse coordinate string to decimal degrees.

### decimal_to_dms
 `decimal_to_dms(decimal: float, is_latitude: bool) -> str`

### decimal_to_dm
 `decimal_to_dm(decimal: float, is_latitude: bool) -> str`

### memoize
 `memoize(func: Callable) -> Callable` Memoization decorator for caching function results.

### memoize_with_expiry
 `memoize_with_expiry(expiry_seconds: float) -> Callable` Memoization decorator with time-based cache expiry.

### validate_input
 `validate_input(**validators) -> Callable` Input validation decorator.

### log_execution
 `log_execution(level: int) -> Callable` Logging decorator for function execution.

### time_execution
 `time_execution(func: Callable) -> Callable` Timing decorator for measuring function execution time.

### requires_positive_values
 `requires_positive_values(*param_names) -> Callable` Decorator to ensure specified parameters contain only positive values.

### requires_finite_values
 `requires_finite_values(*param_names) -> Callable` Decorator to ensure specified parameters contain only finite values.

### handle_exceptions
 `handle_exceptions(return_value: Any) -> Callable` Exception handling decorator.

### deprecated
 `deprecated(message: str) -> Callable` Deprecation decorator.

### requires_numpy_arrays
 `requires_numpy_arrays(*param_names) -> Callable` Decorator to ensure specified parameters are numpy arrays.

### cache_results
 `cache_results(cache_dict: Optional[Dict]) -> Callable` External cache decorator using a provided dictionary.

### validate_output
 `validate_output(output_validator: Callable) -> Callable` Output validation decorator.

### retry_on_failure
 `retry_on_failure(max_retries: int, exceptions: tuple, delay: float) -> Callable` Retry decorator for handling transient failures.

### memoized_func
 `memoized_func(*args, **kwargs)`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### timed_func
 `timed_func(*args, **kwargs)`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### memoized_func
 `memoized_func(*args, **kwargs)`

### clear_cache
 `clear_cache()`

### cache_info
 `cache_info()`

### validated_func
 `validated_func(*args, **kwargs)`

### logged_func
 `logged_func(*args, **kwargs)`

### validated_func
 `validated_func(*args, **kwargs)`

### validated_func
 `validated_func(*args, **kwargs)`

### exception_handled_func
 `exception_handled_func(*args, **kwargs)`

### deprecated_func
 `deprecated_func(*args, **kwargs)`

### array_func
 `array_func(*args, **kwargs)`

### cached_func
 `cached_func(*args, **kwargs)`

### clear_cache
 `clear_cache()`

### get_cache_size
 `get_cache_size()`

### validated_output_func
 `validated_output_func(*args, **kwargs)`

### retry_func
 `retry_func(*args, **kwargs)`

### parallel_compute
 `parallel_compute(func: Callable, data: Union[List, np.ndarray], num_workers: Optional[int], chunk_size: Optional[int], use_processes: bool, max_memory_mb: Optional[float], **kwargs) -> List[Any]` Apply a function to data in parallel with adaptive chunk sizing and memory monitoring.

### parallel_map
 `parallel_map(func: Callable, iterable: Iterable, num_workers: Optional[int], use_processes: bool) -> List[Any]` Parallel version of map function.

### parallel_matrix_operation
 `parallel_matrix_operation(matrix_a: np.ndarray, matrix_b: Optional[np.ndarray], operation: str, num_workers: Optional[int]) -> np.ndarray` Perform parallel matrix operations.

### parallel_matrix_multiply
 `parallel_matrix_multiply(matrix_a: np.ndarray, matrix_b: np.ndarray, num_workers: Optional[int]) -> np.ndarray` Parallel matrix multiplication.

### parallel_distance_matrix
 `parallel_distance_matrix(points_a: np.ndarray, points_b: Optional[np.ndarray], metric: str, num_workers: Optional[int]) -> np.ndarray` Compute distance matrix in parallel.

### parallel_spatial_interpolation
 `parallel_spatial_interpolation(known_points: np.ndarray, known_values: np.ndarray, query_points: np.ndarray, method: str, num_workers: Optional[int], **kwargs) -> np.ndarray` Perform spatial interpolation in parallel.

### parallel_statistical_analysis
 `parallel_statistical_analysis(data: np.ndarray, analysis_func: Callable, num_workers: Optional[int], **kwargs) -> Any` Perform statistical analysis in parallel.

### get_optimal_worker_count
 `get_optimal_worker_count(data_size: int, operation_complexity: str) -> int` Determine optimal number of workers based on data size and operation complexity.

### parallel_file_processing
 `parallel_file_processing(file_list: List[str], processing_func: Callable, num_workers: Optional[int], file_batch_size: int) -> List[Any]` Process multiple files in parallel.

### memory_efficient_parallel
 `memory_efficient_parallel(func: Callable, data: Union[List, np.ndarray], max_memory_mb: float, num_workers: Optional[int]) -> List[Any]` Memory-efficient parallel processing.

### multiply_chunk
 `multiply_chunk(start_row: int, end_row: int) -> np.ndarray`

### distance_chunk
 `distance_chunk(start_row: int, end_row: int) -> np.ndarray`

### interpolate_chunk
 `interpolate_chunk(chunk_indices: np.ndarray) -> np.ndarray`

### analyze_chunk
 `analyze_chunk(chunk: np.ndarray) -> Any`

### process_batch
 `process_batch(batch: List[str]) -> List[Any]`

### validate_probabilities
 `validate_probabilities(func: Callable) -> Callable` Decorator to validate probability distributions.

### validate_coordinates
 `validate_coordinates(func: Callable) -> Callable` Decorator to validate spatial coordinates.

### validate_numerical
 `validate_numerical(func: Callable) -> Callable` Decorator to validate numerical inputs.

### validate_shape
 `validate_shape(expected_shape: Tuple[int, ...], axis: int)` Decorator to validate array shapes.

### validate_range
 `validate_range(param_name: str, min_val: float, max_val: float)` Decorator to validate parameter ranges.

### wrapper
 `wrapper(*args, **kwargs)`

### wrapper
 `wrapper(*args, **kwargs)`

### wrapper
 `wrapper(*args, **kwargs)`

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### wrapper
 `wrapper(*args, **kwargs)`

### wrapper
 `wrapper(*args, **kwargs)`

## Capabilities

- **12 classes** for core functionality
- **106 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-MATH/src/geo_infer_math/utils`
- **Type**: Directory Node
