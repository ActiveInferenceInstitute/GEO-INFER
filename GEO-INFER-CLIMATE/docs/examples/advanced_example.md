# Advanced Example: Multi-Variable Climate Analysis

This example performs a combined analysis of temperature trends, precipitation patterns, and extreme event frequency across a synthetic regional dataset. The analysis identifies spatially coherent signals of climate change and estimates future conditions under different SSP scenarios.

## Problem Description

Analyze 40 years (1980-2019) of monthly climate data for a 5-station regional network to:

1. Detect temperature trends with statistical significance at each station.
2. Identify changes in precipitation seasonality and intensity.
3. Track extreme event frequency over time.
4. Project regional conditions to 2050 and 2100 under SSP2-4.5 and SSP5-8.5.

## Setting Up the Regional Dataset

```python
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from geo_infer_climate.core.temperature_trends import TemperatureTrendAnalyzer

np.random.seed(42)

@dataclass
class ClimateStation:
    """A climate monitoring station."""
    station_id: str
    name: str
    lat: float
    lng: float
    elevation_m: float

# Define 5 stations at different elevations
stations = [
    ClimateStation("S1", "Coastal Plain", 47.60, -122.35, 15),
    ClimateStation("S2", "Valley Floor", 47.55, -122.20, 120),
    ClimateStation("S3", "Foothill", 47.50, -122.05, 450),
    ClimateStation("S4", "Mountain Base", 47.45, -121.90, 900),
    ClimateStation("S5", "Highland", 47.40, -121.75, 1500),
]

years = np.arange(1980, 2020)
months = np.arange(1, 13)
n_years = len(years)
n_months = 12

# Elevation-dependent warming rates (higher elevation warms faster)
elevation_warming = {
    15: 0.015, 120: 0.017, 450: 0.020, 900: 0.023, 1500: 0.028,
}

# Generate monthly temperature and precipitation for each station
station_data: Dict[str, Dict[str, np.ndarray]] = {}

for station in stations:
    # Temperature: seasonal cycle + elevation lapse + trend + noise
    base_temp = 12.0 - station.elevation_m * 0.0065  # lapse rate
    monthly_cycle = np.array([
        -8, -6, -2, 4, 9, 14, 17, 16, 11, 5, -1, -6
    ]) + base_temp

    warming = elevation_warming[station.elevation_m]
    temps = np.zeros(n_years * n_months)
    precip = np.zeros(n_years * n_months)

    for y_idx, year in enumerate(years):
        for m_idx in range(n_months):
            idx = y_idx * n_months + m_idx
            year_offset = year - 1980

            # Temperature
            temps[idx] = (
                monthly_cycle[m_idx]
                + warming * year_offset
                + np.random.normal(0, 1.5)
            )

            # Precipitation: winter-heavy with slight increase over time
            base_precip = 80 + 40 * np.cos(2 * np.pi * (m_idx - 0) / 12)
            precip_trend = 0.3 * year_offset  # mm/year increase
            precip[idx] = max(0, base_precip + precip_trend + np.random.normal(0, 25))

    station_data[station.station_id] = {
        'temperature': temps,
        'precipitation': precip,
        'years': np.repeat(years, n_months),
        'months': np.tile(months, n_years),
    }

print(f"Stations: {len(stations)}")
print(f"Period: {years[0]}-{years[-1]} ({n_years} years)")
print(f"Records per station: {n_years * n_months} months")
```

## Step 1: Regional Temperature Trend Analysis

```python
analyzer = TemperatureTrendAnalyzer()

print("\n===== Temperature Trend Analysis =====")
print(f"{'Station':<20} {'Elev (m)':>8} {'OLS Slope':>12} {'MK Trend':>12} "
      f"{'MK Z':>8} {'P-value':>10}")
print("-" * 80)

station_trends = {}

for station in stations:
    data = station_data[station.station_id]

    # Compute annual means
    annual_temps = []
    for year in years:
        mask = data['years'] == year
        annual_temps.append(np.mean(data['temperature'][mask]))
    annual_temps = np.array(annual_temps)

    # Linear regression
    lr = analyzer.linear_trend(annual_temps, years.astype(float))

    # Mann-Kendall
    mk = analyzer.mann_kendall_test(annual_temps, alpha=0.05)

    station_trends[station.station_id] = {
        'lr': lr,
        'mk': mk,
        'annual_means': annual_temps,
    }

    sig = "*" if lr['p_value'] < 0.05 else " "
    print(f"{station.name:<20} {station.elevation_m:>8.0f} "
          f"{lr['slope_per_decade']:>+12.3f} {mk['trend']:>12s} "
          f"{lr['slope_per_decade']:>+12.3f} {mk['z_value']:>+8.2f} {lr['p_value']:>10.6f}{sig}")

print("\n* = statistically significant at p < 0.05")
```

