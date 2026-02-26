# GEO-INFER-CLIMATE API Reference

Complete class and method reference for the GEO-INFER-CLIMATE module.

---

## core.climate_data

### ClimateDataProcessor

Load, validate, and process climate datasets.

```python
class ClimateDataProcessor:
    def __init__(self, config: Optional[Dict] = None)
```

**Attributes:**

- `supported_formats`: `['netcdf', 'grib', 'csv', 'hdf5']`
- `supported_datasets`: `['cmip6', 'era5', 'ncep', 'observations']`

#### `load_dataset(file_path: str, dataset_type: str, variables: Optional[List[str]] = None) -> xr.Dataset`

Load a climate dataset from file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `str` | Path to the data file (.nc, .grib, .grib2) |
| `dataset_type` | `str` | One of `cmip6`, `era5`, `ncep`, `observations` |
| `variables` | `Optional[List[str]]` | Subset of variables to load |

Returns an `xarray.Dataset`. Raises `ValueError` for unsupported dataset types or file formats. Raises `FileNotFoundError` if the file does not exist.

#### `validate_dataset(dataset: xr.Dataset) -> Dict[str, bool]`

Validate dataset structure and quality.

Returns a dictionary with:

| Key | Description |
|-----|-------------|
| `has_coordinates` | Dataset has at least one coordinate |
| `has_time_dimension` | `time` dimension exists |
| `has_spatial_dimensions` | `lat`/`latitude` and `lon`/`longitude` dimensions exist |
| `data_complete` | All variables have data |
| `no_missing_values` | No NaN values in any variable |

---

## core.temperature_trends

### TemperatureTrendAnalyzer

Analyze temperature trends using parametric and non-parametric methods.

```python
class TemperatureTrendAnalyzer:
    def __init__(self, config: Optional[Dict] = None)
```

#### `linear_trend(time_series: np.ndarray, years: Optional[np.ndarray] = None) -> Dict[str, float]`

Ordinary least squares linear regression trend.

| Parameter | Type | Description |
|-----------|------|-------------|
| `time_series` | `np.ndarray` | Temperature observations |
| `years` | `Optional[np.ndarray]` | Corresponding year values; integer indices if None |

Returns:

| Key | Type | Description |
|-----|------|-------------|
| `slope` | `float` | Regression slope (deg C/year) |
| `intercept` | `float` | Regression intercept |
| `r_squared` | `float` | Coefficient of determination |
| `p_value` | `float` | Statistical significance |
| `std_error` | `float` | Standard error of slope |
| `slope_per_decade` | `float` | Slope multiplied by 10 |
| `n_observations` | `int` | Number of valid observations |

Returns zero-valued dict if fewer than 3 valid observations. NaN values in either array are excluded.

#### `mann_kendall_test(time_series: np.ndarray, alpha: float = 0.05) -> Dict[str, float]`

Non-parametric Mann-Kendall trend test.

The test statistic S is computed as:

```
S = sum_{i < j} sgn(x_j - x_i)
```

Variance: `Var(S) = n(n-1)(2n+5) / 18` (adjusted for ties)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_series` | `np.ndarray` | required | Temperature observations |
| `alpha` | `float` | 0.05 | Significance level |

Returns:

| Key | Type | Description |
|-----|------|-------------|
| `trend` | `str` | `"increasing"`, `"decreasing"`, or `"no trend"` |
| `s_statistic` | `float` | Mann-Kendall S value |
| `z_score` | `float` | Standardized Z statistic |
| `p_value` | `float` | Two-sided p-value |
| `sens_slope` | `float` | Sen's slope (median pairwise slope) |
| `sens_intercept` | `float` | Intercept from Sen's method |
| `n_observations` | `int` | Number of observations used |

---

## core.extreme_events

### ExtremeEventType (Enum)

| Value | Description |
|-------|------------|
| `HEATWAVE` | Extended period of high temperatures |
| `COLDSPELL` | Extended period of low temperatures |
| `DROUGHT` | Extended period of low precipitation |
| `FLOOD` | Excessive precipitation or water level event |
| `STORM` | Severe storm event |
| `EXTREME_PRECIPITATION` | Single-event extreme rainfall |
| `COMPOUND` | Multiple concurrent extreme events |

### Severity (Enum)

`MINOR`, `MODERATE`, `SEVERE`, `EXTREME`, `CATASTROPHIC`.

### ExtremeEvent (dataclass)

```python
@dataclass
class ExtremeEvent:
    event_id: str
    event_type: ExtremeEventType
    start_date: str
    end_date: str
    duration_days: int
    peak_value: float
    severity: Severity
    location: Optional[Tuple[float, float]] = None
    area_km2: Optional[float] = None
    return_period_years: Optional[float] = None
```

### ExtremeEventAnalyzer

```python
class ExtremeEventAnalyzer:
    def __init__(self, config: Optional[Dict] = None)
