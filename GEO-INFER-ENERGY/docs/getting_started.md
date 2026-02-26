# Getting Started with GEO-INFER-ENERGY

This guide covers installation, core concepts, and a first working example of renewable energy site assessment.

## Installation

Install the module in editable mode using `uv`:

```bash
uv pip install -e ./GEO-INFER-ENERGY
```

To install with optional spatial dependencies:

```bash
uv pip install -e "./GEO-INFER-ENERGY[spatial]"
```

Verify the installation:

```python
import geo_infer_energy
print(geo_infer_energy.__version__)
# 0.1.0
```

## Core Concepts

### Spatial Energy Modeling

GEO-INFER-ENERGY treats energy analysis as a spatial problem. Every resource assessment, demand forecast, and grid analysis operates on georeferenced data -- typically `xarray.DataArray` objects with latitude/longitude coordinates.

This spatial-first approach means you can:

- Map solar irradiance across a region at any resolution.
- Score wind farm sites by combining meteorological data with terrain constraints.
- Identify grid reliability gaps by overlaying generation capacity on demand patterns.

### Renewable Resource Assessment

The `RenewableResourceAssessor` is the primary entry point for evaluating where to build renewable energy projects. It supports nine resource types defined in the `RenewableType` enum:

| Type | Description | Key Metric |
|------|-------------|------------|
| `SOLAR_PV` | Photovoltaic panels | GHI (kWh/m2/day) |
| `SOLAR_THERMAL` | Concentrated solar power | DNI (kWh/m2/day) |
| `ONSHORE_WIND` | Land-based wind turbines | Wind speed (m/s) |
| `OFFSHORE_WIND` | Marine wind turbines | Wind speed (m/s) |
| `HYDROPOWER` | Run-of-river or dam | Flow rate + head |
| `GEOTHERMAL` | Subsurface heat | Temperature (C) |
| `BIOMASS` | Organic fuel sources | Feedstock density |
| `WAVE` | Ocean wave energy | Wave height (m) |
| `TIDAL` | Tidal stream energy | Current speed (m/s) |

### Site Suitability Classification

Every site assessment produces a `SuitabilityClass`:

- **EXCELLENT**: Resource score >= 0.8 after constraint adjustment.
- **GOOD**: Score >= 0.6.
- **MODERATE**: Score >= 0.4.
- **MARGINAL**: Score >= 0.2.
- **UNSUITABLE**: Score < 0.2 or hard constraint (e.g., protected area).

### Solar Physics

The `SolarAnalyzer` implements physics-based irradiance modeling:

1. **Solar declination** via the Spencer (1971) equation.
2. **Hour angle** from solar time.
3. **Solar elevation** from latitude, declination, and hour angle.
4. **Clear-sky GHI** using the Hottel (1976) model with altitude correction.
5. **Daily insolation** by quarter-hour integration of GHI over 24 hours.
6. **Optimal tilt** using the Jacobson-Jadhav (2018) approximation.

## First Example: Solar Resource Assessment

This example estimates clear-sky solar potential for a location and computes the expected PV output.

```python
from geo_infer_energy.core.solar_analysis import SolarAnalyzer

# Initialize the analyzer
solar = SolarAnalyzer()

# Site parameters: latitude 35.0 N, summer solstice (day 172), 500m altitude
latitude = 35.0
day_of_year = 172
altitude_m = 500.0

# Calculate daily clear-sky insolation
daily_kwh = solar.daily_insolation(latitude, day_of_year, altitude_m)
print(f"Daily insolation: {daily_kwh:.2f} kWh/m2/day")

# Calculate optimal panel tilt for this latitude
tilt = solar.optimal_tilt_angle(latitude)
print(f"Optimal tilt angle: {tilt:.1f} degrees")

# Estimate PV output for a 100 m2 array
pv_output = solar.estimate_pv_output(
    ghi_kwh_m2_day=daily_kwh,
    panel_area_m2=100.0,
    efficiency=0.20,
    performance_ratio=0.80,
)

print(f"Daily output: {pv_output['daily_kwh']:.1f} kWh")
print(f"Annual output: {pv_output['annual_mwh']:.1f} MWh")
print(f"Peak capacity: {pv_output['peak_capacity_kw']:.1f} kW")
print(f"Capacity factor: {pv_output['capacity_factor']:.2%}")
```

Expected output (approximate):

```
Daily insolation: 8.43 kWh/m2/day
Optimal tilt angle: 29.7 degrees
Daily output: 134.9 kWh
Annual output: 49.2 MWh
Peak capacity: 20.0 kW
Capacity factor: 28.1%
```

## Second Example: Site Suitability Scoring

Use the `RenewableResourceAssessor` to evaluate a candidate solar site:

```python
from geo_infer_energy.core.renewable_resources import (
    RenewableResourceAssessor,
    RenewableType,
)

assessor = RenewableResourceAssessor()

# Evaluate a candidate solar PV site
result = assessor.assess_site_suitability(
    location=(-118.25, 34.05),  # Los Angeles area
    resource_type=RenewableType.SOLAR_PV,
    resource_value=5.8,  # kWh/m2/day average GHI
    constraints={
        "protected_area": False,
        "steep_slope": False,
        "poor_access": False,
        "grid_distance_km": 12,
    },
)

print(f"Suitability class: {result['suitability_class']}")
print(f"Resource score: {result['resource_score']}")
print(f"Final score: {result['final_score']}")
print(f"Development recommended: {result['development_recommended']}")
```

## Third Example: Grid Reliability

Assess whether a region's generation capacity meets demand:

```python
import numpy as np
import xarray as xr
from geo_infer_energy.core.energy_grid import EnergyGridOptimizer

optimizer = EnergyGridOptimizer()

# Create sample spatial data (10x10 grid)
coords = {"lat": np.linspace(33, 35, 10), "lon": np.linspace(-119, -117, 10)}
generation = xr.DataArray(np.random.uniform(800, 1200, (10, 10)), dims=["lat", "lon"], coords=coords)
peak_demand = xr.DataArray(np.random.uniform(600, 1000, (10, 10)), dims=["lat", "lon"], coords=coords)

reliability = optimizer.assess_grid_reliability(
    generation_capacity=generation,
    peak_demand=peak_demand,
    reserve_margin=0.15,
)

print(f"Mean reliability index: {float(reliability['reliability_index'].mean()):.3f}")
print(f"Cells with capacity deficit: {int((reliability['capacity_deficit'] > 0).sum())}")
```

## Next Steps

- Read the [API Reference](api_reference.md) for the full method catalog.
- Try the [Solar Siting Example](examples/basic_example.md) for an H3-indexed workflow.
- See the [Integrated Energy Planning Example](examples/advanced_example.md) for multi-resource optimization.
