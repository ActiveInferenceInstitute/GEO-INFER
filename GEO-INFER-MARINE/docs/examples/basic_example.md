# Basic Example: Coastal Risk Assessment

This example demonstrates how to combine a Digital Elevation Model, storm surge projections, and population data to create a coastal vulnerability index and identify communities at highest risk.

## Overview

The workflow has five steps:

1. Generate coastal elevation and bathymetric data.
2. Model storm surge scenarios at different return periods.
3. Compute coastal vulnerability using `CoastalAnalyzer`.
4. Overlay population data to create an exposure-weighted risk score.
5. Rank coastal segments by combined risk.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-MARINE
```

## Step 1: Prepare Coastal Elevation Data

Create a synthetic DEM for a coastal region. In production, use LIDAR-derived DEMs or SRTM/ALOS data.

```python
import numpy as np
import xarray as xr
from geo_infer_marine.core.coastal_analysis import CoastalAnalyzer

# Define a coastal transect: 30 cells along coast, 20 cells inland
lat = np.linspace(33.5, 34.5, 30)
lon = np.linspace(-118.5, -118.0, 20)
coords = {"lat": lat, "lon": lon}

# Elevation increases from coast (west) to inland (east)
lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")
distance_from_coast = (lon_grid - lon.min()) / (lon.max() - lon.min())
elevation = xr.DataArray(
    np.clip(
        -2 + 15 * distance_from_coast + np.random.normal(0, 0.5, (30, 20)),
        -5, 25
    ),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "meters above MSL", "source": "synthetic DEM"},
)

print(f"Elevation range: {float(elevation.min()):.1f} to {float(elevation.max()):.1f} m")
print(f"Cells below sea level: {int((elevation < 0).sum())}")
print(f"Cells below 2m: {int((elevation < 2).sum())}")
```

## Step 2: Model Storm Surge Scenarios

Define storm surge heights for different return period events.

```python
# Storm surge scenarios (meters above MSL)
scenarios = {
    "10_year": 1.2,   # Common storm
    "50_year": 2.0,   # Moderate event
    "100_year": 2.8,  # Major storm
    "500_year": 3.5,  # Extreme event
}

# Sea level rise projections to add on top
slr_2050 = 0.3   # meters by 2050
slr_2100 = 0.8   # meters by 2100

print("Storm Surge + SLR Combined Scenarios:")
for name, surge in scenarios.items():
    print(f"  {name:>10}: {surge:.1f}m surge | "
          f"{surge + slr_2050:.1f}m with 2050 SLR | "
          f"{surge + slr_2100:.1f}m with 2100 SLR")
```

## Step 3: Compute Vulnerability for Each Scenario

```python
coastal = CoastalAnalyzer()
results = {}

for scenario_name, surge_height in scenarios.items():
    # Sea level for this scenario (surge + current SLR)
    sea_level = xr.DataArray(
        np.full((30, 20), surge_height + slr_2050),
        dims=["lat", "lon"],
        coords=coords,
    )

    # Significant wave height during storm
    wave_height = xr.DataArray(
        np.random.uniform(2.0, 5.0, (30, 20)),
        dims=["lat", "lon"],
        coords=coords,
    )

    # Assess vulnerability
    vuln = coastal.assess_coastal_vulnerability(
        elevation=elevation,
        sea_level=sea_level,
        wave_height=wave_height,
    )

    # Count inundated cells (relative elevation < 0)
    inundated = int((vuln["relative_elevation"] < 0).sum())
    total_cells = elevation.size

    results[scenario_name] = {
        "vulnerability": vuln,
        "inundated_cells": inundated,
        "inundation_pct": inundated / total_cells * 100,
        "mean_vulnerability": float(vuln["vulnerability_index"].mean()),
        "max_vulnerability": float(vuln["vulnerability_index"].max()),
    }

    print(f"\n{scenario_name} Scenario:")
    print(f"  Inundated cells: {inundated} ({inundated / total_cells:.1%})")
    print(f"  Mean vulnerability: {results[scenario_name]['mean_vulnerability']:.4f}")
    print(f"  Max vulnerability: {results[scenario_name]['max_vulnerability']:.4f}")
```

## Step 4: Population Exposure Overlay

Weight vulnerability by population density to identify where people are most at risk.

```python
# Synthetic population density (people per cell)
# Higher near coast, concentrated in certain areas
population = xr.DataArray(
    np.clip(
        500 * (1 - distance_from_coast) + np.random.exponential(200, (30, 20)),
        0, 2000,
    ),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "people per cell"},
)

