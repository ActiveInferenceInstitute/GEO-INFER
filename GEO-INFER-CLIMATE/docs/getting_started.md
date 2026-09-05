# Getting Started with GEO-INFER-CLIMATE

This guide covers installation, core concepts, and running your first climate analysis.

## Installation

```bash
uv pip install -e ./GEO-INFER-CLIMATE
```

### Dependencies

Required:

- `numpy` -- Numerical array operations
- `scipy` -- Statistical tests (linregress, distributions)
- `pandas` -- Tabular data handling
- `xarray` -- Multi-dimensional climate data arrays

Optional (for tests and data loading):

- `netCDF4` -- NetCDF file reading
- `cfgrib` -- GRIB file reading (requires eccodes)
- `geopandas`, `h3`, `shapely` -- used by the test fixtures

## Core Concepts

### Climate Data Processing

`ClimateDataProcessor` handles loading and validation of climate datasets. Supported formats:

| Format | Extensions | Engine |
|--------|-----------|--------|
| NetCDF | `.nc`, `.netcdf` | xarray default |
| GRIB | `.grib`, `.grib2` | cfgrib |
| CSV | `.csv` | pandas |
| HDF5 | `.hdf5`, `.h5` | h5netcdf |

Supported dataset types: `cmip6`, `era5`, `ncep`, `observations`.

Validation checks: coordinate presence, time dimension, spatial dimensions (lat/lon), data completeness, missing value detection.

### Temperature Trend Analysis

`TemperatureTrendAnalyzer` provides two complementary methods:

**Linear regression** (`linear_trend`): Standard ordinary least squares fit. Returns slope, intercept, R-squared, p-value, standard error, and slope per decade. Requires at least 3 observations. NaN values are automatically excluded.

**Mann-Kendall test** (`mann_kendall_test`): Non-parametric trend test. The S statistic is:

```
S = sum_{i < j} sgn(x_j - x_i)
```
With variance: `Var(S) = n(n-1)(2n+5) / 18`

Returns trend direction ("increasing", "decreasing", "no trend"), the S statistic (`s_statistic`), the standardized Z value (`z_value`), p-value, and significance. Sen's slope is available separately via `sens_slope()`.


### Extreme Event Detection

`ExtremeEventAnalyzer` detects extreme weather events using percentile-based thresholds:

| Event Type | Default Percentile | Min Duration |
|-----------|-------------------|-------------|
| Heatwave | 90th | 3 days |
| Cold spell | 10th | 3 days |
| Drought | 10th | 30 days |
| Flood | 95th | 1 day |

Each detected event is summarized in a plain-dict `events` list with per-event indices, duration, and intensity; the result dictionary also carries the absolute threshold and day counts.

### Climate Indices

`ClimateIndicesCalculator` computes the Standardized Precipitation Index (gamma or normal distribution), the Rothfusz heat index, extreme indices (hot/cold days), and a first-order Palmer-style drought index (built on Thornthwaite potential evapotranspiration).

### Climate Projections

`ClimateProjections` extrapolates future climate from historical trends scaled by SSP scenario factors:

| Scenario | Factor | Description |
|----------|--------|-------------|
| SSP1-2.6 | 0.5 | Low emissions, sustainability pathway |
| SSP2-4.5 | 1.0 | Medium emissions, middle of the road |
| SSP3-7.0 | 1.5 | High emissions, regional rivalry |
| SSP5-8.5 | 2.0 | Very high emissions, fossil-fuel development |

Note: this is a simplified linear-scaling projection (illustrative, not a model emulator).

## First Example: Temperature Trend Detection

Analyze 50 years of synthetic annual mean temperature data to detect warming trends.

