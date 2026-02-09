# GEO-INFER-ECON: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-ECON** module provides economic analysis capabilities for agents, enabling spatial economics, market analysis, and economic impact assessment in geospatial contexts.

## Agent Capabilities

### 1. Spatial Economics

```python
from geo_infer_econ import SpatialEconomist

# Analyze spatial economic patterns
economist = SpatialEconomist()

analysis = economist.analyze(
    region=metro_area,
    indicators=["gdp", "employment", "income"],
    spatial_units="census_tract")

print(f"Economic hotspots: {analysis.hotspots}")
print(f"Growth corridors: {analysis.growth_areas}")```

### 2. Market Analysis

```python
from geo_infer_econ import MarketAnalyzer

# Analyze real estate markets
market = MarketAnalyzer()

assessment = market.assess(
    area=neighborhood,
    property_type="residential",
    metrics=["price_trends", "inventory", "days_on_market"])

print(f"Median price: ${assessment.median_price}")
print(f"YoY change: {assessment.price_change}%")```

### 3. Economic Impact

```python
from geo_infer_econ import ImpactAnalyzer

# Assess economic impacts
impact = ImpactAnalyzer()

study = impact.analyze(
    project=new_development,
    methods=["input_output", "fiscal"],
    time_horizon=10)

print(f"Direct jobs: {study.direct_jobs}")
print(f"Total economic output: ${study.total_output}M")
print(f"Tax revenue: ${study.tax_revenue}M")```

### 4. Cost-Benefit Analysis

```python
from geo_infer_econ import CostBenefitAnalyzer

# Perform cost-benefit analysis
cba = CostBenefitAnalyzer()

result = cba.analyze(
    project=infrastructure_project,
    costs=project_costs,
    benefits=["travel_time", "safety", "emissions"],
    discount_rate=0.03)

print(f"NPV: ${result.npv}M")
print(f"BCR: {result.benefit_cost_ratio}")```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Spatial Economics** | ✅ Ready | Regional analysis |
| **Market Analysis** | ✅ Ready | Real estate, retail |
| **Impact Analysis** | ✅ Ready | Economic impacts |
| **Cost-Benefit** | ✅ Ready | Project evaluation |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **EconomicAdvisorAgent** | 🔮 High | Investment guidance |
| **MarketPredictorAgent** | 🔮 Medium | Price forecasting |

## Use Cases

### Site Selection

```python
from geo_infer_econ import SiteSelector

selector = SiteSelector()

sites = selector.find_optimal(
    business_type="retail",
    criteria={"population": 50000, "income": 75000},
    competitors=existing_stores)
```

---

This AGENTS.md documents how GEO-INFER-ECON provides economic capabilities for agents.

**Last Updated**: 2026-01-26
