# Advanced Example: Integrated Energy Planning

This example demonstrates combining solar and wind resource assessment with grid reliability analysis, storage sizing, and LCOE comparison to produce an integrated energy plan for a region.

## Overview

The workflow covers:

1. Assess both solar and wind potential across the same region.
2. Calculate capacity factors and LCOE for each resource.
3. Evaluate grid supply-demand balance with the combined renewable portfolio.
4. Size energy storage to manage intermittency.
5. Compare scenarios: solar-only, wind-only, and hybrid.

## Setup

```python
import numpy as np
import xarray as xr
from geo_infer_energy.core.solar_analysis import SolarAnalyzer
from geo_infer_energy.core.renewable_resources import (
    RenewableResourceAssessor,
    RenewableType,
    RenewableSite,
)
from geo_infer_energy.core.energy_grid import EnergyGridOptimizer
from geo_infer_energy.core.energy_demand import EnergyDemandForecaster
```

## Step 1: Create Regional Resource Data

Build synthetic solar irradiance and wind speed rasters that represent a 100 km x 100 km region.

```python
# Define spatial grid (20x20 cells)
lat = np.linspace(34.0, 35.0, 20)
lon = np.linspace(-118.0, -117.0, 20)
coords = {"lat": lat, "lon": lon}

# Solar irradiance: higher in the south and east (desert)
lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")
solar_base = 5.0 + 1.5 * (lat_grid - 34.0) / 1.0 - 0.5 * (lon_grid + 118.0)
solar_irradiance = xr.DataArray(
    np.clip(solar_base + np.random.normal(0, 0.3, (20, 20)), 3.0, 8.0),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "kWh/m2/day", "description": "Mean daily GHI"},
)

# Wind speed: higher in the northwest (mountain passes)
wind_base = 7.0 - 2.0 * (lat_grid - 34.0) + 1.5 * (lon_grid + 118.0)
wind_speed = xr.DataArray(
    np.clip(wind_base + np.random.normal(0, 0.5, (20, 20)), 3.0, 12.0),
    dims=["lat", "lon"],
    coords=coords,
    attrs={"units": "m/s", "description": "Mean wind speed at 80m"},
)

# Terrain slope for constraint filtering
slope = xr.DataArray(
    np.random.uniform(0, 30, (20, 20)),
    dims=["lat", "lon"],
    coords=coords,
)
```

## Step 2: Assess Solar and Wind Potential

```python
assessor = RenewableResourceAssessor()

# Solar potential assessment
solar_potential = assessor.assess_solar_potential(
    solar_irradiance=solar_irradiance,
    slope=slope,
)

# Wind potential assessment
wind_potential = assessor.assess_wind_potential(
    wind_speed=wind_speed,
)

print("Solar potential range:")
print(f"  Min: {float(solar_potential['annual_energy'].min()):.0f} kWh/m2/year")
print(f"  Max: {float(solar_potential['annual_energy'].max()):.0f} kWh/m2/year")
print(f"  Mean: {float(solar_potential['annual_energy'].mean()):.0f} kWh/m2/year")

print("\nWind potential range:")
print(f"  Min: {float(wind_potential['energy_potential'].min()):.0f} kWh/year")
print(f"  Max: {float(wind_potential['energy_potential'].max()):.0f} kWh/year")
```

## Step 3: Calculate LCOE for Both Resources

Compare the economic viability of solar PV versus onshore wind.

```python
# Solar LCOE at representative capacity factor
solar_cf = 0.24  # Typical for this region
solar_lcoe = assessor.calculate_lcoe(
    resource_type=RenewableType.SOLAR_PV,
    capacity_mw=50.0,
    capacity_factor=solar_cf,
    discount_rate=0.07,
    lifetime_years=25,
)

# Wind LCOE at representative capacity factor
wind_cf = 0.32  # Typical for mountain pass sites
wind_lcoe = assessor.calculate_lcoe(
    resource_type=RenewableType.ONSHORE_WIND,
    capacity_mw=50.0,
    capacity_factor=wind_cf,
    discount_rate=0.07,
    lifetime_years=25,
)

print("\nLCOE Comparison")
print("-" * 50)
print(f"{'Resource':<20}{'CF':>8}{'LCOE ($/MWh)':>15}{'Rating':>15}")
print("-" * 50)
print(f"{'Solar PV':<20}{solar_cf:>8.2f}{solar_lcoe['lcoe_usd_mwh']:>15.2f}"
      f"{solar_lcoe['competitiveness']:>15}")
print(f"{'Onshore Wind':<20}{wind_cf:>8.2f}{wind_lcoe['lcoe_usd_mwh']:>15.2f}"
      f"{wind_lcoe['competitiveness']:>15}")
```

## Step 4: Grid Reliability with Combined Renewables

Evaluate whether the combined solar + wind generation meets regional demand.

