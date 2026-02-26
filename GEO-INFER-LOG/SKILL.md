---
name: geo-infer-log
description: Logistics optimization including route planning, fleet management, delivery scheduling, and supply chain modeling. Use when optimizing delivery routes, managing fleets, analyzing supply chain resilience, or computing emissions from transportation.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-time
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-LOG

## Instructions

### Core Capabilities

- **Delivery**: KMeans clustering, Voronoi tessellation, Haversine service areas
- **Transport**: Dijkstra routing, betweenness centrality, max-flow, emissions
- **Supply chain**: PuLP MILP optimization, articulation points, EOQ, Monte Carlo
- **Fleet management**: Vehicle routing, real-time tracking, ETA calculation
- **Observability**: Enhanced structured logging with spatial context

### Key Imports

```python
from geo_infer_log import LastMileRouter, DeliveryScheduler, ServiceAreaAnalyzer
from geo_infer_log import EmissionsCalculator, TransportationNetworkAnalyzer
from geo_infer_log import SupplyChainModel, FacilityLocator, InventoryManager
from geo_infer_log import EnhancedLogger, PerformanceMetrics
```

All logistics classes are lazy-loaded via `__getattr__` — zero cost until accessed.

## Examples

```python
from geo_infer_log import FacilityLocator

locator = FacilityLocator(n_facilities=5)
locations = locator.locate_facilities(demand_points)
coverage = locator.analyze_coverage(locations, demand_points)
```

## Guidelines

- All implementations are real (KMeans, Dijkstra, PuLP) — no placeholders
- Submodules (`api`, `core`, `models`, `utils`) lazy-loaded on attribute access
- Logger used for all output — no `print()` statements
- Test: `uv run python -m pytest GEO-INFER-LOG/tests/ -v`

### Integrations

- **ECON** → Logistics cost feeding economic models
- **TRANSPORT** → Route optimization and emissions calculation
- **RISK** → Supply chain risk and disruption modeling
- **SPACE** → H3-based delivery zone tessellation
- **OPS** → Logistics operation monitoring
