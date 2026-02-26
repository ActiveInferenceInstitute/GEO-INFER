# GEO-INFER-FOREST API Reference

Complete API reference for the `geo_infer_forest` package.

## ForestInventory

**Module**: `geo_infer_forest.core.forest_inventory`

Forest inventory and biomass estimation from spatial data.

### Constructor

```python
ForestInventory(config: Optional[Dict] = None)
```

### Methods

#### `estimate_biomass(forest_cover: xr.DataArray, tree_density: Optional[xr.DataArray] = None) -> xr.DataArray`

Estimate forest biomass from cover percentage and optional tree density.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `forest_cover` | `xr.DataArray` | -- | Forest cover percentage (0-100) |
| `tree_density` | `Optional[xr.DataArray]` | `None` | Tree density data; normalizes to max value |

**Returns**: Biomass in tons/ha. Base rate is 100 t/ha for 100% mature forest cover.

#### `calculate_forest_area(forest_cover: xr.DataArray, cell_area: Optional[xr.DataArray] = None) -> xr.DataArray`

Calculate forest area per cell.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `forest_cover` | `xr.DataArray` | -- | Forest cover percentage (0-100) |
| `cell_area` | `Optional[xr.DataArray]` | `None` | Area per cell in km2 (defaults to 0.1 km2) |

**Returns**: Forest area per cell in km2.

---

## CarbonSequestrationModeler

**Module**: `geo_infer_forest.core.carbon_sequestration`

Carbon stock and sequestration rate modeling for forests.

### Constructor

```python
CarbonSequestrationModeler(config: Optional[Dict] = None)
```

**Attributes**:
- `carbon_fraction` (`float`): Carbon content as fraction of dry biomass. Default: 0.5.

### Methods

#### `calculate_carbon_stock(biomass: xr.DataArray) -> xr.DataArray`

Convert biomass to carbon stock.

| Parameter | Type | Description |
|-----------|------|-------------|
| `biomass` | `xr.DataArray` | Forest biomass in tons/ha |

**Returns**: Carbon stock in tC/ha (biomass * 0.5).

#### `estimate_sequestration_rate(biomass_growth: xr.DataArray, time_period: float = 1.0) -> xr.DataArray`

Estimate carbon sequestration rate from annual biomass growth.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `biomass_growth` | `xr.DataArray` | -- | Annual biomass growth (t/ha/year) |
| `time_period` | `float` | `1.0` | Time period in years |

**Returns**: Sequestration rate in tC/ha/year.

#### `calculate_carbon_credits(carbon_sequestration: xr.DataArray, area: xr.DataArray, price_per_ton: float = 50.0) -> xr.DataArray`

Calculate carbon credit value. Converts C to CO2-eq (3.67x factor), multiplies by area and price.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `carbon_sequestration` | `xr.DataArray` | -- | Sequestration rate (tC/ha/year) |
| `area` | `xr.DataArray` | -- | Area in hectares |
| `price_per_ton` | `float` | `50.0` | Price per ton CO2-eq in USD |

**Returns**: Carbon credit value in USD/year.

---

## CanopyAnalyzer

**Module**: `geo_infer_forest.core.canopy_analysis`

Vegetation index computation, canopy cover estimation, LAI, and gap detection.

### Constructor

```python
CanopyAnalyzer(config: Optional[Dict] = None)
```

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `ndvi_forest_threshold` | `float` | `0.4` | NDVI threshold for forest classification |
| `ndvi_dense_threshold` | `float` | `0.7` | NDVI threshold for dense canopy |

### Methods

#### `calculate_ndvi(red: xr.DataArray, nir: xr.DataArray) -> xr.DataArray`

Calculate Normalized Difference Vegetation Index: `(NIR - Red) / (NIR + Red)`.

**Returns**: NDVI values clamped to [-1, 1]. Named `"ndvi"`.

#### `calculate_evi(red: xr.DataArray, nir: xr.DataArray, blue: xr.DataArray, gain: float = 2.5, c1: float = 6.0, c2: float = 7.5, l_soil: float = 1.0) -> xr.DataArray`

