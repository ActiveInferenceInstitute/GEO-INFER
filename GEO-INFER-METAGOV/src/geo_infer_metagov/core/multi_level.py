"""Multi-level governance framework implementation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GovernanceLevel(Enum):
    """Governance organizational levels."""
    LOCAL = "local"
    WATERSHED = "watershed"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"


class CoordinationMechanism(Enum):
    """Coordination mechanisms between governance levels."""
    VERTICAL_ALIGNMENT = "vertical_alignment"
    HORIZONTAL_INTEGRATION = "horizontal_integration"
    SUBSIDIARITY = "subsidiarity"
    NETWORKED_GOVERNANCE = "networked_governance"
    MARKET_BASED = "market_based"
    CONSENSUS_BUILDING = "consensus_building"


@dataclass
class GovernanceEntity:
    """Represents a governing body or organization."""
    entity_id: str
    name: str
    governance_level: GovernanceLevel
    jurisdiction: Dict[str, Any]
    responsibilities: List[str]
    authority_domain: str
    stakeholders: List[str] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=dict)
    capacity: float = 1.0


@dataclass
class GovernanceStructure:
    """Represents a complete governance structure."""
    governance_id: str
    spatial_scope: Dict[str, Any]
    governance_levels: List[GovernanceLevel]
    entities: List[GovernanceEntity]
    coordination_mechanisms: List[CoordinationMechanism]
    decision_domains: List[str]
    stakeholder_groups: List[str]
    reporting_relationships: Dict[str, List[str]] = field(default_factory=dict)
    information_flows: Dict[str, List[str]] = field(default_factory=dict)
    decision_escalation_rules: Dict[str, Dict[str, str]] = field(default_factory=dict)


class MultiLevelGovernanceFramework:
    """
    Framework for designing and coordinating governance across multiple organizational levels.
    
    Implements vertical coordination (local-regional-national), horizontal coordination
    (cross-sectoral, cross-jurisdictional), subsidiarity principles, and nested governance
    structures for managing complex geospatial systems.
    
    References:
    - Benz et al. (2007). Multi-level Governance and Democracy
    - Piattoni, S. (2010). The Multi-level Governance of Regional Policy
    - Termeer, C. J., et al. (2010). Governance capabilities for dealing with conflict
    """
    
    def __init__(
        self,
        governance_levels: Optional[List[str]] = None,
        coordination_mechanisms: Optional[List[str]] = None,
        domain_coverage: Optional[List[str]] = None
    ):
        """
        Initialize multi-level governance framework.
        
        Parameters:
        -----------
        governance_levels : List[str]
            Levels of governance (local, regional, national, international)
        coordination_mechanisms : List[str]
            Coordination approaches between levels
        domain_coverage : List[str]
            Policy domains covered (environmental, civic, commercial, social)
        """
        # Normalize governance levels
        default_levels = ['local', 'regional', 'national']
        levels_to_use = governance_levels or default_levels
        
        self.governance_levels = []
        for level in levels_to_use:
            try:
                self.governance_levels.append(GovernanceLevel(level.lower()))
            except ValueError:
                # If level not in enum, try to use a supported level
                logger.warning(f"Governance level '{level}' not recognized, using 'regional'")
                self.governance_levels.append(GovernanceLevel.REGIONAL)
        
        self.coordination_mechanisms = [
            CoordinationMechanism(mech) if isinstance(mech, str) else mech
            for mech in (coordination_mechanisms or ['vertical_alignment', 'horizontal_integration'])
        ]
        self.domain_coverage = domain_coverage or ['environmental', 'civic', 'commercial']
        self.governance_structures: Dict[str, GovernanceStructure] = {}
        
    def design_governance_structure(
        self,
        spatial_scope: Dict[str, Any],
        stakeholder_groups: List[Dict[str, Any]],
        decision_domains: List[str],
        time_horizons: List[int]
    ) -> GovernanceStructure:
        """
        Design comprehensive multi-level governance structure.
        
        Parameters:
        -----------
        spatial_scope : Dict[str, Any]
            Geographic boundaries and spatial extent
        stakeholder_groups : List[Dict[str, Any]]
            Groups participating in governance
        decision_domains : List[str]
            Areas requiring governance decisions
        time_horizons : List[int]
            Planning horizons in years (e.g., [1, 5, 10, 20])
            
        Returns:
        --------
        GovernanceStructure
            Designed multi-level governance architecture
        """
        governance_id = f"mlg_{spatial_scope.get('name', 'region')}_{len(self.governance_structures)}"
        
        # Create governance entities for each level
        entities = self._create_governance_entities(
            stakeholder_groups=stakeholder_groups,
            decision_domains=decision_domains,
            spatial_scope=spatial_scope
        )
        
        # Establish reporting relationships
        reporting_relationships = self._establish_reporting_relationships(entities)
        
        # Design information flows
        information_flows = self._design_information_flows(
            entities=entities,
            decision_domains=decision_domains
        )
        
        # Set decision escalation rules
        decision_escalation = self._set_decision_escalation_rules(
            entities=entities,
            decision_domains=decision_domains,
            time_horizons=time_horizons
        )
        
        # Create governance structure
        structure = GovernanceStructure(
            governance_id=governance_id,
            spatial_scope=spatial_scope,
            governance_levels=self.governance_levels,
            entities=entities,
            coordination_mechanisms=self.coordination_mechanisms,
            decision_domains=decision_domains,
            stakeholder_groups=[sg.get('name', f'group_{i}') for i, sg in enumerate(stakeholder_groups)],
            reporting_relationships=reporting_relationships,
            information_flows=information_flows,
            decision_escalation_rules=decision_escalation
        )
        
        self.governance_structures[governance_id] = structure
        logger.info(f"Governance structure designed: {governance_id}")
        return structure
    
    def _create_governance_entities(
        self,
        stakeholder_groups: List[Dict[str, Any]],
        decision_domains: List[str],
        spatial_scope: Dict[str, Any]
    ) -> List[GovernanceEntity]:
        """Create governance entities for each level."""
        entities = []
        level_idx = 0
        
        for level in self.governance_levels:
            entity_id = f"entity_{level.value}_{spatial_scope.get('name', 'region')}"
            
            # Allocate stakeholders and domains to this level
            allocated_stakeholders = [
                sg.get('name', f'stakeholder_{i}')
                for i, sg in enumerate(stakeholder_groups)
                if i % len(self.governance_levels) == level_idx
            ]
            
            allocated_domains = [
                domain for i, domain in enumerate(decision_domains)
                if i % len(self.governance_levels) == level_idx
            ]
            
            entity = GovernanceEntity(
                entity_id=entity_id,
                name=f"{level.value.capitalize()} Authority",
                governance_level=level,
                jurisdiction=spatial_scope,
                responsibilities=allocated_domains,
                authority_domain=', '.join(allocated_domains) or 'general',
                stakeholders=allocated_stakeholders,
                resources={'budget': 1000000.0 * (len(self.governance_levels) - level_idx)},
                capacity=0.7 + (0.1 * level_idx)
            )
            
            entities.append(entity)
            level_idx += 1
        
        return entities
    
    def _establish_reporting_relationships(
        self,
        entities: List[GovernanceEntity]
    ) -> Dict[str, List[str]]:
        """Establish hierarchical reporting relationships."""
        reporting = {}
        
        for i, entity in enumerate(entities):
            # Lower levels report to higher levels (local → regional → national)
            if i > 0:
                reporting[entity.entity_id] = [entities[i - 1].entity_id]
            else:
                reporting[entity.entity_id] = []
        
        return reporting
    
    def _design_information_flows(
        self,
        entities: List[GovernanceEntity],
        decision_domains: List[str]
    ) -> Dict[str, List[str]]:
        """Design information flows between governance levels."""
        flows = {}
        
        for entity in entities:
            # Both upward (monitoring) and downward (directives) flows
            target_entities = [e.entity_id for e in entities if e.entity_id != entity.entity_id]
            flows[entity.entity_id] = target_entities
        
        return flows
    
    def _set_decision_escalation_rules(
        self,
        entities: List[GovernanceEntity],
        decision_domains: List[str],
        time_horizons: List[int]
    ) -> Dict[str, Dict[str, str]]:
        """Set rules for escalating decisions to higher governance levels."""
        escalation_rules = {}
        
        for domain in decision_domains:
            escalation_rules[domain] = {
                'implementation_level': 'local',
                'coordination_level': 'regional',
                'strategic_level': 'national',
                'escalation_condition': 'cross_jurisdictional_impact',
                'escalation_time_horizon': str(min(time_horizons))
            }
        
        return escalation_rules
    
    def coordinate_vertical_levels(
        self,
        governance_structure: GovernanceStructure,
        policy_proposal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate decision-making across vertical governance levels.
        
        Parameters:
        -----------
        governance_structure : GovernanceStructure
            Multi-level governance architecture
        policy_proposal : Dict[str, Any]
            Policy proposal requiring coordination
            
        Returns:
        --------
        Dict[str, Any]
            Coordination outcomes with approval status at each level
        """
        coordination_result = {
            'proposal_id': policy_proposal.get('id', 'proposal_unknown'),
            'level_approvals': {},
            'cross_level_conflicts': [],
            'coordinated_implementation': {}
        }
        
        # Evaluate proposal at each governance level
        for entity in governance_structure.entities:
            approval = self._evaluate_at_level(
                entity=entity,
                policy_proposal=policy_proposal,
                coordination_mechanisms=governance_structure.coordination_mechanisms
            )
            
            coordination_result['level_approvals'][entity.entity_id] = approval
        
        # Identify cross-level conflicts
        conflicts = self._identify_conflicts(
            level_approvals=coordination_result['level_approvals'],
            entities=governance_structure.entities
        )
        coordination_result['cross_level_conflicts'] = conflicts
        
        # Determine coordinated implementation
        implementation = self._determine_implementation(
            level_approvals=coordination_result['level_approvals'],
            conflicts=conflicts
        )
        coordination_result['coordinated_implementation'] = implementation
        
        return coordination_result
    
    def _evaluate_at_level(
        self,
        entity: GovernanceEntity,
        policy_proposal: Dict[str, Any],
        coordination_mechanisms: List[CoordinationMechanism]
    ) -> Dict[str, Any]:
        """Evaluate policy proposal at specific governance level."""
        return {
            'entity_id': entity.entity_id,
            'level': entity.governance_level.value,
            'approval_status': 'approved' if entity.capacity > 0.6 else 'conditional',
            'stakeholder_consensus': 0.75,
            'resource_availability': entity.resources.get('budget', 0) > 500000,
            'coordination_mechanisms_aligned': len(coordination_mechanisms) > 0
        }
    
    def _identify_conflicts(
        self,
        level_approvals: Dict[str, Dict[str, Any]],
        entities: List[GovernanceEntity]
    ) -> List[Dict[str, Any]]:
        """Identify conflicts between governance levels."""
        conflicts = []
        
        level_statuses = [approval.get('approval_status') for approval in level_approvals.values()]
        if 'approved' in level_statuses and 'conditional' in level_statuses:
            conflicts.append({
                'type': 'consistency_conflict',
                'description': 'Inconsistent approval status across levels',
                'severity': 'medium'
            })
        
        return conflicts
    
    def _determine_implementation(
        self,
        level_approvals: Dict[str, Dict[str, Any]],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine coordinated implementation strategy."""
        all_approved = all(
            approval.get('approval_status') == 'approved'
            for approval in level_approvals.values()
        )
        
        return {
            'implementation_possible': all_approved or len(conflicts) < 2,
            'required_modifications': len(conflicts),
            'recommended_approach': 'phased' if len(conflicts) > 0 else 'immediate'
        }
    
    def apply_subsidiarity_principle(
        self,
        governance_structure: GovernanceStructure,
        decision_domain: str
    ) -> Dict[str, Any]:
        """
        Apply subsidiarity principle to determine appropriate governance level for decision.
        
        Subsidiarity suggests decisions should be made at the most local level possible,
        escalating only when necessary for coordination or broader impacts.
        
        Parameters:
        -----------
        governance_structure : GovernanceStructure
            Multi-level governance architecture
        decision_domain : str
            Domain requiring governance decision
            
        Returns:
        --------
        Dict[str, Any]
            Subsidiarity analysis with recommended decision level
        """
        # Find entities responsible for this domain
        relevant_entities = [
            e for e in governance_structure.entities
            if decision_domain in e.responsibilities
        ]
        
        if not relevant_entities:
            relevant_entities = governance_structure.entities
        
        # Sort by governance level (local first)
        relevant_entities.sort(key=lambda e: list(GovernanceLevel).index(e.governance_level))
        
        result = {
            'decision_domain': decision_domain,
            'subsidiary_level': relevant_entities[0].governance_level.value if relevant_entities else None,
            'relevant_entities': [e.entity_id for e in relevant_entities],
            'escalation_needed': len(relevant_entities) > 1,
            'coordination_requirements': self._determine_coordination_requirements(relevant_entities)
        }
        
        return result
    
    def _determine_coordination_requirements(self, entities: List[GovernanceEntity]) -> List[str]:
        """Determine what coordination is needed."""
        if len(entities) == 1:
            return []
        return ['information_sharing', 'stakeholder_alignment', 'resource_coordination']
