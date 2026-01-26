# core
 ## Overview
 This directory contains core components. It includes 11 Python modules. ## Components
 ### geometr
y
.py Geometry Module **Classes**: `Point`, `LineString`, `Polygon` **Functions**: `haversine_distance`, `vincenty_distance`, `bearing`, `destination_point`, `point_in_polygon`, `buffer_point`, `line_intersection`, `polygon_area_spherical`, `great_circle_distance`, `is_on_segment` ### gpu_acceleratio
n
.py GPU Acceleration Module **Classes**: `GPUAccelerator` **Functions**: `is_gpu_available`, `get_gpu_info`, `benchmark_gpu_performance`, `gpu_matrix_multiply`, `gpu_distance_matrix`, `gpu_spatial_interpolation` ### graph_theor
y
.py Graph Theory Module **Classes**: `GraphNode`, `GraphEdge`, `SpatialGraph`, `NetworkFlow` **Functions**: `find`, `union` ### integratio
n
.py Module Integration Utilities **Classes**: `ModuleIntegrator` **Functions**: `create_integrated_workflow`, `environmental_monitoring_workflow`, `verify_with_theorem_proving`, `information_theory_analysis`, `urban_planning_workflow`, `verify_with_theorem_proving`, `information_theory_analysis`, `public_health_workflow`, `environmental_analysis`, `urban_analysis`, `health_analysis` ### interpolatio
n
.py Spatial Interpolation Methods **Classes**: `InterpolationConfig`, `SpatialInterpolator`, `IDWInterpolator`, `KrigingInterpolator`, `RBFInterpolator`, `LinearInterpolator`, `CubicInterpolator`, `InterpolationManager` **Functions**: `create_interpolation_manager`, `interpolate_spatial_data`, `create_interpolation_grid` ### linalg_tenso
r
.py Linear Algebra and Tensor Operations Module **Classes**: `TensorData`, `MatrixOperations`, `TensorOperations`, `SpatialLinearAlgebra` ### numerical_method
s
.py Numerical Methods Module **Classes**: `InterpolationResult`, `OptimizationResult`, `ODEsolution`, `SpatialInterpolator`, `SpatialOptimizer`, `ODESolver`, `PDEsolver` **Functions**: `numerical_integration`, `find_root`, `minimize_scalar_function` ### optimizatio
n
.py Mathematical Optimization Methods **Classes**: `OptimizationConfig`, `Optimizer`, `GradientDescentOptimizer`, `GeneticAlgorithmOptimizer`, `ScipyOptimizer`, `MultiObjectiveOptimizer`, `OptimizationManager` **Functions**: `create_optimization_manager`, `optimize_function`, `compare_optimization_methods` ### spatial_statistic
s
.py Spatial Statistics Module **Classes**: `SpatialDescriptiveStats`, `MoranI` **Functions**: `getis_ord_g`, `ripley_k`, `semivariogram`, `spatial_descriptive_statistics`, `spatial_entropy`, `local_indicators_spatial_association` ### symbolic_mat
h
.py Symbolic Mathematics Module **Classes**: `SymbolicMath` **Functions**: `create_symbolic_math_engine`, `define_spatial_model`, `compute_spatial_gradients` ### transform
s
.py Coordinate Systems and Transformations Module **Classes**: `CRSDefinition`, `CoordinateTransformer` **Functions**: `geographic_to_projected`, `projected_to_geographic`, `utm_zone_from_lon_lat`, `utm_central_meridian`, `datum_transformation`, `affine_transformation`, `rotation_matrix_2d`, `rotation_matrix_3d`, `scale_matrix_2d`, `scale_matrix_3d`, `shear_matrix_2d`, `sinh`, `cosh`, `tanh`, `atanh`, `exp`, `log` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 