# Getting Started with GEO-INFER-MARINE

This guide covers installation, core concepts, and first working examples for oceanographic data processing, coastal analysis, and marine spatial planning.

## Installation

Install the module in editable mode using `uv`:

```bash
uv pip install -e ./GEO-INFER-MARINE
```

To install with NetCDF support:

```bash
uv pip install -e "./GEO-INFER-MARINE" netCDF4
```

Verify the installation:

```python
import geo_infer_marine
print(geo_infer_marine.__version__)
# 0.2.0
```

## Core Concepts

### Ocean Spatial Analysis

Marine analysis operates in a fundamentally different spatial context than terrestrial work. Key differences:

- **3D data**: Ocean properties (temperature, salinity, currents) vary with depth.
- **Dynamic boundaries**: Coastlines, sea ice edges, and ocean fronts move over time.
- **Sparse observations**: In-situ ocean data is much sparser than satellite-derived land data.
- **Coordinate conventions**: Ocean models use U/V velocity components on staggered grids.

GEO-INFER-MARINE uses `xarray.Dataset` throughout, which naturally handles multi-dimensional ocean data with named coordinates (latitude, longitude, depth, time).

### Coastal Hazard Modeling

The `CoastalAnalyzer` evaluates coastal vulnerability by combining:

- **Elevation**: Digital Elevation Model (DEM) data relative to sea level.
- **Sea level**: Current mean sea level and projected rise.
- **Wave height**: Storm wave and swell energy.

The vulnerability index uses inverse relative elevation: areas barely above sea level receive the highest scores. Wave height amplifies vulnerability through an additive factor.

### Marine Spatial Planning

Marine Spatial Planning (MSP) resolves competing uses of ocean space:

- Conservation (marine protected areas)
- Energy (offshore wind, tidal)
- Fisheries
- Shipping routes
- Recreation

The `MarineSpatialPlanner` supports MPA network design through biodiversity-priority ranking and offshore wind siting through combined wind resource and bathymetric analysis.

### Fisheries Analysis

Stock density estimation uses Catch Per Unit Effort (CPUE) as a proxy for abundance. The framework supports:

- Spatial CPUE mapping
- Spawning area identification
- MPA spillover analysis

## First Example: Ocean Current Analysis

Load velocity component data and compute current magnitude and direction.

```python
import numpy as np
import xarray as xr
from geo_infer_marine.core.oceanographic_data import OceanographicDataProcessor

processor = OceanographicDataProcessor()

# Create synthetic ocean velocity fields (20x20 grid)
lat = np.linspace(30, 35, 20)
lon = np.linspace(-125, -120, 20)
coords = {"lat": lat, "lon": lon}

# U (east-west) and V (north-south) velocity components (m/s)
u_velocity = xr.DataArray(
    np.random.uniform(-0.5, 0.8, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "m/s", "description": "Eastward velocity"},
)

v_velocity = xr.DataArray(
    np.random.uniform(-0.3, 0.6, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "m/s", "description": "Northward velocity"},
)

# Calculate current magnitude and direction
currents = processor.calculate_ocean_currents(u_velocity, v_velocity)

print(f"Current magnitude range: {float(currents['current_magnitude'].min()):.3f} - "
      f"{float(currents['current_magnitude'].max()):.3f} m/s")
print(f"Mean current speed: {float(currents['current_magnitude'].mean()):.3f} m/s")
print(f"Direction range: {float(currents['current_direction'].min()):.1f} - "
      f"{float(currents['current_direction'].max()):.1f} degrees")
```

## Second Example: Coastal Vulnerability

Assess coastal vulnerability from elevation and sea-level data.

