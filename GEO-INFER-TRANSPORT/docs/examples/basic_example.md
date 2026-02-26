# Basic Example: Network Routing

This example demonstrates how to load a road network from edge definitions, compute shortest paths, analyze network structure, and prepare data for map visualization.

## Overview

The workflow covers:

1. Build a realistic road network with multiple road classes.
2. Compute shortest paths by time and distance.
3. Analyze network centrality to find critical intersections.
4. Compute an origin-destination matrix.
5. Find alternative routes.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-TRANSPORT
```

## Step 1: Build a Road Network

Create a network representing a small town with a grid of streets plus a bypass highway.

```python
from geo_infer_transport import TransportNetwork

network = TransportNetwork(
    network_type="road",
    modes=["car", "bicycle", "pedestrian"],
    crs="EPSG:4326",
)

# Define nodes with locations
nodes = [
    {"id": "N1", "location": {"lat": 42.000, "lon": -124.200}, "type": "intersection"},
    {"id": "N2", "location": {"lat": 42.000, "lon": -124.190}, "type": "intersection"},
    {"id": "N3", "location": {"lat": 42.000, "lon": -124.180}, "type": "intersection"},
    {"id": "N4", "location": {"lat": 42.005, "lon": -124.200}, "type": "intersection"},
    {"id": "N5", "location": {"lat": 42.005, "lon": -124.190}, "type": "intersection"},
    {"id": "N6", "location": {"lat": 42.005, "lon": -124.180}, "type": "intersection"},
    {"id": "N7", "location": {"lat": 42.010, "lon": -124.200}, "type": "intersection"},
    {"id": "N8", "location": {"lat": 42.010, "lon": -124.190}, "type": "intersection"},
    {"id": "N9", "location": {"lat": 42.010, "lon": -124.180}, "type": "intersection"},
    # Highway bypass nodes
    {"id": "H1", "location": {"lat": 41.998, "lon": -124.210}, "type": "highway_junction"},
    {"id": "H2", "location": {"lat": 42.012, "lon": -124.170}, "type": "highway_junction"},
]

# Define edges (road segments)
edges = [
    # East-west streets (residential)
    {"id": "e01", "from": "N1", "to": "N2", "road_class": "residential", "length_m": 850, "speed_limit": 30},
    {"id": "e02", "from": "N2", "to": "N3", "road_class": "residential", "length_m": 850, "speed_limit": 30},
    {"id": "e03", "from": "N4", "to": "N5", "road_class": "secondary", "length_m": 850, "speed_limit": 40},
    {"id": "e04", "from": "N5", "to": "N6", "road_class": "secondary", "length_m": 850, "speed_limit": 40},
    {"id": "e05", "from": "N7", "to": "N8", "road_class": "residential", "length_m": 850, "speed_limit": 30},
    {"id": "e06", "from": "N8", "to": "N9", "road_class": "residential", "length_m": 850, "speed_limit": 30},
    # North-south streets
    {"id": "e07", "from": "N1", "to": "N4", "road_class": "secondary", "length_m": 550, "speed_limit": 40},
    {"id": "e08", "from": "N4", "to": "N7", "road_class": "secondary", "length_m": 550, "speed_limit": 40},
    {"id": "e09", "from": "N2", "to": "N5", "road_class": "primary", "length_m": 550, "speed_limit": 50},
    {"id": "e10", "from": "N5", "to": "N8", "road_class": "primary", "length_m": 550, "speed_limit": 50},
    {"id": "e11", "from": "N3", "to": "N6", "road_class": "secondary", "length_m": 550, "speed_limit": 40},
    {"id": "e12", "from": "N6", "to": "N9", "road_class": "secondary", "length_m": 550, "speed_limit": 40},
    # Highway bypass (one-way, higher speed)
    {"id": "e13", "from": "H1", "to": "N1", "road_class": "trunk", "length_m": 1200, "speed_limit": 80},
    {"id": "e14", "from": "N9", "to": "H2", "road_class": "trunk", "length_m": 1200, "speed_limit": 80},
    {"id": "e15", "from": "H1", "to": "H2", "road_class": "motorway", "length_m": 3500, "speed_limit": 100, "one_way": True},
]

# Build the network
summary = network.build_from_edges(edges, nodes)
print(f"Network built:")
print(f"  Nodes: {summary['nodes_created']}")
print(f"  Edges: {summary['edges_created']}")
print(f"  Connected: {summary['is_connected']}")
```

## Step 2: Get Network Statistics

```python
stats = network.get_statistics()

