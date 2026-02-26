# Basic Example: Forest Carbon Stock Estimation

This example demonstrates the complete workflow from forest cover data through biomass estimation to carbon stock calculation and credit valuation.

## Overview

The workflow has five steps:

1. Load or generate forest cover and tree density data.
2. Estimate above-ground biomass using `ForestInventory`.
3. Convert biomass to carbon stock using `CarbonSequestrationModeler`.
4. Estimate annual carbon sequestration from growth rates.
5. Calculate the monetary value of carbon credits.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-FOREST
```

## Step 1: Prepare Forest Cover Data

In production, this data comes from satellite-derived land cover products (e.g., Hansen Global Forest Change, Copernicus Tree Cover Density). Here we create representative data for Del Norte County, California -- a heavily forested coastal region.

```python
import numpy as np
import xarray as xr

# Del Norte County approximate bounds
lat = np.linspace(41.46, 42.01, 30)
lon = np.linspace(-124.41, -123.54, 30)
coords = {"lat": lat, "lon": lon}

# Forest cover: high in mountains (east), lower near coast (west)
lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")
coastal_effect = np.clip((lon_grid + 124.0) * 5, 0, 1)
forest_cover = xr.DataArray(
    np.clip(60 + 30 * coastal_effect + np.random.normal(0, 5, (30, 30)), 0, 100),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "percent", "source": "simulated"},
)

# Tree density: old-growth redwood areas have lower density but larger trees
tree_density = xr.DataArray(
    np.random.uniform(150, 600, (30, 30)),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "trees/ha"},
)

print(f"Forest cover range: {float(forest_cover.min()):.0f}% - {float(forest_cover.max()):.0f}%")
print(f"Mean tree density: {float(tree_density.mean()):.0f} trees/ha")
```

## Step 2: Estimate Biomass

```python
from geo_infer_forest.core.forest_inventory import ForestInventory

inventory = ForestInventory()

# Estimate above-ground biomass
biomass = inventory.estimate_biomass(forest_cover, tree_density)

print(f"\nBiomass Statistics:")
print(f"  Mean: {float(biomass.mean()):.1f} t/ha")
print(f"  Min:  {float(biomass.min()):.1f} t/ha")
print(f"  Max:  {float(biomass.max()):.1f} t/ha")
print(f"  Std:  {float(biomass.std()):.1f} t/ha")

# Calculate forest area
forest_area = inventory.calculate_forest_area(forest_cover)
total_area_km2 = float(forest_area.sum())
print(f"\nTotal forest area: {total_area_km2:.1f} km2")
```

## Step 3: Convert to Carbon Stock

```python
from geo_infer_forest.core.carbon_sequestration import CarbonSequestrationModeler

modeler = CarbonSequestrationModeler()

# Carbon stock = biomass * 0.5
carbon_stock = modeler.calculate_carbon_stock(biomass)

print(f"\nCarbon Stock:")
print(f"  Mean: {float(carbon_stock.mean()):.1f} tC/ha")
print(f"  Total region: {float(carbon_stock.sum()):.0f} tC")

# Convert to CO2 equivalent for context
co2_eq = carbon_stock * 3.67
print(f"  CO2 equivalent: {float(co2_eq.sum()):.0f} tCO2-eq")
```

## Step 4: Estimate Annual Sequestration

Temperate coastal forests typically sequester 2-6 tC/ha/year depending on age, species composition, and climate.

```python
# Simulate annual biomass growth: 2-5% of standing biomass
growth_rate = np.random.uniform(0.02, 0.05, biomass.shape)
biomass_growth = xr.DataArray(
    biomass.values * growth_rate,
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "t/ha/year"},
)

# Calculate carbon sequestration rate
sequestration_rate = modeler.estimate_sequestration_rate(biomass_growth)

print(f"\nAnnual Carbon Sequestration:")
print(f"  Mean: {float(sequestration_rate.mean()):.2f} tC/ha/year")
print(f"  Total: {float(sequestration_rate.sum()):.0f} tC/year")
```

## Step 5: Calculate Carbon Credit Value

```python
# Area per cell (approximately 0.1 km2 = 10 ha at this resolution)
cell_area_ha = xr.DataArray(
    np.full((30, 30), 10.0),
    dims=["lat", "lon"],
    coords=coords,
)

# Carbon credit value at $50/tCO2
credit_value = modeler.calculate_carbon_credits(
    carbon_sequestration=sequestration_rate,
    area=cell_area_ha,
    price_per_ton=50.0,
)

total_credit = float(credit_value.sum())
print(f"\nCarbon Credit Value (at $50/tCO2):")
print(f"  Total annual value: ${total_credit:,.0f}")
print(f"  Per hectare: ${float(credit_value.mean() / 10.0):,.0f}/ha/year")

# Sensitivity: also calculate at $25 and $100/tCO2
for price in [25.0, 100.0]:
    val = modeler.calculate_carbon_credits(sequestration_rate, cell_area_ha, price)
    print(f"  At ${price:.0f}/tCO2: ${float(val.sum()):,.0f}/year")
```

## Step 6: Identify High-Value Carbon Cells

Find the top 10% of cells by carbon credit value for prioritized conservation.

```python
# Flatten and rank
values = credit_value.values.flatten()
threshold = np.percentile(values, 90)

high_value_mask = credit_value >= threshold
n_high_value = int(high_value_mask.sum())
high_value_total = float(credit_value.where(high_value_mask, 0).sum())

print(f"\nHigh-Value Cells (top 10%):")
print(f"  Count: {n_high_value} cells")
print(f"  Combined value: ${high_value_total:,.0f}/year")
print(f"  Fraction of total: {high_value_total / total_credit:.1%}")
```

## Expected Results

For Del Norte County with its dense old-growth and second-growth forests:

- Mean biomass: 40-70 t/ha (lower with density normalization).
- Carbon stock: 20-35 tC/ha.
- Sequestration rate: 0.5-1.5 tC/ha/year.
- Carbon credit value: significant given the large forested area.

These values are conservative compared to measured data for coastal redwood forests, which can exceed 500 t/ha biomass. The simplified allometric model uses linear scaling from cover percentage rather than species-specific equations.

## Next Steps

- Use real satellite-derived forest cover from GEO-INFER-DATA to replace simulated data.
- Integrate with GEO-INFER-SPACE for H3-indexed spatial aggregation.
- Combine with the deforestation detection workflow to track carbon loss over time.
- See the [Advanced Example](advanced_example.md) for habitat connectivity analysis.
