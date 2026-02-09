# Agent
: core

## Scope
 This directory contains core components for the module. It provides 40 classes and 64 functions.

## Classes
 and Functions

### Point
 Representation of a 2D point with optional z-coordinate.

**Methods**:
- `distance_to(other: 'Point') -> float`: Calculate Euclidean distance to another point.
- `to_array() -> np.ndarray`: Convert to numpy array.

### LineString
 Representation of a line string (sequence of points).

**Methods**:
- `length() -> float`: Calculate the length of the line string.
- `to_array() -> np.ndarray`: Convert to numpy array.

### Polygon
 Representation of a polygon (exterior ring and optional interior rings).

**Methods**:
- `area() -> float`: Calculate the area of the polygon using Shoelace formula.
- `centroid() -> Point`: Calculate the centroid of the polygon.

### GPUAccelerator
 GPU acceleration manager for geospatial computations.

**Methods**:
- `accelerate_matrix_operations(matrices: List[np.ndarray], operation: str) -> List[np.ndarray]`: Accelerate matrix operations using GPU.
- `accelerate_distance_calculations(points1: np.ndarray, points2: np.ndarray) -> np.ndarray`: Accelerate distance matrix calculations using GPU.
- `accelerate_spatial_interpolation(known_points: np.ndarray, known_values: np.ndarray, query_points: np.ndarray, method: str, **kwargs) -> np.ndarray`: Accelerate spatial interpolation using GPU.
- `accelerate_clustering(data: np.ndarray, coordinates: np.ndarray, method: str, **kwargs) -> Dict[str, Any]`: Accelerate clustering operations using GPU.
- `get_performance_info() -> Dict[str, Any]`: Get information about GPU acceleration performance.
- `benchmark_acceleration(test_data: Dict[str, np.ndarray]) -> Dict[str, Any]`: Benchmark GPU vs CPU performance.

### GraphNode
 Representation of a graph node.

### GraphEdge
 Representation of a graph edge.

### SpatialGraph
 Spatial graph representation with geospatial operations.

**Methods**:
- `add_node(node_id: Any, coordinates: Optional[np.ndarray], **attributes) -> None`: Add a node to the graph.
- `add_edge(source: Any, target: Any, weight: float, **attributes) -> None`: Add an edge to the graph.
- `remove_node(node_id: Any) -> None`: Remove a node and all its edges from the graph.
- `get_neighbors(node_id: Any) -> List[Any]`: Get list of neighboring nodes.
- `get_edge_weight(source: Any, target: Any) -> Optional[float]`: Get weight of edge between two nodes.
- `shortest_path(start: Any, end: Any, algorithm: str) -> Tuple[List[Any], float]`: Find shortest path between two nodes.
- `minimum_spanning_tree(algorithm: str) -> 'SpatialGraph'`: Compute minimum spanning tree of the graph.
- `connected_components() -> List[List[Any]]`: Find connected components in the graph.
- `centrality_measures() -> Dict[str, Dict[Any, float]]`: Calculate various centrality measures for nodes.
- `spatial_network_analysis() -> Dict[str, Any]`: Perform spatial network analysis.

### NetworkFlow
 Network flow algorithms for spatial networks.

**Methods**:
- `max_flow(graph: SpatialGraph, source: Any, sink: Any) -> Tuple[float, Dict[Tuple[Any, Any], float]]`: Calculate maximum flow from source to sink using Ford-Fulkerson algorithm.

### ModuleIntegrator
 Helper class for integrating different GEO-INFER-MATH modules.

**Methods**:
- `check_module_compatibility(module_name: str) -> Dict[str, Any]`: Check if a module and its dependencies are available.
- `create_integrated_analysis_pipeline(analysis_type: str, **kwargs) -> Callable`: Create an integrated analysis pipeline combining multiple modules.
- `validate_cross_module_data_flow(source_module: str, target_module: str, data: Any) -> Dict[str, Any]`: Validate data compatibility between modules.

### InterpolationConfig
 Configuration for interpolation methods.

### SpatialInterpolator
 Abstract base class for spatial interpolators.

**Methods**:
- `fit(coordinates: np.ndarray, values: np.ndarray) -> 'SpatialInterpolator'`: Fit the interpolator to training data.
- `predict(coordinates: np.ndarray) -> np.ndarray`: Predict values at coordinates.
- `cross_validate(coordinates: np.ndarray, values: np.ndarray, n_folds: int) -> Dict[str, float]`: Perform cross-validation.

