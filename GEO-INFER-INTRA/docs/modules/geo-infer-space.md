# GEO-INFER-SPACE: Spatial Analysis Engine

> **Explanation**: Understanding Spatial Analysis in GEO-INFER
> 
> This module provides comprehensive spatial analysis capabilities using H3 geospatial indexing and advanced spatial algorithms for geographic data processing.

## 🎯 What is GEO-INFER-SPACE?

GEO-INFER-SPACE is the spatial analysis engine that provides advanced geospatial capabilities using H3 hexagonal indexing and spatial algorithms. It enables:

- **H3 Geospatial Indexing**: Hierarchical hexagonal grid system for spatial data
- **Spatial Analysis**: Advanced geometric and spatial statistical analysis
- **Spatial Relationships**: Topological, metric, and directional spatial relationships
- **Spatial Indexing**: Efficient spatial data structures and algorithms
- **Coordinate Systems**: Support for multiple coordinate reference systems
- **Spatial Optimization**: Advanced spatial optimization algorithms
- **Spatial Machine Learning**: Spatial-aware machine learning capabilities

### Key Concepts

#### H3 Geospatial Indexing
H3 is a hierarchical hexagonal grid system that provides:
- **Global Coverage**: Covers the entire Earth with hexagonal cells
- **Hierarchical Resolution**: 16 resolution levels from ~4,000km² to ~0.9m²
- **Efficient Indexing**: Fast spatial queries and operations
- **Consistent Geometry**: Hexagonal cells provide uniform spatial relationships
- **Spatial Hierarchies**: Multi-resolution spatial analysis

```python
import h3
from geo_infer_space import SpatialAnalyzer

# Create H3 index for a location
h3_index = h3.latlng_to_cell(37.7749, -122.4194, 9)
print(f"H3 Index: {h3_index}")

# Get neighboring cells with advanced options
neighbors = h3.grid_disk(h3_index, 1)
print(f"Neighbors: {len(neighbors)} cells")

# Perform multi-resolution analysis
multi_res_analysis = h3.multi_resolution_analysis(
    location=(37.7749, -122.4194),
    resolutions=[7, 8, 9, 10],
    analysis_type='hierarchical'
)
```

#### Spatial Analysis Capabilities
The module provides comprehensive spatial analysis tools with advanced features:

```python
from geo_infer_space import SpatialAnalyzer

# Initialize spatial analyzer with advanced features
analyzer = SpatialAnalyzer(
    coordinate_system='EPSG:4326',
    h3_resolution=9,
    parallel_processing=True,
    gpu_acceleration=True
)

# Perform spatial clustering with multiple algorithms
clusters = analyzer.cluster_points(
    points=point_data,
    method='hdbscan',  # Hierarchical density-based clustering
    parameters={
        'min_cluster_size': 5,
        'min_samples': 3,
        'cluster_selection_epsilon': 0.1
    }
)

# Calculate spatial statistics with uncertainty
stats = analyzer.calculate_spatial_statistics(
    data=spatial_data,
    statistics=['mean', 'std', 'min', 'max', 'skewness', 'kurtosis'],
    include_uncertainty=True,
    confidence_level=0.95
)

# Perform spatial interpolation with multiple methods
interpolated = analyzer.interpolate(
    points=known_points,
    values=known_values,
    method='kriging',  # Advanced geostatistical interpolation
    parameters={
        'variogram_model': 'spherical',
        'nugget': 0.1,
        'range': 1000,
        'sill': 1.0
    }
)
```

## 📚 Core Features

### 1. H3 Geospatial Operations

**Purpose**: Efficient spatial indexing and operations using H3 with advanced capabilities.

```python
from geo_infer_space.h3 import H3Analyzer

# Create H3 analyzer with advanced features
h3_analyzer = H3Analyzer(
    default_resolution=9,
    coordinate_system='EPSG:4326',
    parallel_processing=True
)

# Convert coordinates to H3 with validation
h3_index = h3_analyzer.coordinates_to_h3(
    lat=37.7749,
    lng=-122.4194,
    resolution=9,
    validate=True
)

# Get H3 cell boundaries with precision control
boundaries = h3_analyzer.get_cell_boundaries(
    h3_index,
    precision=6  # Decimal places for coordinates
)

# Perform spatial queries with advanced options
nearby_cells = h3_analyzer.get_neighbors(
    h3_index,
    radius=2,
    include_center=False,
    return_distances=True
)

# Aggregate data by H3 cells with multiple aggregation methods
aggregated = h3_analyzer.aggregate_by_cell(
    data=spatial_data,
    resolution=9,
    aggregation_methods=['mean', 'std', 'count', 'sum'],
    fill_missing=True
)

# Multi-resolution analysis
multi_res_data = h3_analyzer.multi_resolution_analysis(
    data=spatial_data,
    resolutions=[7, 8, 9, 10],
    analysis_type='hierarchical'
)
```

