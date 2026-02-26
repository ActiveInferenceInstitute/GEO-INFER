# GEO-INFER-CLIMATE Documentation

GEO-INFER-CLIMATE provides climate data processing, trend analysis, anomaly detection, extreme event identification, and climate change projections. The module works with standard climate data formats (NetCDF, GRIB) and supports CMIP6 scenarios for future projections.

## Module Overview

GEO-INFER-CLIMATE operates across five functional areas:

1. **Data Processing** -- Load, validate, and transform climate datasets from CMIP6, ERA5, NCEP, and observational sources.
2. **Temperature Trends** -- Linear regression and Mann-Kendall non-parametric trend tests with Sen's slope estimator.
3. **Extreme Events** -- Detection of heatwaves, cold spells, droughts, floods, and extreme precipitation using percentile-based thresholds.
4. **Climate Projections** -- Future climate projections under SSP scenarios (SSP1-2.6, SSP2-4.5, SSP3-7.0, SSP5-8.5).
5. **Impact Assessment** -- Climate impact classification, downscaling, and precipitation analysis.

## Core Capabilities

- **Multi-format data loading**: NetCDF (.nc), GRIB (.grib, .grib2), with xarray backend for efficient multi-dimensional array operations.
- **Dataset validation**: Check for required coordinates, time dimensions, spatial dimensions, data completeness, and missing values.
- **Parametric trends**: Ordinary least squares regression with slope, intercept, R-squared, p-value, standard error, and per-decade slope.
- **Non-parametric trends**: Mann-Kendall test with S statistic, variance calculation, Z-score, p-value, and Sen's slope median estimator.
- **Extreme event detection**: Percentile-based thresholds for heatwaves (90th), cold spells (10th), drought (10th), floods (95th), extreme precipitation (99th), with configurable minimum duration.
- **Climate projections**: Scenario-based scaling (SSP1-2.6 through SSP5-8.5) applied to historical trends.
- **Climate indices**: Standard climate indices including consecutive dry days, growing degree days, and frost days.

## Integration Points

| Module | Integration |
|--------|------------|
| GEO-INFER-SPACE | Spatial interpolation and H3 grid mapping for climate variables |
| GEO-INFER-TIME | Temporal analysis, seasonal decomposition, and time series management |
| GEO-INFER-BAYES | Bayesian uncertainty quantification for projections and trend significance |
| GEO-INFER-DATA | Data pipeline management for climate dataset ingestion |
| GEO-INFER-RISK | Climate hazard inputs for risk modeling |

## Documentation Contents

- [Getting Started](getting_started.md) -- Installation, core concepts, first climate analysis
- [API Reference](api_reference.md) -- Class and method documentation
- [Basic Example: Temperature Anomaly Detection](examples/basic_example.md) -- Detect anomalies in a synthetic dataset
- [Advanced Example: Multi-Variable Climate Analysis](examples/advanced_example.md) -- Combined trend and extreme event analysis

## Architecture

```
geo_infer_climate/
  core/
    climate_data.py          -- ClimateDataProcessor (loading, validation)
    temperature_trends.py    -- TemperatureTrendAnalyzer (linear, Mann-Kendall)
    extreme_events.py        -- ExtremeEventAnalyzer (heatwave, drought, flood)
    projections.py           -- ClimateProjections (SSP scenario projections)
    precipitation_analysis.py -- Precipitation trend and intensity analysis
    climate_indices.py       -- Standard climate index calculations
    downscaling.py           -- Statistical downscaling methods
    impact_assessment.py     -- Climate impact classification
    classification.py        -- Climate zone classification
  models/
    climate_models.py        -- Data models for climate entities
  api/
    endpoints.py             -- REST API for climate analytics
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
print(f"Sen's slope: {mk['sens_slope']:.4f} deg C/year")
```

## Key Concepts

**Mann-Kendall test** is a non-parametric trend test that does not require normal distribution. The test statistic S counts the number of positive minus negative differences between all pairs of observations. It is particularly useful for climate data which often has non-normal distributions and outliers.

**Sen's slope** is the median of all pairwise slopes between data points. It provides a robust estimate of trend magnitude that is resistant to outliers, making it preferred over linear regression slope for climate trend reporting.

**SSP scenarios** (Shared Socioeconomic Pathways) define future greenhouse gas concentration trajectories: SSP1-2.6 (sustainability), SSP2-4.5 (middle of the road), SSP3-7.0 (regional rivalry), SSP5-8.5 (fossil-fuel development). These drive the scaling factors for climate projections.

**Return periods** describe the expected interval between extreme events of a given magnitude. A 100-year return period means such an event has a 1% probability of occurring in any given year.