### IDWInterpolator
 Inverse Distance Weighting interpolator.

**Methods**:
- `fit(coordinates: np.ndarray, values: np.ndarray) -> 'IDWInterpolator'`: Fit IDW interpolator to training data.
- `predict(coordinates: np.ndarray) -> np.ndarray`: Predict values using IDW interpolation.

### KrigingInterpolator
 Ordinary Kriging interpolator.

**Methods**:
- `fit(coordinates: np.ndarray, values: np.ndarray) -> 'KrigingInterpolator'`: Fit Kriging interpolator to training data.
- `predict(coordinates: np.ndarray) -> np.ndarray`: Predict values using Kriging interpolation.

### RBFInterpolator
 Radial Basis Function interpolator.

**Methods**:
- `fit(coordinates: np.ndarray, values: np.ndarray) -> 'RBFInterpolator'`: Fit RBF interpolator to training data.
- `predict(coordinates: np.ndarray) -> np.ndarray`: Predict values using RBF interpolation.

### LinearInterpolator
 Linear interpolation using scipy's griddata.

**Methods**:
- `fit(coordinates: np.ndarray, values: np.ndarray) -> 'LinearInterpolator'`: Fit linear interpolator to training data.
- `predict(coordinates: np.ndarray) -> np.ndarray`: Predict values using linear interpolation.

### CubicInterpolator
 Cubic interpolation using scipy's griddata.

**Methods**:
- `fit(coordinates: np.ndarray, values: np.ndarray) -> 'CubicInterpolator'`: Fit cubic interpolator to training data.
- `predict(coordinates: np.ndarray) -> np.ndarray`: Predict values using cubic interpolation.

### InterpolationManager
 Manager for multiple interpolation methods.

**Methods**:
- `interpolate(coordinates: np.ndarray, values: np.ndarray, prediction_coords: np.ndarray, method: Optional[str]) -> np.ndarray`: Perform spatial interpolation.
- `compare_methods(coordinates: np.ndarray, values: np.ndarray, test_coordinates: Optional[np.ndarray], test_values: Optional[np.ndarray]) -> Dict[str, Dict[str, float]]`: Compare different interpolation methods.
- `create_interpolation_grid(bounds: Dict[str, float], resolution: Optional[float]) -> Tuple[np.ndarray, Dict[str, Any]]`: Create a regular grid for interpolation.
- `interpolate_to_grid(coordinates: np.ndarray, values: np.ndarray, bounds: Dict[str, float], method: Optional[str], resolution: Optional[float]) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]`: Interpolate data to a regular grid.

### TensorData
 Container for multi-dimensional geospatial data.

### MatrixOperations
 Linear algebra operations for geospatial matrices.

**Methods**:
- `condition_number(matrix: np.ndarray) -> float`: Calculate the condition number of a matrix.
- `is_positive_definite(matrix: np.ndarray, tolerance: float) -> bool`: Check if a matrix is positive definite.
- `nearest_positive_definite(matrix: np.ndarray, epsilon: float) -> np.ndarray`: Find the nearest positive definite matrix.
- `spatial_weights_matrix(points: np.ndarray, method: str, k: int, threshold: Optional[float]) -> np.ndarray`: Create spatial weights matrix from point coordinates.
- `moran_i_matrix(values: np.ndarray, weights_matrix: np.ndarray) -> Dict[str, float]`: Calculate Moran's I statistic using matrix operations.

### TensorOperations
 Operations for multi-dimensional geospatial data.

**Methods**:
- `create_spatiotemporal_tensor(spatial_data: List[np.ndarray], temporal_indices: List[float], spatial_coords: Optional[np.ndarray]) -> TensorData`: Create a spatiotemporal tensor from spatial data over time.
- `tensor_unfold(tensor: TensorData, mode: int) -> Tuple[np.ndarray, Dict[str, Any]]`: Unfold tensor along a specific mode (MATRICIZATION).
- `tensor_fold(unfolded_matrix: np.ndarray, shape_info: Dict[str, Any]) -> np.ndarray`: Fold unfolded matrix back into tensor.
- `principal_component_analysis(tensor: TensorData, n_components: Optional[int]) -> Dict[str, Any]`: Perform PCA on tensor data.
- `tensor_decomposition(tensor: TensorData, rank: int, method: str) -> Dict[str, Any]`: Perform tensor decomposition (CP or Tucker).