print(f"\nPopulation Distribution:")
print(f"  Total population: {int(population.sum()):,}")
print(f"  Mean density: {float(population.mean()):.0f} people/cell")

# Calculate exposure-weighted risk for the 100-year scenario
vuln_100yr = results["100_year"]["vulnerability"]
exposure = vuln_100yr["vulnerability_index"] * population

# Normalize to 0-100 risk score
risk_score = (exposure / float(exposure.max()) * 100)
risk_score = xr.where(risk_score > 100, 100, risk_score)

print(f"\nExposure-Weighted Risk (100-year):")
print(f"  Mean risk score: {float(risk_score.mean()):.1f}")
print(f"  High risk cells (score > 50): {int((risk_score > 50).sum())}")
print(f"  Critical risk cells (score > 80): {int((risk_score > 80).sum())}")

# People in high-risk zones
high_risk_pop = float(population.where(risk_score > 50, 0).sum())
print(f"  People in high-risk zones: {int(high_risk_pop):,}")
```

## Step 5: Rank Coastal Segments

Aggregate risk by latitude bands to identify the most vulnerable coastal segments.

```python
# Group by latitude bands (3 cells per segment = ~10 segments)
segment_size = 3
n_segments = len(lat) // segment_size

print(f"\nCoastal Segment Risk Ranking:")
print(f"{'Rank':<6}{'Segment':<12}{'Lat Range':>18}{'Population':>12}"
      f"{'Inundated':>12}{'Risk Score':>12}")
print("-" * 72)

segment_risks = []
for i in range(n_segments):
    start = i * segment_size
    end = start + segment_size
    seg_risk = float(risk_score[start:end, :].mean())
    seg_pop = int(population[start:end, :].sum())
    seg_inundated = int((vuln_100yr["relative_elevation"][start:end, :] < 0).sum())
    seg_lat_min = lat[start]
    seg_lat_max = lat[min(end - 1, len(lat) - 1)]

    segment_risks.append({
        "segment": f"S{i+1:02d}",
        "lat_range": f"{seg_lat_min:.2f}-{seg_lat_max:.2f}",
        "population": seg_pop,
        "inundated": seg_inundated,
        "risk_score": seg_risk,
    })

# Sort by risk score descending
segment_risks.sort(key=lambda s: s["risk_score"], reverse=True)

for rank, seg in enumerate(segment_risks, 1):
    print(f"{rank:<6}{seg['segment']:<12}{seg['lat_range']:>18}"
          f"{seg['population']:>12,}{seg['inundated']:>12}"
          f"{seg['risk_score']:>12.1f}")
```

## Step 6: Erosion Trend Analysis

Assess long-term shoreline change to complement the storm event analysis.

```python
# Simulate shoreline position over 5 time periods
time_periods = [2000, 2005, 2010, 2015, 2020]
shoreline_base = np.linspace(0, 100, 30)

shoreline_data = xr.DataArray(
    np.column_stack([
        shoreline_base - i * np.random.uniform(0.2, 0.8, 30)
        for i in range(5)
    ]).T,
    dims=["time", "lat"],
    coords={"time": time_periods, "lat": lat},
)

erosion = coastal.analyze_coastal_erosion(shoreline_data, time_periods)
mean_rate = float(erosion["erosion_rates"].mean())

print(f"\nShoreline Erosion Analysis:")
print(f"  Periods analyzed: {len(time_periods) - 1}")
print(f"  Mean erosion rate: {mean_rate:.2f} m/period")
print(f"  Annual rate (5yr periods): {mean_rate / 5:.2f} m/year")
```

## Key Takeaways

1. **Vulnerability is nonlinear with elevation**: A 1m rise in sea level dramatically increases risk for areas currently at 1-3m elevation.
2. **Population weighting is essential**: An uninhabited low-lying area has different policy implications than a densely populated one.
3. **Return period matters**: Design coastal defenses to the scenario that matches the asset lifecycle (50-year for infrastructure, 100-year for critical facilities).
4. **Combine chronic and acute hazards**: Erosion trends reveal long-term risk that single-event analysis misses.

## Next Steps

- Use real DEM data from GEO-INFER-DATA (LIDAR, Copernicus DEM).
- Integrate with GEO-INFER-RISK for multi-hazard coastal risk scoring.
- See the [Advanced Example](advanced_example.md) for fisheries stock assessment.
