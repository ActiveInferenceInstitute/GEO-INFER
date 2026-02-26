---
name: geo-infer-time
description: Time series analysis and temporal modeling for geospatial data. Use when analyzing temporal patterns, forecasting spatial time series, detecting change points, or working with spatio-temporal datasets.
prerequisites:
  required:
    - geo-infer-math
  recommended:
    - geo-infer-data
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-TIME

## Instructions

### Core Capabilities

- **Time series analysis**: Decomposition, trend detection, seasonality
- **Forecasting**: ARIMA, exponential smoothing, temporal GP
- **Change detection**: CUSUM, Bayesian change points, structural breaks
- **Temporal indexing**: Time-aware spatial queries, temporal resolution management
- **Spatio-temporal**: Joint analysis of spatial and temporal dimensions

### Key Imports

```python
from geo_infer_time.core.time_series import TimeSeriesAnalyzer
from geo_infer_time.core.forecasting import Forecaster
from geo_infer_time.core.change_detection import ChangePointDetector
```

## Examples

```python
from geo_infer_time.core.time_series import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer(frequency="daily")
decomposition = analyzer.decompose(series, method="stl")
trend = decomposition.trend
seasonal = decomposition.seasonal
```

## Guidelines


### Integrations

- Integrates with SPACE for spatio-temporal analysis
- ISO 8601 for all datetime handling
- Test: `uv run python -m pytest GEO-INFER-TIME/tests/ -v`