### SpatialLinearAlgebra
 Specialized linear algebra for spatial problems.

**Methods**:
- `solve_spatial_regression(X: np.ndarray, y: np.ndarray, weights_matrix: Optional[np.ndarray]) -> Dict[str, Any]`: Solve spatial regression with optional spatial weights.
- `spatial_eigen_analysis(weights_matrix: np.ndarray, n_eigenvectors: int) -> Dict[str, Any]`: Perform eigen analysis of spatial weights matrix.
- `cholesky_decomposition(matrix: np.ndarray) -> np.ndarray`: Perform Cholesky decomposition for positive definite matrices.
- `matrix_inverse(matrix: np.ndarray, method: str) -> np.ndarray`: Compute matrix inverse using various methods.

### InterpolationResult
 Container for interpolation results.

### OptimizationResult
 Container for optimization results.

### ODEsolution
 Container for ODE solution.

### SpatialInterpolator
 spatial interpolation methods.

**Methods**:
- `fit(points: np.ndarray, values: np.ndarray, **kwargs) -> 'SpatialInterpolator'`: Fit the interpolator to training data.
- `predict(query_points: np.ndarray) -> np.ndarray`: Predict values at query points.

### SpatialOptimizer
 Optimization methods for spatial problems.

**Methods**:
- `minimize(objective: Callable, bounds: List[Tuple[float, float]], initial_guess: Optional[np.ndarray], **kwargs) -> OptimizationResult`: Minimize objective function.

### ODESolver
 ODE solver for spatial-temporal models.

**Methods**:
- `solve(ode_function: Callable, t_span: Tuple[float, float], y0: np.ndarray, t_eval: Optional[np.ndarray], **kwargs) -> ODEsolution`: Solve ODE system.

### PDEsolver
 PDE solver for spatial-temporal problems.

**Methods**:
- `solve_diffusion(initial_condition: np.ndarray, diffusion_coefficient: float, time_steps: int, dt: float, dx: float) -> np.ndarray`: Solve 1D diffusion equation using finite differences.
- `solve_wave_equation(initial_displacement: np.ndarray, initial_velocity: np.ndarray, wave_speed: float, time_steps: int, dt: float, dx: float) -> Tuple[np.ndarray, np.ndarray]`: Solve 1D wave equation using finite differences.

### OptimizationConfig
 Configuration for optimization algorithms.

### Optimizer
 Abstract base class for optimizers.

**Methods**:
- `optimize(objective_function: Callable, bounds: List[Tuple[float, float]], initial_guess: Optional[np.ndarray]) -> Dict[str, Any]`: Optimize the objective function.
- `get_best_solution() -> Tuple[np.ndarray, float]`: Get the best solution found.

### GradientDescentOptimizer
 Gradient descent optimizer.

**Methods**:
- `optimize(objective_function: Callable, bounds: List[Tuple[float, float]], initial_guess: Optional[np.ndarray], gradient_function: Optional[Callable]) -> Dict[str, Any]`: Optimize using gradient descent.

### GeneticAlgorithmOptimizer
 Genetic algorithm optimizer.

**Methods**:
- `optimize(objective_function: Callable, bounds: List[Tuple[float, float]], initial_guess: Optional[np.ndarray]) -> Dict[str, Any]`: Optimize using genetic algorithm.

### ScipyOptimizer
 Wrapper for scipy optimization methods.

**Methods**:
- `optimize(objective_function: Callable, bounds: List[Tuple[float, float]], initial_guess: Optional[np.ndarray], method: str) -> Dict[str, Any]`: Optimize using scipy methods.

### MultiObjectiveOptimizer
 Multi-objective optimization using NSGA-II.

**Methods**:
- `optimize(objective_functions: List[Callable], bounds: List[Tuple[float, float]], initial_guess: Optional[np.ndarray]) -> Dict[str, Any]`: Optimize multiple objectives using NSGA-II.

### OptimizationManager
 Manager for multiple optimization methods.

**Methods**:
- `optimize(objective_function: Callable, bounds: List[Tuple[float, float]], method: str, **kwargs) -> Dict[str, Any]`: Perform optimization.
- `compare_methods(objective_function: Callable, bounds: List[Tuple[float, float]], methods: Optional[List[str]]) -> Dict[str, Dict[str, Any]]`: Compare different optimization methods.

### SpatialDescriptiveStats
 Container for spatial descriptive statistics.

