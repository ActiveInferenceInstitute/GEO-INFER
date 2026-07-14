"""Organizational integration for governance-organization alignment."""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Optional organizational integration
try:
    from geo_infer_org.core import OrganizationModel
    ORG_AVAILABLE = True
except ImportError:
    ORG_AVAILABLE = False
    logger.warning("GEO-INFER-ORG not available, organizational features disabled")


class OrganizationalGovernanceIntegration:
    """
    Integrate organizational structures with governance systems.
    
    Provides:
    - Governance entity to organizational role mapping
    - Organizational capacity assessment
    - Governance-organization alignment checking
    - Organizational learning integration
    
    References:
    - Organizational design for governance
    - Capacity building for governance institutions
    """
    
    def __init__(self):
        """Initialize organizational governance integration."""
        if ORG_AVAILABLE:
            self.org_available = True
        else:
            self.org_available = False
            logger.warning("Organizational integration disabled - GEO-INFER-ORG not available")
    
    def map_governance_to_organizational_structure(
        self,
        governance_entities: List[Dict[str, Any]],
        organizational_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map governance entities to organizational roles and structure.
        
        Parameters:
        -----------
        governance_entities : List[Dict[str, Any]]
            Governance entities to map
        organizational_structure : Dict[str, Any]
            Organizational structure definition
            
        Returns:
        --------
        Dict[str, Any]
            Mapping between governance and organizational structures
        """
        mapping = {
            'mapped': True,
            'entity_role_mapping': {},
            'coverage': 0.0,
            'alignment_score': 0.0
        }
        
        if not self.org_available:
            mapping['mapped'] = False
            mapping['reason'] = 'Organizational module not available'
            return mapping
        
        # Extract organizational roles
        org_roles = organizational_structure.get('roles', [])
        org_units = organizational_structure.get('units', [])
        
        # Map entities to roles
        entity_role_mapping = {}
        for entity in governance_entities:
            entity_id = entity.get('entity_id', 'unknown')
            entity_level = entity.get('governance_level', 'unknown')
            entity_responsibilities = entity.get('responsibilities', [])
            
            # Find matching organizational role
            matched_role = None
            for role in org_roles:
                role_level = role.get('level', '')
                role_responsibilities = role.get('responsibilities', [])
                
                # Check for match
                if entity_level.lower() in role_level.lower():
                    # Check responsibility overlap
                    overlap = len(set(entity_responsibilities) & set(role_responsibilities))
                    if overlap > 0 or not role_responsibilities:
                        matched_role = role
                        break
            
            entity_role_mapping[entity_id] = {
                'entity': entity,
                'matched_role': matched_role,
                'match_quality': 0.8 if matched_role else 0.3
            }
        
        mapping['entity_role_mapping'] = entity_role_mapping
        
        # Calculate coverage
        mapped_count = sum(1 for m in entity_role_mapping.values() if m['matched_role'] is not None)
        mapping['coverage'] = mapped_count / len(governance_entities) if governance_entities else 0.0
        
        # Calculate alignment score
        if entity_role_mapping:
            avg_match_quality = sum(m['match_quality'] for m in entity_role_mapping.values()) / len(entity_role_mapping)
            mapping['alignment_score'] = avg_match_quality
        
        return mapping
    
    def assess_organizational_capacity(
        self,
        governance_entities: List[Dict[str, Any]],
        organizational_capacity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess organizational capacity for governance functions.
        
        Parameters:
        -----------
        governance_entities : List[Dict[str, Any]]
            Governance entities requiring capacity
        organizational_capacity_data : Dict[str, Any]
            Organizational capacity information
            
        Returns:
        --------
        Dict[str, Any]
            Capacity assessment results
        """
        assessment = {
            'capacity_assessed': True,
            'entity_capacity': {},
            'overall_capacity': 0.0,
            'capacity_gaps': []
        }
        
        if not self.org_available:
            assessment['capacity_assessed'] = False
            assessment['reason'] = 'Organizational module not available'
            return assessment
        
        # Assess capacity for each entity
        for entity in governance_entities:
            entity_id = entity.get('entity_id', 'unknown')
            entity_responsibilities = entity.get('responsibilities', [])
            
            # Get capacity data for this entity's domain
            capacity_factors = {
                'staffing': organizational_capacity_data.get('staffing_level', 0.5),
                'budget': organizational_capacity_data.get('budget_adequacy', 0.5),
                'expertise': organizational_capacity_data.get('expertise_level', 0.5),
                'systems': organizational_capacity_data.get('system_capacity', 0.5)
            }
            
            # Calculate overall capacity
            entity_capacity = sum(capacity_factors.values()) / len(capacity_factors)
            
            assessment['entity_capacity'][entity_id] = {
                'capacity_score': entity_capacity,
                'capacity_factors': capacity_factors,
                'responsibilities': entity_responsibilities
            }
            
            # Identify capacity gaps
            if entity_capacity < 0.6:
                assessment['capacity_gaps'].append({
                    'entity_id': entity_id,
                    'capacity_score': entity_capacity,
                    'gap_severity': 'high' if entity_capacity < 0.4 else 'medium'
                })
        
        # Calculate overall capacity
        if assessment['entity_capacity']:
            assessment['overall_capacity'] = sum(
                e['capacity_score'] for e in assessment['entity_capacity'].values()
            ) / len(assessment['entity_capacity'])
        
        return assessment
    
    def check_governance_organization_alignment(
        self,
        governance_structure: Dict[str, Any],
        organizational_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check alignment between governance structure and organizational structure.
        
        Parameters:
        -----------
        governance_structure : Dict[str, Any]
            Governance structure definition
        organizational_structure : Dict[str, Any]
            Organizational structure definition
            
        Returns:
        --------
        Dict[str, Any]
            Alignment assessment
        """
        alignment = {
            'alignment_checked': True,
            'overall_alignment': 0.0,
            'alignment_factors': {},
            'misalignments': []
        }
        
        if not self.org_available:
            alignment['alignment_checked'] = False
            alignment['reason'] = 'Organizational module not available'
            return alignment
        
        # Check structural alignment
        gov_levels = governance_structure.get('governance_levels', [])
        org_levels = organizational_structure.get('levels', [])
        
        level_alignment = len(set(str(l).lower() for l in gov_levels) & 
                             set(str(l).lower() for l in org_levels)) / max(1, len(gov_levels))
        alignment['alignment_factors']['level_alignment'] = level_alignment
        
        # Check responsibility alignment
        gov_entities = governance_structure.get('entities', [])
        org_roles = organizational_structure.get('roles', [])
        
        all_gov_responsibilities = set()
        for entity in gov_entities:
            all_gov_responsibilities.update(entity.get('responsibilities', []))
        
        all_org_responsibilities = set()
        for role in org_roles:
            all_org_responsibilities.update(role.get('responsibilities', []))
        
        responsibility_alignment = len(all_gov_responsibilities & all_org_responsibilities) / max(1, len(all_gov_responsibilities))
        alignment['alignment_factors']['responsibility_alignment'] = responsibility_alignment
        
        # Identify misalignments
        missing_in_org = all_gov_responsibilities - all_org_responsibilities
        if missing_in_org:
            alignment['misalignments'].append({
                'type': 'missing_organizational_roles',
                'description': f'Governance responsibilities not covered by organization: {list(missing_in_org)[:5]}',
                'severity': 'high' if len(missing_in_org) > 3 else 'medium'
            })
        
        # Calculate overall alignment
        alignment['overall_alignment'] = (
            level_alignment * 0.4 +
            responsibility_alignment * 0.6
        )
        
        return alignment


