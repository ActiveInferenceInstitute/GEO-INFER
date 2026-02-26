---
name: geo-infer-econ
description: Geospatial economics and bioregional market modeling. Use when analyzing spatial economic patterns, bioregional markets, location-based pricing, call auctions, or supply-demand modeling with geographic context.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-time
    - geo-infer-bayes
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-ECON

## Instructions

### Core Capabilities

- **Bioregional markets**: Call auction mechanics, location multipliers
- **Spatial economics**: Geographic price modeling, trade flow analysis
- **Supply-demand**: Spatially-aware supply chain economics
- **Impact assessment**: Economic impact of spatial interventions
- **Logistics integration**: Bridge to LOG module for supply chain analysis

### Key Imports

```python
from geo_infer_econ.bioregional.bioregional_markets import BioregionalMarket
from geo_infer_econ.core.spatial_economics import SpatialEconomicModel
from geo_infer_econ.integrations.logistics_integration import LogisticsEconomicAnalyzer
```

## Examples

```python
from geo_infer_econ.bioregional.bioregional_markets import BioregionalMarket

market = BioregionalMarket(region="pacific_northwest")
market.add_bid(buyer="co_op_a", price=12.50, quantity=100, location=(45.5, -122.6))
market.add_ask(seller="farm_b", price=11.00, quantity=80, location=(45.3, -122.8))
result = market.clear_auction()
print(f"Clearing price: ${result.price:.2f}, Volume: {result.volume}")
```

```python
from geo_infer_econ.integrations.logistics_integration import LogisticsEconomicAnalyzer

analyzer = LogisticsEconomicAnalyzer()
cost = analyzer.compute_transport_cost(
    origin=(45.5, -122.6), destination=(47.6, -122.3),
    cargo_tonnes=50
)
print(f"Transport cost: ${cost.total:.2f}")
```

## Guidelines

- Call auction and location multiplier are real implementations
- Logistics integration bridges ECON↔LOG modules
- Logger used instead of print() for all output
- Test: `uv run python -m pytest GEO-INFER-ECON/tests/ -v`

### Integrations

- **LOG** → Supply chain logistics cost modeling
- **AG** → Agricultural commodity market analysis
- **TRANSPORT** → Transportation cost for trade flows
- **RISK** → Economic risk and insurance modeling
- **SPACE** → Location multiplier spatial analysis
