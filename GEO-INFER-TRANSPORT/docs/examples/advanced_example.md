# Advanced Example: Traffic Modeling and Demand Prediction

This example demonstrates traffic flow analysis, network-wide congestion modeling, time-stepped simulation, incident detection, and traffic forecasting using Active Inference-inspired adaptive routing.

## Overview

The workflow covers:

1. Analyze traffic flow on individual road segments.
2. Model congestion across a network using the BPR function.
3. Run a time-stepped traffic simulation.
4. Detect incidents from speed anomalies.
5. Forecast future traffic volumes.
6. Demonstrate adaptive routing with real-time traffic updates.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-TRANSPORT
```

## Step 1: Traffic Flow Analysis per Segment

Analyze traffic conditions on individual road segments using observed counts.

```python
from geo_infer_transport import TrafficAnalyzer

traffic = TrafficAnalyzer(model_type="bpr", time_resolution="15min")

# Define road segments with capacity
segments = {
    "main_st_n": {"id": "main_st_n", "speed_limit": 50, "capacity": 1800, "lanes": 2},
    "main_st_s": {"id": "main_st_s", "speed_limit": 50, "capacity": 1800, "lanes": 2},
    "highway_101": {"id": "highway_101", "speed_limit": 100, "capacity": 4000, "lanes": 4},
    "elm_ave": {"id": "elm_ave", "speed_limit": 30, "capacity": 800, "lanes": 1},
    "oak_blvd": {"id": "oak_blvd", "speed_limit": 40, "capacity": 1200, "lanes": 2},
}

# Simulated 15-minute count data for peak hour
import numpy as np
np.random.seed(42)

count_data = {
    "main_st_n": [
        {"count": 380, "speed_kmh": 35},
        {"count": 420, "speed_kmh": 32},
        {"count": 445, "speed_kmh": 28},
        {"count": 410, "speed_kmh": 30},
    ],
    "main_st_s": [
        {"count": 350, "speed_kmh": 40},
        {"count": 365, "speed_kmh": 38},
        {"count": 390, "speed_kmh": 35},
        {"count": 370, "speed_kmh": 37},
    ],
    "highway_101": [
        {"count": 950, "speed_kmh": 95},
        {"count": 980, "speed_kmh": 92},
        {"count": 1020, "speed_kmh": 88},
        {"count": 990, "speed_kmh": 90},
    ],
    "elm_ave": [
        {"count": 80, "speed_kmh": 28},
        {"count": 75, "speed_kmh": 29},
        {"count": 90, "speed_kmh": 26},
        {"count": 85, "speed_kmh": 27},
    ],
    "oak_blvd": [
        {"count": 250, "speed_kmh": 35},
        {"count": 270, "speed_kmh": 33},
        {"count": 280, "speed_kmh": 31},
        {"count": 260, "speed_kmh": 34},
    ],
}

print("Per-Segment Flow Analysis (Peak Hour)")
print("-" * 70)
print(f"{'Segment':<15}{'Volume':>8}{'Speed':>8}{'Density':>10}{'LOS':>6}")
print("-" * 70)

flow_results = {}
for seg_id, seg in segments.items():
    flow = traffic.analyze_flow(seg, count_data[seg_id], time_period="peak")
    flow_results[seg_id] = flow
    print(f"{seg_id:<15}{flow.volume:>8}{flow.speed:>8.1f}{flow.density:>10.1f}{flow.level_of_service:>6}")
```

## Step 2: Network-Wide Congestion Model

Apply the BPR congestion function across all segments simultaneously.

```python
# Network flows (vehicles per hour)
network_flows = {seg_id: flow.volume for seg_id, flow in flow_results.items()}

# Capacity per segment
capacity_data = {seg_id: seg["capacity"] for seg_id, seg in segments.items()}

# Model congestion
congestion = traffic.model_congestion(
    network_flows=network_flows,
    capacity_data=capacity_data,
    algorithm="bpr",
)

print(f"\nNetwork Congestion Summary:")
print(f"  Total segments: {congestion['summary']['total_segments']}")
print(f"  Congested segments: {congestion['summary']['congested_segments']}")
print(f"  Average delay factor: {congestion['summary']['average_delay_factor']:.3f}")

