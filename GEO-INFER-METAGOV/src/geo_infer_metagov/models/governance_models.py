"""Comprehensive data models for governance systems."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum


class GovernanceStatus(Enum):
    """Governance status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    TRANSITIONING = "transitioning"
    COMPLETED = "completed"
    INACTIVE = "inactive"


class DecisionType(Enum):
    """Decision types in governance."""
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    EMERGENCY = "emergency"


class ParticipationLevel(Enum):
    """Levels of stakeholder participation."""
    INFORM = "inform"
    CONSULT = "consult"
    INVOLVE = "involve"
    COLLABORATE = "collaborate"
    EMPOWER = "empower"


@dataclass
class GoverningEntity:
    """Represents a governing entity or body."""
    entity_id: str
    name: str
    governance_level: str
    jurisdiction: Optional[Dict[str, Any]] = None
    authorities: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    budget: Optional[float] = None
    staff_count: Optional[int] = None
    contact_information: Optional[Dict[str, str]] = None
    established_date: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        if self.established_date is None:
            self.established_date = datetime.now()


@dataclass
class StakeholderProfile:
    """Comprehensive stakeholder profile."""
    stakeholder_id: str
    name: str
    category: str
    interests: List[str] = field(default_factory=list)
    decision_power: float = 0.5
    influence_sphere: Optional[List[str]] = None
    resources_available: Optional[Dict[str, Any]] = None
    constraints: List[str] = field(default_factory=list)
    communication_preferences: Optional[Dict[str, str]] = None
    participation_history: List[Dict[str, Any]] = field(default_factory=list)
    satisfaction_score: Optional[float] = None
    
    def calculate_engagement_level(self) -> float:
        """Calculate engagement level based on participation history."""
        if not self.participation_history:
            return 0.0
        
        recent_participations = [p for p in self.participation_history 
                                if p.get('recency_score', 0) > 0.5]
        
        return len(recent_participations) / max(len(self.participation_history), 1)


@dataclass
class DecisionDomain:
    """Represents a decision domain in governance."""
    domain_id: str
    name: str
    description: str
    scope: Dict[str, Any]
    responsible_entities: List[str]
    stakeholders_affected: List[str]
    decision_types: List[DecisionType]
    escalation_paths: Optional[List[str]] = None
    performance_indicators: Optional[List[str]] = None
    decisions_made: int = 0
    average_resolution_time: Optional[float] = None


@dataclass
class GovernanceRule:
    """Represents a governance rule or policy."""
    rule_id: str
    name: str
    description: str
    rule_type: str  # 'boundary', 'choice', 'monitoring', etc.
    applies_to: List[str]  # domains, entities, etc.
    enforcement_mechanism: str
    effectiveness_score: float = 0.5
    adoption_date: datetime = field(default_factory=datetime.now)
    review_date: Optional[datetime] = None
    exceptions: List[str] = field(default_factory=list)


@dataclass
class CoordinationMechanism:
    """Represents a coordination mechanism between entities."""
    mechanism_id: str
    name: str
    description: str
    coordinating_entities: List[str]
    coordination_type: str  # 'hierarchical', 'peer', 'network', etc.
    communication_frequency: str
    effectiveness: float = 0.5
    conflicts_resolved: int = 0
    conflicts_escalated: int = 0
    
    def get_success_rate(self) -> float:
        """Calculate conflict resolution success rate."""
        total = self.conflicts_resolved + self.conflicts_escalated
        if total == 0:
            return 0.0
        return self.conflicts_resolved / total


@dataclass
class PerformanceIndicator:
    """Represents a governance performance indicator."""
    indicator_id: str
    name: str
    dimension: str  # 'efficiency', 'equity', 'effectiveness', etc.
    metric_type: str  # 'quantitative' or 'qualitative'
    target_value: float
    current_value: Optional[float] = None
    measurement_frequency: str = "quarterly"
    data_sources: List[str] = field(default_factory=list)
    last_measured: Optional[datetime] = None
    trend: Optional[str] = None  # 'improving', 'stable', 'declining'
    
    def calculate_performance_gap(self) -> float:
        """Calculate gap between target and current value."""
        if self.current_value is None:
            return 1.0
        return abs(self.target_value - self.current_value) / self.target_value


