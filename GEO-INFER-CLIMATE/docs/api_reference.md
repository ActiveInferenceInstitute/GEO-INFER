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

#### `preprocess_dataset(dataset: xr.Dataset, operations: Optional[List[str]] = None) -> xr.Dataset`

Standardize coordinate names and apply common operations (e.g. `'detrend'`, `'remove_outliers'`).

#### `extract_temporal_subset(dataset: xr.Dataset, start_date: str, end_date: str) -> xr.Dataset`

Select a time slice (inclusive of both endpoints).

#### `extract_spatial_subset(dataset: xr.Dataset, lat_range: Tuple[float, float], lon_range: Tuple[float, float]) -> xr.Dataset`

Select a latitude/longitude bounding box.

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

#### `mann_kendall_test(time_series: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]`

Non-parametric Mann-Kendall trend test.

The test statistic S is computed as:

```
S = sum_{i < j} sgn(x_j - x_i)
```

Variance: `Var(S) = n(n-1)(2n+5) / 18` (adjusted for ties)

Returns:

| Key | Type | Description |
|-----|------|-------------|
| `s_statistic` | `int` | Mann-Kendall S value |
| `z_value` | `float` | Standardized Z statistic |
| `p_value` | `float` | Two-sided p-value |
| `trend` | `str` | `"increasing"`, `"decreasing"`, or `"no trend"` |
| `significant` | `bool` | `p_value < alpha` |
| `alpha` | `float` | Significance level used |
| `n_observations` | `int` | Number of observations used |

Returns a zero-valued "no trend" result if fewer than 4 observations.


#### `sens_slope(time_series: np.ndarray) -> Dict[str, float]`

Sen's slope estimator (median of all pairwise slopes) with a 95% confidence interval. Returns `median_slope`, `lower_ci`, `upper_ci`, `slope_per_decade`, `n_slopes`.

#### `detect_changepoint(time_series: np.ndarray) -> Dict[str, float]`

Single changepoint detection via the cumulative sum method (requires at least 6 observations). Returns `changepoint_index` (-1 if none), `mean_before`, `mean_after`, `magnitude`, `n_observations`.

#### `calculate_heat_island_effect(urban_temps: np.ndarray, rural_temps: np.ndarray) -> Dict[str, float]`

Urban heat island intensity (`T_urban - T_rural`). Returns `mean_uhi_c`, `max_uhi_c`, `min_uhi_c`, `std_uhi_c`, `urban_mean_c`, `rural_mean_c`, `n_observations`.

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
| `flood_percentile` | 95.0 | Streamflow percentile for flood |
| `extreme_precip_percentile` | 99.0 | Precipitation percentile for extreme event |

All `detect_*` methods accept `xr.DataArray` input whose first dimension is time; 1-D `(time,)` and 3-D `(time, lat, lon)` inputs are supported. Each returns a dictionary with an `events` list (plain dicts) plus summary counts.

#### `detect_heatwaves(temperature: xr.DataArray, threshold_percentile: float = 90.0, min_duration: int = 3) -> Dict[str, Any]`

Detect heatwave events from temperature data.

Returns dictionary with:

| Key | Type | Description |
|-----|------|-------------|
| `threshold_temp` | `float` | Absolute threshold derived from the percentile |
| `threshold_percentile` | `float` | Percentile used |
| `min_duration` | `int` | Minimum run length |
| `events_detected` | `int` | Number of qualifying events |
| `events` | `list[dict]` | Per event: `start_index`, `end_index`, `duration_days`, `max_temp`, `mean_temp`, and `cell` (`[lat_idx, lon_idx]`) for gridded input |
| `total_hot_days` | `int` | Number of days above the threshold |

#### `detect_cold_spells(temperature: xr.DataArray, threshold_percentile: float = 10.0, min_duration: int = 3) -> Dict[str, Any]`

Same structure as `detect_heatwaves` but for runs at or below the cold threshold; per-event keys are `min_temp` and `mean_temp`, and the summary adds `total_cold_days`.

#### `detect_droughts(precipitation: xr.DataArray, threshold_percentile: float = 10.0, min_duration: int = 30) -> Dict[str, Any]`

Detect droughts as consecutive runs with precipitation at or below the percentile threshold.

Returns dictionary with: `threshold_precip`, `threshold_percentile`, `min_duration`, `events_detected`, `events` (per event: `start_index`, `end_index`, `duration_days`, `min_precip`, `mean_precip`, and `cell` for gridded input), and `total_dry_days`.

#### `detect_floods(streamflow: xr.DataArray, threshold_percentile: float = 95.0, min_duration: int = 1) -> Dict[str, Any]`

Detect flood events from streamflow data.

Returns dictionary with: `threshold_flow`, `threshold_percentile`, `events_detected`, `events` (per event: `start_index`, `end_index`, `duration_days`, `peak_flow`, `mean_flow`, `exceedance_factor`), and `max_peak`.

