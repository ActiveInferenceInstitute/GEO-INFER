# Advanced Example: Fisheries Stock Assessment with MPA Effectiveness

This example demonstrates a complete fisheries analysis workflow combining spatial CPUE mapping, habitat suitability modeling, MPA network design, and effectiveness evaluation.

## Overview

The workflow covers:

1. Generate spatial catch and effort data for a fishery.
2. Compute Catch Per Unit Effort (CPUE) as a stock density proxy.
3. Model habitat suitability from environmental variables.
4. Design an MPA network targeting biodiversity hotspots.
5. Evaluate MPA effectiveness through spillover and CPUE trends.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-MARINE
```

## Step 1: Generate Fishery Data

Create synthetic catch and effort data for a bottom trawl fishery over a continental shelf region.

```python
import numpy as np
import xarray as xr

np.random.seed(42)

# Define shelf region: 25x25 grid covering ~250 km of coastline
lat = np.linspace(42.0, 44.0, 25)
lon = np.linspace(-125.5, -124.0, 25)
coords = {"lat": lat, "lon": lon}
lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")

# Bathymetry: deeper offshore (west)
depth = xr.DataArray(
    np.clip(200 * (125.5 + lon_grid) / 1.5 + np.random.normal(0, 10, (25, 25)), 10, 500),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "meters"},
)

# Fish abundance pattern: peak at 80-150m depth
abundance_factor = np.exp(-0.5 * ((depth.values - 120) / 40) ** 2)

# Catch data (kg per haul)
catch = xr.DataArray(
    np.clip(500 * abundance_factor + np.random.normal(0, 50, (25, 25)), 0, 1000),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "kg/haul"},
)

# Effort data (hours trawled)
effort = xr.DataArray(
    np.random.uniform(2, 12, (25, 25)),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "hours"},
)

print(f"Catch range: {float(catch.min()):.0f} - {float(catch.max()):.0f} kg/haul")
print(f"Mean effort: {float(effort.mean()):.1f} hours")
print(f"Depth range: {float(depth.min()):.0f} - {float(depth.max()):.0f} m")
```

## Step 2: Compute CPUE Index

CPUE (Catch Per Unit Effort) serves as a relative index of stock abundance.

```python
# Calculate CPUE (kg per hour)
cpue = catch / effort
cpue_standardized = cpue / float(cpue.max())

print(f"\nCPUE Analysis:")
print(f"  Mean CPUE: {float(cpue.mean()):.1f} kg/hr")
print(f"  Max CPUE: {float(cpue.max()):.1f} kg/hr")
print(f"  Min CPUE: {float(cpue.min()):.1f} kg/hr")
print(f"  CV: {float(cpue.std() / cpue.mean()):.2f}")

# Identify high-CPUE cells (top 25%)
cpue_threshold = float(cpue.quantile(0.75))
hotspots = cpue > cpue_threshold
print(f"  High-CPUE threshold: {cpue_threshold:.1f} kg/hr")
print(f"  Hotspot cells: {int(hotspots.sum())} ({int(hotspots.sum()) / cpue.size:.1%})")
```

## Step 3: Habitat Suitability Model

Combine environmental variables to model species habitat preferences.

```python
# Sea Surface Temperature (seasonal composite)
sst = xr.DataArray(
    12.0 + 2.0 * (lat_grid - 42) / 2.0 + np.random.normal(0, 0.3, (25, 25)),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "degrees C"},
)

# Bottom substrate type (soft = 1, hard = 0)
substrate = xr.DataArray(
    (np.random.random((25, 25)) > 0.4).astype(float),
    dims=["lat", "lon"],
    coords=coords,
)

# Habitat suitability index (HSI)
# Optimal: depth 80-150m, SST 12-14 C, soft substrate
depth_suitability = np.exp(-0.5 * ((depth.values - 120) / 40) ** 2)
sst_suitability = np.exp(-0.5 * ((sst.values - 13) / 1.5) ** 2)
substrate_suitability = substrate.values * 0.7 + 0.3  # Soft preferred but not required

hsi = xr.DataArray(
    depth_suitability * sst_suitability * substrate_suitability,
    dims=["lat", "lon"],
    coords=coords,
)

print(f"\nHabitat Suitability Index:")
print(f"  Mean HSI: {float(hsi.mean()):.3f}")
print(f"  Prime habitat (HSI > 0.5): {int((hsi > 0.5).sum())} cells")
print(f"  Correlation CPUE vs HSI: {np.corrcoef(cpue.values.flatten(), hsi.values.flatten())[0,1]:.3f}")
```

## Step 4: Design MPA Network

Use the `MarineSpatialPlanner` to designate an MPA network based on combined biodiversity and habitat scores.

```python
from geo_infer_marine.core.marine_spatial_planning import MarineSpatialPlanner

planner = MarineSpatialPlanner()

# Biodiversity proxy: combine HSI with species richness indicator
species_richness = xr.DataArray(
    np.clip(hsi.values * 0.6 + np.random.uniform(0.1, 0.4, (25, 25)), 0, 1),
    dims=["lat", "lon"],
    coords=coords,
)

# Threat: fishing pressure (normalized effort)
fishing_threat = effort / float(effort.max())

# Design MPA network: 30% coverage
mpa = planner.design_mpa_network(
    biodiversity_data=species_richness,
    threat_data=fishing_threat,
    target_coverage=0.30,
)

mpa_mask = mpa["mpa_mask"]
coverage = float(mpa["coverage"])