print(f"\nPer-Segment Congestion:")
print(f"{'Segment':<15}{'V/C':>8}{'Delay':>8}{'Condition':>14}")
print("-" * 45)
for seg in congestion["segments"]:
    print(f"{seg['segment_id']:<15}{seg['vc_ratio']:>8.3f}"
          f"{seg['delay_factor']:>8.3f}{seg['condition']:>14}")
```

## Step 3: Traffic Simulation

Run a time-stepped simulation to model traffic flow evolution over one hour.

```python
from geo_infer_transport import TransportNetwork, RoutingEngine

# Build a simple network for simulation
sim_network = TransportNetwork()
sim_edges = [
    {"id": "e1", "from": "A", "to": "B", "road_class": "primary", "length_m": 2000, "speed_limit": 60},
    {"id": "e2", "from": "B", "to": "C", "road_class": "primary", "length_m": 1500, "speed_limit": 50},
    {"id": "e3", "from": "A", "to": "C", "road_class": "secondary", "length_m": 3000, "speed_limit": 40},
]
sim_network.build_from_edges(sim_edges)

# Create OD demand matrix
router = RoutingEngine(network=sim_network)
od = router.calculate_matrix(
    origins=[{"node_id": "A", "id": "A"}],
    destinations=[{"node_id": "C", "id": "C"}],
)

# Run 1-hour simulation with 60-second time steps
simulation = traffic.simulate_traffic(
    network=sim_network,
    demand_matrix=od,
    simulation_hours=1,
    time_step_seconds=60,
)

print(f"\nTraffic Simulation:")
print(f"  Duration: {simulation['duration_hours']} hour")
print(f"  Time step: {simulation['time_step_seconds']} seconds")
print(f"  Total steps: {simulation['total_steps']}")
print(f"  Total trips: {simulation['statistics']['total_trips']}")
print(f"  Completed trips: {simulation['statistics']['completed_trips']}")

# Show first 10 and last 5 steps
print(f"\n{'Step':>6}{'Time':>8}{'Vehicles':>10}{'Speed':>8}{'V/C':>8}{'Congestion':>14}")
print("-" * 54)
for result in simulation["results"][:10]:
    print(f"{result['step']:>6}{result['time_seconds']:>8}"
          f"{result['vehicles_in_network']:>10}"
          f"{result['average_speed_kmh']:>8.1f}{result['vc_ratio']:>8.3f}"
          f"{result['congestion_level']:>14}")
if len(simulation["results"]) > 15:
    print(f"  ... ({len(simulation['results']) - 15} steps omitted)")
    for result in simulation["results"][-5:]:
        print(f"{result['step']:>6}{result['time_seconds']:>8}"
              f"{result['vehicles_in_network']:>10}"
              f"{result['average_speed_kmh']:>8.1f}{result['vc_ratio']:>8.3f}"
              f"{result['congestion_level']:>14}")
```

## Step 4: Incident Detection

Detect traffic incidents by comparing current conditions to historical baselines.

```python
# Historical baseline speeds
historical = {
    "main_st_n": {"speed": 45},
    "main_st_s": {"speed": 42},
    "highway_101": {"speed": 95},
    "elm_ave": {"speed": 28},
    "oak_blvd": {"speed": 38},
}

# Current conditions (main_st_n has significant speed drop)
current = {
    "main_st_n": {"speed": 18},   # 60% drop -- likely incident
    "main_st_s": {"speed": 38},
    "highway_101": {"speed": 88},
    "elm_ave": {"speed": 25},
    "oak_blvd": {"speed": 34},
}

incidents = traffic.detect_incidents(
    current_data=current,
    historical_baseline=historical,
    threshold=0.3,
)

print(f"\nIncident Detection:")
print(f"  Incidents found: {len(incidents)}")
for inc in incidents:
    print(f"  [{inc['severity'].upper()}] {inc['segment_id']}: "
          f"speed {inc['current_speed']} km/h (expected {inc['expected_speed']} km/h), "
          f"deviation {inc['deviation']:.0%}")