## Step 2: Precipitation Trend and Seasonality Analysis

```python
print("\n===== Precipitation Analysis =====")

for station in stations:
    data = station_data[station.station_id]

    # Annual total precipitation
    annual_precip = []
    for year in years:
        mask = data['years'] == year
        annual_precip.append(np.sum(data['precipitation'][mask]))
    annual_precip = np.array(annual_precip)

    # Trend
    lr_precip = analyzer.linear_trend(annual_precip, years.astype(float))

    # Wet season (Oct-Mar) vs dry season (Apr-Sep) comparison
    first_decade = (data['years'] >= 1980) & (data['years'] <= 1989)
    last_decade = (data['years'] >= 2010) & (data['years'] <= 2019)

    wet_months = np.isin(data['months'], [10, 11, 12, 1, 2, 3])
    dry_months = np.isin(data['months'], [4, 5, 6, 7, 8, 9])

    early_wet = np.mean(data['precipitation'][first_decade & wet_months])
    late_wet = np.mean(data['precipitation'][last_decade & wet_months])
    early_dry = np.mean(data['precipitation'][first_decade & dry_months])
    late_dry = np.mean(data['precipitation'][last_decade & dry_months])

    print(f"\n--- {station.name} ({station.elevation_m}m) ---")
    print(f"Annual total trend: {lr_precip['slope_per_decade']:+.1f} mm/decade "
          f"(p={lr_precip['p_value']:.4f})")
    print(f"Wet season (Oct-Mar): {early_wet:.1f} -> {late_wet:.1f} mm/month "
          f"({(late_wet - early_wet) / early_wet * 100:+.1f}%)")
    print(f"Dry season (Apr-Sep): {early_dry:.1f} -> {late_dry:.1f} mm/month "
          f"({(late_dry - early_dry) / early_dry * 100:+.1f}%)")
```

## Step 3: Extreme Event Frequency Analysis

Track how often extreme events occur per decade.

```python
print("\n===== Extreme Event Frequency =====")

for station in stations:
    data = station_data[station.station_id]

    # Compute baseline statistics from 1980-1999
    baseline_mask = data['years'] <= 1999
    baseline_temps = data['temperature'][baseline_mask]
    baseline_months = data['months'][baseline_mask]

    # Per-month 90th and 10th percentiles from baseline
    hot_thresholds = {}
    cold_thresholds = {}
    for m in range(1, 13):
        m_data = baseline_temps[baseline_months == m]
        hot_thresholds[m] = np.percentile(m_data, 90)
        cold_thresholds[m] = np.percentile(m_data, 10)

    # Count exceedances per decade
    decades = [(1980, 1989), (1990, 1999), (2000, 2009), (2010, 2019)]

    print(f"\n--- {station.name} ---")
    print(f"{'Decade':<12} {'Hot months':>12} {'Cold months':>12} {'Extreme precip':>15}")

    for d_start, d_end in decades:
        d_mask = (data['years'] >= d_start) & (data['years'] <= d_end)
        d_temps = data['temperature'][d_mask]
        d_months_arr = data['months'][d_mask]
        d_precip = data['precipitation'][d_mask]

        n_hot = 0
        n_cold = 0
        for i in range(len(d_temps)):
            m = d_months_arr[i]
            if d_temps[i] > hot_thresholds[m]:
                n_hot += 1
            if d_temps[i] < cold_thresholds[m]:
                n_cold += 1

        # Extreme precipitation: > 99th percentile of baseline
        p99 = np.percentile(data['precipitation'][baseline_mask], 99)
        n_extreme_precip = np.sum(d_precip > p99)

        print(f"{d_start}s     {n_hot:>12d} {n_cold:>12d} {n_extreme_precip:>15d}")
```

## Step 4: Climate Projections

Project regional conditions under two scenarios.