print(f"\nMPA Network Design:")
print(f"  Coverage: {coverage:.1%}")
print(f"  MPA cells: {int(mpa_mask.sum())}")
print(f"  Mean HSI inside MPA: {float(hsi.where(mpa_mask).mean()):.3f}")
print(f"  Mean HSI outside MPA: {float(hsi.where(~mpa_mask).mean()):.3f}")
print(f"  Mean CPUE inside MPA: {float(cpue.where(mpa_mask).mean()):.1f} kg/hr")
print(f"  Mean CPUE outside MPA: {float(cpue.where(~mpa_mask).mean()):.1f} kg/hr")
```

## Step 5: Evaluate MPA Effectiveness

Simulate a 10-year trajectory to assess stock recovery inside the MPA and spillover to adjacent fishing grounds.

```python
# Simulate stock dynamics
years = 10
growth_rate = 0.15  # 15% annual population growth when unfished
mortality_rate = 0.25  # Fishing mortality outside MPA
spillover_rate = 0.10  # 10% annual emigration from MPA to adjacent cells

biomass_inside = np.zeros(years + 1)
biomass_outside = np.zeros(years + 1)
biomass_inside[0] = float(cpue.where(mpa_mask).mean())
biomass_outside[0] = float(cpue.where(~mpa_mask).mean())

for yr in range(years):
    # Inside MPA: growth only (no fishing), some emigration
    biomass_inside[yr + 1] = biomass_inside[yr] * (1 + growth_rate - spillover_rate)

    # Outside MPA: growth, fishing mortality, immigration from MPA
    spillover = biomass_inside[yr] * spillover_rate * (coverage / (1 - coverage))
    biomass_outside[yr + 1] = (
        biomass_outside[yr] * (1 + growth_rate - mortality_rate) + spillover
    )

print(f"\n10-Year MPA Effectiveness Simulation:")
print(f"{'Year':>6}{'Inside MPA':>14}{'Outside MPA':>14}{'Ratio':>10}")
print("-" * 44)
for yr in range(0, years + 1, 2):
    ratio = biomass_inside[yr] / biomass_outside[yr] if biomass_outside[yr] > 0 else 0
    print(f"{yr:>6}{biomass_inside[yr]:>14.1f}{biomass_outside[yr]:>14.1f}{ratio:>10.2f}")

recovery_pct = (biomass_inside[-1] - biomass_inside[0]) / biomass_inside[0] * 100
spillover_pct = (biomass_outside[-1] - biomass_outside[0]) / biomass_outside[0] * 100

print(f"\n  Inside MPA recovery: +{recovery_pct:.0f}%")
print(f"  Outside MPA change (spillover effect): +{spillover_pct:.0f}%")
```

## Step 6: Spawning Area Identification

Identify potential spawning aggregation sites based on habitat conditions and seasonal CPUE peaks.

```python
# Spawning criteria: high HSI + moderate depth (80-120m) + warm SST
spawning_depth = (depth > 80) & (depth < 120)
spawning_sst = sst > 12.5
spawning_habitat = hsi > 0.5

spawning_areas = spawning_depth & spawning_sst & spawning_habitat
spawning_in_mpa = spawning_areas & mpa_mask

print(f"\nSpawning Area Analysis:")
print(f"  Total spawning cells: {int(spawning_areas.sum())}")
print(f"  Spawning cells in MPA: {int(spawning_in_mpa.sum())}")
print(f"  Protection rate: {int(spawning_in_mpa.sum()) / max(int(spawning_areas.sum()), 1):.1%}")

if int(spawning_in_mpa.sum()) / max(int(spawning_areas.sum()), 1) < 0.5:
    print("  WARNING: Less than 50% of spawning habitat is protected.")
    print("  Consider expanding MPA boundaries to cover spawning aggregation sites.")
```

## Step 7: Summary Report

```python
print("\n" + "=" * 60)
print("FISHERIES STOCK ASSESSMENT SUMMARY")
print("=" * 60)
print(f"  Study area: {lat.min():.1f}-{lat.max():.1f}N, {lon.min():.1f}-{lon.max():.1f}W")
print(f"  Grid size: {len(lat)} x {len(lon)} cells")
print(f"  Depth range: {float(depth.min()):.0f}-{float(depth.max()):.0f} m")
print(f"  Mean CPUE: {float(cpue.mean()):.1f} kg/hr")
print(f"  CPUE hotspots: {int(hotspots.sum())} cells")
print(f"  Habitat quality (mean HSI): {float(hsi.mean()):.3f}")
print(f"  MPA coverage: {coverage:.1%}")
print(f"  10-yr stock recovery (MPA): +{recovery_pct:.0f}%")
print(f"  10-yr spillover benefit: +{spillover_pct:.0f}%")
print(f"  Spawning area protection: {int(spawning_in_mpa.sum()) / max(int(spawning_areas.sum()), 1):.0%}")
```

## Key Takeaways

1. **CPUE correlates with habitat**: The spatial CPUE pattern strongly tracks the habitat suitability model, validating both approaches.
2. **MPA design captures biodiversity and fisheries co-benefits**: Priority-based MPA selection preferentially includes high-CPUE and high-HSI cells.
3. **Spillover is real but slow**: Benefits to adjacent fishing grounds accumulate over years and depend on the emigration rate and MPA-to-fishing-area ratio.
4. **Spawning protection is critical**: MPAs that miss spawning aggregation sites provide reduced recruitment benefits regardless of adult stock recovery.

## Next Steps

- Integrate with GEO-INFER-TIME for seasonal CPUE trend analysis.
- Use GEO-INFER-DATA for real fisheries observer data and satellite AIS vessel tracking.
- Combine with GEO-INFER-ECON to model economic impacts of MPA closures on fishing communities.