```python
optimizer = EnergyGridOptimizer()

# Simulate supply as combination of solar and wind (MW per cell)
solar_supply = solar_potential["annual_energy"] / 8760 * 0.001  # Convert to MW
wind_supply = wind_potential["energy_potential"] / 8760 * 0.001
combined_supply = solar_supply + wind_supply

# Regional demand pattern (higher in urban southwest)
demand = xr.DataArray(
    np.random.uniform(0.5, 2.0, (20, 20)) * (1 + 0.5 * (35.0 - lat_grid)),
    dims=["lat", "lon"],
    coords=coords,
)

# Optimize grid balance
balance = optimizer.optimize_grid_network(
    demand=demand,
    supply=combined_supply,
)

print("\nGrid Balance Summary")
print(f"  Total supply: {float(combined_supply.sum()):.1f} MW")
print(f"  Total demand: {float(demand.sum()):.1f} MW")
print(f"  Net balance: {float(balance['balance'].sum()):.1f} MW")
print(f"  Cells with deficit: {int((balance['deficit'] > 0).sum())}")
print(f"  Mean reliability: {float(balance['reliability'].mean()):.3f}")
```

## Step 5: Storage Sizing

Determine how much battery storage is needed to manage solar intermittency at 50% renewable penetration.

```python
# Create hourly generation and demand profiles (24 hours)
hours = np.arange(24)

# Solar generation profile: peaks at noon, zero at night
solar_profile_hourly = xr.DataArray(
    np.maximum(0, 50.0 * np.sin(np.pi * (hours - 6) / 12) ** 2 * (hours >= 6) * (hours <= 18)),
    dims=["hour"],
    coords={"hour": hours},
)

# Demand profile: morning and evening peaks
demand_profile_hourly = xr.DataArray(
    30.0 + 20.0 * np.sin(np.pi * hours / 12) + 15.0 * (hours >= 17) * (hours <= 21),
    dims=["hour"],
    coords={"hour": hours},
)

storage = assessor.analyze_storage_requirements(
    generation_profile=solar_profile_hourly,
    demand_profile=demand_profile_hourly,
    renewable_penetration=0.50,
)

print("\nStorage Requirements (50% Renewable Penetration)")
print(f"  Power capacity: {storage['recommended_storage']['power_capacity_mw']:.1f} MW")
print(f"  Energy capacity: {storage['recommended_storage']['energy_capacity_mwh']:.1f} MWh")
print(f"  Duration: {storage['recommended_storage']['duration_hours']:.0f} hours")
print(f"  Curtailment without storage: {storage['curtailment_rate_pct']:.1f}%")
```

## Step 6: Register Portfolio and Compare Scenarios

Register the solar and wind sites and compare three scenarios.

```python
# Register solar site
solar_site = RenewableSite(
    site_id="solar_mojave_01",
    name="Mojave Solar Farm",
    location=(-117.5, 34.5),
    resource_type=RenewableType.SOLAR_PV,
    capacity_mw=50.0,
    capacity_factor=solar_cf,
    annual_generation_gwh=50.0 * solar_cf * 8.760,
    lcoe_usd_mwh=solar_lcoe["lcoe_usd_mwh"],
)
assessor.register_site(solar_site)

# Register wind site
wind_site = RenewableSite(
    site_id="wind_tehachapi_01",
    name="Tehachapi Wind Farm",
    location=(-118.3, 35.1),
    resource_type=RenewableType.ONSHORE_WIND,
    capacity_mw=50.0,
    capacity_factor=wind_cf,
    annual_generation_gwh=50.0 * wind_cf * 8.760,
    lcoe_usd_mwh=wind_lcoe["lcoe_usd_mwh"],
)
assessor.register_site(wind_site)

# Get combined portfolio summary
portfolio = assessor.get_portfolio_summary()
print("\nPortfolio Summary")
print(f"  Total sites: {portfolio['site_count']}")
print(f"  Total capacity: {portfolio['total_capacity_mw']:.0f} MW")
print(f"  Total generation: {portfolio['total_generation_gwh']:.1f} GWh/year")
print(f"  Weighted capacity factor: {portfolio['weighted_capacity_factor']:.2%}")

for rtype, data in portfolio["by_resource_type"].items():
    print(f"  {rtype}: {data['count']} sites, {data['capacity_mw']:.0f} MW, "
          f"{data['generation_gwh']:.1f} GWh")
```

## Step 7: Demand Forecast

Project demand growth over the next decade and evaluate future adequacy.

```python
forecaster = EnergyDemandForecaster()

# Create a 5-year historical demand series
historical_time = np.arange(5)
historical_values = np.array([100, 105, 108, 112, 118])  # GWh/year
historical = xr.DataArray(
    historical_values,
    dims=["time"],
    coords={"time": historical_time},
)

forecast = forecaster.forecast_demand(
    historical_demand=historical,
    forecast_years=10,
)

print("\nDemand Forecast (10-year)")
print(f"  Current demand: {historical_values[-1]:.0f} GWh/year")
print(f"  Portfolio generation: {portfolio['total_generation_gwh']:.1f} GWh/year")
```

## Key Takeaways

This integrated planning workflow reveals several practical insights:

1. **Resource complementarity**: Solar and wind often have anti-correlated generation profiles, reducing combined variability.
2. **Storage sizing scales with penetration**: At 50% renewable penetration, 4 hours of storage covers most daily variability. Higher penetration requires longer duration.
3. **LCOE is necessary but not sufficient**: Grid integration costs, storage requirements, and transmission expansion must factor into planning.
4. **Spatial granularity matters**: H3 hexagonal grids allow consistent aggregation across resource types and demand patterns.

## Next Steps

- Use GEO-INFER-CLIMATE to incorporate climate change projections into long-term resource estimates.
- Integrate with GEO-INFER-ECON for full cost-benefit analysis including carbon pricing.
- Deploy the grid reliability assessment at higher spatial resolution using GEO-INFER-SPACE H3 backends.
