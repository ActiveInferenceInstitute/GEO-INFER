# Getting Started with GEO-INFER-TRANSPORT

This guide covers installation, core concepts, and first working examples for transport network analysis, routing, and traffic modeling.

## Installation

Install the module in editable mode:

```bash
uv pip install -e ./GEO-INFER-TRANSPORT
```

Core dependency is `networkx`. Install optional dependencies for visualization:

```bash
uv pip install folium geopandas
```

Verify the installation:

```python
import geo_infer_transport
print(geo_infer_transport.__version__)
# 0.2.0
```

## Core Concepts

### Graph-Based Network Analysis

Transportation networks are naturally modeled as directed graphs where:

- **Nodes** represent intersections, stops, or decision points.
- **Edges** represent road segments, rail lines, or paths.
- **Edge attributes** carry length, speed limit, travel time, road class, and lane count.

GEO-INFER-TRANSPORT uses `networkx.DiGraph` as its graph backend, which provides access to the full suite of NetworkX graph algorithms while remaining lightweight and dependency-minimal.

### Road Classification

The module uses a seven-class road hierarchy:

| Class | Example | Typical Speed |
|-------|---------|--------------|
| `MOTORWAY` | Highway, interstate | 100-130 km/h |
| `TRUNK` | Major highway | 80-110 km/h |
| `PRIMARY` | Primary road | 60-80 km/h |
| `SECONDARY` | Secondary road | 40-60 km/h |
| `TERTIARY` | Local connector | 30-50 km/h |
| `RESIDENTIAL` | Neighborhood street | 20-40 km/h |
| `SERVICE` | Parking, access road | 10-20 km/h |

### Transport Modes

Seven modes are supported, enabling multi-modal network analysis:

- `CAR`, `TRUCK`, `BUS`: Motorized vehicle modes
- `BICYCLE`, `PEDESTRIAN`: Active transport modes
- `RAIL`, `SUBWAY`: Fixed-guideway transit modes

### BPR Congestion Function

Traffic congestion is modeled using the Bureau of Public Roads (BPR) function:

```
t = t0 * (1 + alpha * (V/C)^beta)
```

Where:
- `t0` = free-flow travel time
- `V` = volume (vehicles per hour)
- `C` = capacity (vehicles per hour)
- `alpha = 0.15`, `beta = 4` (standard parameters)

This produces a smooth delay curve that increases sharply as volume approaches capacity.

## First Example: Build and Query a Network

```python
from geo_infer_transport import TransportNetwork

# Create a road network
network = TransportNetwork(network_type="road", modes=["car", "bicycle"])

# Define edges (road segments)
edges = [
    {"id": "e1", "from": "A", "to": "B", "road_class": "primary", "length_m": 1000, "speed_limit": 60},
    {"id": "e2", "from": "B", "to": "C", "road_class": "secondary", "length_m": 800, "speed_limit": 40},
    {"id": "e3", "from": "A", "to": "C", "road_class": "residential", "length_m": 1500, "speed_limit": 30},
    {"id": "e4", "from": "C", "to": "D", "road_class": "primary", "length_m": 1200, "speed_limit": 60},
    {"id": "e5", "from": "B", "to": "D", "road_class": "secondary", "length_m": 900, "speed_limit": 40, "one_way": True},
]

# Build the network
summary = network.build_from_edges(edges)
print(f"Nodes: {summary['nodes_created']}")
print(f"Edges: {summary['edges_created']}")
print(f"Connected: {summary['is_connected']}")

# Get network statistics
stats = network.get_statistics()
print(f"Total length: {stats['total_length_km']:.1f} km")
print(f"Density: {stats['density']:.3f}")
print(f"Road classes: {stats['road_class_distribution']}")
```

## Second Example: Shortest Path Routing

```python
from geo_infer_transport import TransportNetwork, RoutingEngine

# Build network (from above)
network = TransportNetwork()
network.build_from_edges(edges)

# Create routing engine
router = RoutingEngine(network=network, algorithm="dijkstra")

# Calculate route
route = router.route(
    origin={"node_id": "A"},
    destination={"node_id": "D"},
    mode="car",
    optimization="time",
)

print(f"Path: {' -> '.join(route.path)}")
print(f"Distance: {route.total_distance_m / 1000:.1f} km")
print(f"Travel time: {route.total_time_s / 60:.1f} minutes")
print(f"Instructions: {route.instructions}")
```

## Third Example: Network Connectivity Analysis

```python
# Analyze connectivity
connectivity = network.analyze_connectivity(method="components")
print(f"Strongly connected components: {connectivity['strongly_connected_components']}")
print(f"Is strongly connected: {connectivity['is_strongly_connected']}")

# Reachability from a node
reach = network.analyze_connectivity(
    method="reachability",
    origin="A",
    destinations=["C", "D"],
)
print(f"Reachable from A: {reach['reachable_nodes']} nodes")
print(f"Reachability ratio: {reach['reachability_ratio']:.1%}")
print(f"Destinations reachable: {reach['destinations_reachable']}")

# Find critical nodes (betweenness centrality)
centrality = network.calculate_centrality(
    centrality_type="betweenness",
    weight="length",
    top_n=5,
)
print(f"\nMost critical nodes:")
for node in centrality["top_nodes"]:
    print(f"  {node['node_id']}: centrality = {node['centrality']:.4f}")
```

## Fourth Example: Origin-Destination Matrix

```python
# Compute OD matrix
origins = [{"node_id": "A", "id": "A"}, {"node_id": "B", "id": "B"}]
destinations = [{"node_id": "C", "id": "C"}, {"node_id": "D", "id": "D"}]

od_matrix = router.calculate_matrix(origins, destinations, metric="time")

print(f"OD Matrix (travel time in seconds):")
print(f"  Origins: {od_matrix['origins']}")
print(f"  Destinations: {od_matrix['destinations']}")
for i, row in enumerate(od_matrix['matrix']):
    print(f"  {od_matrix['origins'][i]}: {row}")
```

## Fifth Example: Traffic Flow Analysis

```python
from geo_infer_transport import TrafficAnalyzer

traffic = TrafficAnalyzer(model_type="bpr", time_resolution="15min")

# Analyze flow on a road segment
segment = {"id": "main_st", "speed_limit": 50, "capacity": 1800}
counts = [
    {"count": 120, "speed_kmh": 45},
    {"count": 135, "speed_kmh": 42},
    {"count": 128, "speed_kmh": 44},
    {"count": 142, "speed_kmh": 38},
]

flow = traffic.analyze_flow(segment, counts, time_period="peak")
print(f"Volume: {flow.volume} veh/hr")
print(f"Speed: {flow.speed} km/h")
print(f"Density: {flow.density} veh/km")
print(f"Level of Service: {flow.level_of_service}")
```

## Sixth Example: Alternative Routes

```python
# Find 3 alternative routes
alternatives = router.find_alternatives(
    origin={"node_id": "A"},
    destination={"node_id": "D"},
    count=3,
    variation=0.3,
)

for i, alt in enumerate(alternatives):
    label = "Primary" if i == 0 else f"Alternative {i}"
    print(f"{label}: {' -> '.join(alt.path)}, "
          f"{alt.total_distance_m/1000:.1f} km, "
          f"{alt.total_time_s/60:.1f} min")
```

## Next Steps

- Read the [API Reference](api_reference.md) for the full method catalog.
- Try the [Network Routing Example](examples/basic_example.md) for a larger network with visualization.
- See the [Traffic Modeling Example](examples/advanced_example.md) for congestion simulation with demand prediction.