### 2. Spatial Statistics

**Purpose**: Advanced spatial statistical analysis with uncertainty quantification.

```python
from geo_infer_space.statistics import SpatialStatisticsEngine

# Initialize spatial statistics engine
spatial_stats = SpatialStatisticsEngine(
    coordinate_system='EPSG:4326',
    confidence_level=0.95,
    bootstrap_samples=10000
)

# Global spatial autocorrelation
moran_i = spatial_stats.global_moran_i(
    data=spatial_data,
    spatial_weights=spatial_weights,
    significance_test=True,
    permutation_test=True
)

# Local spatial autocorrelation
local_moran = spatial_stats.local_moran_i(
    data=spatial_data,
    spatial_weights=spatial_weights,
    significance_level=0.05
)

# Spatial regression with multiple models
spatial_regression = spatial_stats.spatial_regression(
    dependent_variable=dependent_var,
    independent_variables=independent_vars,
    spatial_weights=spatial_weights,
    model_type='spatial_lag',  # or 'spatial_error', 'spatial_durbin'
    diagnostics=True
)

# Geographically weighted regression
gwr_result = spatial_stats.geographically_weighted_regression(
    dependent_variable=dependent_var,
    independent_variables=independent_vars,
    coordinates=coordinates,
    bandwidth='adaptive',
    kernel='gaussian'
)
```

### 3. Spatial Clustering and Classification

**Purpose**: Advanced spatial clustering and classification algorithms.

```python
from geo_infer_space.clustering import SpatialClusteringEngine

# Initialize spatial clustering engine
clustering_engine = SpatialClusteringEngine(
    coordinate_system='EPSG:4326',
    distance_metric='haversine',
    parallel_processing=True
)

# Hierarchical density-based clustering
hdbscan_clusters = clustering_engine.hdbscan_clustering(
    points=spatial_points,
    min_cluster_size=5,
    min_samples=3,
    cluster_selection_epsilon=0.1,
    return_probabilities=True
)

# Spatial K-means with constraints
spatial_kmeans = clustering_engine.spatial_kmeans(
    points=spatial_points,
    n_clusters=5,
    spatial_constraints=True,
    max_iterations=1000
)

# Spectral clustering for spatial data
spectral_clusters = clustering_engine.spectral_clustering(
    points=spatial_points,
    n_clusters=5,
    affinity='rbf',
    gamma=0.1
)

# Spatial classification with machine learning
spatial_classifier = clustering_engine.spatial_classification(
    training_data=training_points,
    features=feature_data,
    algorithm='random_forest',
    spatial_cross_validation=True
)
```

### 4. Spatial Interpolation

**Purpose**: Advanced spatial interpolation methods with uncertainty quantification.

```python
from geo_infer_space.interpolation import SpatialInterpolationEngine

# Initialize spatial interpolation engine
interpolation_engine = SpatialInterpolationEngine(
    coordinate_system='EPSG:4326',
    parallel_processing=True
)

# Kriging interpolation with variogram modeling
kriging_result = interpolation_engine.kriging_interpolation(
    points=known_points,
    values=known_values,
    target_points=target_points,
    variogram_model='spherical',
    parameters={
        'nugget': 0.1,
        'range': 1000,
        'sill': 1.0
    },
    include_uncertainty=True
)

# Inverse distance weighting
idw_result = interpolation_engine.inverse_distance_weighting(
    points=known_points,
    values=known_values,
    target_points=target_points,
    power=2,
    max_neighbors=10
)

# Radial basis function interpolation
rbf_result = interpolation_engine.radial_basis_function(
    points=known_points,
    values=known_values,
    target_points=target_points,
    function='multiquadric',
    smoothing=0.1
)

# Spline interpolation
spline_result = interpolation_engine.spline_interpolation(
    points=known_points,
    values=known_values,
    target_points=target_points,
    method='thin_plate',
    smoothing=0.1
)
```

### 5. Spatial Optimization

**Purpose**: Advanced spatial optimization algorithms for complex spatial problems.

