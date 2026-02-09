# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 0 classes and 11 functions.

## Classes
 and Functions

### validate_spatial_scope
 `validate_spatial_scope(spatial_scope: Dict[str, Any]) -> bool` Validate spatial scope dictionary.

### validate_stakeholder_groups
 `validate_stakeholder_groups(stakeholder_groups: List[Dict[str, Any]]) -> bool` Validate stakeholder groups list.

### validate_decision_domains
 `validate_decision_domains(decision_domains: List[str]) -> bool` Validate decision domains list.

### calculate_collaboration_potential
 `calculate_collaboration_potential(stakeholders: List[Dict[str, Any]]) -> float` Calculate collaboration potential based on stakeholder interests.

### calculate_power_concentration
 `calculate_power_concentration(stakeholders: List[Dict[str, Any]]) -> Tuple[float, str]` Calculate power concentration among stakeholders.

### extract_governance_metrics
 `extract_governance_metrics(governance_structure: Any) -> Dict[str, Any]` Extract key metrics from governance structure.

### generate_governance_report
 `generate_governance_report(governance_structure: Any, title: Optional[str]) -> str` Generate a governance structure report.

### format_governance_output
 `format_governance_output(data: Any, format_type: str) -> str` Format governance data for output.

### merge_governance_structures
 `merge_governance_structures(structure1: Any, structure2: Any, strategy: str) -> Dict[str, Any]` Merge two governance structures.

### validate_ostrom_principles
 `validate_ostrom_principles(principles: List[str]) -> Tuple[bool, List[str]]` Validate Ostrom design principles.

### calculate_governance_health_score
 `calculate_governance_health_score(metrics: Dict[str, float]) -> float` Calculate overall governance health score.

## Capabilities

- **11 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-METAGOV/src/geo_infer_metagov/utils`
- **Type**: Directory Node
