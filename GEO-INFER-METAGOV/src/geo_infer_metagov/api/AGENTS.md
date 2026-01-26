# Agent
: api ## Scope
 This directory contains api components for the module. It provides 5 classes and 0 functions. ## Classes
 and Functions ### APIVersio
n
 API version enumeration. ### APIRespons
e
 Standard API response format. ### APIErro
r
 Standard API error format. ### GovernanceAP
I
 REST API for governance framework operations. **Methods**: - `create_governance_structure(spatial_scope: Dict[str, Any], stakeholder_groups: List[Dict[str, Any]], decision_domains: List[str], governance_levels: List[str], coordination_mechanisms: List[str]) -> APIResponse`: Create a governance structure via API. - `get_governance_structure(governance_id: str) -> APIResponse`: Retrieve governance structure by ID. - `list_governance_structures(filter_by: Optional[Dict[str, Any]], limit: int, offset: int) -> APIResponse`: List governance structures with optional filtering. - `update_governance_structure(governance_id: str, updates: Dict[str, Any]) -> APIResponse`: Update governance structure. - `delete_governance_structure(governance_id: str) -> APIResponse`: Delete governance structure. - `analyze_governance_structure(governance_id: str, analysis_type: str) -> APIResponse`: Perform analysis on governance structure. - `get_health_status() -> APIResponse`: Get API health status. ### StakeholderAP
I
 REST API for stakeholder management operations. **Methods**: - `create_stakeholder(name: str, category: str, interests: List[str], decision_power: float) -> APIResponse`: Create stakeholder record. - `get_stakeholder(stakeholder_id: str) -> APIResponse`: Retrieve stakeholder by ID. - `list_stakeholders(category: Optional[str]) -> APIResponse`: List stakeholders with optional filtering by category. ## Capabilities
 - **5 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-METAGOV/src/geo_infer_metagov/api` - **Type**: Directory Node 