"""
Lumping Operations for H3 Nested Systems.

This module provides algorithms for lumping (combining) H3 cells into larger
units based on various criteria such as similarity, proximity, and constraints.
"""

import logging
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False
    logger.warning("h3-py package not available")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.warning("NumPy not available. Some lumping features will be limited.")

try:
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Advanced clustering will be limited.")


class LumpingStrategy(Enum):
    """Strategies for lumping H3 cells."""
    SIMILARITY_BASED = "similarity_based"
    PROXIMITY_BASED = "proximity_based"
    HIERARCHICAL = "hierarchical"
    CONSTRAINT_BASED = "constraint_based"
    DENSITY_BASED = "density_based"
    ATTRIBUTE_BASED = "attribute_based"
    CUSTOM = "custom"


class SimilarityMetric(Enum):
    """Metrics for measuring cell similarity."""
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    COSINE = "cosine"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    CUSTOM = "custom"


@dataclass
class LumpingCriterion:
    """
    Defines criteria for lumping cells.
    """
    
    criterion_id: str
    criterion_type: str  # e.g., "similarity", "proximity", "attribute"
    
    # Criterion parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Thresholds
    threshold: float = 0.5
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    
    # Weights
    weight: float = 1.0
    
    # Validation function
    validation_function: Optional[Callable] = None
    
    def evaluate(self, cell1, cell2) -> float:
        """
        Evaluate criterion for two cells.
        
        Args:
            cell1: First cell
            cell2: Second cell
            
        Returns:
            Criterion score (0.0 to 1.0)
        """
        if self.validation_function:
            try:
                return self.validation_function(cell1, cell2, self.parameters)
            except Exception as e:
                logger.warning(f"Criterion evaluation failed: {e}")
                return 0.0
        
        return 0.5  # Default neutral score


@dataclass
class LumpingResult:
    """
    Result of a lumping operation.
    """
    
    operation_id: str
    strategy: LumpingStrategy
    
    # Input cells
    input_cells: List[str] = field(default_factory=list)
    
    # Output lumps
    lumps: Dict[str, List[str]] = field(default_factory=dict)  # lump_id -> cell_indices
    
    # Lump properties
    lump_properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Quality metrics
    quality_score: float = 0.0
    compactness_score: float = 0.0
    similarity_score: float = 0.0
    
    # Statistics
    num_input_cells: int = 0
    num_output_lumps: int = 0
    reduction_ratio: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0
    
    def __post_init__(self):
        """Calculate derived statistics."""
        self.num_input_cells = len(self.input_cells)
        self.num_output_lumps = len(self.lumps)
        
        if self.num_input_cells > 0:
            self.reduction_ratio = 1.0 - (self.num_output_lumps / self.num_input_cells)


