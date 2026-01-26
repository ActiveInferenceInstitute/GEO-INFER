# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 12 classes and 106 functions. ## Classes
 and Functions ### ComputationCach
e
 Cache manager for expensive computations. **Methods**: - `get(key: str) -> Optional[Any]`: Get cached value. - `set(key: str, value: Any)`: Set cached value. - `clear()`: Clear all cached values. - `info() -> dict`: Get cache information. ### MathErro
r
 Base exception for mathematical operations. ### NumericalErro
r
 Exception for numerical computation errors. ### ConvergenceErro
r
 Exception for convergence failures in iterative methods. ### SingularMatrixErro
r
 Exception for singular matrix operations. ### TheoremProvingErro
r
 Exception for theorem proving errors. ### ProofVerificationErro
r
 Exception for proof verification errors. ### InformationTheoryErro
r
 Exception for information theory errors. ### InvalidDistributionErro
r
 Exception for invalid probability distributions. ### SpatialErro
r
 Exception for spatial operation errors. ### CoordinateErro
r
 Exception for coordinate transformation errors. ### GeometryErro
r
 Exception for geometric operation errors. ### cache_resul
t
 `cache_result(maxsize: int, ttl: Optional[float])` Decorator to cache function results. ### decorato
r
 `decorator(func: Callable) -> Callable` ### serialize_ar
g
 `serialize_arg(arg)` ### wrappe
r
 `wrapper(*args, **kwargs)` ### get_constan
t
 `get_constant(category: str, name: str) -> Any` Get a constant value by category and name. ### list_constant
s
 `list_constants(category: Optional[str]) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]` List available constants. ### degrees_to_radian
