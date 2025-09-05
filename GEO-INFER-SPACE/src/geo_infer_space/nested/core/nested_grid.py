"""
Nested H3 Grid System.

This module provides the core classes for managing nested H3 hexagonal grids
with hierarchical relationships, boundary management, and system-level operations.
"""

import logging
import math
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available. Some functionality will be limited.")

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False
    logger.warning("h3-py package not available. Install with 'pip install h3'")

# Import H3 components from the main h3 module
try:
    from ...h3.core import H3Grid, H3Cell
    from ...h3.operations import grid_disk, grid_distance, neighbor_cells
    H3_CORE_AVAILABLE = True
except ImportError:
    H3_CORE_AVAILABLE = False
    logger.warning("H3 core components not available")


class NestedCellType(Enum):
    """Types of nested cells based on their role in the system."""
    CORE = "core"           # Interior cells
    BOUNDARY = "boundary"   # Cells on system boundaries
    INTERFACE = "interface" # Cells at interfaces between subsystems
    BRIDGE = "bridge"       # Cells connecting different hierarchical levels
    ISOLATED = "isolated"   # Cells with no connections


class NestedSystemState(Enum):
    """States of nested systems."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSITIONING = "transitioning"
    MERGING = "merging"
    SPLITTING = "splitting"
    STABLE = "stable"


@dataclass
class NestedCell:
    """
    Enhanced H3 cell with nested system capabilities.
    
    Extends the basic H3Cell with hierarchical relationships,
    boundary information, and message passing capabilities.
    """
    
    # Core H3 properties
    h3_cell: H3Cell
    
    # Nested system properties
    system_id: Optional[str] = None
    parent_cells: Set[str] = field(default_factory=set)
    child_cells: Set[str] = field(default_factory=set)
    neighbor_cells: Set[str] = field(default_factory=set)
    
    # Cell classification
    cell_type: NestedCellType = NestedCellType.CORE
    hierarchy_level: int = 0
    
    # Boundary information
    is_boundary: bool = False
    boundary_ids: Set[str] = field(default_factory=set)
    boundary_strength: float = 0.0
    
    # Message passing
    message_queue: List[Any] = field(default_factory=list)
    message_history: List[Any] = field(default_factory=list)
    
    # System dynamics
    state_variables: Dict[str, Any] = field(default_factory=dict)
    flow_variables: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize nested cell after creation."""
        if H3_AVAILABLE and self.h3_cell:
            # Initialize neighbor relationships
            self._update_neighbors()
            
            # Set initial state
            self.updated_at = datetime.now()
    
    @property
    def index(self) -> str:
        """Get H3 index of the cell."""
        return self.h3_cell.index if self.h3_cell else ""
    
    @property
    def resolution(self) -> int:
        """Get H3 resolution of the cell."""
        return self.h3_cell.resolution if self.h3_cell else 0
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        """Get latitude, longitude coordinates."""
        if self.h3_cell:
            return (self.h3_cell.latitude, self.h3_cell.longitude)
        return (0.0, 0.0)
    
    @property
    def area_km2(self) -> float:
        """Get area of the cell in square kilometers."""
        if self.h3_cell and hasattr(self.h3_cell, 'area_km2'):
            return self.h3_cell.area_km2
        return 1.0  # Default area for mock cells
    
    @property
    def latitude(self) -> float:
        """Get latitude of the cell."""
        if self.h3_cell and hasattr(self.h3_cell, 'latitude'):
            return self.h3_cell.latitude
        return 0.0
    
    @property
    def longitude(self) -> float:
        """Get longitude of the cell."""
        if self.h3_cell and hasattr(self.h3_cell, 'longitude'):
            return self.h3_cell.longitude
        return 0.0
    
    def _update_neighbors(self):
        """Update neighbor cell relationships."""
        if not H3_AVAILABLE or not self.h3_cell:
            return
        
        try:
            neighbors = neighbor_cells(self.h3_cell.index)
            self.neighbor_cells = set(neighbors)
        except Exception as e:
            logger.warning(f"Failed to update neighbors for {self.index}: {e}")
    
    def add_parent(self, parent_index: str):
        """Add a parent cell relationship."""
        self.parent_cells.add(parent_index)
        self.updated_at = datetime.now()
    
    def add_child(self, child_index: str):
        """Add a child cell relationship."""
        self.child_cells.add(child_index)
        self.updated_at = datetime.now()
    
    def set_boundary(self, boundary_id: str, strength: float = 1.0):
        """Mark cell as boundary with specified strength."""
        self.is_boundary = True
        self.boundary_ids.add(boundary_id)
        self.boundary_strength = max(self.boundary_strength, strength)
        self.cell_type = NestedCellType.BOUNDARY
        self.updated_at = datetime.now()
    
    def add_message(self, message: Any):
        """Add message to the cell's queue."""
        self.message_queue.append(message)
        self.updated_at = datetime.now()
    
    def process_messages(self) -> List[Any]:
        """Process and return all queued messages."""
        messages = self.message_queue.copy()
        self.message_history.extend(messages)
        self.message_queue.clear()
        self.updated_at = datetime.now()
        return messages
    
    def update_state(self, variable: str, value: Any):
        """Update a state variable."""
        self.state_variables[variable] = value
        self.updated_at = datetime.now()
    
    def update_flow(self, variable: str, value: float):
        """Update a flow variable."""
        self.flow_variables[variable] = value
        self.updated_at = datetime.now()
    
    def get_connectivity_degree(self) -> int:
        """Get the connectivity degree (number of connections)."""
        return len(self.neighbor_cells) + len(self.parent_cells) + len(self.child_cells)
    
    def is_connected_to(self, other_index: str) -> bool:
        """Check if connected to another cell."""
        return (other_index in self.neighbor_cells or 
                other_index in self.parent_cells or 
                other_index in self.child_cells)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'index': self.index,
            'resolution': self.resolution,
            'coordinates': self.coordinates,
            'system_id': self.system_id,
            'parent_cells': list(self.parent_cells),
            'child_cells': list(self.child_cells),
            'neighbor_cells': list(self.neighbor_cells),
            'cell_type': self.cell_type.value,
            'hierarchy_level': self.hierarchy_level,
            'is_boundary': self.is_boundary,
            'boundary_ids': list(self.boundary_ids),
            'boundary_strength': self.boundary_strength,
            'state_variables': self.state_variables,
            'flow_variables': self.flow_variables,
            'connectivity_degree': self.get_connectivity_degree(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class NestedSystem:
    """
    A nested system representing a collection of connected H3 cells.
    
    Systems can contain subsystems and be part of larger systems,
    forming hierarchical nested structures.
    """
    
    def __init__(self, system_id: str, name: str = "", description: str = ""):
        """
        Initialize nested system.
        
        Args:
            system_id: Unique system identifier
            name: Human-readable system name
            description: System description
        """
        self.system_id = system_id
        self.name = name or system_id
        self.description = description
        
        # System composition
        self.cells: Dict[str, NestedCell] = {}
        self.subsystems: Dict[str, 'NestedSystem'] = {}
        self.parent_system: Optional['NestedSystem'] = None
        
        # System properties
        self.state = NestedSystemState.ACTIVE
        self.hierarchy_level = 0
        self.boundary_cells: Set[str] = set()
        
        # System metrics
        self.total_area: float = 0.0
        self.center_coordinates: Tuple[float, float] = (0.0, 0.0)
        self.bounding_box: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        
        # System dynamics
        self.system_variables: Dict[str, Any] = {}
        self.flow_balance: Dict[str, float] = {}
        
        # Metadata
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_cell(self, cell: NestedCell):
        """Add a cell to the system."""
        cell.system_id = self.system_id
        cell.hierarchy_level = self.hierarchy_level
        self.cells[cell.index] = cell
        self._update_system_metrics()
        self.updated_at = datetime.now()
    
    def remove_cell(self, cell_index: str) -> bool:
        """Remove a cell from the system."""
        if cell_index in self.cells:
            del self.cells[cell_index]
            self.boundary_cells.discard(cell_index)
            self._update_system_metrics()
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_subsystem(self, subsystem: 'NestedSystem'):
        """Add a subsystem."""
        subsystem.parent_system = self
        subsystem.hierarchy_level = self.hierarchy_level + 1
        self.subsystems[subsystem.system_id] = subsystem
        self.updated_at = datetime.now()
    
    def remove_subsystem(self, system_id: str) -> bool:
        """Remove a subsystem."""
        if system_id in self.subsystems:
            self.subsystems[system_id].parent_system = None
            del self.subsystems[system_id]
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_all_cells(self, include_subsystems: bool = True) -> Dict[str, NestedCell]:
        """Get all cells in the system and optionally subsystems."""
        all_cells = self.cells.copy()
        
        if include_subsystems:
            for subsystem in self.subsystems.values():
                all_cells.update(subsystem.get_all_cells(include_subsystems=True))
        
        return all_cells
    
    def get_boundary_cells(self) -> Dict[str, NestedCell]:
        """Get all boundary cells in the system."""
        return {idx: cell for idx, cell in self.cells.items() if cell.is_boundary}
    
    def detect_boundaries(self, external_cells: Set[str] = None):
        """Detect and mark boundary cells."""
        if not self.cells:
            return
        
        self.boundary_cells.clear()
        
        for cell_index, cell in self.cells.items():
            is_boundary = False
            
            # Check if cell has neighbors outside the system
            for neighbor_idx in cell.neighbor_cells:
                if neighbor_idx not in self.cells:
                    if external_cells is None or neighbor_idx in external_cells:
                        is_boundary = True
                        break
            
            if is_boundary:
                cell.set_boundary(f"{self.system_id}_boundary")
                self.boundary_cells.add(cell_index)
        
        self.updated_at = datetime.now()
    
    def calculate_connectivity(self) -> Dict[str, Any]:
        """Calculate system connectivity metrics."""
        if not self.cells:
            return {'error': 'No cells in system'}
        
        # Internal connections
        internal_connections = 0
        external_connections = 0
        
        for cell in self.cells.values():
            for neighbor_idx in cell.neighbor_cells:
                if neighbor_idx in self.cells:
                    internal_connections += 1
                else:
                    external_connections += 1
        
        # Avoid double counting internal connections
        internal_connections //= 2
        
        total_possible = len(self.cells) * 6  # Max 6 neighbors per hexagon
        connectivity_ratio = internal_connections / max(1, total_possible)
        
        return {
            'internal_connections': internal_connections,
            'external_connections': external_connections,
            'total_connections': internal_connections + external_connections,
            'connectivity_ratio': connectivity_ratio,
            'boundary_ratio': len(self.boundary_cells) / len(self.cells),
            'system_compactness': internal_connections / max(1, external_connections)
        }
    
    def _update_system_metrics(self):
        """Update system-level metrics."""
        if not self.cells:
            return
        
        # Calculate total area
        self.total_area = sum(cell.area_km2 for cell in self.cells.values())
        
        # Calculate center coordinates
        if self.cells:
            lats = [cell.coordinates[0] for cell in self.cells.values()]
            lngs = [cell.coordinates[1] for cell in self.cells.values()]
            self.center_coordinates = (
                sum(lats) / len(lats),
                sum(lngs) / len(lngs)
            )
            
            # Calculate bounding box
            self.bounding_box = (
                min(lngs), min(lats),  # min_lng, min_lat
                max(lngs), max(lats)   # max_lng, max_lat
            )
    
    def merge_with(self, other_system: 'NestedSystem') -> 'NestedSystem':
        """Merge with another system."""
        merged_system = NestedSystem(
            system_id=f"{self.system_id}_merged_{other_system.system_id}",
            name=f"{self.name} + {other_system.name}",
            description=f"Merged system: {self.description} | {other_system.description}"
        )
        
        # Add all cells from both systems
        for cell in self.cells.values():
            merged_system.add_cell(cell)
        
        for cell in other_system.cells.values():
            merged_system.add_cell(cell)
        
        # Add subsystems
        for subsystem in self.subsystems.values():
            merged_system.add_subsystem(subsystem)
        
        for subsystem in other_system.subsystems.values():
            merged_system.add_subsystem(subsystem)
        
        # Update state
        merged_system.state = NestedSystemState.MERGING
        
        return merged_system
    
    def split_by_criteria(self, criteria_func) -> List['NestedSystem']:
        """Split system based on criteria function."""
        if not self.cells:
            return [self]
        
        # Group cells by criteria
        groups = defaultdict(list)
        for cell in self.cells.values():
            group_key = criteria_func(cell)
            groups[group_key].append(cell)
        
        # Create new systems for each group
        split_systems = []
        for i, (group_key, group_cells) in enumerate(groups.items()):
            new_system = NestedSystem(
                system_id=f"{self.system_id}_split_{i}",
                name=f"{self.name}_split_{i}",
                description=f"Split from {self.system_id} by criteria: {group_key}"
            )
            
            for cell in group_cells:
                new_system.add_cell(cell)
            
            new_system.state = NestedSystemState.SPLITTING
            split_systems.append(new_system)
        
        return split_systems
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary."""
        connectivity = self.calculate_connectivity()
        
        return {
            'system_id': self.system_id,
            'name': self.name,
            'description': self.description,
            'state': self.state.value,
            'hierarchy_level': self.hierarchy_level,
            'num_cells': len(self.cells),
            'num_subsystems': len(self.subsystems),
            'num_boundary_cells': len(self.boundary_cells),
            'total_area_km2': self.total_area,
            'center_coordinates': self.center_coordinates,
            'bounding_box': self.bounding_box,
            'connectivity_metrics': connectivity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class NestedH3Grid:
    """
    Advanced H3 grid with nested system capabilities.
    
    Manages multiple nested systems, hierarchical relationships,
    and provides comprehensive analysis and manipulation tools.
    """
    
    def __init__(self, name: str = "NestedH3Grid"):
        """
        Initialize nested H3 grid.
        
        Args:
            name: Grid name for identification
        """
        self.name = name
        
        # Grid components
        self.cells: Dict[str, NestedCell] = {}
        self.systems: Dict[str, NestedSystem] = {}
        
        # Hierarchical structure
        self.hierarchy_levels: Dict[int, Set[str]] = defaultdict(set)
        self.root_systems: Set[str] = set()
        
        # Grid properties
        self.resolutions: Set[int] = set()
        self.total_area: float = 0.0
        self.bounding_box: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        
        # Metadata
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_cell(self, h3_cell: H3Cell, system_id: Optional[str] = None) -> NestedCell:
        """Add an H3 cell to the grid."""
        nested_cell = NestedCell(h3_cell=h3_cell, system_id=system_id)
        self.cells[nested_cell.index] = nested_cell
        self.resolutions.add(nested_cell.resolution)
        self._update_grid_metrics()
        self.updated_at = datetime.now()
        return nested_cell
    
    def create_system(self, system_id: str, cell_indices: List[str], 
                     name: str = "", description: str = "") -> NestedSystem:
        """Create a new nested system from cells."""
        system = NestedSystem(system_id, name, description)
        
        for cell_index in cell_indices:
            if cell_index in self.cells:
                system.add_cell(self.cells[cell_index])
        
        self.systems[system_id] = system
        self.hierarchy_levels[system.hierarchy_level].add(system_id)
        
        if system.parent_system is None:
            self.root_systems.add(system_id)
        
        system.detect_boundaries()
        self.updated_at = datetime.now()
        
        return system
    
    def create_hierarchical_system(self, base_resolution: int, 
                                  target_resolutions: List[int],
                                  bounds: Tuple[float, float, float, float]) -> Dict[int, NestedSystem]:
        """Create hierarchical nested systems across multiple resolutions."""
        if not H3_AVAILABLE:
            logger.error("H3 not available for hierarchical system creation")
            return {}
        
        hierarchical_systems = {}
        
        try:
            # Create base system at target resolution
            min_lat, min_lng, max_lat, max_lng = bounds
            
            for resolution in sorted(target_resolutions):
                system_id = f"hierarchical_res_{resolution}"
                
                # Generate H3 cells for this resolution within bounds
                # This is a simplified approach - in practice, you'd use more sophisticated methods
                center_lat = (min_lat + max_lat) / 2
                center_lng = (min_lng + max_lng) / 2
                
                if H3_CORE_AVAILABLE:
                    from ...h3.core import H3Cell
                    center_cell = H3Cell.from_coordinates(center_lat, center_lng, resolution)
                    
                    # Get surrounding cells
                    surrounding_indices = grid_disk(center_cell.index, 5)  # 5-ring neighborhood
                    
                    # Create cells and system
                    cell_indices = []
                    for h3_index in surrounding_indices:
                        h3_cell = H3Cell(index=h3_index, resolution=resolution)
                        nested_cell = self.add_cell(h3_cell, system_id)
                        cell_indices.append(h3_index)
                    
                    # Create the system
                    system = self.create_system(
                        system_id, 
                        cell_indices,
                        name=f"Hierarchical System Resolution {resolution}",
                        description=f"System at H3 resolution {resolution}"
                    )
                    
                    hierarchical_systems[resolution] = system
        
        except Exception as e:
            logger.error(f"Failed to create hierarchical system: {e}")
        
        return hierarchical_systems
    
    def detect_all_boundaries(self):
        """Detect boundaries for all systems in the grid."""
        for system in self.systems.values():
            system.detect_boundaries()
        self.updated_at = datetime.now()
    
    def get_system_by_id(self, system_id: str) -> Optional[NestedSystem]:
        """Get system by ID."""
        return self.systems.get(system_id)
    
    def get_systems_at_level(self, level: int) -> List[NestedSystem]:
        """Get all systems at a specific hierarchy level."""
        system_ids = self.hierarchy_levels.get(level, set())
        return [self.systems[sid] for sid in system_ids if sid in self.systems]
    
    def get_root_systems(self) -> List[NestedSystem]:
        """Get all root-level systems."""
        return [self.systems[sid] for sid in self.root_systems if sid in self.systems]
    
    def merge_systems(self, system_id1: str, system_id2: str) -> Optional[NestedSystem]:
        """Merge two systems."""
        system1 = self.systems.get(system_id1)
        system2 = self.systems.get(system_id2)
        
        if not system1 or not system2:
            return None
        
        merged_system = system1.merge_with(system2)
        self.systems[merged_system.system_id] = merged_system
        
        # Remove original systems
        del self.systems[system_id1]
        del self.systems[system_id2]
        
        self.updated_at = datetime.now()
        return merged_system
    
    def split_system(self, system_id: str, criteria_func) -> List[NestedSystem]:
        """Split a system based on criteria."""
        system = self.systems.get(system_id)
        if not system:
            return []
        
        split_systems = system.split_by_criteria(criteria_func)
        
        # Remove original system and add split systems
        del self.systems[system_id]
        for split_system in split_systems:
            self.systems[split_system.system_id] = split_system
        
        self.updated_at = datetime.now()
        return split_systems
    
    def _update_grid_metrics(self):
        """Update grid-level metrics."""
        if not self.cells:
            return
        
        # Calculate total area
        self.total_area = sum(cell.area_km2 for cell in self.cells.values())
        
        # Calculate bounding box
        if self.cells:
            lats = [cell.coordinates[0] for cell in self.cells.values()]
            lngs = [cell.coordinates[1] for cell in self.cells.values()]
            self.bounding_box = (
                min(lngs), min(lats),  # min_lng, min_lat
                max(lngs), max(lats)   # max_lng, max_lat
            )
    
    def get_grid_summary(self) -> Dict[str, Any]:
        """Get comprehensive grid summary."""
        return {
            'name': self.name,
            'num_cells': len(self.cells),
            'num_systems': len(self.systems),
            'num_hierarchy_levels': len(self.hierarchy_levels),
            'resolutions': sorted(list(self.resolutions)),
            'total_area_km2': self.total_area,
            'bounding_box': self.bounding_box,
            'root_systems': list(self.root_systems),
            'hierarchy_distribution': {
                level: len(systems) for level, systems in self.hierarchy_levels.items()
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def export_to_geojson(self) -> Dict[str, Any]:
        """Export grid to GeoJSON format."""
        features = []
        
        for cell in self.cells.values():
            if cell.h3_cell:
                feature = cell.h3_cell.to_geojson()
                
                # Add nested system properties
                feature['properties'].update({
                    'system_id': cell.system_id,
                    'cell_type': cell.cell_type.value,
                    'hierarchy_level': cell.hierarchy_level,
                    'is_boundary': cell.is_boundary,
                    'boundary_strength': cell.boundary_strength,
                    'connectivity_degree': cell.get_connectivity_degree()
                })
                
                features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features,
            'properties': {
                'grid_name': self.name,
                'grid_summary': self.get_grid_summary()
            }
        }
