# GEO-INFER-MARINE API Reference

Complete API reference for the `geo_infer_marine` package.

## OceanographicDataProcessor

**Module**: `geo_infer_marine.core.oceanographic_data`

Load, process, and analyze 3D oceanographic datasets.

### Constructor

```python
OceanographicDataProcessor(config: Optional[Dict] = None)
```

### Methods

#### `load_oceanographic_data(file_path: str, variables: Optional[List[str]] = None) -> xr.Dataset`

Load oceanographic data from NetCDF files.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | -- | Path to `.nc` or `.netcdf` file |
| `variables` | `Optional[List[str]]` | `None` | Subset of variables to load |

**Returns**: `xr.Dataset` with oceanographic variables.

**Raises**: `ValueError` for unsupported file formats.

#### `process_3d_ocean_data(dataset: xr.Dataset, depth_levels: Optional[List[float]] = None) -> xr.Dataset`

Process 3D oceanographic data. Optionally subset to specific depth levels.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset` | `xr.Dataset` | -- | Dataset with depth dimension |
| `depth_levels` | `Optional[List[float]]` | `None` | Specific depth levels to extract |

**Returns**: Processed dataset.

#### `calculate_ocean_currents(u_velocity: xr.DataArray, v_velocity: xr.DataArray) -> xr.Dataset`

Calculate current magnitude and direction from U/V velocity components.

| Parameter | Type | Description |
|-----------|------|-------------|
| `u_velocity` | `xr.DataArray` | Eastward velocity (m/s) |
| `v_velocity` | `xr.DataArray` | Northward velocity (m/s) |

**Returns**: Dataset with `current_magnitude` (m/s) and `current_direction` (degrees from east, counterclockwise positive).

---

## CoastalAnalyzer

**Module**: `geo_infer_marine.core.coastal_analysis`

Coastal zone vulnerability and erosion assessment.

### Constructor

```python
CoastalAnalyzer(config: Optional[Dict] = None)
```

### Methods

#### `assess_coastal_vulnerability(elevation: xr.DataArray, sea_level: xr.DataArray, wave_height: Optional[xr.DataArray] = None) -> xr.Dataset`

Assess coastal vulnerability to sea-level rise. Vulnerability is computed as `1 / (relative_elevation + 1)`, amplified by wave height.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `elevation` | `xr.DataArray` | -- | Coastal DEM (meters above datum) |
| `sea_level` | `xr.DataArray` | -- | Sea level anomaly (meters) |
| `wave_height` | `Optional[xr.DataArray]` | `None` | Significant wave height (meters) |

**Returns**: Dataset with `relative_elevation` and `vulnerability_index`.

#### `analyze_coastal_erosion(shoreline_data: xr.DataArray, time_periods: list) -> xr.Dataset`

Analyze coastal erosion rates between time periods.

| Parameter | Type | Description |
|-----------|------|-------------|
| `shoreline_data` | `xr.DataArray` | Shoreline position with time dimension |
| `time_periods` | `list` | Time labels to compare |

**Returns**: Dataset with `erosion_rates` (positive = erosion, negative = accretion).

---

## MarineEcosystemModeler

**Module**: `geo_infer_marine.core.marine_ecosystems`

Marine ecosystem health assessment and habitat suitability modeling.

---

## SeaLevelAnalyzer

**Module**: `geo_infer_marine.core.sea_level`

Sea-level trend analysis and inundation zone mapping.

---

## MarineSpatialPlanner

**Module**: `geo_infer_marine.core.marine_spatial_planning`

Marine spatial planning tools for MPA design and ocean use zoning.

### Constructor

```python
MarineSpatialPlanner(config: Optional[Dict] = None)
```

### Methods

#### `design_mpa_network(biodiversity_data: xr.DataArray, threat_data: Optional[xr.DataArray] = None, target_coverage: float = 0.3) -> xr.Dataset`

Design an MPA network by selecting the highest-priority cells to meet coverage targets.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `biodiversity_data` | `xr.DataArray` | -- | Biodiversity index (higher = richer) |
| `threat_data` | `Optional[xr.DataArray]` | `None` | Threat/pressure data; amplifies priority |
| `target_coverage` | `float` | `0.3` | Target fraction of area for MPAs (0-1) |

Priority calculation: `priority = biodiversity_normalized * (1 + threat_normalized)`. Cells above the quantile threshold matching the coverage target are designated as MPAs.

**Returns**: Dataset with `mpa_mask` (boolean), `priority` (float), `coverage` (scalar fraction).

#### `optimize_offshore_wind_siting(wind_resource: xr.DataArray, depth: xr.DataArray, exclusion_zones: Optional[xr.DataArray] = None, max_depth: float = 50.0) -> xr.Dataset`

Optimize offshore wind farm locations based on wind resource and bathymetry.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `wind_resource` | `xr.DataArray` | -- | Wind speed or power potential |
| `depth` | `xr.DataArray` | -- | Water depth (meters, positive) |
| `exclusion_zones` | `Optional[xr.DataArray]` | `None` | Boolean mask of excluded areas |
| `max_depth` | `float` | `50.0` | Maximum viable installation depth |

Suitability = `wind_suitability * depth_suitability`. Depths beyond `max_depth` receive zero suitability.

**Returns**: Dataset with `suitability`, `wind_suitability`, `depth_suitability`.

---

## OceanCurrentModeler

**Module**: `geo_infer_marine.core.ocean_currents`

Ocean current field analysis and modeling.

---

## MarineWaterQuality

**Module**: `geo_infer_marine.core.water_quality`

Marine water quality index computation from temperature, salinity, dissolved oxygen, and chlorophyll measurements.

---

## CoralReefAssessor

**Module**: `geo_infer_marine.core.coral_reef`

Coral reef health monitoring and bleaching risk assessment.

---

## Data Format Conventions

### Coordinate Systems

All spatial data uses `EPSG:4326` (WGS84) by default. Depth uses positive-down convention (depth increases with depth).

### Standard Dimension Names

| Dimension | Name | Units |
|-----------|------|-------|
| Latitude | `lat` | decimal degrees |
| Longitude | `lon` | decimal degrees |
| Depth | `depth` | meters (positive down) |
| Time | `time` | datetime64 |

### NetCDF Compatibility

The `OceanographicDataProcessor.load_oceanographic_data()` method reads standard CF-compliant NetCDF files (`.nc`, `.netcdf`). Common sources include:

- Copernicus Marine Service (CMEMS)
- NOAA NCEP reanalysis
- HYCOM global ocean model
- GEBCO bathymetric grids