```

## Step 5: Traffic Forecasting

Predict traffic volumes for the next hour using EWMA-based forecasting.

```python
# Historical 15-minute volume counts (last 3 hours = 12 intervals)
historical_volumes = [
    {"volume": 1200, "timestamp": "07:00"},
    {"volume": 1350, "timestamp": "07:15"},
    {"volume": 1500, "timestamp": "07:30"},
    {"volume": 1650, "timestamp": "07:45"},
    {"volume": 1750, "timestamp": "08:00"},
    {"volume": 1800, "timestamp": "08:15"},
    {"volume": 1820, "timestamp": "08:30"},
    {"volume": 1780, "timestamp": "08:45"},
    {"volume": 1700, "timestamp": "09:00"},
    {"volume": 1600, "timestamp": "09:15"},
    {"volume": 1450, "timestamp": "09:30"},
    {"volume": 1350, "timestamp": "09:45"},
]

forecast = traffic.forecast_traffic(
    historical_data=historical_volumes,
    forecast_horizon="1h",
    model="arima",
)

print(f"\nTraffic Forecast (next 1 hour):")
print(f"  Model: EWMA (alpha={forecast['parameters']['alpha']})")
print(f"  Trend: {forecast['parameters']['trend']:.1f} veh/interval")
print(f"\n{'Offset':>8}{'Predicted':>10}{'Low 95%':>10}{'High 95%':>10}")
print("-" * 38)
for f in forecast["forecasts"]:
    print(f"{f['time_offset_minutes']:>6}min{f['predicted_volume']:>10}"
          f"{f['confidence_lower']:>10}{f['confidence_upper']:>10}")
```

## Step 6: Adaptive Routing with Real-Time Traffic

Demonstrate how traffic data feeds back into routing decisions.

```python
# Build a network with multiple route options
adaptive_net = TransportNetwork()
adaptive_net.build_from_edges([
    {"id": "fast", "from": "Start", "to": "End", "road_class": "primary", "length_m": 5000, "speed_limit": 60},
    {"id": "alt1", "from": "Start", "to": "Mid", "road_class": "secondary", "length_m": 3000, "speed_limit": 40},
    {"id": "alt2", "from": "Mid", "to": "End", "road_class": "secondary", "length_m": 3000, "speed_limit": 40},
])

adaptive_router = RoutingEngine(
    network=adaptive_net,
    algorithm="dijkstra",
    real_time_traffic=True,
)

# Route without traffic
route_free = adaptive_router.route(
    origin={"node_id": "Start"},
    destination={"node_id": "End"},
    optimization="time",
)
print(f"\nFree-flow route: {' -> '.join(route_free.path)} ({route_free.total_time_s/60:.1f} min)")

# Simulate incident on direct route: 3x delay
adaptive_router.update_traffic({"fast": 3.0, "fast_rev": 3.0})

# Route with traffic -- should prefer alternative
route_traffic = adaptive_router.route(
    origin={"node_id": "Start"},
    destination={"node_id": "End"},
    optimization="time",
)
print(f"With incident:   {' -> '.join(route_traffic.path)} ({route_traffic.total_time_s/60:.1f} min)")

# Clear incident
adaptive_router.update_traffic({"fast": 1.0, "fast_rev": 1.0})
route_cleared = adaptive_router.route(
    origin={"node_id": "Start"},
    destination={"node_id": "End"},
    optimization="time",
)
print(f"After clearing:  {' -> '.join(route_cleared.path)} ({route_cleared.total_time_s/60:.1f} min)")
```

## Key Takeaways

1. **BPR function captures nonlinear congestion**: Delay increases gently at low V/C ratios but explodes near capacity. This matches real-world observations.
2. **Simulation reveals dynamics**: Static analysis misses the buildup and dissipation of congestion over time. The simulation shows how vehicles accumulate and drain.
3. **Incident detection is threshold-sensitive**: Too low a threshold produces false positives from normal variation. Too high misses real incidents.
4. **Forecasting requires sufficient history**: The EWMA model needs at least 3 historical points to estimate trend. More data produces tighter confidence intervals.
5. **Adaptive routing closes the loop**: Real-time traffic feeds back into route choice, enabling the system to adapt to changing conditions -- a core principle of Active Inference.

## Next Steps

- Integrate with GEO-INFER-ACT for full Active Inference-based traffic management.
- Use GEO-INFER-SIM for agent-based microsimulation with individual vehicle behavior.
- Connect to GEO-INFER-IOT for real sensor data feeds instead of synthetic counts.
- Apply GEO-INFER-TIME for seasonal and day-of-week traffic pattern decomposition.