```

**Default thresholds:**

| Threshold | Default | Description |
|-----------|---------|-------------|
| `heatwave_percentile` | 90.0 | Temperature percentile for heatwave |
| `coldspell_percentile` | 10.0 | Temperature percentile for cold spell |
| `drought_percentile` | 10.0 | Precipitation percentile for drought |
| `flood_percentile` | 95.0 | Precipitation percentile for flood |
| `extreme_precip_percentile` | 99.0 | Precipitation percentile for extreme event |

#### `detect_heatwaves(temperature: xr.DataArray, threshold_percentile: float = 90.0, min_duration: int = 3) -> Dict[str, Any]`

Detect heatwave events from temperature data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | `xr.DataArray` | required | Daily temperature data |
| `threshold_percentile` | `float` | 90.0 | Percentile threshold |
| `min_duration` | `int` | 3 | Minimum consecutive days |

Returns dictionary with: `events` (list of ExtremeEvent), `threshold_value`, `n_events`, `total_heatwave_days`, `max_duration`, `max_peak_value`.

#### `detect_cold_spells(temperature: xr.DataArray, threshold_percentile: float = 10.0, min_duration: int = 3) -> Dict[str, Any]`

Same structure as `detect_heatwaves` but for cold spells below the threshold percentile.

#### `detect_drought(precipitation: xr.DataArray, threshold_percentile: float = 10.0, min_duration: int = 30) -> Dict[str, Any]`

Detect drought periods from precipitation data.

#### `detect_extreme_precipitation(precipitation: xr.DataArray, threshold_percentile: float = 99.0) -> Dict[str, Any]`

Detect single-day extreme precipitation events.

#### `calculate_return_period(values: np.ndarray, event_value: float) -> float`

Calculate the return period in years for an event of given magnitude using the Weibull plotting position formula: `T = (n + 1) / m` where m is the rank of the event in descending order.

---

## core.projections

### ClimateProjections

```python
class ClimateProjections:
    def __init__(self, config: Optional[Dict] = None)
```

**Attributes:**

- `scenarios`: `['ssp126', 'ssp245', 'ssp370', 'ssp585']`

#### `project_future_climate(historical_data: xr.DataArray, scenario: str = 'ssp245', years: List[int] = None) -> xr.DataArray`

Project future climate values.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `historical_data` | `xr.DataArray` | required | Historical climate data with time dimension |
| `scenario` | `str` | `'ssp245'` | SSP scenario identifier |
| `years` | `List[int]` | `[2050, 2100]` | Target projection years |

Returns an `xr.DataArray` with projected values at each target year. Raises `ValueError` for unknown scenarios.

**Scenario scaling factors:**

| Scenario | Factor | Warming by 2100 (approximate) |
|----------|--------|-------------------------------|
| `ssp126` | 0.5 | +1.0 to +1.8 deg C |
| `ssp245` | 1.0 | +2.1 to +3.5 deg C |
| `ssp370` | 1.5 | +2.8 to +4.6 deg C |
| `ssp585` | 2.0 | +3.3 to +5.7 deg C |

---

## core.climate_indices

### Climate Index Functions

Standard climate indices for characterizing climate variability.

#### `consecutive_dry_days(precipitation: np.ndarray, threshold: float = 1.0) -> int`

Maximum number of consecutive days with precipitation below `threshold` mm.

#### `growing_degree_days(temperature: np.ndarray, base_temp: float = 10.0) -> float`

Sum of (daily_temp - base_temp) for all days where daily_temp > base_temp.

#### `frost_days(min_temperature: np.ndarray) -> int`

Count of days where minimum temperature is below 0 deg C.

#### `tropical_nights(min_temperature: np.ndarray, threshold: float = 20.0) -> int`

Count of days where minimum temperature remains above `threshold` deg C.

#### `precipitation_concentration_index(monthly_precipitation: np.ndarray) -> float`

Measure of precipitation seasonality. Ranges from 8.3 (uniform) to 100 (concentrated in single month).

---

## core.downscaling

### Statistical Downscaling

Methods for increasing spatial resolution of climate data.

#### `bias_correction_quantile_mapping(observed, modeled_historical, modeled_future) -> np.ndarray`

Apply quantile mapping bias correction to adjust modeled climate data to match observed distributions.

#### `delta_method(observed_baseline, modeled_baseline, modeled_future) -> np.ndarray`

Apply delta change method: add the modeled change signal to the observed baseline.

---

## core.precipitation_analysis

### Precipitation Analysis

Tools for analyzing precipitation patterns.

#### `intensity_duration_frequency(precipitation: np.ndarray, durations: List[int], return_periods: List[float]) -> Dict`

Compute IDF curves for given durations and return periods using Gumbel distribution fitting.

#### `seasonal_decomposition(monthly_data: np.ndarray) -> Dict[str, np.ndarray]`

Decompose precipitation into trend, seasonal, and residual components.