```python
from geo_infer_space.optimization import SpatialOptimizationEngine

# Initialize spatial optimization engine
spatial_optimizer = SpatialOptimizationEngine(
    coordinate_system='EPSG:4326',
    algorithm='genetic_algorithm',
    parallel_processing=True
)

# Facility location optimization
facility_solution = spatial_optimizer.facility_location_optimization(
    demand_points=demand_locations,
    candidate_facilities=facility_candidates,
    objective='minimize_cost',
    constraints=['budget', 'coverage'],
    algorithm='p_median'
)

# Route optimization with multiple constraints
route_solution = spatial_optimizer.route_optimization(
    start_location=start_point,
    end_location=end_point,
    waypoints=intermediate_points,
    constraints=['time', 'distance', 'traffic', 'fuel'],
    algorithm='ant_colony'
)

# Spatial resource allocation
resource_solution = spatial_optimizer.resource_allocation_optimization(
    resources=available_resources,
    demands=spatial_demands,
    constraints=allocation_constraints,
    objective='maximize_coverage',
    algorithm='linear_programming'
)

# Spatial network optimization
network_solution = spatial_optimizer.network_optimization(
    network=spatial_network,
    objective='minimize_cost',
    constraints=['capacity', 'connectivity'],
    algorithm='minimum_spanning_tree'
)
```

### 6. Spatial Machine Learning

**Purpose**: Spatial-aware machine learning capabilities.

```python
from geo_infer_space.ml import SpatialMachineLearningEngine

# Initialize spatial ML engine
spatial_ml = SpatialMachineLearningEngine(
    coordinate_system='EPSG:4326',
    spatial_features=True,
    parallel_processing=True
)

# Spatial random forest
spatial_rf = spatial_ml.spatial_random_forest(
    training_data=training_data,
    features=feature_data,
    spatial_weights=spatial_weights,
    n_estimators=100,
    max_depth=10
)

# Geographically weighted neural network
spatial_nn = spatial_ml.spatial_neural_network(
    training_data=training_data,
    features=feature_data,
    coordinates=coordinates,
    architecture='mlp',
    spatial_regularization=True
)

# Spatial support vector machine
spatial_svm = spatial_ml.spatial_support_vector_machine(
    training_data=training_data,
    features=feature_data,
    spatial_kernel='rbf',
    spatial_weights=spatial_weights
)

# Spatial ensemble methods
spatial_ensemble = spatial_ml.spatial_ensemble(
    base_models=[model1, model2, model3],
    spatial_weights=spatial_weights,
    aggregation_method='weighted_average'
)
```

## 🔧 API Reference

### SpatialAnalyzer

The core spatial analyzer class.

```python
class SpatialAnalyzer:
    def __init__(self, coordinate_system='EPSG:4326', h3_resolution=9, 
                 parallel_processing=True, gpu_acceleration=False):
        """
        Initialize spatial analyzer.
        
        Args:
            coordinate_system (str): Coordinate reference system
            h3_resolution (int): Default H3 resolution
            parallel_processing (bool): Enable parallel processing
            gpu_acceleration (bool): Enable GPU acceleration
        """
    
    def cluster_points(self, points, method='kmeans', **kwargs):
        """Perform spatial clustering with multiple algorithms."""
    
    def calculate_spatial_statistics(self, data, statistics, **kwargs):
        """Calculate spatial statistics with uncertainty."""
    
    def interpolate(self, points, values, method='kriging', **kwargs):
        """Perform spatial interpolation with multiple methods."""
    
    def spatial_autocorrelation(self, data, method='moran_i'):
        """Calculate spatial autocorrelation measures."""
```

### H3Analyzer

H3 geospatial operations.

```python
class H3Analyzer:
    def __init__(self, default_resolution=9, coordinate_system='EPSG:4326'):
        """
        Initialize H3 analyzer.
        
        Args:
            default_resolution (int): Default H3 resolution
            coordinate_system (str): Coordinate reference system
        """
    
    def coordinates_to_h3(self, lat, lng, resolution, validate=True):
        """Convert coordinates to H3 index with validation."""
    
    def get_cell_boundaries(self, h3_index, precision=6):
        """Get H3 cell boundaries with precision control."""
    
    def get_neighbors(self, h3_index, radius, include_center=False):
        """Get neighboring cells with advanced options."""
    
    def aggregate_by_cell(self, data, resolution, aggregation_methods):
        """Aggregate data by H3 cells with multiple methods."""
```

### SpatialStatisticsEngine

Advanced spatial statistics.

