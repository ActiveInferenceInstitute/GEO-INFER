# Agent
: boundaries

## Scope
 This directory contains boundaries components for the module. It provides 9 classes and 0 functions.

## Classes
 and Functions

### BoundaryOperation
 Types of boundary operations.

### FlowDirection
 Direction of flow across boundaries.

### BoundaryFlow
 Represents flow across a boundary.

**Methods**:
- `update_flow(new_rate: float, flow_data: Optional[Dict[str, Any]])`: Update flow rate and data.

### BoundaryConstraint
 Represents constraints on boundary behavior.

**Methods**:
- `validate(value: Any) -> bool`: Validate a value against this constraint.

### H3BoundaryManager
 boundary management for nested H3 systems.

**Methods**:
- `detect_boundaries(nested_grid, method: BoundaryDetectionMethod, **kwargs) -> Dict[str, List[BoundarySegment]]`: Detect boundaries in nested grid systems.
- `get_shared_boundaries(system_id1: str, system_id2: str) -> List[BoundarySegment]`: Find boundaries shared between two systems.
- `split_boundary(boundary_id: str, split_points: List[str]) -> List[BoundarySegment]`: Split a boundary segment at specified points.
- `merge_boundaries(boundary_ids: List[str]) -> BoundarySegment`: Merge multiple boundary segments into one.
- `create_flow(source_system: str, target_system: str, flow_type: str, **kwargs) -> BoundaryFlow`: Create a flow between two systems.
- `update_flow(flow_id: str, new_rate: float, flow_data: Optional[Dict[str, Any]])`: Update flow rate and data.
- `add_constraint(boundary_segment_id: str, constraint_type: str, parameters: Dict[str, Any], validation_function: Optional[Callable]) -> BoundaryConstraint`: Add a constraint to a boundary.
- `get_boundary_permeability(boundary_id: str, flow_type: str) -> float`: Calculate boundary permeability for a specific flow type.
- `analyze_flow_network(network_id: str) -> Dict[str, Any]`: Analyze flow patterns in a network.
- `get_boundary_statistics() -> Dict[str, Any]`: Get boundary statistics.

### BoundaryType
 Types of boundaries in nested systems.

### BoundaryDetectionMethod
 Methods for boundary detection.

### BoundarySegment
 Represents a segment of a boundary.

### BoundaryDetector
 boundary detection for nested geospatial systems.

**Methods**:
- `detect_boundaries(nested_grid, method: BoundaryDetectionMethod, system_ids: Optional[List[str]], **kwargs) -> Dict[str, List[BoundarySegment]]`: Detect boundaries in nested systems.
- `get_boundary_summary() -> Dict[str, Any]`: Get summary of boundary detection results.

## Capabilities

- **9 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_space/nested/boundaries`
- **Type**: Directory Node
