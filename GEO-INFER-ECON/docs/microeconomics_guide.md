# Microeconomics Guide

## Introduction

This guide covers microeconomic analysis capabilities in GEO-INFER-ECON, focusing on individual market behavior and spatial microeconomics.

## Location Theory

### Central Place Theory

```python
from geo_infer_econ import CentralPlaceAnalyzer

# Analyze market areas
analyzer = CentralPlaceAnalyzer()

hierarchy = analyzer.identify_hierarchy(
    settlements=cities,
    services=commercial_data
)
```

### Bid-Rent Model

```python
from geo_infer_econ import BidRentModel

# Land value analysis
model = BidRentModel(cbd_location=downtown)

values = model.predict(
    locations=parcels,
    factors=["distance_cbd", "accessibility"]
)
```

## Consumer Behavior

### Trade Area Analysis

```python
from geo_infer_econ import TradeAreaAnalyzer

# Define retail trade areas
trade = TradeAreaAnalyzer()

area = trade.huff_model(
    stores=retail_locations,
    attractiveness="square_footage",
    friction=2.0
)
```

### Demand Estimation

```python
# Estimate consumer demand
demand = trade.estimate_demand(
    population=demographics,
    income=income_data,
    elasticity=-0.5
)
```

## Market Analysis

### Competition Analysis

```python
from geo_infer_econ import CompetitionAnalyzer

comp = CompetitionAnalyzer()

gaps = comp.find_gaps(
    existing=competitor_locations,
    demand=population_centers
)
```

## Key Concepts

| Concept | Application |
|---------|-------------|
| Trade Areas | Retail catchment |
| Bid-Rent | Land values |
| Agglomeration | Clustering effects |
| Accessibility | Service coverage |

---

**Last Updated**: 2026-02-24
