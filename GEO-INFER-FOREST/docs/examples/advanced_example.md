# Advanced Example: Biodiversity Habitat Connectivity Analysis

This example demonstrates how to combine canopy analysis, deforestation detection, and fragmentation metrics to assess habitat connectivity and identify priority wildlife corridors.

## Overview

Habitat fragmentation is a primary threat to biodiversity in forested landscapes. This workflow:

1. Computes NDVI and classifies canopy density to create a forest mask.
2. Detects recent deforestation using two-date change detection.
3. Calculates fragmentation indices (edge density, core fraction).
4. Computes annual deforestation rates from a multi-year time series.
5. Identifies priority conservation corridors based on core habitat patches.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-FOREST
```

## Step 1: Create Forest Mask from NDVI

Start with satellite band data and classify canopy density.

```python
import numpy as np
import xarray as xr
from geo_infer_forest.core.canopy_analysis import CanopyAnalyzer

analyzer = CanopyAnalyzer(config={
    "ndvi_forest_threshold": 0.4,
    "ndvi_dense_threshold": 0.7,
})

# Simulate a 50x50 pixel scene (~2500 ha at 30m resolution)
np.random.seed(42)
rows, cols = 50, 50

# Create a landscape with forest patches and clearings
forest_pattern = np.zeros((rows, cols))
# Large forest block in the west
forest_pattern[:, :25] = np.random.uniform(0.5, 0.85, (rows, 25))
# Scattered patches in the east
forest_pattern[:, 25:] = np.random.uniform(0.1, 0.5, (rows, 25))
# Dense corridor in the center
forest_pattern[20:30, :] = np.random.uniform(0.6, 0.9, (10, cols))

# Generate red and NIR bands consistent with forest pattern
red = xr.DataArray(0.15 - 0.10 * forest_pattern + np.random.normal(0, 0.01, (rows, cols)))
nir = xr.DataArray(0.15 + 0.40 * forest_pattern + np.random.normal(0, 0.02, (rows, cols)))
red = xr.where(red < 0.01, 0.01, red)
nir = xr.where(nir < 0.05, 0.05, nir)

# Calculate NDVI
ndvi = analyzer.calculate_ndvi(red, nir)
print(f"NDVI range: {float(ndvi.min()):.3f} to {float(ndvi.max()):.3f}")
print(f"Mean NDVI: {float(ndvi.mean()):.3f}")

# Classify canopy density
density_class = analyzer.classify_canopy_density(ndvi)
for cls in range(5):
    count = int((density_class == cls).sum())
    pct = count / (rows * cols) * 100
    labels = ["Non-forest", "Sparse", "Moderate", "Dense", "Very dense"]
    print(f"  Class {cls} ({labels[cls]}): {count} pixels ({pct:.1f}%)")
```

## Step 2: Detect Recent Deforestation

Simulate a second acquisition date where clearing has occurred in the southeast.

```python
from geo_infer_forest.core.deforestation import DeforestationDetector

detector = DeforestationDetector(config={
    "change_threshold": 0.15,
    "confidence_level": 0.95,
})

# Simulate NDVI from one year ago (before clearing)
ndvi_before = ndvi.copy()

# Simulate current NDVI (after clearing in southeast quadrant)
ndvi_after = ndvi.copy()
clearing = np.zeros((rows, cols))
clearing[35:45, 30:45] = np.random.uniform(0.20, 0.40, (10, 15))
ndvi_after = ndvi_after - clearing

# Two-date change detection
change = detector.detect_change_two_date(ndvi_before, ndvi_after)

print(f"\nDeforestation Detection:")
print(f"  Deforestation rate: {change.attrs['deforestation_rate']:.4f}")
print(f"  Deforested pixels: {change.attrs['deforested_pixel_count']}")
print(f"  Total pixels: {change.attrs['total_pixel_count']}")
print(f"  Area affected: ~{change.attrs['deforested_pixel_count'] * 0.09:.1f} ha (at 30m resolution)")
```

## Step 3: Calculate Fragmentation Indices

Assess how fragmented the current forest landscape is.

```python
# Create binary forest mask from current NDVI
forest_mask = xr.DataArray(
    (ndvi_after.values > 0.4).astype(float),
    dims=ndvi_after.dims,
)

fragmentation = detector.calculate_fragmentation_index(forest_mask)

print(f"\nFragmentation Analysis:")
print(f"  Forest fraction: {fragmentation['forest_fraction']:.3f}")
print(f"  Edge density: {fragmentation['edge_density']:.3f}")
print(f"  Core fraction: {fragmentation['core_fraction']:.3f}")
print(f"  Edge pixels: {fragmentation['edge_pixel_count']}")
print(f"  Core pixels: {fragmentation['core_pixel_count']}")
print(f"  Fragmentation index: {fragmentation['fragmentation_index']:.3f}")
```

## Step 4: Annual Deforestation Rate from Time Series

Compute compound annual deforestation rates from a multi-year forest cover series.

```python
# Simulate 5-year forest cover decline
years = np.arange(2020, 2025)
cover_values = [82.0, 80.5, 78.8, 76.2, 74.0]

forest_cover_series = xr.DataArray(
    np.array(cover_values).reshape(5, 1, 1) * np.ones((1, rows, cols)),
    dims=["time", "y", "x"],
    coords={"time": years},
)