class H3LumpingEngine:
    """
    Advanced lumping engine for H3 nested systems.
    
    Provides multiple algorithms for combining H3 cells into larger units
    based on similarity, proximity, constraints, and other criteria.
    """
    
    def __init__(self, name: str = "H3LumpingEngine"):
        """
        Initialize lumping engine.
        
        Args:
            name: Engine name for identification
        """
        self.name = name
        
        # Lumping criteria
        self.criteria: Dict[str, LumpingCriterion] = {}
        
        # Results storage
        self.lumping_results: Dict[str, LumpingResult] = {}
        
        # Statistics
        self.operation_stats: Dict[str, int] = defaultdict(int)
        
        # Metadata
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_criterion(self, criterion: LumpingCriterion) -> str:
        """
        Add a lumping criterion.
        
        Args:
            criterion: Lumping criterion to add
            
        Returns:
            Criterion ID
        """
        self.criteria[criterion.criterion_id] = criterion
        self.updated_at = datetime.now()
        return criterion.criterion_id
    
    def remove_criterion(self, criterion_id: str) -> bool:
        """
        Remove a lumping criterion.
        
        Args:
            criterion_id: ID of criterion to remove
            
        Returns:
            True if criterion was removed
        """
        if criterion_id in self.criteria:
            del self.criteria[criterion_id]
            self.updated_at = datetime.now()
            return True
        return False
    
    def lump_cells(self, nested_grid, strategy: LumpingStrategy = LumpingStrategy.SIMILARITY_BASED,
                   system_id: Optional[str] = None, **kwargs) -> LumpingResult:
        """
        Lump cells in a nested grid system.
        
        Args:
            nested_grid: NestedH3Grid instance
            strategy: Lumping strategy to use
            system_id: Specific system to lump (None for all)
            **kwargs: Strategy-specific parameters
            
        Returns:
            LumpingResult instance
        """
        start_time = datetime.now()
        operation_id = f"lump_{uuid.uuid4().hex[:8]}"
        
        # Get cells to lump
        if system_id:
            system = nested_grid.get_system_by_id(system_id)
            if not system:
                raise ValueError(f"System {system_id} not found")
            cells = list(system.cells.values())
        else:
            cells = []
            for system in nested_grid.systems.values():
                cells.extend(system.cells.values())
        
        if not cells:
            return LumpingResult(
                operation_id=operation_id,
                strategy=strategy,
                processing_time=0.0
            )
        
        # Apply lumping strategy
        if strategy == LumpingStrategy.SIMILARITY_BASED:
            lumps = self._lump_by_similarity(cells, **kwargs)
        elif strategy == LumpingStrategy.PROXIMITY_BASED:
            lumps = self._lump_by_proximity(cells, **kwargs)
        elif strategy == LumpingStrategy.HIERARCHICAL:
            lumps = self._lump_hierarchical(cells, **kwargs)
        elif strategy == LumpingStrategy.CONSTRAINT_BASED:
            lumps = self._lump_by_constraints(cells, **kwargs)
        elif strategy == LumpingStrategy.DENSITY_BASED:
            lumps = self._lump_by_density(cells, **kwargs)
        elif strategy == LumpingStrategy.ATTRIBUTE_BASED:
            lumps = self._lump_by_attributes(cells, **kwargs)
        else:
            logger.warning(f"Unknown lumping strategy: {strategy}")
            lumps = self._lump_by_similarity(cells, **kwargs)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Create result
        result = LumpingResult(
            operation_id=operation_id,
            strategy=strategy,
            input_cells=[cell.index for cell in cells],
            lumps=lumps,
            processing_time=processing_time
        )
        
        # Calculate quality metrics
        result.quality_score = self._calculate_quality_score(cells, lumps)
        result.compactness_score = self._calculate_compactness_score(lumps)
        result.similarity_score = self._calculate_similarity_score(cells, lumps)
        
        # Store result
        self.lumping_results[operation_id] = result
        self.operation_stats[strategy.value] += 1
        self.updated_at = datetime.now()
        
        return result
    
    def _lump_by_similarity(self, cells: List, **kwargs) -> Dict[str, List[str]]:
        """Lump cells based on similarity."""
        similarity_threshold = kwargs.get('similarity_threshold', 0.7)
        metric = kwargs.get('metric', SimilarityMetric.EUCLIDEAN)
        attribute_fields = kwargs.get('attribute_fields', ['value'])
        
        if not NUMPY_AVAILABLE:
            logger.warning("NumPy required for similarity-based lumping")
            return self._simple_proximity_lumping(cells)
        
        # Extract features for similarity calculation
        features = []
        cell_indices = []
        
        for cell in cells:
            feature_vector = []
            for field in attribute_fields:
                if field in cell.state_variables:
                    feature_vector.append(cell.state_variables[field])
                else:
                    feature_vector.append(0.0)
            
            if feature_vector:
                features.append(feature_vector)
                cell_indices.append(cell.index)
        
        if not features:
            return {}
        
        features = np.array(features)
        
        # Calculate similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(features, metric)
        
        # Find similar cells and group them
        lumps = {}
        visited = set()
        lump_counter = 0
        
        for i, cell_idx in enumerate(cell_indices):
            if cell_idx in visited:
                continue
            
            # Find similar cells
            similar_cells = [cell_idx]
            visited.add(cell_idx)
            
            for j, other_cell_idx in enumerate(cell_indices):
                if (i != j and other_cell_idx not in visited and 
                    similarity_matrix[i, j] >= similarity_threshold):
                    similar_cells.append(other_cell_idx)
                    visited.add(other_cell_idx)
            
            if similar_cells:
                lump_id = f"lump_similarity_{lump_counter}"
                lumps[lump_id] = similar_cells
                lump_counter += 1
        
        return lumps
    
    def _lump_by_proximity(self, cells: List, **kwargs) -> Dict[str, List[str]]:
        """Lump cells based on spatial proximity."""
        distance_threshold = kwargs.get('distance_threshold', 2)  # H3 distance
        
        if not H3_AVAILABLE:
            logger.warning("h3-py required for proximity-based lumping")
            return self._simple_proximity_lumping(cells)
        
        lumps = {}
        visited = set()
        lump_counter = 0
        
        for cell in cells:
            if cell.index in visited:
                continue
            
            # Find nearby cells using H3 grid_disk
            try:
                nearby_indices = h3.grid_disk(cell.index, distance_threshold)
                
                # Filter to cells in our input set
                nearby_cells = []
                for other_cell in cells:
                    if (other_cell.index in nearby_indices and 
                        other_cell.index not in visited):
                        nearby_cells.append(other_cell.index)
                        visited.add(other_cell.index)
                
                if nearby_cells:
                    lump_id = f"lump_proximity_{lump_counter}"
                    lumps[lump_id] = nearby_cells
                    lump_counter += 1
            
            except Exception as e:
                logger.warning(f"Failed to calculate proximity for cell {cell.index}: {e}")
                continue
        
        return lumps
    
    def _lump_hierarchical(self, cells: List, **kwargs) -> Dict[str, List[str]]:
        """Lump cells using hierarchical clustering."""
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("scikit-learn and NumPy required for hierarchical lumping")
            return self._simple_proximity_lumping(cells)
        
        n_clusters = kwargs.get('n_clusters', None)
        linkage = kwargs.get('linkage', 'ward')
        attribute_fields = kwargs.get('attribute_fields', ['value'])
        
        # Extract features
        features = []
        cell_indices = []
        
        for cell in cells:
            feature_vector = []
            for field in attribute_fields:
                if field in cell.state_variables:
                    feature_vector.append(cell.state_variables[field])
                else:
                    feature_vector.append(0.0)
            
            if feature_vector:
                features.append(feature_vector)
                cell_indices.append(cell.index)
        
        if len(features) < 2:
            return {}
        
        features = np.array(features)
        
        # Determine number of clusters if not specified
        if n_clusters is None:
            n_clusters = max(2, len(cells) // 5)  # Heuristic: ~5 cells per cluster
        
        # Perform hierarchical clustering
        try:
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage=linkage
            )
            cluster_labels = clustering.fit_predict(features)
            
            # Group cells by cluster
            lumps = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                lump_id = f"lump_hierarchical_{label}"
                lumps[lump_id].append(cell_indices[i])
            
            return dict(lumps)
        
        except Exception as e:
            logger.warning(f"Hierarchical clustering failed: {e}")
            return self._simple_proximity_lumping(cells)
    
    def _lump_by_constraints(self, cells: List, **kwargs) -> Dict[str, List[str]]:
        """Lump cells based on constraints."""
        max_lump_size = kwargs.get('max_lump_size', 10)
        min_lump_size = kwargs.get('min_lump_size', 2)
        constraint_field = kwargs.get('constraint_field', 'constraint_value')
        
        # Group cells by constraint values
        constraint_groups = defaultdict(list)
        
        for cell in cells:
            if constraint_field in cell.state_variables:
                constraint_value = cell.state_variables[constraint_field]
                constraint_groups[constraint_value].append(cell.index)
            else:
                constraint_groups['unconstrained'].append(cell.index)
        
        # Create lumps respecting size constraints
        lumps = {}
        lump_counter = 0
        
        for constraint_value, cell_group in constraint_groups.items():
            if len(cell_group) < min_lump_size:
                continue
            
            # Split large groups into multiple lumps
            while cell_group:
                lump_size = min(max_lump_size, len(cell_group))
                lump_cells = cell_group[:lump_size]
                cell_group = cell_group[lump_size:]
                
                if len(lump_cells) >= min_lump_size:
                    lump_id = f"lump_constraint_{constraint_value}_{lump_counter}"
                    lumps[lump_id] = lump_cells
                    lump_counter += 1
        
        return lumps
    
    def _lump_by_density(self, cells: List, **kwargs) -> Dict[str, List[str]]:
        """Lump cells using density-based clustering."""
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            logger.warning("scikit-learn and NumPy required for density-based lumping")
            return self._simple_proximity_lumping(cells)
        
        eps = kwargs.get('eps', 0.5)
        min_samples = kwargs.get('min_samples', 3)
        attribute_fields = kwargs.get('attribute_fields', ['value'])
        
        # Extract features
        features = []
        cell_indices = []
        
        for cell in cells:
            feature_vector = []
            for field in attribute_fields:
                if field in cell.state_variables:
                    feature_vector.append(cell.state_variables[field])
                else:
                    feature_vector.append(0.0)
            
            if feature_vector:
                features.append(feature_vector)
                cell_indices.append(cell.index)
        
        if len(features) < min_samples:
            return {}
        
        features = np.array(features)
        
        # Perform DBSCAN clustering
        try:
            clustering = DBSCAN(eps=eps, min_samples=min_samples)
            cluster_labels = clustering.fit_predict(features)
            
            # Group cells by cluster (ignore noise points with label -1)
            lumps = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                if label >= 0:  # Not noise
                    lump_id = f"lump_density_{label}"
                    lumps[lump_id].append(cell_indices[i])
            
            return dict(lumps)
        
        except Exception as e:
            logger.warning(f"Density-based clustering failed: {e}")
            return self._simple_proximity_lumping(cells)
    
    def _lump_by_attributes(self, cells: List, **kwargs) -> Dict[str, List[str]]:
        """Lump cells based on attribute values."""
        grouping_field = kwargs.get('grouping_field', 'category')
        
        # Group cells by attribute value
        attribute_groups = defaultdict(list)
        
        for cell in cells:
            if grouping_field in cell.state_variables:
                attribute_value = cell.state_variables[grouping_field]
                attribute_groups[str(attribute_value)].append(cell.index)
            else:
                attribute_groups['no_attribute'].append(cell.index)
        
        # Convert to lumps
        lumps = {}
        for attribute_value, cell_group in attribute_groups.items():
            if cell_group:
                lump_id = f"lump_attribute_{attribute_value}"
                lumps[lump_id] = cell_group
        
        return lumps
    
    def _simple_proximity_lumping(self, cells: List) -> Dict[str, List[str]]:
        """Simple proximity-based lumping fallback."""
        lumps = {}
        
        # Just group each cell as its own lump
        for i, cell in enumerate(cells):
            lump_id = f"lump_simple_{i}"
            lumps[lump_id] = [cell.index]
        
        return lumps
    
    def _calculate_similarity_matrix(self, features: np.ndarray, 
                                   metric: SimilarityMetric) -> np.ndarray:
        """Calculate similarity matrix between features."""
        n = len(features)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                else:
                    if metric == SimilarityMetric.EUCLIDEAN:
                        distance = np.linalg.norm(features[i] - features[j])
                        similarity = 1.0 / (1.0 + distance)
                    elif metric == SimilarityMetric.MANHATTAN:
                        distance = np.sum(np.abs(features[i] - features[j]))
                        similarity = 1.0 / (1.0 + distance)
                    elif metric == SimilarityMetric.COSINE:
                        dot_product = np.dot(features[i], features[j])
                        norms = np.linalg.norm(features[i]) * np.linalg.norm(features[j])
                        similarity = dot_product / norms if norms > 0 else 0.0
                    else:
                        similarity = 0.5  # Default
                    
                    similarity_matrix[i, j] = similarity
        
        return similarity_matrix
    
    def _calculate_quality_score(self, cells: List, lumps: Dict[str, List[str]]) -> float:
        """Calculate overall quality score for lumping result."""
        if not lumps:
            return 0.0
        
        # Simple quality metric based on lump size distribution
        lump_sizes = [len(cell_list) for cell_list in lumps.values()]
        
        if not lump_sizes:
            return 0.0
        
        # Prefer moderate lump sizes (not too small, not too large)
        avg_size = sum(lump_sizes) / len(lump_sizes)
        size_variance = sum((size - avg_size) ** 2 for size in lump_sizes) / len(lump_sizes)
        
        # Quality decreases with high variance
        quality = 1.0 / (1.0 + size_variance / avg_size) if avg_size > 0 else 0.0
        
        return min(1.0, max(0.0, quality))
    
    def _calculate_compactness_score(self, lumps: Dict[str, List[str]]) -> float:
        """Calculate compactness score for lumps."""
        if not lumps or not H3_AVAILABLE:
            return 0.0
        
        compactness_scores = []
        
        for lump_id, cell_indices in lumps.items():
            if len(cell_indices) < 2:
                compactness_scores.append(1.0)
                continue
            
            try:
                # Calculate average distance between cells in lump
                total_distance = 0
                pair_count = 0
                
                for i, cell1 in enumerate(cell_indices):
                    for cell2 in cell_indices[i+1:]:
                        distance = h3.grid_distance(cell1, cell2)
                        total_distance += distance
                        pair_count += 1
                
                if pair_count > 0:
                    avg_distance = total_distance / pair_count
                    # Compactness is inverse of average distance
                    compactness = 1.0 / (1.0 + avg_distance)
                    compactness_scores.append(compactness)
            
            except Exception as e:
                logger.warning(f"Failed to calculate compactness for lump {lump_id}: {e}")
                compactness_scores.append(0.5)
        
        return sum(compactness_scores) / len(compactness_scores) if compactness_scores else 0.0
    
    def _calculate_similarity_score(self, cells: List, lumps: Dict[str, List[str]]) -> float:
        """Calculate similarity score within lumps."""
        # This would calculate how similar cells are within each lump
        # For now, return a placeholder
        return 0.5
    
    def get_lumping_statistics(self) -> Dict[str, Any]:
        """Get lumping engine statistics."""
        total_operations = sum(self.operation_stats.values())
        
        return {
            'engine_name': self.name,
            'total_operations': total_operations,
            'operation_stats': dict(self.operation_stats),
            'active_criteria': len(self.criteria),
            'stored_results': len(self.lumping_results),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