#### `detect_compound_events(temperature: xr.DataArray, precipitation: xr.DataArray, temp_threshold_percentile: float = 90.0, precip_threshold_percentile: float = 10.0) -> Dict[str, Any]`

Detect compound hot-and-dry events. Returns `compound_type`, `temp_threshold`, `precip_threshold`, `days_analyzed`, `compound_days`, `compound_frequency`, `events_detected`, `events`, and `correlation`.

#### `calculate_return_period(data: xr.DataArray, value: float, method: str = "gev") -> Dict[str, Any]`

Calculate the return period for an extreme value.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `xr.DataArray` | required | Historical data for fitting |
| `value` | `float` | required | Event magnitude |
| `method` | `str` | `"gev"` | `"empirical"` (Weibull plotting position `T = (n+1)/m`), `"gumbel"`, or `"gev"` (moment approximation) |

Returns:

| Key | Type | Description |
|-----|------|-------------|
| `value` | `float` | Input value |
| `method` | `str` | Method used |
| `return_period_years` | `Optional[float]` | Estimated return period (None if infinite) |
| `exceedance_probability` | `float` | Annual exceedance probability |
| `severity` | `str` | One of the `Severity` values, from the return period |
| `historical_stats` | `dict` | `mean`, `std`, `max`, `min` of the input data |

#### `calculate_climate_indices(temperature: xr.DataArray, precipitation: Optional[xr.DataArray] = None) -> Dict[str, Any]`

Standard climate extreme indices: `TXx`, `TNn`, `TX90p`, `TX10p`, `DTR`, `SU25`, `FD0`, `WSDI`; plus `PRCPTOT`, `RX1day`, `SDII`, `R10mm`, `R20mm`, `CDD`, `CWD` when precipitation is given. Returns `{"indices": {...}, "description": {...}}`.

#### `register_event(event: ExtremeEvent) -> str` / `get_event_statistics() -> Dict[str, Any]`

Registry for constructed `ExtremeEvent` records and per-type statistics.

---

## core.climate_indices

### ClimateIndicesCalculator

```python
class ClimateIndicesCalculator:
    def __init__(self, config: Optional[Dict] = None)
```

All methods operate along the `time` dimension; per-cell computation for gridded input is handled regardless of axis position.

#### `calculate_spi(precipitation: xr.DataArray, timescale: int = 3, distribution: str = 'gamma') -> xr.DataArray`

Standardized Precipitation Index. Precipitation is accumulated with a rolling sum over `timescale` steps first; the first `timescale - 1` steps are NaN. With `distribution='gamma'` the gamma distribution is fit per cell (floc=0) with the Thom mixed-distribution correction for zero precipitation; `distribution='normal'` uses a z-score. The result is named `SPI_<timescale>`.

#### `calculate_heat_index(temperature: xr.DataArray, humidity: Optional[xr.DataArray] = None) -> xr.DataArray`

Apparent temperature. Without `humidity`, returns the input temperature (named `heat_index`); with relative humidity (0-100) applies the Rothfusz regression (result in deg C).

#### `calculate_extreme_indices(temperature: xr.DataArray, precipitation: Optional[xr.DataArray] = None) -> xr.Dataset`

Dataset with `hot_days` (above 90th percentile), `cold_days` (below 10th percentile), `max_temp`, `min_temp`; plus `heavy_precip_days` (above 95th percentile) and `total_precip` when precipitation is provided.

#### `calculate_pdsi(precipitation: xr.DataArray, temperature: xr.DataArray, awc: float = 100.0) -> xr.DataArray`

First-order Palmer-style drought severity index: Thornthwaite PET, monthly water balance `P - PET`, cumulative anomaly, z-score rescaling onto the Palmer scale, clipped to [-6, +6]. **This is not the full Palmer (1965) water-balance system**; `awc` is retained for API compatibility but unused. Input is monthly data.

---

## core.downscaling

### DownscalingMethods

```python
class DownscalingMethods:
    def __init__(self, config: Optional[Dict] = None)
```

#### `bias_correction(model_data: xr.DataArray, observed_data: xr.DataArray, method: str = 'linear') -> xr.DataArray`

Bias-correct model data against observations on the same grid.

| Method | Description |
|--------|-------------|
| `linear` | Mean and variance rescaling to the observed moments |
| `quantile` | Empirical quantile mapping: per-cell transfer function from 25 quantile pairs, applied by piecewise-linear interpolation; values outside the calibrated range are clamped to the endpoint corrections |

Raises `ValueError` for unknown methods.

#### `statistical_downscaling(coarse_data: xr.DataArray, method: str = 'linear') -> xr.DataArray`

Interpolation-only downscaling: refines the grid by a factor of two in latitude and longitude. `method` is the xarray interpolation method (`'linear'` or `'nearest'`); other values raise `ValueError`. Regression- and machine-learning-based downscaling are not implemented.

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

