# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 0 classes and 36 functions.

## Classes
 and Functions

### km_to_miles
 `km_to_miles(kilometers: float) -> float` Convert kilometers to miles.

### miles_to_km
 `miles_to_km(miles: float) -> float` Convert miles to kilometers.

### meters_to_feet
 `meters_to_feet(meters: float) -> float` Convert meters to feet.

### feet_to_meters
 `feet_to_meters(feet: float) -> float` Convert feet to meters.

### km_per_hour_to_mph
 `km_per_hour_to_mph(kph: float) -> float` Convert kilometers per hour to miles per hour.

### mph_to_km_per_hour
 `mph_to_km_per_hour(mph: float) -> float` Convert miles per hour to kilometers per hour.

### liters_to_gallons
 `liters_to_gallons(liters: float) -> float` Convert liters to gallons (US).

### gallons_to_liters
 `gallons_to_liters(gallons: float) -> float` Convert gallons (US) to liters.

### kg_to_pounds
 `kg_to_pounds(kg: float) -> float` Convert kilograms to pounds.

### pounds_to_kg
 `pounds_to_kg(pounds: float) -> float` Convert pounds to kilograms.

### cubic_meters_to_cubic_feet
 `cubic_meters_to_cubic_feet(cubic_meters: float) -> float` Convert cubic meters to cubic feet.

### cubic_feet_to_cubic_meters
 `cubic_feet_to_cubic_meters(cubic_feet: float) -> float` Convert cubic feet to cubic meters.

### celsius_to_fahrenheit
 `celsius_to_fahrenheit(celsius: float) -> float` Convert Celsius to Fahrenheit.

### fahrenheit_to_celsius
 `fahrenheit_to_celsius(fahrenheit: float) -> float` Convert Fahrenheit to Celsius.

### minutes_to_hours
 `minutes_to_hours(minutes: float) -> float` Convert minutes to hours.

### hours_to_minutes
 `hours_to_minutes(hours: float) -> float` Convert hours to minutes.

### haversine_distance
 `haversine_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float` Calculate the great circle distance between two points on the earth.

### get_bbox
 `get_bbox(points: List[Tuple[float, float]], buffer: float) -> Tuple[float, float, float, float]` Get the bounding box for a list of coordinates.

### coords_to_geojson
 `coords_to_geojson(coords: List[Tuple[float, float]], geometry_type: str) -> Dict` Convert a list of coordinates to GeoJSON format.

### points_to_gdf
 `points_to_gdf(points: List[Tuple[float, float]], properties: Optional[List[Dict]]) -> gpd.GeoDataFrame` Convert a list of points to a GeoDataFrame.

### route_to_linestring
 `route_to_linestring(coords: List[Tuple[float, float]]) -> LineString` Convert route coordinates to a LineString geometry.

### create_buffer
 `create_buffer(point: Tuple[float, float], distance_km: float) -> Polygon` Create a buffer around a point with a specified radius.

### calculate_route_distance
 `calculate_route_distance(coords: List[Tuple[float, float]]) -> float` Calculate the total distance of a route using Haversine formula.

### get_centroid
 `get_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]` Calculate the geographic centroid of a set of points.

### within_distance
 `within_distance(point: Tuple[float, float], target: Tuple[float, float], max_distance_km: float) -> bool` Check if a point is within a specified distance of a target.

### solve_tsp
 `solve_tsp(points: List[Tuple[float, float]], start_index: int, end_index: Optional[int], time_windows: Optional[List[Tuple[int, int]]], time_matrix: Optional[List[List[int]]]) -> Dict` Solve a Traveling Salesman Problem (TSP).

### solve_vrp
 `solve_vrp(depots: List[Tuple[float, float]], deliveries: List[Tuple[float, float]], num_vehicles: int, vehicle_capacities: Optional[List[float]], delivery_demands: Optional[List[float]], time_windows: Optional[List[Tuple[int, int]]], max_distance: Optional[float], max_time: Optional[int]) -> Dict` Solve a Vehicle Routing Problem (VRP).

### distance_callback
 `distance_callback(from_index, to_index)`

### time_callback
 `time_callback(from_index, to_index)`

### distance_callback
 `distance_callback(from_index, to_index)`

### time_callback
 `time_callback(from_index, to_index)`

### demand_callback
 `demand_callback(from_index)` Return the demand of the node.

### plot_route
 `plot_route(route: List[Tuple[float, float]], points_of_interest: Optional[List[Tuple[float, float]]], labels: Optional[List[str]], title: str, figsize: Tuple[int, int], basemap: bool) -> plt.Figure` Plot a route on a map.

### plot_network
 `plot_network(graph: nx.Graph, node_positions: Optional[Dict[Any, Tuple[float, float]]], node_colors: Optional[Dict[Any, str]], edge_weights: Optional[Dict[Tuple[Any, Any], float]], highlight_path: Optional[List[Any]], title: str, figsize: Tuple[int, int]) -> plt.Figure` Plot a network graph.

### plot_service_area
 `plot_service_area(service_areas: Dict[str, gpd.GeoDataFrame], facilities: Optional[gpd.GeoDataFrame], demand_points: Optional[gpd.GeoDataFrame], title: str, figsize: Tuple[int, int], basemap: bool) -> plt.Figure` Plot service areas on a map.

### create_interactive_map
 `create_interactive_map(routes: Optional[List[List[Tuple[float, float]]]], service_areas: Optional[Dict[str, gpd.GeoDataFrame]], facilities: Optional[gpd.GeoDataFrame], demand_points: Optional[gpd.GeoDataFrame], center: Optional[Tuple[float, float]], zoom: int) -> folium.Map` Create an interactive map with Folium.

## Capabilities

- **36 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-LOG/src/geo_infer_log/utils`
- **Type**: Directory Node