### MoranI
 Implementation of Moran's I statistic for spatial autocorrelation.

**Methods**:
- `compute(values: np.ndarray, coords: np.ndarray) -> Dict[str, float]`: Compute Moran's I statistic.

### SymbolicMath
 Symbolic mathematics engine for geospatial analysis.

**Methods**:
- `define_spatial_model(variables: List[str], equations: List[str], constraints: Optional[List[str]]) -> Dict[str, Any]`: Define a symbolic spatial model.
- `compute_gradients(model: Dict[str, Any], parameters: List[str]) -> Dict[str, Any]`: Compute gradients of model equations with respect to parameters.
- `optimize_symbolic_model(model: Dict[str, Any], objective: str, parameters: List[str], bounds: Optional[Dict[str, Tuple[float, float]]]) -> Dict[str, Any]`: Optimize a symbolic model.
- `derive_spatial_relationships(coordinates: np.ndarray, values: np.ndarray, relationship_type: str) -> Dict[str, Any]`: Derive symbolic relationships between spatial coordinates and values.
- `create_symbolic_spatial_field(domain: Dict[str, float], expression: str, variables: List[str]) -> Dict[str, Any]`: Create a symbolic spatial field.
- `evaluate_symbolic_expression(expression: Any, variable_values: Dict[str, float]) -> float`: Evaluate a symbolic expression with given variable values.
- `differentiate_spatially(expression: Any, variables: List[str]) -> Dict[str, Any]`: Compute spatial derivatives of an expression.
- `integrate_spatially(expression: Any, variables: List[str], limits: Dict[str, Tuple[float, float]]) -> Dict[str, Any]`: Compute spatial integrals of an expression.
- `solve_spatial_equations(equations: List[Any], variables: List[str]) -> Dict[str, Any]`: Solve systems of spatial equations.
- `get_backend_info() -> Dict[str, Any]`: Get information about the symbolic math backend.
- `generate_proof(expression: Any, operation: str, result: Optional[Any]) -> Optional[Dict[str, Any]]`: Generate proof for a symbolic operation.
- `verify_operation(original: Any, result: Any, operation: str) -> bool`: Verify a symbolic operation using theorem proving.
- `improved_differentiate(expression: Any, variable: Any, order: int, verify: bool) -> Tuple[Any, Optional[Dict[str, Any]]]`: automatic differentiation with optional proof generation.
- `verify_spatial_model(model: Dict[str, Any], constraints: Optional[List[str]]) -> Dict[str, Any]`: Verify a spatial model using theorem proving.
- `symbolic_to_numeric_with_proof(expression: Any, variable_values: Dict[str, float], preserve_proof: bool) -> Tuple[float, Optional[Dict[str, Any]]]`: Convert symbolic expression to numeric with proof preservation.

### CRSDefinition
 Definition of a Coordinate Reference System.

### CoordinateTransformer
 Class for transforming coordinates between different CRS.

**Methods**:
- `transform_point(point: Tuple[float, float, Optional[float]]) -> Tuple[float, float, Optional[float]]`: Transform a single point.
- `transform_points(points: np.ndarray) -> np.ndarray`: Transform multiple points.

### haversine_distance
 `haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float` Calculate the great circle distance between two points on the Earth's surface.

### vincenty_distance
 `vincenty_distance(lat1: float, lon1: float, lat2: float, lon2: float, max_iterations: int, tolerance: float) -> float` Calculate the geodesic distance between two points using Vincenty's formula.

### bearing
 `bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float` Calculate the initial bearing from point 1 to point 2.

### destination_point
 `destination_point(lat: float, lon: float, bearing: float, distance: float) -> Tuple[float, float]` Calculate the destination point given a starting point, bearing, and distance.

### point_in_polygon
 `point_in_polygon(point: Point, polygon: Polygon) -> bool` Determine if a point is inside a polygon using the ray casting algorithm.

### buffer_point
 `buffer_point(lat: float, lon: float, distance: float, segments: int) -> List[Tuple[float, float]]` Create a circular buffer around a point.

### line_intersection
 `line_intersection(line1_start: Point, line1_end: Point, line2_start: Point, line2_end: Point) -> Optional[Point]` Find the intersection point of two line segments.

### polygon_area_spherical
 `polygon_area_spherical(polygon: List[Tuple[float, float]]) -> float` Calculate the area of a polygon on the Earth's surface.