```python
from geo_infer_marine.core.coastal_analysis import CoastalAnalyzer

coastal = CoastalAnalyzer()

# Coastal elevation profile (meters above sea level)
# Lower values near coast (west), higher inland (east)
lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")
elevation = xr.DataArray(
    np.clip(5.0 * (lon_grid + 125) + np.random.normal(0, 0.5, (20, 20)), 0, 30),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "meters"},
)

# Current sea level (reference datum)
sea_level = xr.DataArray(
    np.full((20, 20), 0.3),  # 0.3m mean sea level anomaly
    dims=["lat", "lon"],
    coords=coords,
)

# Significant wave height
wave_height = xr.DataArray(
    np.random.uniform(1.0, 3.5, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "meters"},
)

# Assess vulnerability
vulnerability = coastal.assess_coastal_vulnerability(
    elevation=elevation,
    sea_level=sea_level,
    wave_height=wave_height,
)

print(f"\nCoastal Vulnerability Assessment:")
print(f"  Mean vulnerability index: {float(vulnerability['vulnerability_index'].mean()):.4f}")
print(f"  Max vulnerability: {float(vulnerability['vulnerability_index'].max()):.4f}")
print(f"  Min relative elevation: {float(vulnerability['relative_elevation'].min()):.2f} m")
print(f"  Cells below 1m elevation: {int((vulnerability['relative_elevation'] < 1.0).sum())}")
```

## Third Example: MPA Network Design

Design a marine protected area network prioritized by biodiversity.

```python
from geo_infer_marine.core.marine_spatial_planning import MarineSpatialPlanner

planner = MarineSpatialPlanner()

# Biodiversity index (0-1 scale, higher = more species-rich)
biodiversity = xr.DataArray(
    np.random.uniform(0.2, 0.95, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
)

# Threat/pressure from fishing activity
fishing_pressure = xr.DataArray(
    np.random.uniform(0.0, 1.0, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
)

# Design MPA network targeting 30% coverage
mpa = planner.design_mpa_network(
    biodiversity_data=biodiversity,
    threat_data=fishing_pressure,
    target_coverage=0.30,
)

actual_coverage = float(mpa['coverage'])
print(f"\nMPA Network Design:")
print(f"  Target coverage: 30%")
print(f"  Actual coverage: {actual_coverage:.1%}")
print(f"  Cells designated MPA: {int(mpa['mpa_mask'].sum())}")
print(f"  Mean priority in MPA: {float(mpa['priority'].where(mpa['mpa_mask']).mean()):.3f}")
print(f"  Mean priority outside: {float(mpa['priority'].where(~mpa['mpa_mask']).mean()):.3f}")
```

## Fourth Example: Offshore Wind Siting

Find optimal locations for offshore wind farms considering wind resource and water depth.

```python
# Wind resource (m/s at hub height)
wind_resource = xr.DataArray(
    np.random.uniform(6.0, 11.0, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
)

# Bathymetric depth (meters, positive = deeper)
depth = xr.DataArray(
    np.clip(10.0 * (lon_grid + 125) + np.random.normal(0, 3, (20, 20)), 5, 100),
    dims=["lat", "lon"],
    coords=coords,
)

# Exclusion zones (MPAs from previous step)
exclusion = mpa["mpa_mask"]

# Find optimal sites (max depth 50m for fixed-bottom turbines)
wind_sites = planner.optimize_offshore_wind_siting(
    wind_resource=wind_resource,
    depth=depth,
    exclusion_zones=exclusion,
    max_depth=50.0,
)

viable = wind_sites["suitability"] > 0.3
print(f"\nOffshore Wind Siting:")
print(f"  Viable cells (suitability > 0.3): {int(viable.sum())}")
print(f"  Mean suitability: {float(wind_sites['suitability'].mean()):.3f}")
print(f"  Best suitability: {float(wind_sites['suitability'].max()):.3f}")
```

## Next Steps

- Read the [API Reference](api_reference.md) for the full method catalog.
- Try the [Coastal Risk Assessment](examples/basic_example.md) for a population-weighted vulnerability workflow.
- See the [Fisheries Stock Assessment](examples/advanced_example.md) for CPUE analysis and MPA effectiveness evaluation.
