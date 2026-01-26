# Agent
: generation ## Scope
 This directory contains generation components for the module. It provides 4 classes and 17 functions. ## Classes
 and Functions ### CustomAlgorithmFramewor
k
 Framework for creating and managing custom procedural art algorithms. **Methods**: - `register_algorithm(name: str, algorithm_function: Callable, description: str, parameters: Optional[Dict], example_usage: str) -> None`: Register a custom algorithm. - `unregister_algorithm(name: str) -> None`: Unregister a custom algorithm. - `get_algorithm_info(name: str) -> Dict`: Get information about a registered algorithm. - `list_algorithms() -> List[str]`: List all registered algorithm names. - `execute_algorithm(name: str, data: Any, width: int, height: int, **params) -> Any`: Execute a registered custom algorithm. - `save_algorithms_to_file(filepath: str) -> None`: Save registered algorithms to a JSON file for persistence. - `load_algorithms_from_file(filepath: str) -> None`: Load algorithms from a JSON file. ### GenerativeMa
p
 A class for creating generative art from geospatial data. **Methods**: - `from_elevation(cls, region: Union[str, np.ndarray, Tuple[float, float, float, float]], resolution: int, abstraction_level: float, style: str) -> 'GenerativeMap'`: Create generative art from elevation data. - `save(output_path: str) -> str`: Save the generated art to a file. - `show() -> None`: Display the generated art. - `create_animation(output_path: str, parameter_sweep: str, values: List[float], duration: float, fps: int) -> str`: Create an animated generative map by varying a parameter. - `apply_texture(texture_type: str, **kwargs) -> 'GenerativeMap'`: Apply a texture overlay to the generated map. - `blend_with(other_map: 'GenerativeMap', alpha: float) -> 'GenerativeMap'`: Blend this map with another GenerativeMap. - `add_effects(effects: List[str], **kwargs) -> 'GenerativeMap'`: Apply visual effects to the generated map. - `export_multi_format(base_path: str, formats: List[str]) -> List[str]`: Export the map in multiple formats. ### PerformanceOptimize
r
 Performance optimization utilities for geospatial art generation. **Methods**: - `get_cache_key(func_name: str, args: tuple, kwargs: dict) -> str`: Generate a cache key for function call. - `cached_execution(func: Callable, args: tuple, kwargs: dict, cache_key: Optional[str]) -> Any`: Execute a function with caching. - `parallel_execution(func: Callable, parameter_sets: List[Dict], max_workers: Optional[int], progress_callback: Optional[Callable]) -> List[Any]`: Execute a function in parallel with different parameter sets. - `benchmark_function(func: Callable, args: tuple, kwargs: dict, iterations: int) -> Dict[str, float]`: Benchmark a function's performance. - `optimize_resolution(target_time: float, min_resolution: int, max_resolution: int, test_function: Optional[Callable], test_args: tuple, test_kwargs: dict) -> int`: Find optimal resolution for target execution time. - `memory_efficient_processing(data: np.ndarray, chunk_size: int, process_function: Callable) -> np.ndarray`: Process large arrays in chunks to manage memory usage. - `create_performance_report() -> Dict[str, Any]`: Create a performance report. ### ProceduralAr
t
 A class for creating procedural and algorithmic art from geospatial data. **Methods**: - `from_geo_coordinates(cls, lat: float, lon: float, algorithm: str, additional_params: Optional[Dict]) -> 'ProceduralArt'`: Create procedural art seeded by geographic coordinates. - `from_geo_features(cls, feature_type: str, feature_count: int, algorithm: str, additional_params: Optional[Dict]) -> 'ProceduralArt'`: Create procedural art based on geographic feature statistics. - `generate() -> None`: Generate the procedural art based on the selected algorithm and parameters. - `save(output_path: str) -> str`: Save the generated art to a file. - `show() -> None`: Display the generated art. ### example_spiral_algorith
m
 `example_spiral_algorithm(data, params, width, height)` Example custom algorithm that creates spiral patterns. ### example_cellular_growth_algorith
m
 `example_cellular_growth_algorithm(data, params, width, height)` Example algorithm simulating cellular growth patterns. ### example_fractal_landscape_algorith
m
 `example_fractal_landscape_algorithm(data, params, width, height)` Example algorithm creating fractal landscape patterns. ### animat
e
 `animate(frame_num)` ### cache_resul
t
 `cache_result(cache_optimizer: PerformanceOptimizer)` Decorator for caching function results. ### parallel_ma
p
 `parallel_map(func: Callable, items: List[Any], max_workers: Optional[int]) -> List[Any]` Apply a function to a list of items in parallel. ### time_executio
n
 `time_execution(func: Callable)` Decorator for timing function execution. ### decorato
r
 `decorator(func)` ### wrappe
r
 `wrapper(params)` ### wrappe
r
 `wrapper(*args, **kwargs)` ### wrappe
r
 `wrapper(*args, **kwargs)` ### test_functio
n
 `test_function(resolution)` ### draw_branc
h
 `draw_branch(x, y, length, angle, branch_depth, ax)` ### dragon_curv
e
 `dragon_curve(x, y, length, angle, depth)` ### hilbert_curv
e
 `hilbert_curve(order, x, y, lg, i1, i2)` ### koch_curv
e
 `koch_curve(x1, y1, x2, y2, depth)` ### remove_squar
e
 `remove_square(x, y, size)` ## Capabilities
 - **4 classes** for core functionality - **17 functions** for utility operations ## Integration
 - **Location**: `src/geo_infer_art/core/generation` - **Type**: Directory Node 