s
 `degrees_to_radians(degrees: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert degrees to radians. ### radians_to_degree
s
 `radians_to_degrees(radians: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert radians to degrees. ### celsius_to_fahrenhei
t
 `celsius_to_fahrenheit(celsius: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Celsius to Fahrenheit. ### fahrenheit_to_celsiu
s
 `fahrenheit_to_celsius(fahrenheit: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Fahrenheit to Celsius. ### kelvin_to_celsiu
s
 `kelvin_to_celsius(kelvin: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Kelvin to Celsius. ### celsius_to_kelvi
n
 `celsius_to_kelvin(celsius: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert Celsius to Kelvin. ### meters_to_fee
t
 `meters_to_feet(meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert meters to feet. ### feet_to_meter
s
 `feet_to_meters(feet: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert feet to meters. ### meters_to_mile
s
 `meters_to_miles(meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert meters to miles. ### miles_to_meter
s
 `miles_to_meters(miles: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert miles to meters. ### meters_to_kilometer
s
 `meters_to_kilometers(meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert meters to kilometers. ### kilometers_to_meter
s
 `kilometers_to_meters(kilometers: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert kilometers to meters. ### square_meters_to_square_fee
t
 `square_meters_to_square_feet(sq_meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square meters to square feet. ### square_feet_to_square_meter
s
 `square_feet_to_square_meters(sq_feet: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square feet to square meters. ### square_meters_to_acre
s
 `square_meters_to_acres(sq_meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square meters to acres. ### acres_to_square_meter
s
 `acres_to_square_meters(acres: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert acres to square meters. ### square_meters_to_hectare
s
 `square_meters_to_hectares(sq_meters: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert square meters to hectares. ### hectares_to_square_meter
s
 `hectares_to_square_meters(hectares: Union[float, np.ndarray]) -> Union[float, np.ndarray]` Convert hectares to square meters. ### cartesian_to_pola
r
 `cartesian_to_polar(x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]` Convert Cartesian coordinates to polar coordinates. ### polar_to_cartesia
n
 `polar_to_cartesian(radius: Union[float, np.ndarray], angle: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]` Convert polar coordinates to Cartesian coordinates. ### spherical_to_cartesia
n
 `spherical_to_cartesian(radius: Union[float, np.ndarray], theta: Union[float, np.ndarray], phi: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray], Union[float, np.ndarray]]` Convert spherical coordinates to Cartesian coordinates. ### cartesian_to_spherica
l
 `cartesian_to_spherical(x: Union[float, np.ndarray], y: Union[float, np.ndarray], z: Union[float, np.ndarray]) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray], Union[float, np.ndarray]]` Convert Cartesian coordinates to spherical coordinates. ### normalize_arra
y
 `normalize_array(array: np.ndarray, method: str, feature_range: Tuple[float, float]) -> np.ndarray` Normalize array using specified method. ### standardize_arra
y
 `standardize_array(array: np.ndarray, center: bool, scale: bool) -> np.ndarray` Standardize array (center and/or scale). ### convert_data_type
s
 `convert_data_types(data: Any, target_type: type) -> Any` Convert data to target type with appropriate handling. ### format_coordinate_strin
g
 `format_coordinate_string(lat: float, lon: float, format_type: str) -> str` Format coordinates as a string. ### parse_coordinate_strin
g
 `parse_coordinate_string(coord_string: str) -> Tuple[float, float]` Parse coordinate string to decimal degrees. ### decimal_to_dm
s
 `decimal_to_dms(decimal: float, is_latitude: bool) -> str` ### decimal_to_d
m
 `decimal_to_dm(decimal: float, is_latitude: bool) -> str` ### memoiz
e
 `memoize(func: Callable) -> Callable` Memoization decorator for caching function results. ### memoize_with_expir
y
 `memoize_with_expiry(expiry_seconds: float) -> Callable` Memoization decorator with time-based cache expiry. ### validate_inpu
t
 `validate_input(**validators) -> Callable` Input validation decorator. ### log_executio
n
 `log_execution(level: int) -> Callable` Logging decorator for function execution. ### time_executio
n
 `time_execution(func: Callable) -> Callable` Timing decorator for measuring function execution time. ### requires_positive_value
s
 `requires_positive_values(*param_names) -> Callable` Decorator to ensure specified parameters contain only positive values. ### requires_finite_value
s
 `requires_finite_values(*param_names) -> Callable` Decorator to ensure specified parameters contain only finite values. ### handle_exception
s
 `handle_exceptions(return_value: Any) -> Callable` Exception handling decorator. ### deprecate
d
 `deprecated(message: str) -> Callable` Deprecation decorator. ### requires_numpy_array
s
 `requires_numpy_arrays(*param_names) -> Callable` Decorator to ensure specified parameters are numpy arrays. ### cache_result
s
 `cache_results(cache_dict: Optional[Dict]) -> Callable` External cache decorator using a provided dictionary. ### validate_outpu
t
 `validate_output(output_validator: Callable) -> Callable` Output validation decorator. ### retry_on_failur
e
 `retry_on_failure(max_retries: int, exceptions: tuple, delay: float) -> Callable` Retry decorator for handling transient failures. ### memoized_fun
c
 `memoized_func(*args, **kwargs)` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### timed_fun
c
 `timed_func(*args, **kwargs)` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### memoized_fun
c
 `memoized_func(*args, **kwargs)` ### clear_cach
e
 `clear_cache()` ### cache_inf
o
 `cache_info()` ### validated_fun
c
 `validated_func(*args, **kwargs)` ### logged_fun
c
 `logged_func(*args, **kwargs)` ### validated_fun
c
 `validated_func(*args, **kwargs)` ### validated_fun
c
 `validated_func(*args, **kwargs)` ### exception_handled_fun
c
 `exception_handled_func(*args, **kwargs)` ### deprecated_fun
c
 `deprecated_func(*args, **kwargs)` ### array_fun
c
 `array_func(*args, **kwargs)` ### cached_fun
c
 `cached_func(*args, **kwargs)` ### clear_cach
e
 `clear_cache()` ### get_cache_siz
e
 `get_cache_size()` ### validated_output_fun
c
 `validated_output_func(*args, **kwargs)` ### retry_fun
c
 `retry_func(*args, **kwargs)` ### parallel_comput
e
 `parallel_compute(func: Callable, data: Union[List, np.ndarray], num_workers: Optional[int], chunk_size: Optional[int], use_processes: bool, max_memory_mb: Optional[float], **kwargs) -> List[Any]` Apply a function to data in parallel with adaptive chunk sizing and memory monitoring. ### parallel_ma
p
 `parallel_map(func: Callable, iterable: Iterable, num_workers: Optional[int], use_processes: bool) -> List[Any]` Parallel version of map function. ### parallel_matrix_operatio
n
 `parallel_matrix_operation(matrix_a: np.ndarray, matrix_b: Optional[np.ndarray], operation: str, num_workers: Optional[int]) -> np.ndarray` Perform parallel matrix operations. ### parallel_matrix_multipl
y
 `parallel_matrix_multiply(matrix_a: np.ndarray, matrix_b: np.ndarray, num_workers: Optional[int]) -> np.ndarray` Parallel matrix multiplication. ### parallel_distance_matri
x
 `parallel_distance_matrix(points_a: np.ndarray, points_b: Optional[np.ndarray], metric: str, num_workers: Optional[int]) -> np.ndarray` Compute distance matrix in parallel. ### parallel_spatial_interpolatio
n
 `parallel_spatial_interpolation(known_points: np.ndarray, known_values: np.ndarray, query_points: np.ndarray, method: str, num_workers: Optional[int], **kwargs) -> np.ndarray` Perform spatial interpolation in parallel. ### parallel_statistical_analysi
s
 `parallel_statistical_analysis(data: np.ndarray, analysis_func: Callable, num_workers: Optional[int], **kwargs) -> Any` Perform statistical analysis in parallel. ### get_optimal_worker_coun
t
 `get_optimal_worker_count(data_size: int, operation_complexity: str) -> int` Determine optimal number of workers based on data size and operation complexity. ### parallel_file_processin
g
 `parallel_file_processing(file_list: List[str], processing_func: Callable, num_workers: Optional[int], file_batch_size: int) -> List[Any]` Process multiple files in parallel. ### memory_efficient_paralle
l
 `memory_efficient_parallel(func: Callable, data: Union[List, np.ndarray], max_memory_mb: float, num_workers: Optional[int]) -> List[Any]` Memory-efficient parallel processing. ### multiply_chun
k
 `multiply_chunk(start_row: int, end_row: int) -> np.ndarray` ### distance_chun
k
 `distance_chunk(start_row: int, end_row: int) -> np.ndarray` ### interpolate_chun
k
 `interpolate_chunk(chunk_indices: np.ndarray) -> np.ndarray` ### analyze_chun
k
 `analyze_chunk(chunk: np.ndarray) -> Any` ### process_batc
h
 `process_batch(batch: List[str]) -> List[Any]` ### validate_probabilitie
s
 `validate_probabilities(func: Callable) -> Callable` Decorator to validate probability distributions. ### validate_coordinate
s
 `validate_coordinates(func: Callable) -> Callable` Decorator to validate spatial coordinates. ### validate_numerica
l
 `validate_numerical(func: Callable) -> Callable` Decorator to validate numerical inputs. ### validate_shap
e
 `validate_shape(expected_shape: Tuple[int, ...], axis: int)` Decorator to validate array shapes. ### validate_rang
e
 `validate_range(param_name: str, min_val: float, max_val: float)` Decorator to validate parameter ranges. ### wrappe
r
 `wrapper(*args, **kwargs)` ### wrappe
r
 `wrapper(*args, **kwargs)` ### wrappe
r
 `wrapper(*args, **kwargs)` ### decorato
r
 `decorator(func: Callable) -> Callable` ### decorato
r
 `decorator(func: Callable) -> Callable` ### wrappe
r
 `wrapper(*args, **kwargs)` ### wrappe
r
 `wrapper(*args, **kwargs)` ## Capabilities
 - **12 classes** for core functionality - **106 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-MATH/src/geo_infer_math/utils` - **Type**: Directory Node 