"""Spatial integration for governance boundaries and jurisdiction mapping."""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Optional spatial integration
try:
    from geo_infer_space.core.spatial_indexing import SpatialIndexingInterface
    from geo_infer_space.core.analytics import SpatialAnalyticsInterface
    SPACE_AVAILABLE = True
except ImportError:
    SPACE_AVAILABLE = False
    logger.warning("GEO-INFER-SPACE not available, spatial features disabled")


class SpatialGovernanceIntegration:
    """
    Integrate spatial indexing and analysis for governance boundaries.
    
    Provides:
    - Spatial indexing for governance boundaries
    - Jurisdiction mapping and overlap detection
    - Spatial conflict detection
    - Multi-scale governance support (H3 indexing)
    
    References:
    - H3: A Hierarchical Hexagonal Spatial Index
    - Spatial governance boundaries in multi-level systems
    """
    
    def __init__(self, backend: Optional[str] = None):
        """
        Initialize spatial governance integration.
        
        Parameters:
        -----------
        backend : Optional[str]
            Spatial backend to use ('h3', 'srai', or None for default)
        """
        self.backend = backend
        if SPACE_AVAILABLE:
            self.spatial_indexer = SpatialIndexingInterface(backend=backend)
            self.spatial_analytics = SpatialAnalyticsInterface(backend=backend)
        else:
            self.spatial_indexer = None
            self.spatial_analytics = None
            logger.warning("Spatial integration disabled - GEO-INFER-SPACE not available")
    
    def index_governance_boundary(
        self,
        boundary: Dict[str, Any],
        resolution: int = 9
    ) -> Dict[str, Any]:
        """
        Index governance boundary using spatial indexing.
        
        Parameters:
        -----------
        boundary : Dict[str, Any]
            Boundary definition (polygon, coordinates, or bounds)
        resolution : int
            Spatial resolution level (0-15 for H3)
            
        Returns:
        --------
        Dict[str, Any]
            Indexed boundary with spatial cells
        """
        if not SPACE_AVAILABLE or not self.spatial_indexer:
            return {
                'indexed': False,
                'reason': 'Spatial indexing not available'
            }
        
        try:
            indexed_boundary = {
                'original_boundary': boundary,
                'resolution': resolution,
                'cells': [],
                'cell_count': 0
            }
            
            # Handle different boundary formats
            if 'polygon' in boundary:
                cells = self.spatial_indexer.polygon_to_cells(boundary['polygon'], resolution)
                indexed_boundary['cells'] = cells
                indexed_boundary['cell_count'] = len(cells)
            elif 'coordinates' in boundary:
                coords = boundary['coordinates']
                if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    cell = self.spatial_indexer.latlng_to_cell(coords[0], coords[1], resolution)
                    indexed_boundary['cells'] = [cell]
                    indexed_boundary['cell_count'] = 1
            elif 'bounds' in boundary:
                # Convert bounds to polygon and index
                bounds = boundary['bounds']
                # Simplified: would need proper bounds-to-polygon conversion
                indexed_boundary['cells'] = []
                indexed_boundary['cell_count'] = 0
            
            indexed_boundary['indexed'] = True
            return indexed_boundary
            
        except Exception as e:
            logger.error(f"Error indexing boundary: {e}")
            return {
                'indexed': False,
                'error': str(e)
            }
    
    def detect_jurisdictional_overlaps(
        self,
        boundaries: List[Dict[str, Any]],
        resolution: int = 9
    ) -> Dict[str, Any]:
        """
        Detect overlapping jurisdictions using spatial analysis.
        
        Parameters:
        -----------
        boundaries : List[Dict[str, Any]]
            List of jurisdiction boundaries
        resolution : int
            Spatial resolution for overlap detection
            
        Returns:
        --------
        Dict[str, Any]
            Overlap analysis results
        """
        if not SPACE_AVAILABLE or not self.spatial_indexer:
            return {
                'overlaps_detected': False,
                'reason': 'Spatial analysis not available'
            }
        
        try:
            # Index all boundaries
            indexed_boundaries = []
            for i, boundary in enumerate(boundaries):
                indexed = self.index_governance_boundary(boundary, resolution)
                if indexed.get('indexed'):
                    indexed_boundaries.append({
                        'boundary_id': boundary.get('id', f'boundary_{i}'),
                        'cells': set(indexed.get('cells', []))
                    })
            
            # Find overlaps
            overlaps = []
            for i, b1 in enumerate(indexed_boundaries):
                for b2 in indexed_boundaries[i+1:]:
                    overlap_cells = b1['cells'] & b2['cells']
                    if overlap_cells:
                        overlap_ratio_1 = len(overlap_cells) / len(b1['cells']) if b1['cells'] else 0
                        overlap_ratio_2 = len(overlap_cells) / len(b2['cells']) if b2['cells'] else 0
                        
                        overlaps.append({
                            'boundary_1': b1['boundary_id'],
                            'boundary_2': b2['boundary_id'],
                            'overlap_cells': list(overlap_cells),
                            'overlap_cell_count': len(overlap_cells),
                            'overlap_ratio_1': overlap_ratio_1,
                            'overlap_ratio_2': overlap_ratio_2,
                            'severity': 'high' if max(overlap_ratio_1, overlap_ratio_2) > 0.5 else 'medium' if max(overlap_ratio_1, overlap_ratio_2) > 0.2 else 'low'
                        })
            
            return {
                'overlaps_detected': len(overlaps) > 0,
                'overlap_count': len(overlaps),
                'overlaps': overlaps,
                'resolution_used': resolution
            }
            
        except Exception as e:
            logger.error(f"Error detecting overlaps: {e}")
            return {
                'overlaps_detected': False,
                'error': str(e)
            }
    
    def map_governance_entities_to_spatial_cells(
        self,
        entities: List[Dict[str, Any]],
        resolution: int = 9
    ) -> Dict[str, Any]:
        """
        Map governance entities to spatial cells for multi-scale governance.
        
        Parameters:
        -----------
        entities : List[Dict[str, Any]]
            Governance entities with spatial information
        resolution : int
            Spatial resolution level
            
        Returns:
        --------
        Dict[str, Any]
            Mapping of entities to spatial cells
        """
        if not SPACE_AVAILABLE or not self.spatial_indexer:
            return {
                'mapped': False,
                'reason': 'Spatial indexing not available'
            }
        
        entity_cell_mapping = {}
        
        for entity in entities:
            entity_id = entity.get('id', 'unknown')
            jurisdiction = entity.get('jurisdiction', {})
            
            # Index entity jurisdiction
            indexed = self.index_governance_boundary(jurisdiction, resolution)
            if indexed.get('indexed'):
                entity_cell_mapping[entity_id] = {
                    'cells': indexed.get('cells', []),
                    'cell_count': indexed.get('cell_count', 0),
                    'resolution': resolution
                }
        
        return {
            'mapped': True,
            'entity_cell_mapping': entity_cell_mapping,
            'total_entities': len(entities),
            'mapped_entities': len(entity_cell_mapping),
            'resolution': resolution
        }
    
    def analyze_spatial_governance_coverage(
        self,
        governance_structure: Dict[str, Any],
        spatial_region: Dict[str, Any],
        resolution: int = 9
    ) -> Dict[str, Any]:
        """
        Analyze spatial coverage of governance structure.
        
        Parameters:
        -----------
        governance_structure : Dict[str, Any]
            Governance structure with entities
        spatial_region : Dict[str, Any]
            Region to analyze coverage for
        resolution : int
            Spatial resolution level
            
        Returns:
        --------
        Dict[str, Any]
            Coverage analysis results
        """
        if not SPACE_AVAILABLE:
            return {
                'coverage_analyzed': False,
                'reason': 'Spatial analysis not available'
            }
        
        try:
            # Index the region
            region_indexed = self.index_governance_boundary(spatial_region, resolution)
            if not region_indexed.get('indexed'):
                return {
                    'coverage_analyzed': False,
                    'reason': 'Could not index region'
                }
            
            region_cells = set(region_indexed.get('cells', []))
            
            # Get entities from governance structure
            entities = governance_structure.get('entities', [])
            
            # Calculate coverage
            covered_cells = set()
            entity_coverage = {}
            
            for entity in entities:
                entity_id = entity.get('entity_id', 'unknown')
                jurisdiction = entity.get('jurisdiction', {})
                
                entity_indexed = self.index_governance_boundary(jurisdiction, resolution)
                if entity_indexed.get('indexed'):
                    entity_cells = set(entity_indexed.get('cells', []))
                    covered_cells.update(entity_cells & region_cells)
                    
                    entity_coverage[entity_id] = {
                        'cells_in_region': len(entity_cells & region_cells),
                        'coverage_ratio': len(entity_cells & region_cells) / len(region_cells) if region_cells else 0
                    }
            
            total_coverage = len(covered_cells) / len(region_cells) if region_cells else 0.0
            
            return {
                'coverage_analyzed': True,
                'total_coverage': total_coverage,
                'covered_cells': len(covered_cells),
                'total_region_cells': len(region_cells),
                'entity_coverage': entity_coverage,
                'coverage_gaps': len(region_cells - covered_cells) if region_cells else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing coverage: {e}")
            return {
                'coverage_analyzed': False,
                'error': str(e)
            }