```python
class SpatialStatisticsEngine:
    def __init__(self, coordinate_system='EPSG:4326', confidence_level=0.95):
        """
        Initialize spatial statistics engine.
        
        Args:
            coordinate_system (str): Coordinate reference system
            confidence_level (float): Confidence level for intervals
        """
    
    def global_moran_i(self, data, spatial_weights, significance_test=True):
        """Calculate global Moran's I with significance testing."""
    
    def local_moran_i(self, data, spatial_weights, significance_level=0.05):
        """Calculate local Moran's I with significance testing."""
    
    def spatial_regression(self, dependent_variable, independent_variables, 
                          spatial_weights, model_type='spatial_lag'):
        """Perform spatial regression with multiple models."""
```

## 🎯 Use Cases

### 1. Environmental Monitoring

**Problem**: Monitor environmental conditions across large spatial areas with uncertainty quantification.

**Solution**: Use advanced spatial analysis for comprehensive environmental monitoring.

```python
from geo_infer_space import SpatialAnalyzer
from geo_infer_space.statistics import SpatialStatisticsEngine

# Initialize spatial analysis tools
analyzer = SpatialAnalyzer(parallel_processing=True)
spatial_stats = SpatialStatisticsEngine(confidence_level=0.95)

# Analyze environmental data with spatial statistics
environmental_analysis = spatial_stats.analyze_environmental_data(
    data=environmental_data,
    coordinates=monitoring_stations,
    analysis_types=['autocorrelation', 'trends', 'anomalies']
)

# Perform spatial interpolation for missing data
interpolated_data = analyzer.interpolate_environmental_data(
    known_points=monitoring_stations,
    known_values=environmental_measurements,
    target_area=study_area,
    method='kriging',
    include_uncertainty=True
)

# Detect environmental anomalies
anomalies = analyzer.detect_spatial_anomalies(
    data=environmental_data,
    method='local_outlier_factor',
    threshold=2.0
)

# Generate environmental risk maps
risk_maps = analyzer.generate_environmental_risk_maps(
    data=environmental_data,
    risk_factors=['pollution', 'climate', 'human_activity'],
    aggregation_method='weighted_average'
)
```

### 2. Urban Planning

**Problem**: Optimize urban development with complex spatial constraints and interactions.

**Solution**: Use advanced spatial optimization for urban planning.

```python
from geo_infer_space.optimization import SpatialOptimizationEngine
from geo_infer_space.clustering import SpatialClusteringEngine

# Initialize spatial optimization tools
spatial_optimizer = SpatialOptimizationEngine(algorithm='genetic_algorithm')
clustering_engine = SpatialClusteringEngine()

# Optimize facility locations
optimal_facilities = spatial_optimizer.urban_facility_optimization(
    demand_points=population_centers,
    candidate_facilities=facility_candidates,
    constraints=['budget', 'accessibility', 'environmental_impact'],
    objective='maximize_coverage'
)

# Cluster urban areas for planning
urban_clusters = clustering_engine.cluster_urban_areas(
    points=urban_features,
    method='hdbscan',
    parameters={
        'min_cluster_size': 10,
        'min_samples': 5
    }
)

# Optimize transportation networks
transportation_network = spatial_optimizer.optimize_transportation_network(
    network=existing_network,
    demand=transportation_demand,
    constraints=['capacity', 'budget', 'environmental_impact'],
    objective='minimize_travel_time'
)

# Generate urban development scenarios
development_scenarios = spatial_optimizer.generate_urban_scenarios(
    current_state=current_urban_state,
    development_options=development_options,
    constraints=planning_constraints,
    objectives=['sustainability', 'accessibility', 'economic_growth']
)
```

### 3. Agricultural Analysis

**Problem**: Analyze agricultural patterns and optimize farming practices across spatial scales.

**Solution**: Use multi-scale spatial analysis for agricultural optimization.

```python
from geo_infer_space import SpatialAnalyzer
from geo_infer_space.ml import SpatialMachineLearningEngine

# Initialize spatial analysis tools
analyzer = SpatialAnalyzer()
spatial_ml = SpatialMachineLearningEngine()

# Analyze crop yield patterns
yield_analysis = analyzer.analyze_crop_yields(
    data=crop_yield_data,
    coordinates=field_locations,
    analysis_types=['spatial_trends', 'yield_prediction', 'soil_analysis']
)

# Predict crop yields using spatial ML
yield_predictions = spatial_ml.predict_crop_yields(
    training_data=historical_yield_data,
    features=['soil_type', 'climate', 'management_practices'],
    spatial_weights=spatial_weights,
    algorithm='spatial_random_forest'
)

# Optimize irrigation systems
irrigation_optimization = analyzer.optimize_irrigation_systems(
    field_boundaries=field_boundaries,
    soil_data=soil_characteristics,
    climate_data=climate_conditions,
    water_availability=water_resources,
    objective='minimize_water_use'
)

# Generate precision agriculture recommendations
precision_recommendations = analyzer.generate_precision_recommendations(
    field_data=field_characteristics,
    yield_predictions=yield_predictions,
    economic_data=economic_conditions,
    recommendations=['fertilization', 'irrigation', 'pest_control']
)
```

