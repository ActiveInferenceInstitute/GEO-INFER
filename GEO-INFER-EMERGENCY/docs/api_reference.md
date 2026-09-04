# GEO-INFER-EMERGENCY API Reference

Complete class and method reference for the GEO-INFER-EMERGENCY emergency management module.

---

## core.evacuation

### EvacuationLevel (Enum)

| Value | Description |
|-------|------------|
| `WARNING` | Be prepared to evacuate |
| `ORDER` | Evacuate immediately |
| `LIFT` | Safe to return |

### EvacuationZone (dataclass)

```python
@dataclass
class EvacuationZone:
    zone_id: str
    name: str
    geometry: Dict[str, Any]         # GeoJSON geometry
    population: int
    level: EvacuationLevel = EvacuationLevel.WARNING
    special_populations: List[str] = field(default_factory=list)
```

### Shelter (dataclass)

```python
@dataclass
class Shelter:
    shelter_id: str
    name: str
    location: Dict[str, Any]         # {"lat": float, "lon": float}
    capacity: int
    current_occupancy: int = 0
    services: List[str] = field(default_factory=list)
    accessible: bool = True
```

### EvacuationRoute (dataclass)

```python
@dataclass
class EvacuationRoute:
    route_id: str
    origin_zone: str
    destination_shelter: str
    path: List[Dict[str, float]]     # List of coordinate dicts
    distance_km: float
    estimated_time_minutes: float
    capacity_vehicles_per_hour: int
```

### EvacuationPlanner

Plan and execute evacuations with route optimization, shelter management, and special population support.

```python
class EvacuationPlanner:
    def __init__(
        self,
        road_network: Optional["nx.Graph"] = None,
        population_data: Optional[Dict[str, Any]] = None,
        shelters: Optional[List[Dict[str, Any]]] = None,
        special_needs: Optional[List[str]] = None,
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `road_network` | `Optional[nx.Graph]` | `None` | NetworkX graph whose nodes are routable locations; edges may carry `travel_time` (minutes), `distance` (km), `capacity` (vehicles/hour), `contraflow_capable` |
| `population_data` | `Optional[Dict]` | `None` | Population demographics |
| `shelters` | `Optional[List[Dict]]` | `None` | Shelter location dicts to register |
| `special_needs` | `Optional[List[str]]` | `["hospitals", "nursing_homes", "schools"]` | Special needs facilities |

#### `register_shelter(shelter_data) -> Shelter`

Register a shelter in the system.

| Parameter | Type | Description |
|-----------|------|------------|
| `shelter_data` | `Dict[str, Any]` | Dict with keys: `id`, `name`, `location`, `capacity`, `services`, `accessible` |

Returns the created `Shelter` instance.

#### `plan(affected_zone, population, destinations, phasing, contraflow) -> Dict[str, Any]`

Create a complete evacuation plan.

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `affected_zone` | `Dict[str, Any]` | -- | Zone requiring evacuation (`id`, `name`, `level`, `geometry`) |
| `population` | `Dict[str, Any]` | -- | Population data (`total`, `special_populations`) |
| `destinations` | `List[Dict[str, Any]]` | -- | Shelter destinations |
| `phasing` | `str` | `"staged"` | Strategy: `staged`, `simultaneous`, `time_phased` |
| `contraflow` | `bool` | `False` | Enable contraflow lanes |

Returns dict with keys: `plan_id`, `created_at`, `affected_zone`, `destinations`, `routes`, `phasing`, `contraflow`, `estimated_clearance_time_hours`, `special_populations`, `status`.

**Phasing strategies:**

| Strategy | Phases | Population Split |
|----------|--------|-----------------|
| `staged` | 3 phases | 30% / 40% / 30% with 0h / 2h / 4h delay |
| `simultaneous` | 1 phase | 100% at 0h |
| `time_phased` | 3 phases | 40% / 35% / 25% with 0h / 4h / 8h delay |

#### `optimize_routes(origins, destinations, objectives, constraints) -> Dict[str, Any]`

Optimize evacuation routes with Dijkstra shortest paths over the configured road network. Raises `ValueError` when no road network is configured or an origin/destination is not a network node. Edge-weight precedence: `travel_time` (minutes), then `distance` (km), then unweighted hop counts. Route capacity is the minimum `capacity` along the path (0 when the network carries no capacity attributes).

| Parameter | Type | Description |
|-----------|------|------------|
| `origins` | `List[str]` | Origin zone IDs (network nodes) |
| `destinations` | `List[str]` | Destination shelter IDs (network nodes) |
| `objectives` | `List[str]` | Optimization objectives (e.g., `clearance_time`, `safety`) |
| `constraints` | `Dict[str, Any]` | Constraints (`road_capacity`, `contraflow`) |

Returns dict with `routes` list (`path`, `distance_km`, `estimated_time_minutes`, `capacity_vehicles_per_hour`) and optimization metadata. Unreachable destination pairs are omitted from `routes`.

Contraflow candidates are derived from edges carrying a truthy `contraflow_capable` attribute; networks without such attributes yield no contraflow segments.

#### `estimate_clearance_time(evacuation_plan, traffic_model, scenarios) -> Dict[str, Any]`

Estimate the time to clear all population from evacuation zones.

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `evacuation_plan` | `Dict[str, Any]` | -- | Plan with zone and routes |
| `traffic_model` | `str` | `"dynamic_assignment"` | Traffic simulation model |
| `scenarios` | `List[str]` | `["expected"]` | Scenarios to evaluate |

Returns dict with scenario-keyed clearance estimates including `clearance_hours`.

---

## core.coordinator

### IncidentType (Enum)

| Value | Description |
|-------|------------|
| `WILDFIRE` | Wildland fire events |
| `FLOOD` | River, coastal, flash floods |
| `EARTHQUAKE` | Seismic events |
| `HURRICANE` | Tropical cyclone events |
| `HAZMAT` | Hazardous materials incidents |
| `MASS_CASUALTY` | Mass casualty incidents |
| `TERRORISM` | Terrorism events |
| `CIVIL_UNREST` | Civil disturbance events |
| `INFRASTRUCTURE` | Infrastructure failures |
| `OTHER` | Unclassified incidents |

### IncidentScale (Enum)

| Value | Description |
|-------|------------|
| `TYPE_5` | Local, handled by initial response |
| `TYPE_4` | Expanding incident |
| `TYPE_3` | Extended attack, multi-discipline |
| `TYPE_2` | Complex incident, full overhead |
| `TYPE_1` | Most complex, national significance |

### Incident (dataclass)

```python
@dataclass
class Incident:
    incident_id: str
    incident_type: IncidentType
    name: str
    location: Dict[str, Any]
    scale: IncidentScale
    status: str = "active"
    start_time: datetime = field(default_factory=datetime.now)
    description: str = ""
    affected_area: Optional[Dict[str, Any]] = None
    priority: int = 1
