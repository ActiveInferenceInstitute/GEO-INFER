# Basic Example: Solar Siting Assessment

This example demonstrates how to use GEO-INFER-ENERGY to compute H3-indexed solar irradiance scores, filter by land use constraints, and rank top candidate sites for photovoltaic development.

## Overview

The workflow has four steps:

1. Generate a grid of candidate locations using H3 hexagons.
2. Compute clear-sky daily insolation at each hex centroid.
3. Apply land use and terrain constraints.
4. Rank sites by final suitability score.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-ENERGY
# Optional: for H3 grid generation
uv pip install h3>=4.0.0
```

## Step 1: Generate H3 Candidate Grid

Create a set of H3 hexagons covering a region of interest. This example uses the Mojave Desert area of Southern California.

```python
import h3

# Define bounding box for Mojave Desert region
bounds = {
    "south": 34.5,
    "north": 35.5,
    "west": -117.5,
    "east": -116.0,
}

# Generate H3 cells at resolution 7 (~5.16 km2 per cell)
resolution = 7
cells = set()
lat_step = 0.05
lon_step = 0.05

lat = bounds["south"]
while lat <= bounds["north"]:
    lon = bounds["west"]
    while lon <= bounds["east"]:
        cell = h3.latlng_to_cell(lat, lon, resolution)
        cells.add(cell)
        lon += lon_step
    lat += lat_step

print(f"Generated {len(cells)} candidate H3 cells at resolution {resolution}")
```

## Step 2: Compute Solar Insolation per Cell

Use the `SolarAnalyzer` to calculate daily clear-sky insolation at each hex centroid. We evaluate multiple days across the year to get a representative annual average.

```python
from geo_infer_energy.core.solar_analysis import SolarAnalyzer

solar = SolarAnalyzer()

# Representative days: equinoxes and solstices
sample_days = [80, 172, 266, 355]  # Mar 21, Jun 21, Sep 23, Dec 21

site_results = []

for cell in cells:
    lat, lng = h3.cell_to_latlng(cell)

    # Average insolation across four sample days
    daily_values = []
    for doy in sample_days:
        ghi = solar.daily_insolation(lat, doy, altitude_m=800.0)
        daily_values.append(ghi)

    avg_daily_kwh = sum(daily_values) / len(daily_values)

    # Estimate PV output for a standard 1 MW array (~5000 m2)
    pv = solar.estimate_pv_output(
        ghi_kwh_m2_day=avg_daily_kwh,
        panel_area_m2=5000.0,
        efficiency=0.20,
        performance_ratio=0.80,
    )

    site_results.append({
        "h3_cell": cell,
        "lat": lat,
        "lng": lng,
        "avg_daily_ghi_kwh": round(avg_daily_kwh, 2),
        "annual_mwh": round(pv["annual_mwh"], 1),
        "capacity_factor": round(pv["capacity_factor"], 3),
    })

print(f"Computed solar potential for {len(site_results)} sites")
```

## Step 3: Apply Land Use Constraints

Filter out sites that overlap with protected areas, steep terrain, or are too far from grid infrastructure.

```python
from geo_infer_energy.core.renewable_resources import (
    RenewableResourceAssessor,
    RenewableType,
)

assessor = RenewableResourceAssessor()

scored_sites = []

for site in site_results:
    # Simulated constraint flags (in production, derive from GIS layers)
    constraints = {
        "protected_area": False,
        "steep_slope": site["lat"] > 35.3,  # Simplified terrain proxy
        "poor_access": False,
        "grid_distance_km": 15,  # Assume moderate grid distance
    }

    suitability = assessor.assess_site_suitability(
        location=(site["lng"], site["lat"]),
        resource_type=RenewableType.SOLAR_PV,
        resource_value=site["avg_daily_ghi_kwh"],
        constraints=constraints,
    )

    site.update({
        "suitability_class": suitability["suitability_class"],
        "final_score": suitability["final_score"],
        "constraint_issues": suitability["constraint_issues"],
        "development_recommended": suitability["development_recommended"],
    })

    if suitability["development_recommended"]:
        scored_sites.append(site)

print(f"{len(scored_sites)} sites passed suitability screening")
```

## Step 4: Rank and Report Top Sites

Sort the screened sites by final score and annual generation potential.

```python
# Rank by final score (descending), then by annual generation
ranked = sorted(
    scored_sites,
    key=lambda s: (s["final_score"], s["annual_mwh"]),
    reverse=True,
)

print("\nTop 10 Solar Development Sites")
print("-" * 80)
print(f"{'Rank':<6}{'H3 Cell':<18}{'Lat':>8}{'Lon':>10}"
      f"{'GHI':>8}{'MWh/yr':>10}{'CF':>8}{'Score':>8}{'Class':>12}")
print("-" * 80)

for i, site in enumerate(ranked[:10], 1):
    print(
        f"{i:<6}{site['h3_cell']:<18}{site['lat']:>8.3f}{site['lng']:>10.3f}"
        f"{site['avg_daily_ghi_kwh']:>8.2f}{site['annual_mwh']:>10.1f}"
        f"{site['capacity_factor']:>8.3f}{site['final_score']:>8.2f}"
        f"{site['suitability_class']:>12}"
    )
```

## Step 5: LCOE Estimation for Top Site

Calculate the Levelized Cost of Energy for the highest-ranked site:

```python
top_site = ranked[0]

lcoe_result = assessor.calculate_lcoe(
    resource_type=RenewableType.SOLAR_PV,
    capacity_mw=1.0,
    capacity_factor=top_site["capacity_factor"],
    discount_rate=0.07,
    lifetime_years=25,
)

print(f"\nLCOE for top site ({top_site['h3_cell']}):")
print(f"  LCOE: ${lcoe_result['lcoe_usd_mwh']:.2f}/MWh")
print(f"  Competitiveness: {lcoe_result['competitiveness']}")
print(f"  Lifetime generation: {lcoe_result['lifetime_generation_gwh']:.2f} GWh")
print(f"  Capital cost: ${lcoe_result['capital_cost_usd']:,.0f}")
```

## Expected Output Summary

For the Mojave Desert region, you should see:

- Average daily GHI values of 6-8 kWh/m2/day.
- Capacity factors of 22-30%.
- Most sites classified as GOOD or EXCELLENT.
- LCOE values in the range of $30-50/MWh, typical for high-irradiance desert locations.

## Next Steps

- Combine this solar analysis with the wind assessment from the [Advanced Example](advanced_example.md).
- Integrate with GEO-INFER-SPACE for more precise H3-based spatial aggregation.
- Use GEO-INFER-DATA to ingest real NASA POWER or NSRDB irradiance datasets instead of clear-sky estimates.
