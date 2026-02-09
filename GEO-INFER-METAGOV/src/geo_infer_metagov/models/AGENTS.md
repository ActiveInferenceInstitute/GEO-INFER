# Agent
: models

## Scope
 This directory contains models components for the module. It provides 14 classes and 0 functions.

## Classes
 and Functions

### GovernanceStatus
 Governance status enumeration.

### DecisionType
 Decision types in governance.

### ParticipationLevel
 Levels of stakeholder participation.

### GoverningEntity
 Represents a governing entity or body.

### StakeholderProfile
 stakeholder profile.

**Methods**:
- `calculate_engagement_level() -> float`: Calculate engagement level based on participation history.

### DecisionDomain
 Represents a decision domain in governance.

### GovernanceRule
 Represents a governance rule or policy.

### CoordinationMechanism
 Represents a coordination mechanism between entities.

**Methods**:
- `get_success_rate() -> float`: Calculate conflict resolution success rate.

### PerformanceIndicator
 Represents a governance performance indicator.

**Methods**:
- `calculate_performance_gap() -> float`: Calculate gap between target and current value.

### GovernanceStructure
 governance structure model.

**Methods**:
- `get_entity_by_id(entity_id: str) -> Optional[GoverningEntity]`: Get governing entity by ID.
- `get_stakeholder_by_id(stakeholder_id: str) -> Optional[StakeholderProfile]`: Get stakeholder profile by ID.
- `calculate_average_performance() -> float`: Calculate average performance across all indicators.
- `get_entity_count_by_level() -> Dict[str, int]`: Get count of entities at each governance level.
- `get_stakeholder_categories() -> Set[str]`: Get all stakeholder categories represented.

### ConflictRecord
 Record of a governance conflict.

**Methods**:
- `is_resolved() -> bool`: Check if conflict is resolved.

### AdaptiveManagementCycle
 Represents an adaptive management cycle.

**Methods**:
- `get_duration() -> Optional[float]`: Get cycle duration in days.

### TransparencyRecord
 Records governance transparency and disclosure.

### AccountabilityReport
 Report on governance accountability.

## Capabilities

- **14 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-METAGOV/src/geo_infer_metagov/models`
- **Type**: Directory Node
