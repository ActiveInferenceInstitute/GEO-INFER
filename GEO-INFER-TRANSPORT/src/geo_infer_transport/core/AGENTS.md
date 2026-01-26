# Agent
: core ## Scope
 This directory contains core components for the module. It provides 20 classes and 0 functions. ## Classes
 and Functions ### Isochron
e
 Represents an isochrone (travel time contour). ### ServiceAre
a
 Represents a service area analysis result. ### AccessibilityAnalyze
r
 Analyze accessibility and generate service areas. **Methods**: - `set_network(network: Any) -> None`: Set the transport network. - `calculate_isochrone(origin: Dict[str, Any], travel_times: List[float], mode: str, departure_time: Optional[datetime]) -> List[Isochrone]`: Calculate isochrones from an origin point. - `generate_service_area(facilities: List[Dict[str, Any]], breaks: List[float], mode: str, dissolve: bool) -> List[ServiceArea]`: Generate service areas for facilities. - `analyze_equity(population_groups: Dict[str, Any], accessibility_scores: Dict[str, float], metrics: List[str]) -> Dict[str, Any]`: Analyze accessibility equity across population groups. - `calculate_accessibility_index(origin: Dict[str, Any], destinations: List[Dict[str, Any]], decay_function: str, beta: float) -> Dict[str, Any]`: Calculate accessibility index using gravity-based approach. ### RoadClas
s
 Road classification types. ### TransportMod
e
 Transportation modes. ### NetworkNod
e
 Represents a node in the transport network. ### NetworkEdg
e
 Represents an edge (road segment) in the transport network. ### TransportNetwor
k
 Build and analyze transportation network topology. **Methods**: - `build_from_edges(edges: List[Dict[str, Any]], nodes: Optional[List[Dict[str, Any]]], attributes: Optional[List[str]]) -> Dict[str, Any]`: Build network from edge list. - `analyze_connectivity(method: str, origin: Optional[str], destinations: Optional[List[str]]) -> Dict[str, Any]`: Analyze network connectivity. - `calculate_centrality(centrality_type: str, weight: str, top_n: int) -> Dict[str, Any]`: Calculate network centrality measures. - `get_statistics() -> Dict[str, Any]`: Get network statistics. - `get_subgraph(nodes: Optional[List[str]], bbox: Optional[Dict[str, float]]) -> 'TransportNetwork'`: Extract a subgraph from the network. - `graph() -> nx.DiGraph`: Get the underlying NetworkX graph. ### RoutingAlgorith
m
 Routing algorithms. ### OptimizationCriteri
a
 Route optimization criteria. ### Rout
e
 Represents a computed route. ### RoutingEngin
e
 Multi-modal routing engine with optimization capabilities. **Methods**: - `set_network(network: Any) -> None`: Set the transport network. - `route(origin: Dict[str, Any], destination: Dict[str, Any], mode: str, optimization: str, avoid: Optional[List[str]], via: Optional[List[Dict[str, Any]]]) -> Route`: Calculate a route between origin and destination. - `optimize_route(waypoints: List[Dict[str, Any]], constraints: Dict[str, Any], objective: str) -> Dict[str, Any]`: Optimize route through multiple waypoints. - `calculate_matrix(origins: List[Dict[str, Any]], destinations: List[Dict[str, Any]], metric: str) -> Dict[str, Any]`: Calculate origin-destination matrix. - `find_alternatives(origin: Dict[str, Any], destination: Dict[str, Any], count: int, variation: float) -> List[Route]`: Find alternative routes. - `update_traffic(traffic_data: Dict[str, float]) -> None`: Update traffic data for real-time routing. ### TrafficConditio
n
 Traffic condition levels. ### TrafficCoun
t
 Traffic count observation. ### FlowResul
t
 Traffic flow analysis result. ### TrafficAnalyze
r
 Analyze and model traffic flow patterns. **Methods**: - `analyze_flow(segment: Dict[str, Any], counts: List[Dict[str, Any]], time_period: str) -> FlowResult`: Analyze traffic flow on a road segment. - `model_congestion(network_flows: Dict[str, float], capacity_data: Dict[str, float], algorithm: str) -> Dict[str, Any]`: Model congestion across the network. - `simulate_traffic(network: Any, demand_matrix: Dict[str, Any], simulation_hours: int, time_step_seconds: int) -> Dict[str, Any]`: Simulate traffic flow over time. - `detect_incidents(current_data: Dict[str, Any], historical_baseline: Dict[str, Any], threshold: float) -> List[Dict[str, Any]]`: Detect traffic incidents from anomalies. - `forecast_traffic(historical_data: List[Dict[str, Any]], forecast_horizon: str, model: str) -> Dict[str, Any]`: Forecast future traffic conditions. ### TransitMod
e
 Transit mode types. ### TransitSto
p
 Represents a transit stop. ### TransitRout
e
 Represents a transit route. ### TransitOptimize
r
 Optimize transit network design and service. **Methods**: - `optimize_frequencies(routes: List[Dict[str, Any]], demand_patterns: Dict[str, Any], fleet_constraints: Dict[str, int], optimization_period: str) -> Dict[str, Any]`: Optimize route frequencies. - `analyze_coverage(stops: List[Dict[str, Any]], population_zones: List[Dict[str, Any]], walk_radius_m: float, equity_focus: bool) -> Dict[str, Any]`: Analyze transit coverage. - `design_network(demand_zones: List[Dict[str, Any]], constraints: Dict[str, Any], mode: str, objective: str) -> Dict[str, Any]`: Design a transit network. - `evaluate_scenario(base_network: Dict[str, Any], proposed_changes: List[Dict[str, Any]], metrics: List[str]) -> Dict[str, Any]`: Evaluate a network change scenario. ## Capabilities
 - **20 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-TRANSPORT/src/geo_infer_transport/core` - **Type**: Directory Node 