```python
import numpy as np
from geo_infer_climate.core.temperature_trends import TemperatureTrendAnalyzer

# Create analyzer
analyzer = TemperatureTrendAnalyzer()

# Generate 50 years of synthetic data with 0.02 deg C/year warming + noise
np.random.seed(42)
years = np.arange(1970, 2020)
base_temp = 14.5
warming_rate = 0.02  # deg C per year
noise = np.random.normal(0, 0.3, len(years))
temperatures = base_temp + warming_rate * (years - years[0]) + noise

print(f"Temperature range: {temperatures.min():.2f} to {temperatures.max():.2f} deg C")
print(f"Period: {years[0]} to {years[-1]} ({len(years)} years)")

# ---- Linear Regression ----
trend = analyzer.linear_trend(temperatures, years)

print("\n--- Linear Regression ---")
print(f"Slope: {trend['slope']:.5f} deg C/year")
print(f"Per decade: {trend['slope_per_decade']:.3f} deg C/decade")
print(f"R-squared: {trend['r_squared']:.4f}")
print(f"P-value: {trend['p_value']:.6f}")
print(f"Standard error: {trend['std_error']:.5f}")
print(f"Observations: {trend['n_observations']}")

significance = "statistically significant" if trend['p_value'] < 0.05 else "not significant"
print(f"Trend is {significance} at alpha=0.05")

# ---- Mann-Kendall Test ----
mk = analyzer.mann_kendall_test(temperatures, alpha=0.05)

print("\n--- Mann-Kendall Test ---")
print(f"Trend: {mk['trend']}")
print(f"S statistic: {mk['s_statistic']:.0f}")
print(f"Z-score: {mk['z_value']:.4f}")
print(f"P-value: {mk['p_value']:.6f}")
print(f"Significant: {mk['significant']}")
```

## Working with Extreme Events

Detect heatwaves in daily temperature data with the real API.

```python
import numpy as np
import xarray as xr
from geo_infer_climate.core.extreme_events import ExtremeEventAnalyzer

analyzer = ExtremeEventAnalyzer()

# Generate 10 years of daily temperature data
np.random.seed(42)
n_days = 365 * 10
days = np.arange(n_days)

# Seasonal cycle + trend + random variation
seasonal = 15.0 + 10.0 * np.sin(2 * np.pi * days / 365 - np.pi / 2)
trend = 0.001 * days  # slight warming
noise = np.random.normal(0, 3.0, n_days)
daily_temps = xr.DataArray(seasonal + trend + noise, dims=["time"])

# Add a few heatwave events (artificially boost temperatures)
values = daily_temps.values.copy()
for start in [500, 1200, 2800]:
    values[start:start + 5] += 8.0  # 5-day heatwave
daily_temps = xr.DataArray(values, dims=["time"])

# Detect heatwaves
result = analyzer.detect_heatwaves(daily_temps, threshold_percentile=90.0, min_duration=3)

print(f"90th percentile threshold: {result['threshold_temp']:.1f} deg C")
print(f"Heatwave events (>= 3 days): {result['events_detected']}")
print(f"Total hot days: {result['total_hot_days']}")
for event in result["events"]:
    print(f"  days {event['start_index']}-{event['end_index']}: "
          f"{event['duration_days']} days, peak={event['max_temp']:.1f} deg C")
```

## Climate Projections

Project future climate under SSP scenarios.

```python
import numpy as np
import pandas as pd
import xarray as xr
from geo_infer_climate.core.projections import ClimateProjections

projector = ClimateProjections()
print("Available scenarios:", projector.scenarios)

# Historical annual mean temperature with a 0.02 deg C/year warming trend
years = np.arange(1980, 2021)
historical = xr.DataArray(
    15.5 + 0.02 * (years - years[0]),
    dims=["time"],
    coords={"time": pd.date_range("1980-01-01", periods=len(years), freq="YS")},
)

projected = projector.project_future_climate(historical, scenario="ssp245", years=[2050, 2100])
print(projected)
```

## Working with Climate Data Files

Load and validate real climate datasets.

```python
from geo_infer_climate.core.climate_data import ClimateDataProcessor

processor = ClimateDataProcessor()

# Supported formats
print("Supported formats:", processor.supported_formats)
print("Supported datasets:", processor.supported_datasets)

# Load a NetCDF dataset (when you have one)
# ds = processor.load_dataset(
#     file_path="path/to/temperature_data.nc",
#     dataset_type="era5",
#     variables=["t2m"],  # 2-meter temperature
# )
#
# # Validate the dataset
# validation = processor.validate_dataset(ds)
# print(f"Has time dimension: {validation['has_time_dimension']}")
# print(f"Has spatial dims: {validation['has_spatial_dimensions']}")
# print(f"Data complete: {validation['data_complete']}")
```

## Next Steps

- Read the [API Reference](api_reference.md) for complete method documentation
- Follow the [Basic Example](examples/basic_example.md) for a full anomaly detection workflow
- Explore the [Advanced Example](examples/advanced_example.md) for multi-variable climate analysis