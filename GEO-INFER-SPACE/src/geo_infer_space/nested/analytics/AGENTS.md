# Agent
: analytics

## Scope
 This directory contains analytics components for the module. It provides 27 classes and 0 functions.

## Classes
 and Functions

### FlowType
 Types of flows in nested systems.

### FlowDirection
 Direction of flow.

### FlowPattern
 Flow patterns in systems.

### FlowVector
 Represents a flow vector between cells.

**Methods**:
- `get_flow_rate() -> float`: Calculate flow rate (magnitude/time).

### FlowField
 Represents a flow field across multiple cells.

**Methods**:
- `add_vector(vector: FlowVector)`: Add a flow vector to the field.

### FlowAnalysisResult
 Result of flow analysis.

### H3FlowAnalyzer
 flow analyzer for H3 nested systems.

**Methods**:
- `create_flow_field(field_id: str, flow_type: FlowType) -> FlowField`: Create a flow field.
- `add_flow_vector(field_id: str, source_cell: str, target_cell: str, magnitude: float, direction: float, velocity: float, flow_data: Optional[Dict[str, Any]]) -> FlowVector`: Add a flow vector to a field.
- `analyze_flow_patterns(field_id: str, **kwargs) -> FlowAnalysisResult`: Analyze flow patterns in a field.
- `get_flow_statistics() -> Dict[str, Any]`: Get flow analyzer statistics.

### HierarchyMetric
 Types of hierarchy metrics.

### HierarchyStructure
 Types of hierarchy structures.

### HierarchyNode
 Represents a node in the hierarchy.

**Methods**:
- `add_child(child_id: str)`: Add a child node.
- `remove_child(child_id: str)`: Remove a child node.
- `is_leaf() -> bool`: Check if node is a leaf.
- `is_root() -> bool`: Check if node is a root.

### HierarchyMetrics
 metrics for a hierarchy.

### HierarchyAnalysisResult
 Result of hierarchy analysis.

### H3HierarchyAnalyzer
 hierarchy analyzer for H3 nested systems.

**Methods**:
- `create_hierarchy(hierarchy_id: str) -> Dict[str, HierarchyNode]`: Create a hierarchy.
- `add_node(hierarchy_id: str, node_id: str, level: int, parent_id: Optional[str], h3_index: Optional[str], properties: Optional[Dict[str, Any]]) -> HierarchyNode`: Add a node to a hierarchy.
- `analyze_hierarchy(hierarchy_id: str, **kwargs) -> HierarchyAnalysisResult`: Perform hierarchy analysis.
- `get_hierarchy_statistics() -> Dict[str, Any]`: Get hierarchy analyzer statistics.

### PatternType
 Types of patterns that can be detected.

### PatternScale
 Scale at which patterns are detected.

### DetectionMethod
 Methods for pattern detection.

### Pattern
 Represents a detected pattern.

**Methods**:
- `get_pattern_summary() -> Dict[str, Any]`: Get summary of pattern properties.

### PatternDetectionResult
 Result of pattern detection analysis.

### H3PatternDetector
 pattern detector for H3 nested systems.

**Methods**:
- `register_custom_detector(name: str, detector_function: Callable)`: Register a custom pattern detection function.
- `detect_patterns(nested_grid, system_id: Optional[str], pattern_types: Optional[List[PatternType]], methods: Optional[List[DetectionMethod]], **kwargs) -> PatternDetectionResult`: Detect patterns in nested grid systems.
- `get_pattern_statistics() -> Dict[str, Any]`: Get pattern detector statistics.

### PerformanceMetric
 Types of performance metrics.

### BenchmarkType
 Types of benchmarks.

### OptimizationTarget
 Optimization targets.

### PerformanceMeasurement
 Represents a single performance measurement.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert measurement to dictionary.

### BenchmarkResult
 Result of a benchmark test.

**Methods**:
- `add_measurement(measurement: PerformanceMeasurement)`: Add a measurement to the benchmark.

### PerformanceProfile
 Performance profile for a system or operation.

**Methods**:
- `update_metrics(metrics: Dict[PerformanceMetric, float])`: Update current metrics and trends.

### PerformanceMonitor
 Context manager for monitoring performance.

### H3PerformanceAnalyzer
 performance analyzer for H3 nested systems.

**Methods**:
- `record_measurement(metric_type: PerformanceMetric, value: float, unit: str, operation_name: str, system_context: Optional[Dict[str, Any]], tags: Optional[Dict[str, str]]) -> PerformanceMeasurement`: Record a performance measurement.
- `monitor_operation(operation_name: str) -> PerformanceMonitor`: Create a performance monitor for an operation.
- `run_benchmark(benchmark_type: BenchmarkType, target_function: Callable, test_config: Optional[Dict[str, Any]], **kwargs) -> BenchmarkResult`: Run a benchmark test.
- `create_performance_profile(profile_id: str, target_operation: str, baseline_metrics: Optional[Dict[PerformanceMetric, float]]) -> PerformanceProfile`: Create a performance profile.
- `update_performance_profile(profile_id: str, metrics: Dict[PerformanceMetric, float])`: Update a performance profile with metrics.
- `start_monitoring()`: Start real-time performance monitoring.
- `stop_monitoring()`: Stop real-time performance monitoring.
- `get_performance_summary(operation_name: Optional[str], time_window: Optional[timedelta]) -> Dict[str, Any]`: Get performance summary.
- `get_analyzer_statistics() -> Dict[str, Any]`: Get analyzer statistics.

## Capabilities

- **27 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_space/nested/analytics`
- **Type**: Directory Node