### 4. Disaster Risk Assessment

**Problem**: Assess and predict disaster risks across spatial scales with uncertainty quantification.

**Solution**: Use advanced spatial analysis for comprehensive risk assessment.

```python
from geo_infer_space.statistics import SpatialStatisticsEngine
from geo_infer_space.interpolation import SpatialInterpolationEngine

# Initialize spatial analysis tools
spatial_stats = SpatialStatisticsEngine()
interpolation_engine = SpatialInterpolationEngine()

# Assess multi-hazard risks
multi_hazard_risks = spatial_stats.assess_multi_hazard_risks(
    hazard_data=hazard_information,
    vulnerability_data=vulnerability_indicators,
    exposure_data=exposure_characteristics,
    spatial_weights=spatial_weights
)

# Interpolate risk surfaces
risk_surfaces = interpolation_engine.interpolate_risk_surfaces(
    known_points=risk_assessment_points,
    risk_values=risk_measurements,
    target_area=study_area,
    method='kriging',
    include_uncertainty=True
)

# Generate evacuation routes
evacuation_routes = spatial_stats.optimize_evacuation_routes(
    population_centers=population_locations,
    safe_zones=evacuation_destinations,
    hazard_zones=hazard_areas,
    constraints=['capacity', 'time', 'accessibility']
)

# Predict disaster impacts
impact_predictions = spatial_stats.predict_disaster_impacts(
    hazard_scenarios=hazard_scenarios,
    vulnerability_model=vulnerability_model,
    exposure_data=exposure_data,
    prediction_horizon='2050'
)
```

## 🔗 Integration with Other Modules

### GEO-INFER-ACT Integration

```python
from geo_infer_space import SpatialAnalyzer
from geo_infer_act import ActiveInferenceModel

# Combine spatial analysis with active inference
spatial_analyzer = SpatialAnalyzer()
active_model = ActiveInferenceModel(
    state_space=['temperature', 'humidity'],
    observation_space=['sensor_reading']
)

# Use spatial analysis results as input to active inference
spatial_results = spatial_analyzer.analyze_points(sensor_data)
active_model.update_beliefs(spatial_results)

# Get spatial free energy landscape
spatial_free_energy = spatial_analyzer.calculate_spatial_free_energy(
    active_model=active_model,
    region=analysis_region
)
```

### GEO-INFER-TIME Integration

```python
from geo_infer_space import SpatialAnalyzer
from geo_infer_time import TemporalAnalyzer

# Combine spatial and temporal analysis
spatial_analyzer = SpatialAnalyzer()
temporal_analyzer = TemporalAnalyzer()

# Perform spatiotemporal analysis
spatiotemporal_analysis = spatial_analyzer.spatiotemporal_analysis(
    data=spatiotemporal_data,
    spatial_analyzer=spatial_analyzer,
    temporal_analyzer=temporal_analyzer,
    analysis_types=['trends', 'patterns', 'anomalies']
)
```

### GEO-INFER-AI Integration

```python
from geo_infer_space.ml import SpatialMachineLearningEngine
from geo_infer_ai import AIEngine

# Combine spatial ML with AI capabilities
spatial_ml = SpatialMachineLearningEngine()
ai_engine = AIEngine()

# Use spatial features in AI models
spatial_features = spatial_ml.extract_spatial_features(spatial_data)
ai_model = ai_engine.train_model_with_spatial_features(
    data=training_data,
    spatial_features=spatial_features,
    model_type='spatial_neural_network'
)
```

## 🚨 Troubleshooting

### Common Issues

**H3 indexing problems:**
```python
# Validate H3 indices
h3_analyzer.validate_h3_indices(h3_indices)

# Handle edge cases
edge_cases = h3_analyzer.handle_edge_cases(
    coordinates=problematic_coordinates,
    resolution=9
)

# Use adaptive resolution
adaptive_resolution = h3_analyzer.adaptive_resolution(
    data=spatial_data,
    target_cell_size=1000  # square meters
)
```

