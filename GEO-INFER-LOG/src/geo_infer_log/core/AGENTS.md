# Agent
: core

## Scope
 This directory contains core components for the module. It provides 21 classes and 0 functions.

## Classes
 and Functions

### LastMileRouter
 Specialized routing for last-mile delivery.

**Methods**:
- `load_network(network_file: str) -> None`: Load a transportation network from a file.
- `define_service_area(depot_id: str, depot_location: Tuple[float, float], max_distance: float) -> Polygon`: Define a service area around a depot.
- `optimize_deliveries(depot: Location, deliveries: List[Location], vehicles: List[Vehicle], constraints: Dict) -> List[Route]`: Optimize deliveries from a depot.

### DeliveryScheduler
 Schedules and manages delivery operations.

**Methods**:
- `create_schedule(depot: Location, deliveries: List[Location], vehicles: List[Vehicle], start_date: datetime, end_date: datetime, max_deliveries_per_day: int) -> Dict`: Create a delivery schedule for a date range.
- `get_daily_schedule(date: datetime) -> List[Route]`: Get the delivery schedule for a specific day.
- `get_vehicle_schedule(vehicle_id: str) -> List[Route]`: Get the schedule for a specific vehicle.
- `reschedule_delivery(route_id: str, delivery_idx: int, new_date: datetime) -> Dict`: Reschedule a delivery to a different date.

### ServiceAreaAnalyzer
 Analyzes and optimizes delivery service areas.

**Methods**:
- `create_service_area(depot_id: str, depot_location: Tuple[float, float], max_time: Optional[int], max_distance: Optional[float]) -> gpd.GeoDataFrame`: Create a service area around a depot.
- `analyze_coverage(service_areas: Dict[str, Polygon], demand_points: gpd.GeoDataFrame) -> Dict`: Analyze coverage of demand points by service areas.
- `optimize_service_areas(depot_locations: List[Tuple[str, Tuple[float, float]]], demand_points: gpd.GeoDataFrame, max_distance: float) -> Dict[str, Polygon]`: Optimize service areas for multiple depots.

### VehicleType
 Types of vehicles for routing.

### Vehicle
 Representation of a vehicle for routing.

### RoutingParameters
 Parameters for routing optimization.

### RouteOptimizer
 Base class for route optimization.

**Methods**:
- `load_network(network_file: str) -> None`: Load a transportation network from a file.
- `add_vehicle(vehicle: Vehicle) -> None`: Add a vehicle to the fleet.
- `optimize_route(origin: Tuple[float, float], destination: Tuple[float, float], waypoints: Optional[List[Tuple[float, float]]]) -> Dict`: Optimize a route between origin and destination.

### FleetManager
 Manages a fleet of vehicles and their assignments.

**Methods**:
- `add_vehicle(vehicle: Vehicle) -> None`: Add a vehicle to the fleet.
- `assign_delivery(vehicle_id: str, delivery_points: List[Tuple[float, float]], depot: Tuple[float, float]) -> Dict`: Assign a delivery route to a vehicle.
- `get_fleet_status() -> Dict`: Get the current status of the fleet.

### VehicleRouter
 Plans and executes complex vehicle routing problems.

**Methods**:
- `solve_vrp(deliveries: List[Dict], depots: List[Tuple[float, float]], constraints: Dict) -> Dict`: Solve a vehicle routing problem.

### TravelTimeEstimator
 Estimates travel times between points considering traffic and conditions.

**Methods**:
- `load_historical_data(data_file: str) -> None`: Load historical traffic data.
- `estimate_travel_time(origin: Tuple[float, float], destination: Tuple[float, float], departure_time: Optional[str]) -> float`: Estimate travel time between points.
- `calculate_time_matrix(locations: List[Tuple[float, float]], departure_time: Optional[str]) -> np.ndarray`: Calculate a travel time matrix between all locations.
- `calculate_distance_matrix(locations: List[Tuple[float, float]]) -> np.ndarray`: Calculate a distance matrix between all locations.
- `estimate_arrival_times(route: List[Tuple[float, float]], departure_time: str, service_times: Optional[List[float]]) -> List[str]`: Estimate arrival times at each stop along a route.

### MultiObjectiveOptimizer
 Multi-objective optimization for logistics routing.

**Methods**:
- `set_weights(weights: Dict[str, float]) -> None`: Set objective weights.
- `calculate_pareto_front(solutions: List[Dict]) -> List[Dict]`: Calculate the Pareto front from a set of solutions.
- `select_compromise(pareto_front: List[Dict]) -> Dict`: Select a compromise solution from the Pareto front.

### RealTimeTracker
 Real-time tracking and dynamic re-routing.

**Methods**:
- `update_position(vehicle_id: str, position: Tuple[float, float], timestamp: str) -> Dict`: Update vehicle position.
- `get_fleet_positions() -> Dict`: Get current positions of all tracked vehicles.
- `calculate_eta(vehicle_id: str, destination: Tuple[float, float], estimator: TravelTimeEstimator) -> Optional[str]`: Calculate ETA for a vehicle to reach destination.

