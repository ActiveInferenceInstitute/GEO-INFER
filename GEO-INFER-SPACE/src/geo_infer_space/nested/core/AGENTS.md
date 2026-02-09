# Agent
: core

## Scope
 This directory contains core components for the module. It provides 9 classes and 3 functions.

## Classes
 and Functions

### RelationshipType
 Types of hierarchical relationships.

### HierarchyDirection
 Direction of hierarchy traversal.

### HierarchicalRelationship
 Represents a relationship between two systems in a hierarchy.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert to dictionary representation.

### HierarchyManager
 Manages hierarchical relationships between nested systems.

**Methods**:
- `add_system(system_id: str, level: Optional[int])`: Add a system to the hierarchy.
- `remove_system(system_id: str)`: Remove a system from the hierarchy.
- `add_relationship(source_id: str, target_id: str, relationship_type: RelationshipType, strength: float, properties: Dict[str, Any]) -> str`: Add a hierarchical relationship.
- `remove_relationship(rel_id: str)`: Remove a hierarchical relationship.
- `set_system_level(system_id: str, level: int)`: Set the hierarchical level of a system.
- `get_children(system_id: str) -> Set[str]`: Get direct children of a system.
- `get_parent(system_id: str) -> Optional[str]`: Get parent of a system.
- `get_ancestors(system_id: str) -> List[str]`: Get all ancestors of a system (path to root).
- `get_descendants(system_id: str) -> Set[str]`: Get all descendants of a system.
- `get_siblings(system_id: str) -> Set[str]`: Get siblings of a system (same parent).
- `get_systems_at_level(level: int) -> Set[str]`: Get all systems at a specific level.
- `get_level(system_id: str) -> Optional[int]`: Get the level of a system.
- `find_path(source_id: str, target_id: str) -> Optional[List[str]]`: Find path between two systems in the hierarchy.
- `calculate_hierarchy_metrics() -> Dict[str, Any]`: Calculate hierarchy metrics.
- `validate_hierarchy() -> Dict[str, Any]`: Validate the hierarchy structure and return issues.
- `export_hierarchy() -> Dict[str, Any]`: Export hierarchy structure.
- `get_hierarchy_summary() -> Dict[str, Any]`: Get a summary of the hierarchy.

### NestedCellType
 Types of nested cells based on their role in the system.

### NestedSystemState
 States of nested systems.

### NestedCell
 H3 cell with nested system capabilities.

**Methods**:
- `index() -> str`: Get H3 index of the cell.
- `resolution() -> int`: Get H3 resolution of the cell.
- `coordinates() -> Tuple[float, float]`: Get latitude, longitude coordinates.
- `area_km2() -> float`: Get area of the cell in square kilometers.
- `latitude() -> float`: Get latitude of the cell.
- `longitude() -> float`: Get longitude of the cell.
- `add_parent(parent_index: str)`: Add a parent cell relationship.
- `add_child(child_index: str)`: Add a child cell relationship.
- `set_boundary(boundary_id: str, strength: float)`: Mark cell as boundary with specified strength.
- `add_message(message: Any)`: Add message to the cell's queue.
- `process_messages() -> List[Any]`: Process and return all queued messages.
- `update_state(variable: str, value: Any)`: Update a state variable.
- `update_flow(variable: str, value: float)`: Update a flow variable.
- `get_connectivity_degree() -> int`: Get the connectivity degree (number of connections).
- `is_connected_to(other_index: str) -> bool`: Check if connected to another cell.
- `to_dict() -> Dict[str, Any]`: Convert to dictionary representation.

### NestedSystem
 A nested system representing a collection of connected H3 cells.

**Methods**:
- `add_cell(cell: NestedCell)`: Add a cell to the system.
- `remove_cell(cell_index: str) -> bool`: Remove a cell from the system.
- `add_subsystem(subsystem: 'NestedSystem')`: Add a subsystem.
- `remove_subsystem(system_id: str) -> bool`: Remove a subsystem.
- `get_all_cells(include_subsystems: bool) -> Dict[str, NestedCell]`: Get all cells in the system and optionally subsystems.
- `get_boundary_cells() -> Dict[str, NestedCell]`: Get all boundary cells in the system.
- `detect_boundaries(external_cells: Set[str])`: Detect and mark boundary cells.
- `calculate_connectivity() -> Dict[str, Any]`: Calculate system connectivity metrics.
- `merge_with(other_system: 'NestedSystem') -> 'NestedSystem'`: Merge with another system.
- `split_by_criteria(criteria_func) -> List['NestedSystem']`: Split system based on criteria function.
- `get_system_summary() -> Dict[str, Any]`: Get system summary.

### NestedH3Grid
 H3 grid with nested system capabilities.

**Methods**:
- `add_cell(h3_cell: H3Cell, system_id: Optional[str]) -> NestedCell`: Add an H3 cell to the grid.
- `create_system(system_id: str, cell_indices: List[str], name: str, description: str) -> NestedSystem`: Create a nested system from cells.
- `create_hierarchical_system(base_resolution: int, target_resolutions: List[int], bounds: Tuple[float, float, float, float]) -> Dict[int, NestedSystem]`: Create hierarchical nested systems across multiple resolutions.
- `detect_all_boundaries()`: Detect boundaries for all systems in the grid.
- `get_system_by_id(system_id: str) -> Optional[NestedSystem]`: Get system by ID.
- `get_systems_at_level(level: int) -> List[NestedSystem]`: Get all systems at a specific hierarchy level.
- `get_root_systems() -> List[NestedSystem]`: Get all root-level systems.
- `merge_systems(system_id1: str, system_id2: str) -> Optional[NestedSystem]`: Merge two systems.
- `split_system(system_id: str, criteria_func) -> List[NestedSystem]`: Split a system based on criteria.
- `get_grid_summary() -> Dict[str, Any]`: Get grid summary.
- `export_to_geojson() -> Dict[str, Any]`: Export grid to GeoJSON format.

### grid_disk
 `grid_disk(cell_index: str, k: int)` Get cells within k rings using unified interface.

### grid_distance
 `grid_distance(cell1: str, cell2: str)` Get grid distance using unified interface.

### neighbor_cells
 `neighbor_cells(cell_index: str)` Get immediate neighbors using unified interface.

## Capabilities

- **9 classes** for core functionality
- **3 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_space/nested/core`
- **Type**: Directory Node
