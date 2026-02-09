# Agent
: core

## Scope
 This directory contains core components for the module. It provides 27 classes and 0 functions.

## Classes
 and Functions

### ThreatLevel
 Threat level classifications.

### DataSource
 Types of data sources.

### SensoryInput
 Represents incoming sensor data.

### LayerConfig
 Configuration for a COP layer.

### SituationalAwareness
 Maintain situational awareness through common operating picture,

**Methods**:
- `integrate_sensors(sensor_network: Dict[str, Any], data_types: List[str], sampling_rate: str) -> Dict[str, Any]`: Integrate sensor network data.
- `build_cop(layers: List[Dict[str, Any]], extent: Dict[str, Any], symbology: Dict[str, Any], refresh_rate: int) -> Dict[str, Any]`: Build common operating picture.
- `assess_threat(hazard: Dict[str, Any], affected_area: Dict[str, Any], assets_at_risk: List[Dict[str, Any]], projection_hours: int) -> Dict[str, Any]`: Assess current threat level.
- `fuse_data(sources: List[Dict[str, Any]], fusion_method: str, confidence_weighting: bool) -> Dict[str, Any]`: Fuse data from multiple sources.
- `generate_dashboard(widgets: List[Dict[str, Any]], layout: str, update_frequency: int) -> Dict[str, Any]`: Generate real-time dashboard.
- `get_current_threat_level() -> str`: Get current threat level.

### IncidentType
 Types of emergency incidents.

### IncidentScale
 ICS incident scale classifications.

### Incident
 Represents an emergency incident.

### Agency
 Represents a responding agency.

### IncidentCommand
 Incident Command System structure.

### EmergencyCoordinator
 Coordinate multi-agency emergency response following ICS principles.

**Methods**:
- `register_agency(agency: Agency) -> None`: Register an agency in the coordination system.
- `coordinate(incident: Dict[str, Any], agencies: List[str], resources: Dict[str, Any], incident_action_plan: Optional[Dict[str, Any]]) -> Dict[str, Any]`: Coordinate response to an incident.
- `establish_command(incident_type: str, location: Dict[str, Any], scale: str, command_structure: Dict[str, str]) -> Dict[str, Any]`: Establish incident command structure.
- `request_mutual_aid(requesting_agency: str, resource_needs: List[str], duration_hours: int, staging_areas: List[Dict[str, Any]]) -> Dict[str, Any]`: Request mutual aid from neighboring jurisdictions.
- `generate_sitrep(incident: Dict[str, Any], update_frequency: str, distribution: List[str], format: str) -> Dict[str, Any]`: Generate situation report.
- `get_active_incidents() -> List[Dict[str, Any]]`: Get list of active incidents.

### EvacuationLevel
 Evacuation alert levels.

### EvacuationZone
 Represents an evacuation zone.

### Shelter
 Represents an evacuation shelter.

### EvacuationRoute
 Represents an evacuation route.

### EvacuationPlanner
 Plan and execute evacuations with route optimization,

**Methods**:
- `register_shelter(shelter_data: Dict[str, Any]) -> Shelter`: Register a shelter in the system.
- `plan(affected_zone: Dict[str, Any], population: Dict[str, Any], destinations: List[Dict[str, Any]], phasing: str, contraflow: bool) -> Dict[str, Any]`: Create an evacuation plan.
- `optimize_routes(origins: List[str], destinations: List[str], objectives: List[str], constraints: Dict[str, Any]) -> Dict[str, Any]`: Optimize evacuation routes.
- `plan_shelters(shelter_locations: List[Dict[str, Any]], population_estimate: int, duration_days: int, services: List[str]) -> Dict[str, Any]`: Plan shelter operations.
- `plan_special_populations(facilities: List[Dict[str, Any]], transportation: List[Dict[str, Any]], receiving_facilities: List[Dict[str, Any]], medical_support: bool) -> Dict[str, Any]`: Plan evacuation of special populations.
- `estimate_clearance_time(evacuation_plan: Dict[str, Any], traffic_model: str, scenarios: List[str]) -> Dict[str, Any]`: Estimate evacuation clearance time.

### ResourceStatus
 Status of emergency resources.

### ResourceType
 Types of emergency resources.

### Resource
 Represents an emergency resource unit.

### ResourceRequest
 A request for emergency resources.

### ResourceDeployer
 Optimize deployment and allocation of emergency resources.

**Methods**:
- `register_resource(resource: Resource) -> None`: Register a resource in the deployment system.
- `optimize_allocation(resources: List[Dict[str, Any]], demand_points: List[Dict[str, Any]], constraints: Dict[str, Any], objectives: List[str]) -> Dict[str, Any]`: Optimize resource allocation to demand points.
- `dynamic_redeploy(current_positions: List[Dict[str, Any]], pending_incidents: List[Dict[str, Any]], predicted_demand: Dict[str, Any], strategy: str) -> Dict[str, Any]`: Dynamically redeploy resources based on current conditions.
- `manage_staging(staging_areas: List[Dict[str, Any]], incoming_resources: List[Dict[str, Any]], assignment_queue: List[Dict[str, Any]], prioritization: str) -> Dict[str, Any]`: Manage staging area operations.
- `track_resources(resources: List[Dict[str, Any]], update_frequency: str, metrics: List[str]) -> Dict[str, Any]`: Track resource status and locations.
- `get_resource_status(resource_id: str) -> Optional[Dict[str, Any]]`: Get status of a specific resource.

### SearchPattern
 Standard SAR search patterns.

### SubjectType
 Types of search subjects.

### SearchSubject
 Information about the search subject.

### SearchTeam
 Represents a search team.

### SearchArea
 Defines a search area with probability.

### SearchAndRescue
 Plan and coordinate search and rescue operations with

**Methods**:
- `register_subject(subject_data: Dict[str, Any]) -> SearchSubject`: Register a search subject.
- `register_team(team_data: Dict[str, Any]) -> SearchTeam`: Register a search team.
- `plan_mission(subject: Dict[str, Any], last_known_point: Dict[str, float], search_radius: Optional[float], terrain_type: str, weather: Dict[str, Any]) -> Dict[str, Any]`: Plan a SAR mission.
- `calculate_pod(subject: Dict[str, Any], search_area: Dict[str, Any], search_effort: float, terrain_coverable: str) -> Dict[str, Any]`: Calculate probability of detection (POD).
- `generate_pattern(area: Dict[str, Any], pattern_type: str, team_size: int, visibility_distance: float) -> Dict[str, Any]`: Generate search pattern.
- `coordinate_teams(teams: List[Dict[str, Any]], search_areas: List[Dict[str, Any]], assignments: Dict[str, str], briefing_time: Optional[datetime]) -> Dict[str, Any]`: Coordinate search teams.
- `update_probability(area_id: str, search_result: str, new_information: Dict[str, Any]) -> Dict[str, Any]`: Update search probability based on results.

## Capabilities

- **27 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-EMERGENCY/src/geo_infer_emergency/core`
- **Type**: Directory Node