```

### Agency (dataclass)

```python
@dataclass
class Agency:
    agency_id: str
    name: str
    agency_type: str                  # fire, police, medical, public_works
    jurisdiction: Optional[Dict[str, Any]] = None
    contact_info: Dict[str, str] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
```

### IncidentCommand (dataclass)

```python
@dataclass
class IncidentCommand:
    incident_commander: str
    command_location: Dict[str, Any]
    operations_chief: Optional[str] = None
    planning_chief: Optional[str] = None
    logistics_chief: Optional[str] = None
    finance_chief: Optional[str] = None
    safety_officer: Optional[str] = None
    liaison_officer: Optional[str] = None
    public_info_officer: Optional[str] = None
```

### EmergencyCoordinator

Coordinate multi-agency emergency response following ICS principles.

```python
class EmergencyCoordinator:
    def __init__(
        self,
        command_structure: str = "ics",
        agencies: Optional[List[str]] = None,
        communication_protocol: str = "secure",
        jurisdiction: Optional[Dict[str, Any]] = None,
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `command_structure` | `str` | `"ics"` | Structure type: `ics`, `nims`, `custom` |
| `agencies` | `Optional[List[str]]` | `None` | Initial agency names to register |
| `communication_protocol` | `str` | `"secure"` | Communication security level |
| `jurisdiction` | `Optional[Dict]` | `None` | Jurisdictional boundary geometry |

#### `register_agency(agency) -> None`

Register an agency in the coordination system.

| Parameter | Type | Description |
|-----------|------|------------|
| `agency` | `Agency` | Agency dataclass instance |

#### `coordinate(incident, agencies, resources, incident_action_plan) -> Dict[str, Any]`

Coordinate response to an incident across multiple agencies.

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `incident` | `Dict[str, Any]` | -- | Incident info (`id`, `type`, `name`, `location`, `scale`, `description`) |
| `agencies` | `List[str]` | -- | Responding agency IDs |
| `resources` | `Dict[str, Any]` | -- | Available resources by type |
| `incident_action_plan` | `Optional[Dict]` | `None` | Optional IAP |

Returns dict with: `incident_id`, `incident_name`, `coordination_start`, `command_structure`, `responding_agencies`, `resource_assignments` (per-agency with sector), `communication_channels`, `operational_period`, `status`.

**Communication channels assigned per incident:**

| Channel | Format | Purpose |
|---------|--------|---------|
| Command | `CMD-{id}` | Command coordination |
| Tactical | `TAC-{id}` | Tactical operations |
| Medical | `MED-{id}` | Medical communications |
| Logistics | `LOG-{id}` | Logistics coordination |

**Resource mapping by agency type:**

| Agency Type | Resource Types |
|-------------|---------------|
| `fire` | engines, trucks, personnel |
| `police` | patrol_units, personnel, barriers |
| `medical` | ambulances, personnel, supplies |
| `public_works` | heavy_equipment, trucks, personnel |

#### `establish_command(incident_type, location, scale, command_structure) -> Dict[str, Any]`

Establish an incident command structure.

| Parameter | Type | Description |
|-----------|------|------------|
| `incident_type` | `str` | Type of incident |
| `location` | `Dict[str, Any]` | Command post location |
| `scale` | `str` | Incident scale (type_1 through type_5) |
| `command_structure` | `Dict[str, str]` | ICS positions and personnel names |

---

## core.resources

### ResourceStatus (Enum)

| Value | Description |
|-------|------------|
| `AVAILABLE` | Ready for deployment |
| `ASSIGNED` | Assigned to an incident |
| `EN_ROUTE` | Traveling to incident |
| `ON_SCENE` | At the incident location |
| `OUT_OF_SERVICE` | Not available |
| `RETURNING` | Returning to station |

### ResourceType (Enum)

| Value | Description |
|-------|------------|
| `ENGINE` | Fire engine |
| `TRUCK` | Fire truck |
| `AMBULANCE` | Medical transport |
| `RESCUE_UNIT` | Technical rescue |
| `HAZMAT` | Hazardous materials unit |
| `HELICOPTER` | Rotary-wing aircraft |
| `DOZER` | Heavy equipment |
| `WATER_TENDER` | Water supply vehicle |
| `PERSONNEL` | Human resources |

### Resource (dataclass)

```python
@dataclass
class Resource:
    resource_id: str
    resource_type: ResourceType
    name: str
    status: ResourceStatus = ResourceStatus.AVAILABLE
    location: Optional[Dict[str, float]] = None   # {"lat": float, "lon": float}
    capacity: int = 1
    agency: str = ""
    capabilities: List[str] = field(default_factory=list)
    assigned_incident: Optional[str] = None
```

### ResourceRequest (dataclass)

```python
@dataclass
class ResourceRequest:
    request_id: str
    incident_id: str
    resource_types: List[str]
    quantity: int
    priority: int = 1                # 1 = highest
    location: Dict[str, float] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.now)
    fulfilled: bool = False
```

### ResourceDeployer

Optimize deployment and allocation of emergency resources.

```python
class ResourceDeployer:
    def __init__(
        self,
        resource_types: Optional[List[str]] = None,
        optimization_algorithm: str = "mixed_integer",
        real_time_updates: bool = True,
    )
```

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `resource_types` | `Optional[List[str]]` | `["engines", "ambulances", "rescue_units"]` | Resource types to manage |
| `optimization_algorithm` | `str` | `"mixed_integer"` | Optimization method |
| `real_time_updates` | `bool` | `True` | Enable real-time tracking |

#### `register_resource(resource) -> None`

Register a resource in the deployment system.

| Parameter | Type | Description |
|-----------|------|------------|
| `resource` | `Resource` | Resource dataclass instance |

#### `optimize_allocation(resources, demand_points, constraints, objectives) -> Dict[str, Any]`

Optimize resource allocation to demand points.

| Parameter | Type | Description |
|-----------|------|------------|
| `resources` | `List[Dict[str, Any]]` | Available resources with locations (`id`, `type`, `name`, `location`, `status`, `agency`) |
| `demand_points` | `List[Dict[str, Any]]` | Locations needing resources (`id`, `location`) |
| `constraints` | `Dict[str, Any]` | Constraints: `response_time` (minutes, default 15), `coverage` (fraction, default 0.8) |
| `objectives` | `List[str]` | Objectives (e.g., `minimize_response_time`, `maximize_coverage`) |

Returns dict with: `optimization_algorithm`, `objectives`, `constraints`, `allocations` (list of assignments with `demand_id`, `resource_id`, `estimated_response_time`, `status`), `unallocated_demands`, `metrics` (coverage stats), `feasible`, `timestamp`.

**Metrics returned:**

| Metric | Description |
|--------|------------|
| `total_resources` | Number of input resources |
| `resources_allocated` | Number of resources assigned |
| `total_demands` | Number of demand points |
| `demands_covered` | Number of demands with assigned resources |
| `coverage_rate` | Fraction of demands covered (0.0 to 1.0) |
| `average_response_time` | Mean response time in minutes |

**Feasibility check:** Result is `feasible: true` when `coverage_rate >= constraints["coverage"]` (default 0.8).

#### `dynamic_redeploy(current_positions, pending_incidents, predicted_demand, strategy) -> Dict[str, Any]`

Dynamically redeploy resources based on current conditions.

| Parameter | Type | Default | Description |
|-----------|------|---------|------------|
| `current_positions` | `List[Dict[str, Any]]` | -- | Current resource positions |
| `pending_incidents` | `List[Dict[str, Any]]` | -- | Incidents without resources |
| `predicted_demand` | `Dict[str, Any]` | -- | Predicted future demand areas |
| `strategy` | `str` | `"move_up"` | Redeployment strategy |

Returns redeployment plan with movement instructions.

**Travel time estimation:** Uses Haversine distance with 40 km/h average emergency response speed.
