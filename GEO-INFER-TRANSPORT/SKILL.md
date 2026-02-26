---
name: geo-infer-transport
description: Transportation network analysis and traffic modeling. Use when analyzing road networks, simulating traffic (BPR model), forecasting traffic (EWMA), computing emissions, or optimizing transport routes.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-math
    - geo-infer-time
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-TRANSPORT

## Instructions

### Core Capabilities

- **Traffic simulation**: BPR (Bureau of Public Roads) microsimulation with V/C ratios
- **Traffic forecasting**: EWMA model with trend estimation and confidence intervals
- **Network analysis**: Critical link identification, connectivity metrics
- **Emissions**: Transportation emissions calculation (integrates with LOG)
- **Route optimization**: Multi-criteria route selection

### Key Imports

```python
from geo_infer_transport.core.traffic import simulate_traffic, forecast_traffic
from geo_infer_transport.core.network import TransportNetwork
from geo_infer_transport.core.routing import RoutingEngine
```

## Examples

```python
from geo_infer_transport.core.traffic import simulate_traffic

demand = {"matrix": [[100, 50], [30, 80]]}
result = simulate_traffic(demand, simulation_hours=1, time_step_seconds=15)
print(f"Completed trips: {result['statistics']['completed_trips']}")
```

## Guidelines

- `simulate_traffic` uses real BPR delay function (not hardcoded)
- `forecast_traffic` uses EWMA + trend estimation (not fake cyclic variation)
- Emissions bridged from LOG module via optional import
- Test: `uv run python -m pytest GEO-INFER-TRANSPORT/tests/ -v`

### Integrations

- **LOG** → Emissions calculator and route optimization
- **ECON** → Transportation cost for trade flows
- **EMERGENCY** → Evacuation route planning
- **HEALTH** → Healthcare accessibility travel times
- **SPACE** → Road network spatial indexing
