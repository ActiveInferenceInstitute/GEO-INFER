# GEO-INFER-TRANSPORT API Reference

Complete API reference for the `geo_infer_transport` package.

## TransportNetwork

**Module**: `geo_infer_transport.core.network`

Build and analyze transportation network topology. Uses `networkx.DiGraph` as the graph backend.

### Constructor

```python
TransportNetwork(
    network_type: str = "road",
    modes: Optional[List[str]] = None,
    crs: str = "EPSG:4326",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `network_type` | `str` | `"road"` | Network type: `"road"`, `"rail"`, `"multimodal"` |
| `modes` | `Optional[List[str]]` | `["car", "bicycle", "pedestrian"]` | Supported transport modes |
| `crs` | `str` | `"EPSG:4326"` | Coordinate reference system |

### Properties

#### `graph -> nx.DiGraph`

Access the underlying NetworkX directed graph.

### Methods

#### `build_from_edges(edges: List[Dict], nodes: Optional[List[Dict]] = None, attributes: Optional[List[str]] = None) -> Dict[str, Any]`

Build network from edge and node lists.

**Edge dict keys**: `id`, `from`, `to`, `road_class`, `length_m`, `speed_limit`, `lanes`, `one_way`, `geometry`.

**Returns**: Summary with `nodes_created`, `edges_created`, `network_type`, `is_connected`.

#### `analyze_connectivity(method: str = "components", origin: Optional[str] = None, destinations: Optional[List[str]] = None) -> Dict[str, Any]`

Analyze network connectivity.

| Method | Description | Additional Parameters |
|--------|-------------|----------------------|
| `"components"` | Strongly/weakly connected components | -- |
| `"reachability"` | Nodes reachable from origin | `origin` required |
| `"betweenness"` | Top betweenness centrality nodes | -- |
| `"critical_links"` | Critical links by edge betweenness | -- |

For `"critical_links"`, delegates to GEO-INFER-LOG `TransportationNetworkAnalyzer` if available, otherwise falls back to NetworkX edge betweenness.

#### `calculate_centrality(centrality_type: str = "betweenness", weight: str = "length", top_n: int = 10) -> Dict[str, Any]`

Calculate network centrality measures.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `centrality_type` | `str` | `"betweenness"` | `"betweenness"`, `"closeness"`, or `"degree"` |
| `weight` | `str` | `"length"` | Edge weight attribute |
| `top_n` | `int` | `10` | Number of top nodes to return |

**Returns**: Dictionary with `centrality_type`, `top_nodes` (list of {node_id, centrality}), `mean_centrality`.

#### `get_statistics() -> Dict[str, Any]`

Get network statistics: node/edge count, density, degree distributions, total length, road class distribution.

#### `get_subgraph(nodes: Optional[List[str]] = None, bbox: Optional[Dict[str, float]] = None) -> TransportNetwork`

Extract a subgraph by node list or bounding box.

---

## RoutingEngine

**Module**: `geo_infer_transport.core.routing`

Multi-modal routing with optimization capabilities.

### Constructor

```python
RoutingEngine(
    network: Any = None,
    algorithm: str = "dijkstra",
    modes: Optional[List[str]] = None,
    real_time_traffic: bool = False,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `network` | `Any` | `None` | `TransportNetwork` instance |
| `algorithm` | `str` | `"dijkstra"` | `"dijkstra"`, `"a_star"`, `"bellman_ford"`, `"bidirectional"` |
| `modes` | `Optional[List[str]]` | `["car"]` | Transport modes |
| `real_time_traffic` | `bool` | `False` | Enable traffic-adjusted routing |

Optionally integrates with GEO-INFER-LOG `EmissionsCalculator` for emissions-aware routing.

### Methods

#### `route(origin: Dict, destination: Dict, mode: str = "car", optimization: str = "time", avoid: Optional[List[str]] = None, via: Optional[List[Dict]] = None) -> Route`

Calculate a route between two points.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `origin` | `Dict` | -- | Origin point: `{node_id: str}` or `{lat, lon}` |
| `destination` | `Dict` | -- | Destination point |
| `mode` | `str` | `"car"` | Transport mode |
| `optimization` | `str` | `"time"` | `"time"` or `"distance"` |
| `avoid` | `Optional[List[str]]` | `None` | Features to avoid |
| `via` | `Optional[List[Dict]]` | `None` | Intermediate waypoints |

**Returns**: `Route` object with path, distance, time, and instructions.

#### `optimize_route(waypoints: List[Dict], constraints: Dict, objective: str = "minimize_time") -> Dict[str, Any]`

Optimize route through multiple waypoints using nearest-neighbor TSP heuristic.

**Returns**: Dictionary with `optimized_order`, `waypoints`, `estimated_distance_m`, `estimated_time_s`.

#### `calculate_matrix(origins: List[Dict], destinations: List[Dict], metric: str = "time") -> Dict[str, Any]`

Calculate origin-destination cost matrix.

**Returns**: Dictionary with `origins`, `destinations`, `metric`, `matrix` (2D list), `shape`.

#### `find_alternatives(origin: Dict, destination: Dict, count: int = 3, variation: float = 0.2) -> List[Route]`

Find alternative routes by penalizing edges of the primary route.

#### `update_traffic(traffic_data: Dict[str, float]) -> None`

Update traffic adjustment factors for real-time routing. Maps edge IDs to delay multipliers.

#### `set_network(network: Any) -> None`

Set or replace the transport network.

---

## Route

**Module**: `geo_infer_transport.core.routing`

```python
@dataclass
class Route:
    route_id: str
    origin: str
    destination: str
    path: List[str]
    total_distance_m: float
    total_time_s: float
    geometry: Optional[List[Dict[str, float]]] = None
    instructions: List[str] = field(default_factory=list)
    alternatives: List[Route] = field(default_factory=list)
```

---

## TrafficAnalyzer

**Module**: `geo_infer_transport.core.traffic`

Traffic flow modeling, congestion analysis, and forecasting.

### Constructor

```python
TrafficAnalyzer(
    data_sources: Optional[List[str]] = None,
    model_type: str = "bpr",
    time_resolution: str = "15min",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_sources` | `Optional[List[str]]` | `["sensor", "probe"]` | Traffic data sources |
| `model_type` | `str` | `"bpr"` | Congestion model: `"bpr"`, `"akcelik"`, `"hcm"` |
| `time_resolution` | `str` | `"15min"` | Temporal resolution |

### Level of Service Thresholds

| LOS | V/C Ratio |
|-----|-----------|
| A | <= 0.35 |
| B | <= 0.55 |
| C | <= 0.75 |
| D | <= 0.87 |
| E | <= 0.95 |
| F | > 0.95 |

### Methods

#### `analyze_flow(segment: Dict, counts: List[Dict], time_period: str = "peak") -> FlowResult`

Analyze traffic flow on a road segment.

**Returns**: `FlowResult` with volume, density, speed, and Level of Service (A-F).

#### `model_congestion(network_flows: Dict[str, float], capacity_data: Dict[str, float], algorithm: str = "bpr") -> Dict[str, Any]`

Model congestion across the network using the BPR function.

**Returns**: Dictionary with per-segment congestion and summary statistics.

#### `simulate_traffic(network: Any, demand_matrix: Dict, simulation_hours: int = 1, time_step_seconds: int = 60) -> Dict[str, Any]`

Time-stepped traffic simulation with BPR delay model.

**Returns**: Dictionary with per-step results (vehicles, speed, congestion level, V/C ratio) and statistics.

#### `detect_incidents(current_data: Dict, historical_baseline: Dict, threshold: float = 0.3) -> List[Dict]`

Detect traffic incidents from speed anomalies.

#### `forecast_traffic(historical_data: List[Dict], forecast_horizon: str = "1h", model: str = "arima") -> Dict[str, Any]`

Forecast traffic using EWMA with trend and prediction intervals.

**Returns**: Dictionary with forecast points including `predicted_volume`, `confidence_lower`, `confidence_upper`.

---

## Data Classes and Enums

### RoadClass

```python
class RoadClass(Enum):
    MOTORWAY = "motorway"
    TRUNK = "trunk"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    RESIDENTIAL = "residential"
    SERVICE = "service"
    PATH = "path"
```

### TransportMode

```python
class TransportMode(Enum):
    CAR = "car"
    TRUCK = "truck"
    BUS = "bus"
    BICYCLE = "bicycle"
    PEDESTRIAN = "pedestrian"
    RAIL = "rail"
    SUBWAY = "subway"
```

### TrafficCondition

```python
class TrafficCondition(Enum):
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    CONGESTED = "congested"
    BLOCKED = "blocked"
```

### NetworkNode

```python
@dataclass
class NetworkNode:
    node_id: str
    location: Dict[str, float]  # {"lat": ..., "lon": ...}
    node_type: str = "intersection"
    elevation: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)
```

### NetworkEdge

```python
@dataclass
class NetworkEdge:
    edge_id: str
    from_node: str
    to_node: str
    road_class: RoadClass
    length_m: float
    speed_limit_kmh: float = 50
    lanes: int = 1
    one_way: bool = False
    geometry: Optional[List[Dict[str, float]]] = None
    properties: Dict[str, Any] = field(default_factory=dict)
```

### FlowResult

```python
@dataclass
class FlowResult:
    segment_id: str
    volume: int        # vehicles per hour
    density: float     # vehicles per km
    speed: float       # km/h
    level_of_service: str  # A-F
```

### TrafficCount

```python
@dataclass
class TrafficCount:
    location_id: str
    timestamp: datetime
    count: int
    speed_kmh: Optional[float] = None
    occupancy: Optional[float] = None
    direction: Optional[str] = None
```

---

## AccessibilityAnalyzer

**Module**: `geo_infer_transport.core.accessibility`

Service area computation and accessibility scoring.

---

## TransitOptimizer

**Module**: `geo_infer_transport.core.transit`

Transit network optimization and schedule planning.