@dataclass
class GovernanceStructure:
    """Complete governance structure model."""
    governance_id: str
    spatial_scope: Dict[str, Any]
    governance_levels: List[str]
    governing_entities: List[GoverningEntity] = field(default_factory=list)
    stakeholders: List[StakeholderProfile] = field(default_factory=list)
    decision_domains: List[DecisionDomain] = field(default_factory=list)
    rules: List[GovernanceRule] = field(default_factory=list)
    coordination_mechanisms: List[CoordinationMechanism] = field(default_factory=list)
    performance_indicators: List[PerformanceIndicator] = field(default_factory=list)
    status: GovernanceStatus = GovernanceStatus.PLANNING
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    documentation: Optional[str] = None
    
    def get_entity_by_id(self, entity_id: str) -> Optional[GoverningEntity]:
        """Get governing entity by ID."""
        for entity in self.governing_entities:
            if entity.entity_id == entity_id:
                return entity
        return None
    
    def get_stakeholder_by_id(self, stakeholder_id: str) -> Optional[StakeholderProfile]:
        """Get stakeholder profile by ID."""
        for stakeholder in self.stakeholders:
            if stakeholder.stakeholder_id == stakeholder_id:
                return stakeholder
        return None
    
    def calculate_average_performance(self) -> float:
        """Calculate average performance across all indicators."""
        if not self.performance_indicators:
            return 0.5
        
        current_values = [p.current_value for p in self.performance_indicators 
                         if p.current_value is not None]
        
        if not current_values:
            return 0.5
        
        return sum(current_values) / len(current_values)
    
    def get_entity_count_by_level(self) -> Dict[str, int]:
        """Get count of entities at each governance level."""
        counts: Dict[str, int] = {}
        for entity in self.governing_entities:
            level = entity.governance_level
            counts[level] = counts.get(level, 0) + 1
        return counts
    
    def get_stakeholder_categories(self) -> Set[str]:
        """Get all stakeholder categories represented."""
        return {s.category for s in self.stakeholders}


@dataclass
class ConflictRecord:
    """Record of a governance conflict."""
    conflict_id: str
    conflict_type: str
    severity: float  # 0-1
    stakeholders_involved: List[str]
    root_causes: List[str]
    resolution_mechanism: str
    status: str  # 'open', 'resolved', 'escalated'
    reported_date: datetime = field(default_factory=datetime.now)
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    def is_resolved(self) -> bool:
        """Check if conflict is resolved."""
        return self.status == 'resolved' and self.resolution_date is not None


@dataclass
class AdaptiveManagementCycle:
    """Represents an adaptive management cycle."""
    cycle_id: str
    governance_domain: str
    cycle_number: int
    start_date: datetime
    end_date: Optional[datetime] = None
    objectives: List[str] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    monitoring_results: Optional[Dict[str, Any]] = None
    lessons_learned: List[str] = field(default_factory=list)
    adaptations_made: List[str] = field(default_factory=list)
    next_cycle_recommendations: Optional[str] = None
    
    def get_duration(self) -> Optional[float]:
        """Get cycle duration in days."""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None


@dataclass
class TransparencyRecord:
    """Records governance transparency and disclosure."""
    record_id: str
    information_type: str
    disclosure_content: Dict[str, Any]
    disclosure_date: datetime
    disclosure_channel: str  # 'website', 'meeting', 'report', etc.
    accessibility: List[str]  # 'multiple_languages', 'digital_access', etc.
    public_access_level: str  # 'full', 'partial', 'restricted'
    view_count: Optional[int] = None
    feedback_received: Optional[int] = None


@dataclass
class AccountabilityReport:
    """Report on governance accountability."""
    report_id: str
    reporting_period: str
    reporting_entity: str
    accountable_to: List[str]
    key_activities: List[str]
    performance_against_commitments: Dict[str, float]
    challenges_faced: List[str]
    corrective_actions_taken: List[str]
    external_audits: Optional[List[str]] = None
    stakeholder_feedback: Optional[Dict[str, float]] = None
    report_date: datetime = field(default_factory=datetime.now)


if __name__ == '__main__':
    # Example usage
    entity = GoverningEntity(
        entity_id="gov_001",
        name="Regional Water Authority",
        governance_level="regional",
        authorities=["water_allocation", "quality_monitoring"],
        responsibilities=["ensure_access", "prevent_pollution"]
    )
    
    stakeholder = StakeholderProfile(
        stakeholder_id="sh_001",
        name="Agricultural Cooperative",
        category="agricultural",
        interests=["water_availability", "irrigation_rights"],
        decision_power=0.6
    )
    
    print(f"Entity: {entity.name} ({entity.governance_level})")
    print(f"Stakeholder: {stakeholder.name} ({stakeholder.category})")