annual_rate = detector.calculate_annual_deforestation_rate(forest_cover_series)

print(f"\nAnnual Deforestation Rate:")
print(f"  Start cover: {annual_rate['cover_start_pct']:.1f}%")
print(f"  End cover: {annual_rate['cover_end_pct']:.1f}%")
print(f"  Total loss: {annual_rate['total_loss_pct']:.1f}%")
print(f"  Annual rate: {annual_rate['annual_rate_pct']:.2f}%")
print(f"  Years covered: {annual_rate['years_covered']}")
```

## Step 5: Time-Series Change Detection

Run the z-score-based time-series detector on an NDVI sequence to identify when significant vegetation loss occurred.

```python
# Create NDVI time series with a sudden drop at year 3
time_steps = np.arange(6)
ndvi_ts_values = np.array([0.72, 0.74, 0.71, 0.45, 0.42, 0.40])
ndvi_series = xr.DataArray(
    ndvi_ts_values.reshape(6, 1, 1) * np.ones((1, 5, 5)),
    dims=["time", "y", "x"],
    coords={"time": time_steps},
)

ts_result = detector.detect_change_time_series(ndvi_series, window_size=3)

print(f"\nTime-Series Detection:")
print(f"  Z-scores at each timestep: {[f'{float(ts_result.z_score.isel(time=t, y=0, x=0)):.2f}' for t in range(6)]}")
print(f"  Significant decrease detected: {[bool(ts_result.significant_decrease.isel(time=t, y=0, x=0)) for t in range(6)]}")
```

## Step 6: Canopy Gap Analysis and Corridor Identification

Detect canopy gaps and assess their distribution relative to core habitat.

```python
# Detect gaps in post-deforestation NDVI
gaps = analyzer.detect_canopy_gaps(ndvi_after, gap_threshold=0.4)

print(f"\nCanopy Gap Analysis:")
print(f"  Gap fraction: {gaps.attrs['gap_fraction']:.3f}")
print(f"  Gap pixel count: {gaps.attrs['gap_pixel_count']}")
print(f"  Mean gap NDVI: {gaps.attrs['mean_gap_ndvi']:.3f}")
print(f"  Mean forest NDVI: {gaps.attrs['mean_forest_ndvi']:.3f}")

# Identify the central corridor (rows 20-30)
corridor_mask = forest_mask.copy()
corridor_data = corridor_mask.values if hasattr(corridor_mask, 'values') else corridor_mask
corridor_forest = float(corridor_data[20:30, :].sum())
corridor_total = float(corridor_data[20:30, :].size)
corridor_cover = corridor_forest / corridor_total

print(f"\nCentral Corridor (rows 20-30):")
print(f"  Forest cover: {corridor_cover:.1%}")
print(f"  Width: {10} pixels (~300m at 30m resolution)")
print(f"  Length: {cols} pixels (~1500m)")
print(f"  Connectivity: {'Connected' if corridor_cover > 0.6 else 'Fragmented'}")
```

## Step 7: Conservation Priority Summary

Combine all metrics into a conservation priority assessment.

```python
print("\n" + "=" * 60)
print("HABITAT CONNECTIVITY ASSESSMENT SUMMARY")
print("=" * 60)

health_score = (
    0.3 * fragmentation['core_fraction']
    + 0.3 * (1 - annual_rate['annual_rate_pct'] / 5.0)
    + 0.2 * corridor_cover
    + 0.2 * (1 - gaps.attrs['gap_fraction'])
)

print(f"  Forest extent: {fragmentation['forest_fraction']:.1%}")
print(f"  Core habitat: {fragmentation['core_fraction']:.1%}")
print(f"  Fragmentation index: {fragmentation['fragmentation_index']:.3f}")
print(f"  Annual loss rate: {annual_rate['annual_rate_pct']:.2f}%")
print(f"  Corridor integrity: {corridor_cover:.1%}")
print(f"  Gap fraction: {gaps.attrs['gap_fraction']:.3f}")
print(f"  Composite health score: {health_score:.3f}")

if health_score > 0.7:
    priority = "LOW -- landscape is well-connected"
elif health_score > 0.5:
    priority = "MODERATE -- some fragmentation, corridors need protection"
else:
    priority = "HIGH -- significant fragmentation, restoration needed"

print(f"  Conservation priority: {priority}")
```

## Key Takeaways

1. **Fragmentation is more informative than cover alone**: A landscape with 60% forest cover can be highly fragmented or well-connected depending on patch configuration.
2. **Edge effects compound biodiversity loss**: High edge density exposes more forest to wind, desiccation, invasive species, and human disturbance.
3. **Corridors are critical infrastructure**: Even narrow forest corridors (300m width) can maintain connectivity between core habitat blocks.
4. **Time-series detection catches gradual degradation**: Two-date methods miss slow, incremental canopy loss that the z-score approach identifies.

## Next Steps

- Integrate with GEO-INFER-BIO for species-specific habitat suitability modeling.
- Use GEO-INFER-SPACE to aggregate fragmentation metrics at watershed or H3 cell boundaries.
- Combine with GEO-INFER-CLIMATE projections to assess future corridor viability under warming scenarios.
