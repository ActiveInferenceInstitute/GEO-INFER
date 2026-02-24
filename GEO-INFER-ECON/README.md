---
title: "GEO-INFER-ECON: Spatial Economics"
description: "Economic analysis, market assessment, and impact modeling in geospatial contexts"
purpose: "Provide economic analytical capabilities for spatial planning and decision making"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-24"
dependencies: ["SPACE", "DATA", "TIME"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-DATA", "GEO-INFER-TIME"]
tags: ["economics", "markets", "impact-analysis", "site-selection", "real-estate"]
difficulty: "Intermediate"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-ECON: Spatial Economics

## Overview

**GEO-INFER-ECON** provides spatial economic analysis:

- **Regional Economics**: GDP, employment, income analysis
- **Market Analysis**: Real estate, retail, commercial
- **Impact Assessment**: Economic and fiscal impact studies
- **Site Selection**: Optimal location analysis

## Features

### Regional Economic Analysis

```python
from geo_infer_econ import RegionalEconomist

# Analyze regional economy
economist = RegionalEconomist()

analysis = economist.analyze(
    region=metro_area,
    indicators=["gdp", "employment", "wages"],
    sectors=["tech", "healthcare", "manufacturing"]
)

print(f"GDP: ${analysis.gdp}B")
print(f"Growth sectors: {analysis.growing_sectors}")
```

### Market Analysis

```python
from geo_infer_econ import MarketAnalyzer

# Real estate market analysis
market = MarketAnalyzer()

assessment = market.assess(
    area=neighborhood,
    property_type="residential",
    metrics=["price", "inventory", "days_on_market"]
)

print(f"Median price: ${assessment.median_price}")
print(f"YoY change: {assessment.price_change}%")
```

### Economic Impact

```python
from geo_infer_econ import ImpactAnalyzer

# Assess project impact
impact = ImpactAnalyzer()

study = impact.analyze(
    project=new_development,
    method="input_output"
)

print(f"Jobs created: {study.total_jobs}")
print(f"Economic output: ${study.output}M")
print(f"Tax revenue: ${study.tax_revenue}M")
```

### Site Selection

```python
from geo_infer_econ import SiteSelector

# Find optimal business location
selector = SiteSelector()

sites = selector.find(
    business_type="retail",
    criteria={
        "population": {"min": 50000},
        "income": {"min": 75000},
        "competition": {"max": 3}
    }
)

print(f"Top sites: {sites[:5]}")
```

## Analysis Types

| Type | Application |
|------|-------------|
| **I/O Analysis** | Spending impacts |
| **Fiscal Impact** | Tax revenue |
| **CBA** | Project evaluation |
| **Econometrics** | Forecasting |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-SPACE** | Location analysis |
| **GEO-INFER-DATA** | Economic data |

## Installation

```bash
uv pip install -e "./GEO-INFER-ECON"
```

---

**Status**: Alpha

**Last Updated**: 2026-02-24
