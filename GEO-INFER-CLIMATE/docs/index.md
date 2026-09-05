# GEO-INFER-CLIMATE Documentation

GEO-INFER-CLIMATE provides climate data processing, trend analysis, anomaly detection, extreme event identification, and climate change projections. The module works with standard climate data formats (NetCDF, GRIB) and supports SSP scenarios for simplified future projections.

## Module Overview

GEO-INFER-CLIMATE operates across six functional areas:

1. **Data Processing** -- Load, validate, and transform climate datasets from CMIP6, ERA5, NCEP, and observational sources.
2. **Temperature Trends** -- Linear regression and Mann-Kendall non-parametric trend tests.
3. **Extreme Events** -- Detection of heatwaves, cold spells, droughts, floods, and compound events using percentile-based thresholds, plus return period estimation.
4. **Climate Indices** -- SPI, heat index, extreme indices, and a first-order Palmer-style drought index.
5. **Climate Projections** -- Simplified linear-scaling future projections under SSP scenarios (SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5).
6. **Specialized Analysis** -- Downscaling and bias correction, precipitation (IDF) analysis, impact assessment, and Koppen-Geiger climate classification.

## Core Capabilities

- **Multi-format data loading**: NetCDF (.nc), GRIB (.grib, .grib2), with xarray backend for efficient multi-dimensional array operations.
- **Dataset validation**: Check for required coordinates, time dimensions, spatial dimensions, data completeness, and missing values.
- **Parametric trends**: Ordinary least squares regression with slope, intercept, R-squared, p-value, standard error, and per-decade slope.
- **Non-parametric trends**: Mann-Kendall test with S statistic, variance calculation, Z value, and p-value.
- **Extreme event detection**: Percentile-based thresholds for heatwaves (90th), cold spells (10th), droughts (10th), floods (95th), with configurable minimum duration.
- **Climate projections**: Scenario-based scaling (SSP1-2.6 through SSP5-8.5) applied to historical linear trends (illustrative, not a model emulator).
- **Climate indices**: SPI, Rothfusz heat index, hot/cold day counts, Palmer-style drought index.
- **Koppen-Geiger classification**: Per-site and per-grid climate zone classification.

## Documentation Contents

- [Getting Started](getting_started.md) -- Installation, core concepts, first climate analysis
- [API Reference](api_reference.md) -- Class and method documentation
- [Basic Example: Temperature Anomaly Detection](examples/basic_example.md) -- Detect anomalies in a synthetic dataset
- [Advanced Example: Multi-Variable Climate Analysis](examples/advanced_example.md) -- Combined trend and extreme event analysis

## Architecture

```
geo_infer_climate/
  __init__.py              -- Public API (9 core classes)
  core/
    climate_data.py          -- ClimateDataProcessor (loading, validation)
    temperature_trends.py    -- TemperatureTrendAnalyzer (linear, Mann-Kendall)
    extreme_events.py        -- ExtremeEventAnalyzer (heatwave, drought, flood)
    projections.py           -- ClimateProjections (SSP scenario projections)
    precipitation_analysis.py -- PrecipitationAnalyzer (IDF, Gumbel, gamma)
    climate_indices.py       -- ClimateIndicesCalculator (SPI, heat index, PDSI-style)
    downscaling.py           -- DownscalingMethods (bias correction, interpolation)
    impact_assessment.py     -- ClimateImpactAssessor (agriculture, water)
    classification.py        -- ClimateClassifier (Koppen-Geiger)
```

## Quick Start

```python
import numpy as np
from geo_infer_climate.core.temperature_trends import TemperatureTrendAnalyzer

analyzer = TemperatureTrendAnalyzer()

# Generate 50 years of annual mean temperature data with warming trend
years = np.arange(1970, 2020)
temperatures = 14.5 + 0.02 * (years - 1970) + np.random.normal(0, 0.3, len(years))

# Linear regression trend
trend = analyzer.linear_trend(temperatures, years)
print(f"Slope: {trend['slope']:.4f} deg C/year")
print(f"Per decade: {trend['slope_per_decade']:.3f} deg C/decade")
print(f"R-squared: {trend['r_squared']:.3f}")
print(f"P-value: {trend['p_value']:.4f}")

# Mann-Kendall non-parametric test
mk = analyzer.mann_kendall_test(temperatures)
print(f"MK trend: {mk['trend']}")
print(f"MK p-value: {mk['p_value']:.4f}")
print(f"MK Z value: {mk['z_value']:.4f}")
```

## Key Concepts

**Mann-Kendall test** is a non-parametric trend test that does not require normal distribution. The test statistic S counts the number of positive minus negative differences between all pairs of observations. It is particularly useful for climate data which often has non-normal distributions and outliers.

**SSP scenarios** (Shared Socioeconomic Pathways) define future greenhouse gas concentration trajectories: SSP1-2.6 (sustainability), SSP2-4.5 (middle of the road), SSP3-7.0 (regional rivalry), SSP5-8.5 (fossil-fuel development). These drive the scaling factors for climate projections.

**Return periods** describe the expected interval between extreme events of a given magnitude. A 100-year return period means such an event has a 1% probability of occurring in any given year.