print(f"\nNetwork Statistics:")
print(f"  Graph nodes: {stats['node_count']}")
print(f"  Graph edges: {stats['edge_count']} (includes reverse edges)")
print(f"  Total length: {stats['total_length_km']:.1f} km")
print(f"  Density: {stats['density']:.4f}")
print(f"  Average in-degree: {stats['avg_in_degree']:.1f}")
print(f"  Road class distribution:")
for rc, count in stats['road_class_distribution'].items():
    print(f"    {rc}: {count} edges")
```

## Step 3: Compute Routes

```python
from geo_infer_transport import RoutingEngine

router = RoutingEngine(network=network, algorithm="dijkstra")

# Shortest time route: SW corner to NE corner
route_time = router.route(
    origin={"node_id": "N1"},
    destination={"node_id": "N9"},
    optimization="time",
)

print(f"\nShortest Time Route (N1 -> N9):")
print(f"  Path: {' -> '.join(route_time.path)}")
print(f"  Distance: {route_time.total_distance_m / 1000:.2f} km")
print(f"  Time: {route_time.total_time_s / 60:.1f} min")

# Shortest distance route
route_dist = router.route(
    origin={"node_id": "N1"},
    destination={"node_id": "N9"},
    optimization="distance",
)

print(f"\nShortest Distance Route (N1 -> N9):")
print(f"  Path: {' -> '.join(route_dist.path)}")
print(f"  Distance: {route_dist.total_distance_m / 1000:.2f} km")
print(f"  Time: {route_dist.total_time_s / 60:.1f} min")

# Highway bypass route
route_highway = router.route(
    origin={"node_id": "H1"},
    destination={"node_id": "H2"},
    optimization="time",
)

print(f"\nHighway Bypass (H1 -> H2):")
print(f"  Path: {' -> '.join(route_highway.path)}")
print(f"  Distance: {route_highway.total_distance_m / 1000:.2f} km")
print(f"  Time: {route_highway.total_time_s / 60:.1f} min")
```

## Step 4: Analyze Network Centrality

Find the most critical intersections in the network.

```python
# Betweenness centrality
betweenness = network.calculate_centrality(
    centrality_type="betweenness",
    weight="travel_time",
    top_n=5,
)

print(f"\nBetweenness Centrality (top 5):")
for node in betweenness["top_nodes"]:
    print(f"  {node['node_id']}: {node['centrality']:.4f}")

# Closeness centrality
closeness = network.calculate_centrality(
    centrality_type="closeness",
    weight="length",
    top_n=5,
)

print(f"\nCloseness Centrality (top 5):")
for node in closeness["top_nodes"]:
    print(f"  {node['node_id']}: {node['centrality']:.4f}")
```

## Step 5: Origin-Destination Matrix

```python
origins = [
    {"node_id": "N1", "id": "SW"},
    {"node_id": "N3", "id": "SE"},
    {"node_id": "N7", "id": "NW"},
]

destinations = [
    {"node_id": "N5", "id": "Center"},
    {"node_id": "N9", "id": "NE"},
    {"node_id": "H2", "id": "Hwy"},
]

od = router.calculate_matrix(origins, destinations, metric="time")

print(f"\nOD Matrix (travel time in seconds):")
print(f"  {'':>8}", end="")
for d in od["destinations"]:
    print(f"{d:>10}", end="")
print()

for i, row in enumerate(od["matrix"]):
    print(f"  {od['origins'][i]:>8}", end="")
    for val in row:
        print(f"{val:>10.0f}", end="")
    print()
```

## Step 6: Alternative Routes

```python
alternatives = router.find_alternatives(
    origin={"node_id": "N1"},
    destination={"node_id": "N9"},
    count=3,
    variation=0.3,
)

print(f"\nAlternative Routes (N1 -> N9): {len(alternatives)} found")
for i, alt in enumerate(alternatives):
    label = "Primary" if i == 0 else f"Alt {i}"
    print(f"  {label}: {' -> '.join(alt.path)} "
          f"({alt.total_distance_m/1000:.2f} km, {alt.total_time_s/60:.1f} min)")
```

## Key Takeaways

1. **Road hierarchy matters for routing**: The primary streets and highway bypass offer faster travel despite longer distances, because speed limits are higher.
2. **Centrality reveals vulnerability**: Nodes with high betweenness centrality are potential bottlenecks -- if they fail, the network becomes disconnected.
3. **OD matrices enable planning**: They show which areas are well-connected and which pairs require long travel times.

## Next Steps

- Add real road data from OpenStreetMap using `osmnx`.
- See the [Traffic Modeling Example](advanced_example.md) for congestion simulation.
- Integrate with GEO-INFER-SPACE for H3-based accessibility mapping.