**Spatial analysis performance issues:**
```python
# Enable parallel processing
analyzer.enable_parallel_processing(n_workers=8)

# Use spatial indexing
analyzer.enable_spatial_indexing(
    index_type='rtree',
    max_objects_per_node=10
)

# Enable GPU acceleration
analyzer.enable_gpu_acceleration(
    gpu_memory_gb=8,
    mixed_precision=True
)
```

**Interpolation accuracy issues:**
```python
# Validate interpolation parameters
interpolation_engine.validate_parameters(
    points=known_points,
    values=known_values,
    method='kriging'
)

# Use cross-validation
cv_results = interpolation_engine.cross_validate(
    points=known_points,
    values=known_values,
    method='kriging',
    cv_folds=5
)

# Adjust variogram parameters
optimized_variogram = interpolation_engine.optimize_variogram(
    points=known_points,
    values=known_values,
    method='automatic'
)
```

## 📊 Performance Optimization

### Efficient Spatial Processing

```python
# Enable parallel spatial processing
analyzer.enable_parallel_processing(n_workers=8)

# Enable spatial caching
analyzer.enable_spatial_caching(
    cache_size=10000,
    cache_ttl=1800
)

# Enable adaptive spatial algorithms
analyzer.enable_adaptive_algorithms(
    adaptation_rate=0.1,
    adaptation_threshold=0.05
)
```

### Advanced Spatial Optimization

```python
# Enable spatial indexing
analyzer.enable_spatial_indexing(
    index_type='h3',
    resolution=9
)

# Enable spatial compression
analyzer.enable_spatial_compression(
    compression_method='h3',
    compression_ratio=0.1
)

# Enable spatial streaming
analyzer.enable_spatial_streaming(
    chunk_size=1000,
    streaming_method='progressive'
)
```

## 🔒 Security Considerations

### Spatial Data Privacy
```python
# Enable spatial anonymization
analyzer.enable_spatial_anonymization(
    anonymization_method='k_anonymity',
    k_value=5
)

# Enable differential privacy for spatial data
analyzer.enable_spatial_differential_privacy(
    epsilon=1.0,
    delta=1e-5
)
```

## 🔗 Related Documentation

### Tutorials
- **[Spatial Analysis Basics](../getting_started/spatial_analysis_basics.md)** - Learn spatial analysis fundamentals
- **[H3 Geospatial Indexing Tutorial](../getting_started/h3_tutorial.md)** - Master H3 spatial indexing
- **[Spatial Statistics Tutorial](../getting_started/spatial_statistics_tutorial.md)** - Perform spatial statistical analysis

### How-to Guides
- **[Environmental Monitoring with Spatial Analysis](../examples/environmental_monitoring_spatial.md)** - Build environmental monitoring systems
- **[Urban Planning with Spatial Optimization](../examples/urban_planning_spatial.md)** - Optimize urban development
- **[Agricultural Analysis with Spatial ML](../examples/agricultural_spatial_ml.md)** - Apply spatial ML to agriculture

### Technical Reference
- **[Spatial Analysis API Reference](../api/spatial_reference.md)** - Complete spatial analysis API documentation
- **[H3 Operations Guide](../api/h3_operations.md)** - H3 geospatial operations
- **[Spatial Statistics Methods](../api/spatial_statistics_methods.md)** - Available spatial statistical methods

### Explanations
- **[Spatial Analysis Theory](../spatial_analysis_theory.md)** - Deep dive into spatial analysis concepts
- **[H3 Geospatial Indexing](../h3_geospatial_indexing.md)** - Understanding H3 spatial indexing
- **[Spatial Statistics Theory](../spatial_statistics_theory.md)** - Spatial statistical foundations

### Related Modules
- **[GEO-INFER-ACT](../modules/geo-infer-act.md)** - Active inference capabilities
- **[GEO-INFER-TIME](../modules/geo-infer-time.md)** - Temporal analysis capabilities
- **[GEO-INFER-AI](../modules/geo-infer-ai.md)** - AI and machine learning capabilities
- **[GEO-INFER-MATH](../modules/geo-infer-math.md)** - Mathematical foundations

---

**Ready to get started?** Check out the **[Spatial Analysis Basics Tutorial](../getting_started/spatial_analysis_basics.md)** or explore **[Environmental Monitoring Examples](../examples/environmental_monitoring_spatial.md)**! 