### great_circle_distance
 `great_circle_distance(coords1: np.ndarray, coords2: np.ndarray) -> np.ndarray` Calculate the great circle distance between arrays of points.

### is_on_segment
 `is_on_segment(p: Point, q: Point, r: Point) -> bool`

### is_gpu_available
 `is_gpu_available() -> bool` Check if GPU acceleration is available.

### get_gpu_info
 `get_gpu_info() -> Dict[str, Any]` Get GPU acceleration information.

### benchmark_gpu_performance
 `benchmark_gpu_performance(test_data: Dict[str, np.ndarray]) -> Dict[str, Any]` Benchmark GPU vs CPU performance.

### gpu_matrix_multiply
 `gpu_matrix_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray` GPU-accelerated matrix multiplication.

### gpu_distance_matrix
 `gpu_distance_matrix(points1: np.ndarray, points2: np.ndarray) -> np.ndarray` GPU-accelerated distance matrix calculation.

### gpu_spatial_interpolation
 `gpu_spatial_interpolation(known_points: np.ndarray, known_values: np.ndarray, query_points: np.ndarray, method: str, **kwargs) -> np.ndarray` GPU-accelerated spatial interpolation.

### find
 `find(node)`

### union
 `union(node1, node2)`

### create_integrated_workflow
 `create_integrated_workflow(analysis_steps: List[Dict[str, Any]], data: Dict[str, Any]) -> Dict[str, Any]` Create and execute an integrated workflow combining multiple modules.

### environmental_monitoring_workflow
 `environmental_monitoring_workflow(coordinates: np.ndarray, air_quality: np.ndarray, temperature: np.ndarray, humidity: np.ndarray) -> Dict[str, Any]` Execute a standard environmental monitoring workflow.

### verify_with_theorem_proving
 `verify_with_theorem_proving(theorem: str, assumptions: Optional[List[str]], backend: str) -> Dict[str, Any]` Verify mathematical operation using theorem proving.

### information_theory_analysis
 `information_theory_analysis(coordinates: np.ndarray, values: np.ndarray, analysis_type: str) -> Dict[str, Any]` Perform information theory analysis on spatial data.

### urban_planning_workflow
 `urban_planning_workflow(intersections: np.ndarray, connections: List[Tuple[int, int]], land_use: np.ndarray, population_density: np.ndarray) -> Dict[str, Any]` Execute a standard urban planning workflow.

### verify_with_theorem_proving
 `verify_with_theorem_proving(theorem: str, assumptions: Optional[List[str]], backend: str) -> Dict[str, Any]` Verify mathematical operation using theorem proving.

### information_theory_analysis
 `information_theory_analysis(coordinates: np.ndarray, values: np.ndarray, analysis_type: str) -> Dict[str, Any]` Perform information theory analysis on spatial data.

### public_health_workflow
 `public_health_workflow(neighborhood_coords: np.ndarray, health_metrics: np.ndarray, socioeconomic_features: np.ndarray) -> Dict[str, Any]` Execute a standard public health workflow.

### environmental_analysis
 `environmental_analysis(data: Dict[str, Any]) -> Dict[str, Any]` Integrated environmental analysis combining multiple modules.

### urban_analysis
 `urban_analysis(data: Dict[str, Any]) -> Dict[str, Any]` Integrated urban analysis combining multiple modules.

### health_analysis
 `health_analysis(data: Dict[str, Any]) -> Dict[str, Any]` Integrated health analysis combining multiple modules.

### create_interpolation_manager
 `create_interpolation_manager(config: Optional[InterpolationConfig]) -> InterpolationManager` Create a interpolation manager.

### interpolate_spatial_data
 `interpolate_spatial_data(coordinates: np.ndarray, values: np.ndarray, prediction_coords: np.ndarray, method: str) -> np.ndarray` Convenience function for spatial interpolation.

### create_interpolation_grid
 `create_interpolation_grid(bounds: Dict[str, float], resolution: float) -> np.ndarray` Create a regular interpolation grid.

### numerical_integration
 `numerical_integration(func: Callable, a: float, b: float, method: str, n_points: int) -> float` Numerical integration using various methods.

### find_root
 `find_root(func: Callable, bracket: Tuple[float, float], method: str, **kwargs) -> float` Find root of a function.

### minimize_scalar_function
 `minimize_scalar_function(func: Callable, bounds: Tuple[float, float], method: str, **kwargs) -> float` Minimize a scalar function.