Project future climate values by extrapolating the historical linear trend from the historical mean, scaled by a scenario factor. **This is a simplified linear-scaling projection, not a climate model emulator or ensemble method.** The `time` coordinate may be datetime or numeric years. Raises `ValueError` for unknown scenarios.

**Scenario scaling factors:**

| Scenario | Factor |
|----------|--------|
| `ssp126` | 0.5 |
| `ssp245` | 1.0 |
| `ssp370` | 1.5 |
| `ssp585` | 2.0 |

---

## core.impact_assessment

### ClimateImpactAssessor

```python
class ClimateImpactAssessor:
    def __init__(self, config: Optional[Dict] = None)
```

#### `assess_agricultural_impact(temperature: xr.DataArray, precipitation: xr.DataArray, crop_type: str = 'wheat') -> xr.Dataset`

First-order stress model against per-crop optima (`wheat`: 20 deg C / 500 mm, `corn`: 25 / 600, `rice`: 28 / 1000; unknown crops use 22 / 500). Precipitation must be totals comparable to the annual optimum (mm), not daily values. Returns `temperature_stress`, `precipitation_stress`, `combined_impact`.

#### `assess_water_resources(precipitation: xr.DataArray, temperature: xr.DataArray, evapotranspiration: Optional[xr.DataArray] = None) -> xr.Dataset`

Simple water balance. When ET is omitted it is estimated with a crude linear temperature proxy (`ET = 0.5 * T` mm per step) — pass measured/modelled ET for meaningful results. Returns `water_balance`, `water_deficit`, `precipitation`, `evapotranspiration`.

---

## core.classification

### ClimateClassifier

```python
class ClimateClassifier:
    def __init__(self)
```

#### `koppen_geiger_classify(monthly_temp_c: np.ndarray, monthly_precip_mm: np.ndarray) -> Dict`

Classify one site from 12 monthly mean temperatures (deg C) and 12 monthly precipitation totals (mm) using the Koppen-Geiger system. The aridity threshold is `20 * T_ann` mm (2 * T_ann in cm), adjusted to `20 * T_ann + 280` when >= 70% of annual precipitation falls in the summer (warmer) half, `20 * T_ann + 140` for an even distribution, and left at `20 * T_ann` when >= 70% falls in the winter (cooler) half.

Returns `code`, `description`, `main_group`, `annual_temp_c`, `annual_precip_mm`, `temp_warmest_month`, `temp_coldest_month`, `months_above_10c`.

#### `classify_grid(monthly_temp: xr.DataArray, monthly_precip: xr.DataArray) -> xr.DataArray`

Koppen-Geiger classification per grid cell from monthly climatologies with exactly 12 time steps. Cells with NaN values map to an empty string.

---

## core.precipitation_analysis

### PrecipitationAnalyzer

```python
class PrecipitationAnalyzer:
    def __init__(self, config: Optional[Dict] = None)
```

#### `fit_idf_curve(annual_maxima: Dict[float, np.ndarray]) -> Dict[float, Dict[str, Any]]`

Fit Intensity-Duration-Frequency curves from annual maximum series keyed by duration in hours. Durations with fewer than 3 valid years are skipped; return periods are fixed at `[2, 5, 10, 25, 50, 100]` years. Each entry contains `duration_hours`, `n_years`, `gumbel_mu`, `gumbel_beta`, `mean_depth_mm`, `std_depth_mm`, and `return_period_intensities` (per return period: `depth_mm`, `intensity_mm_h`).

#### `gumbel_return_period(annual_maxima: np.ndarray, design_value: float) -> Dict[str, Optional[float]]`

Return period for a rainfall value via Gumbel distribution moments (requires at least 3 valid years). Returns `exceedance_probability`, `return_period_years`, `gumbel_beta`, `gumbel_mu`.

#### `rainfall_depth_for_return_period(annual_maxima: np.ndarray, return_period_years: float) -> Dict[str, float]`

Design rainfall depth for a given return period via the fitted Gumbel distribution.

#### `calculate_precipitation_statistics(daily_precip: np.ndarray) -> Dict[str, float]`

Standard daily precipitation statistics: `total_mm`, `mean_daily_mm`, `max_daily_mm`, `std_daily_mm`, `wet_day_count`, `dry_day_count`, `wet_day_fraction`, `mean_wet_day_mm`, `max_consecutive_dry_days`, `max_consecutive_wet_days`, `percentile_95_mm`, `percentile_99_mm`, `n_days`.

#### `fit_gamma_distribution(wet_day_precip: np.ndarray) -> Dict[str, float]`

Fit a gamma distribution to wet-day precipitation. Returns `alpha` (shape), `beta` (scale), `loc`, `mean`, `variance` (and zeroed values when no wet days are supplied).