# GEO-INFER-TRANSPORT Documentation

GEO-INFER-TRANSPORT provides transportation network analysis, routing optimization, traffic modeling, and accessibility analysis for the GEO-INFER framework. It supports multi-modal networks (car, truck, bus, bicycle, pedestrian, rail, subway) and integrates graph-based analysis with spatial operations.

## Module Architecture

The module is organized around five core components:

| Component | Class | Purpose |
|-----------|-------|---------|
| Transport Network | `TransportNetwork` | Network topology construction, connectivity, and centrality analysis |
| Routing Engine | `RoutingEngine` | Multi-modal routing with Dijkstra, A*, and Bellman-Ford algorithms |
| Traffic Analyzer | `TrafficAnalyzer` | Traffic flow modeling, congestion detection, and forecasting |
| Accessibility | `AccessibilityAnalyzer` | Service area analysis and accessibility scoring |
| Transit Optimizer | `TransitOptimizer` | Transit network optimization and scheduling |

## Data Flow

```
Edge/Node Data (GeoDataFrame, OSM, GTFS)
        |
        v
TransportNetwork.build_from_edges()
        |
        +--> analyze_connectivity()     # Components, reachability, critical links
        +--> calculate_centrality()     # Betweenness, closeness, degree
        +--> get_statistics()           # Network summary metrics
        |
        v
RoutingEngine(network=...)
        |
        +--> route()                    # Single origin-destination path
        +--> optimize_route()           # Multi-stop TSP-like optimization
        +--> calculate_matrix()         # Origin-destination cost matrix
        +--> find_alternatives()        # Alternative route search
        |
        v
TrafficAnalyzer
        |
        +--> analyze_flow()             # Per-segment Level of Service
        +--> model_congestion()         # Network-wide BPR congestion model
        +--> simulate_traffic()         # Time-stepped traffic simulation
        +--> detect_incidents()         # Anomaly-based incident detection
        +--> forecast_traffic()         # EWMA-based traffic prediction
```

## Key Design Decisions

- The underlying graph is a `networkx.DiGraph`, supporting directed edges for one-way streets.
- Non-one-way edges automatically get reverse edges with identical attributes.
- Travel time is computed as `(length_m / 1000) / speed_limit_kmh * 3600` (seconds).
- Seven road classes are supported: motorway, trunk, primary, secondary, tertiary, residential, service, path.
- The routing engine defaults to Dijkstra but supports A* and Bellman-Ford.
- Traffic congestion uses the BPR (Bureau of Public Roads) function: `t = t0 * (1 + 0.15 * (V/C)^4)`.
- Level of Service (LOS) follows HCM A-F classification based on volume-to-capacity ratio.
- Traffic forecasting uses Exponentially Weighted Moving Average (EWMA) with linear trend and prediction intervals.
- Optional integration with GEO-INFER-LOG for emissions calculation and critical link analysis.

## Integration with Other Modules

- **GEO-INFER-SPACE**: H3 hexagonal indexing for accessibility and service area mapping.
- **GEO-INFER-LOG**: Supply chain and logistics integration, emissions estimation, critical link identification.
- **GEO-INFER-DATA**: Network data ingestion from OpenStreetMap, GTFS transit feeds.
- **GEO-INFER-TIME**: Temporal traffic pattern analysis and forecasting.
- **GEO-INFER-ACT**: Active Inference for adaptive routing and traffic management.
- **GEO-INFER-SIM**: Agent-based traffic simulation integration.
- **GEO-INFER-ECON**: Transport cost modeling and economic accessibility analysis.

## Quick Links

- [Getting Started](getting_started.md) -- installation, core concepts, first routing example
- [API Reference](api_reference.md) -- classes, methods, parameters, return types
- [Basic Example: Network Routing](examples/basic_example.md) -- load network, compute paths, visualize
- [Advanced Example: Traffic Modeling](examples/advanced_example.md) -- congestion simulation with demand prediction

## Package Structure

```
GEO-INFER-TRANSPORT/
  src/geo_infer_transport/
    __init__.py              # Exports 5 core classes
    core/
      network.py             # TransportNetwork, NetworkNode, NetworkEdge, RoadClass
      routing.py             # RoutingEngine, Route, RoutingAlgorithm
      traffic.py             # TrafficAnalyzer, TrafficCondition, FlowResult
      accessibility.py       # AccessibilityAnalyzer
      transit.py             # TransitOptimizer
  tests/
    unit/
    integration/
  docs/                      # This documentation
```

## Dependencies

Core dependency: `networkx` for graph algorithms. No heavy GIS dependencies required for basic operation. Optional dependencies include `geopandas` for spatial network data, `folium` for map visualization, and `osmnx` for OpenStreetMap network import.

## Version

Current version: `0.2.0`