### create_optimization_manager
 `create_optimization_manager(config: Optional[OptimizationConfig]) -> OptimizationManager` Create a optimization manager.

### optimize_function
 `optimize_function(objective_function: Callable, bounds: List[Tuple[float, float]], method: str) -> Dict[str, Any]` Convenience function for optimization.

### compare_optimization_methods
 `compare_optimization_methods(objective_function: Callable, bounds: List[Tuple[float, float]]) -> Dict[str, Dict[str, Any]]` Compare different optimization methods.

### getis_ord_g
 `getis_ord_g(values: np.ndarray, weights_matrix: np.ndarray) -> Dict[str, float]` Calculate Getis-Ord G* statistic for hot spot analysis.

### ripley_k
 `ripley_k(points: np.ndarray, distances: List[float], area: float, boundary_correction: bool) -> Dict[str, np.ndarray]` Calculate Ripley's K function for point pattern analysis.

### semivariogram
 `semivariogram(coords: np.ndarray, values: np.ndarray, lag_distances: List[float], tolerance: float) -> Dict[str, np.ndarray]` Calculate empirical semivariogram.

### spatial_descriptive_statistics
 `spatial_descriptive_statistics(coords: np.ndarray, values: np.ndarray) -> SpatialDescriptiveStats` Calculate spatial descriptive statistics.

### spatial_entropy
 `spatial_entropy(values: np.ndarray, bins: int) -> float` Calculate spatial entropy of a distribution.

### local_indicators_spatial_association
 `local_indicators_spatial_association(values: np.ndarray, weights_matrix: np.ndarray) -> Dict[str, np.ndarray]` Calculate Local Indicators of Spatial Association (LISA).

### create_symbolic_math_engine
 `create_symbolic_math_engine(backend: str) -> SymbolicMath` Create a symbolic math engine.

### define_spatial_model
 `define_spatial_model(variables: List[str], equations: List[str], constraints: Optional[List[str]]) -> Dict[str, Any]` Define a symbolic spatial model.

### compute_spatial_gradients
 `compute_spatial_gradients(model: Dict[str, Any], parameters: List[str]) -> Dict[str, Any]` Compute gradients of spatial model.

### geographic_to_projected
 `geographic_to_projected(lon: float, lat: float, projection: str) -> Tuple[float, float]` Transform geographic coordinates to projected coordinates.

### projected_to_geographic
 `projected_to_geographic(x: float, y: float, projection: str) -> Tuple[float, float]` Transform projected coordinates to geographic coordinates.

### utm_zone_from_lon_lat
 `utm_zone_from_lon_lat(lon: float, lat: float) -> Tuple[int, str]` Determine UTM zone from longitude and latitude.

### utm_central_meridian
 `utm_central_meridian(zone: int) -> float` Calculate the central meridian for a UTM zone.

### datum_transformation
 `datum_transformation(x: float, y: float, z: float, from_datum: str, to_datum: str) -> Tuple[float, float, float]` Transform coordinates between different datums.

### affine_transformation
 `affine_transformation(points: np.ndarray, matrix: np.ndarray, translation: np.ndarray) -> np.ndarray` Apply affine transformation to points.

### rotation_matrix_2d
 `rotation_matrix_2d(angle: float) -> np.ndarray` Create 2D rotation matrix.

### rotation_matrix_3d
 `rotation_matrix_3d(axis: str, angle: float) -> np.ndarray` Create 3D rotation matrix around specified axis.

### scale_matrix_2d
 `scale_matrix_2d(sx: float, sy: float) -> np.ndarray` Create 2D scaling matrix.

### scale_matrix_3d
 `scale_matrix_3d(sx: float, sy: float, sz: float) -> np.ndarray` Create 3D scaling matrix.

### shear_matrix_2d
 `shear_matrix_2d(shx: float, shy: float) -> np.ndarray` Create 2D shear matrix.

### sinh
 `sinh(x: float) -> float` Hyperbolic sine function.

### cosh
 `cosh(x: float) -> float` Hyperbolic cosine function.

### tanh
 `tanh(x: float) -> float` Hyperbolic tangent function.

### atanh
 `atanh(x: float) -> float` Inverse hyperbolic tangent function.

### exp
 `exp(x: float) -> float` Exponential function.

### log
 `log(x: float) -> float` Natural logarithm function.

## Capabilities

- **40 classes** for core functionality
- **64 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-MATH/src/geo_infer_math/core`
- **Type**: Directory Node