Calculate Enhanced Vegetation Index: `G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L)`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gain` | `float` | `2.5` | Gain factor G |
| `c1` | `float` | `6.0` | Atmospheric resistance coefficient (red) |
| `c2` | `float` | `7.5` | Atmospheric resistance coefficient (blue) |
| `l_soil` | `float` | `1.0` | Canopy background adjustment |

**Returns**: EVI values clamped to [-1, 1]. Named `"evi"`.

#### `estimate_canopy_cover(ndvi: xr.DataArray, method: str = "linear") -> xr.DataArray`

Estimate fractional vegetation cover (FVC) from NDVI.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ndvi` | `xr.DataArray` | -- | NDVI values |
| `method` | `str` | `"linear"` | `"linear"` or `"squared"` FVC model |

**Constants**: NDVI_soil = 0.05, NDVI_veg = 0.90.

**Returns**: Canopy cover percentage (0-100). Named `"canopy_cover_pct"`.

#### `estimate_leaf_area_index(ndvi: xr.DataArray, k_ext: float = 0.5) -> xr.DataArray`

Estimate LAI using Beer-Lambert law: `LAI = -ln(1 - FVC) / k_ext`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `k_ext` | `float` | `0.5` | Light extinction coefficient (broadleaf default) |

**Returns**: LAI in m2/m2. Named `"lai"`.

#### `detect_canopy_gaps(ndvi: xr.DataArray, gap_threshold: Optional[float] = None, min_gap_pixels: int = 1) -> xr.Dataset`

Detect canopy gaps from NDVI. Gaps are pixels below the threshold where canopy is absent.

**Returns**: Dataset with `gap_mask` and `ndvi` variables. Attributes include `gap_fraction`, `gap_pixel_count`, `mean_gap_ndvi`, `mean_forest_ndvi`.

#### `classify_canopy_density(ndvi: xr.DataArray) -> xr.DataArray`

Classify canopy density into 5 categories:

| Class | NDVI Range | Label |
|-------|-----------|-------|
| 0 | < 0.2 | Non-forest |
| 1 | 0.2 - 0.4 | Sparse |
| 2 | 0.4 - 0.6 | Moderate |
| 3 | 0.6 - 0.8 | Dense |
| 4 | >= 0.8 | Very dense |

**Returns**: Integer classification. Named `"canopy_density_class"`.

---

## DeforestationDetector

**Module**: `geo_infer_forest.core.deforestation`

Change detection for identifying forest loss from satellite time series.

### Constructor

```python
DeforestationDetector(config: Optional[Dict] = None)
```

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `change_threshold` | `float` | `0.15` | Minimum NDVI decrease for deforestation flag |
| `confidence_level` | `float` | `0.95` | Statistical confidence for time-series detection |

### Methods

#### `detect_change_two_date(before: xr.DataArray, after: xr.DataArray, threshold: Optional[float] = None) -> xr.Dataset`

Two-date change detection. Flags pixels where NDVI decrease exceeds threshold and initial NDVI > 0.3.

**Returns**: Dataset with `change_magnitude`, `relative_change`, `deforestation_mask`. Attributes: `deforestation_rate`, `deforested_pixel_count`.

#### `detect_change_time_series(ndvi_series: xr.DataArray, window_size: int = 3) -> xr.Dataset`

Time-series change detection with rolling baseline z-scores.

**Returns**: Dataset with `z_score`, `significant_decrease`, `cumulative_loss`, `baseline_mean`.

#### `calculate_annual_deforestation_rate(forest_cover_series: xr.DataArray) -> Dict[str, float]`

Compound annual deforestation rate: `rate = 1 - (end/start)^(1/years)`.

**Returns**: Dictionary with `annual_rate_pct`, `total_loss_pct`, `cover_start_pct`, `cover_end_pct`, `years_covered`.

#### `calculate_fragmentation_index(forest_mask: xr.DataArray) -> Dict[str, float]`

Compute fragmentation metrics from a binary forest mask using 4-neighbor edge analysis.

**Returns**: Dictionary with `forest_fraction`, `edge_density`, `core_fraction`, `edge_pixel_count`, `core_pixel_count`, `fragmentation_index`.

---

## WildfireRiskAnalyzer

**Module**: `geo_infer_forest.core.wildfire_risk`

Wildfire risk scoring and fuel load estimation.

---

## ForestHealthMonitor

**Module**: `geo_infer_forest.core.forest_health`

Multi-factor forest health status monitoring integrating canopy, growth, and stress indicators.

---

## FireRiskAssessor

**Module**: `geo_infer_forest.core.fire_risk`

Spatial fire risk assessment combining fuel, weather, and topography factors.