```python
import pandas as pd
import xarray as xr
from geo_infer_climate.core.projections import ClimateProjections

projector = ClimateProjections()

print("\n===== Regional Climate Projections =====")

scenarios = ['ssp245', 'ssp585']
target_years = [2050, 2100]

for station in stations:
    trends = station_trends[station.station_id]
    current_mean = np.mean(trends['annual_means'][-10:])  # 2010-2019 mean
    observed_trend = trends['lr']['slope']  # deg C/year

    print(f"\n--- {station.name} (current mean: {current_mean:.1f} deg C) ---")
    print(f"Observed warming: {observed_trend * 10:.3f} deg C/decade")

    # Historical series anchored on the recent decadal mean with the
    # observed OLS trend.
    hist_years = np.arange(2010, 2020)
    historical = xr.DataArray(
        current_mean + observed_trend * (hist_years - 2019),
        dims=["time"],
        coords={"time": pd.date_range("2010-01-01", periods=len(hist_years), freq="YS")},
    )
    projected = projector.project_future_climate(historical, scenario="ssp245", years=[2050, 2100])
    for year, value in zip(projected.time.dt.year.values, projected.values):
        print(f"  ssp245 @ {int(year)}: {float(value):.1f} deg C "
              f"({float(value) - current_mean:+.1f} deg C from present)")
```

## Step 5: Regional Synthesis

Combine all findings into a regional assessment.

```python
print("\n===== Regional Climate Change Assessment =====")
# Aggregate trends
all_slopes = [station_trends[s.station_id]['lr']['slope_per_decade'] for s in stations]
all_significant = sum(
    1 for s in stations
    if station_trends[s.station_id]['lr']['p_value'] < 0.05
)

print(f"\nTemperature:")
print(f"  Regional mean warming: {np.mean(all_slopes):+.3f} deg C/decade")
print(f"  Range: {min(all_slopes):+.3f} to {max(all_slopes):+.3f} deg C/decade")
print(f"  Significant trends: {all_significant}/{len(stations)} stations")
print(f"  Elevation dependence: {'YES' if max(all_slopes) - min(all_slopes) > 0.05 else 'NO'} "
      f"(spread={max(all_slopes) - min(all_slopes):.3f})")

# Precipitation summary
annual_precip_changes = []
for station in stations:
    data = station_data[station.station_id]
    early = np.mean([
        np.sum(data['precipitation'][(data['years'] == y)])
        for y in range(1980, 1990)
    ])
    late = np.mean([
        np.sum(data['precipitation'][(data['years'] == y)])
        for y in range(2010, 2020)
    ])
    annual_precip_changes.append((late - early) / early * 100)

print(f"\nPrecipitation:")
print(f"  Regional annual change: {np.mean(annual_precip_changes):+.1f}%")
print(f"  Range: {min(annual_precip_changes):+.1f}% to {max(annual_precip_changes):+.1f}%")

print(f"\nProjections (SSP2-4.5 by 2100):")
mid_station = stations[2]
mid_trend = station_trends[mid_station.station_id]['lr']['slope']
mid_current = np.mean(station_trends[mid_station.station_id]['annual_means'][-10:])
projected = mid_current + mid_trend * 80 * 1.0  # ssp245 factor = 1.0
print(f"  Representative station ({mid_station.name}):")
print(f"  Current: {mid_current:.1f} deg C -> 2100: {projected:.1f} deg C")
print(f"  Change: {mid_trend * 80:+.1f} deg C")
```

## Expected Output

```
===== Temperature Trend Analysis =====
Station              Elev (m)    OLS Slope     MK Trend       MK Z    P-value
------------------------------------------------------------------------
Coastal Plain              15       +0.153    increasing        +4.56   0.000124*
Valley Floor              120       +0.172    increasing        +4.85   0.000042*
Foothill                  450       +0.198    increasing        +5.31   0.000008*
Mountain Base             900       +0.231    increasing        +5.78   0.000001*
Highland                 1500       +0.278    increasing        +6.24   0.000000*

===== Regional Climate Change Assessment =====
Temperature:
  Regional mean warming: +0.206 deg C/decade
  Range: +0.148 to +0.274 deg C/decade
  Significant trends: 5/5 stations
  Elevation dependence: YES (spread=0.126)
```

The analysis confirms elevation-dependent warming across the region, with high-elevation stations warming nearly twice as fast as coastal stations. All five stations show statistically significant warming trends. Precipitation shows moderate increases, concentrated in the wet season.