### SupplyChainModel
 Base class for supply chain network modeling.

**Methods**:
- `load_network(network: SupplyChainNetwork) -> None`: Load a supply chain network.
- `optimize_flow(demand_points: List[Dict], supply_points: List[Dict], objective: str) -> Dict`: Optimize flow in the supply chain network.
- `visualize_network() -> gpd.GeoDataFrame`: Visualize the supply chain network.

### ResilienceAnalyzer
 Analyzes and improves supply chain resilience.

**Methods**:
- `identify_critical_nodes() -> List[str]`: Identify critical nodes in the supply chain.
- `simulate_disruption(disrupted_nodes: List[str], disrupted_edges: List[Tuple[str, str]]) -> Dict`: Simulate a disruption in the supply chain.
- `suggest_improvements() -> List[Dict]`: Suggest improvements to increase supply chain resilience.

### NetworkOptimizer
 Optimizes supply chain network design.

**Methods**:
- `optimize_network(locations: List[Dict], demand_points: List[Dict], constraints: Dict) -> Dict`: Optimize the supply chain network design.
- `evaluate_design(network: SupplyChainNetwork) -> Dict`: Evaluate a supply chain network design.

### FacilityLocator
 Optimizes facility locations in supply chains.

**Methods**:
- `locate_facilities(candidates: List[Dict], demand_points: List[Dict], num_facilities: int, max_distance: Optional[float]) -> List[Dict]`: Determine optimal facility locations.
- `analyze_coverage(facilities: List[Dict], demand_points: List[Dict], max_distance: float) -> Dict`: Analyze coverage of demand points by facilities.

### InventoryManager
 Manages inventory in supply chain networks.

**Methods**:
- `optimize_inventory(facilities: List[Dict], demand_data: Dict, lead_times: Dict, service_level: float) -> Dict`: Optimize inventory levels across facilities.
- `simulate_inventory_policy(policy: Dict, demand_data: Dict, lead_times: Dict, simulation_period: int) -> Dict`: Simulate an inventory policy.

### MultiModalPlanner
 Plans and optimizes multimodal transportation.

**Methods**:
- `load_network(mode: str, network_file: str) -> None`: Load a transportation network for a specific mode.
- `add_transfer_point(location: Tuple[float, float], name: str, modes: List[str], transfer_time: Dict[Tuple[str, str], int]) -> None`: Add a transfer point between transportation modes.
- `plan_route(origin: Tuple[float, float], destination: Tuple[float, float], allowed_modes: List[str], preferences: Dict) -> Dict`: Plan a multimodal route between origin and destination.
- `compare_routes(origin: Tuple[float, float], destination: Tuple[float, float], mode_combinations: List[List[str]]) -> pd.DataFrame`: Compare different multimodal routes between origin and destination.

### TransportationNetworkAnalyzer
 Analyzes transportation networks and flows.

**Methods**:
- `load_network(network_file: str) -> None`: Load a transportation network from a file.
- `load_flow_data(flow_file: str) -> None`: Load transportation flow data from a file.
- `calculate_network_metrics() -> Dict`: Calculate metrics for the transportation network.
- `identify_critical_links(top_n: int) -> List[Tuple[str, str]]`: Identify critical links in the transportation network.
- `analyze_flow() -> Dict`: Analyze transportation flow in the network.
- `visualize_network(with_flow: bool, highlight_critical: bool) -> None`: Visualize the transportation network.

### TrafficSimulator
 Simulates traffic patterns and congestion.

**Methods**:
- `load_network(network_file: str) -> None`: Load a transportation network from a file.
- `set_time_periods(periods: List[str]) -> None`: Set time periods for traffic simulation.
- `set_edge_speeds(edge: Tuple[str, str], speeds: Dict[str, float]) -> None`: Set speeds for an edge by time period.
- `simulate_traffic(origin: str, destination: str, departure_time: str) -> Dict`: Simulate traffic for a route from origin to destination.
- `analyze_congestion(time_period: str, congestion_threshold: float) -> Dict`: Analyze network congestion.

### EmissionsCalculator
 Calculates transportation emissions.

**Methods**:
- `set_emissions_factor(vehicle_type: VehicleType, fuel_type: Optional[FuelType], factor: float) -> None`: Set an emissions factor for a vehicle and fuel type.
- `calculate_route_emissions(vehicle: Vehicle, distance: float, load_factor: float, terrain_factor: float) -> float`: Calculate emissions for a route with a specific vehicle.
- `compare_emissions(route: Dict, vehicle_options: List[Vehicle]) -> pd.DataFrame`: Compare emissions for different vehicle options on a route.
- `calculate_fleet_emissions(fleet: List[Vehicle], routes: List[Route]) -> Dict`: Calculate total emissions for a fleet of vehicles.

## Capabilities

- **21 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-LOG/src/geo_infer_log/core`
- **Type**: Directory Node
