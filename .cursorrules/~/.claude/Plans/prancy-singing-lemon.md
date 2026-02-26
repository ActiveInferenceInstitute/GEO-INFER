# GEO-INFER-PLACE: Comprehensive Modularity & Test Coverage Plan

## Context

GEO-INFER-PLACE has solid core implementations (zero illegitimate stubs, real H3 integrations, working API clients, graceful degradation) but fails on **documentation accuracy**, **export completeness**, and **test coverage** (~45%). Three blockers prevent it from being production-reliable:

1. **README.md describes a completely different API** — promises `PlaceAnalyzer`, `PlacemakingPlanner`, `PlaceSemantics` (none exist in PLACE; `PlaceAnalyzer` is actually a SPACE class). Anyone following the docs gets `ImportError` or `None`.
2. **Main `__init__.py` exports only 5 of 19 H3 functions** and has a broken `create_analyzer()` that returns a SPACE class instead of a PLACE class.
3. **7 source modules are completely untested**: `place_interface.py` (359 lines, the primary API), `unified_backend.py` (1484 lines), `comprehensive_dashboard.py`, `dashboard/core.py`, `dashboard/analyzers.py`, most of `integration.py`.

---

## Scope

**All paths relative to:** `GEO-INFER-PLACE/`

---

## Track 1 — Fix README.md (Documentation-Code Alignment)

**File:** `README.md`

Complete rewrite. The current README describes "sense of place / community identity" — a totally different design from the actual geospatial data analysis framework.

**New README must document:**
- Real entry point: `PlaceInterface` (not `PlaceAnalyzer`)
- Supported locations: `del_norte`, `cascadia`
- Four domain analyzers: `ForestHealthMonitor`, `CoastalResilienceAnalyzer`, `FireRiskAssessor`, `SeismicHazardAnalyzer`
- Real data sources: CAL FIRE, NOAA, USGS with retry+cache
- Module bridges: `PlaceDataManager` (DATA), `PlaceTemporalAnalyzer` (TIME)
- H3 spatial indexing utilities
- Cascadia agricultural pipeline (separate entry point: `cascadia_main.py`)

**Working code examples to include:**
```python
# Primary API
from geo_infer_place import PlaceInterface
pi = PlaceInterface("del_norte")
results = pi.run_full_analysis()
print(pi.status())

# Individual analyzers
forest = pi.get_analyzer("forest_health")
coastal = pi.get_analyzer("coastal_resilience")

# Data access
quakes = pi.get_earthquakes()
tides = pi.get_tide_data()
fires = pi.get_fire_perimeters(start_year=2020)
```

**Remove all references to:** `PlaceAnalyzer.assess()`, `PlacemakingPlanner`, `PlaceSemantics`, `PlaceContext`, `PlaceEvaluator`, `PlaceReasoner`, `PlaceRecommender` — these do not exist in geo_infer_place.

---

## Track 2 — Fix `src/geo_infer_place/__init__.py`

**File:** `src/geo_infer_place/__init__.py`

### 2a. Fix broken `create_analyzer()` function (lines 145-168)

Current code returns `geo_infer_space.PlaceAnalyzer` (which is `None` when SPACE not installed). Replace with PlaceInterface factory:

```python
def create_analyzer(location_code: str, config_path: Optional[str] = None) -> "PlaceInterface":
    """Create a PlaceInterface for a specific location."""
    supported = ["del_norte", "cascadia"]
    if location_code not in supported:
        raise ValueError(f"Location '{location_code}' not supported. Available: {supported}")
    return PlaceInterface(location=location_code)
```

### 2b. Complete H3 exports

Current `__init__.py` re-exports only 5 H3 functions. Add the missing 14 from `utils/h3_operations.py` to both the imports and `__all__`:

**Add to imports block (around line 76-82):**
```python
from .utils.h3_operations import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_latlng_boundary,   # ADD
    geo_to_cells,               # ADD
    polygon_to_cells,
    grid_disk,
    grid_distance,              # ADD
    grid_ring,                  # ADD
    cell_area,                  # ADD
    get_resolution,             # ADD
    is_valid_cell,
    are_neighbor_cells,         # ADD
    cells_to_geodataframe,      # ADD
    cell_to_parent,             # ADD
    cell_to_children,           # ADD
    compact_cells,              # ADD
    uncompact_cells,            # ADD
    estimate_cell_count,        # ADD
)
```

**Add all new names to `__all__`.**

### 2c. Clarify PlaceAnalyzer re-export

The current code re-exports `PlaceAnalyzer` from `geo_infer_space` (or `None`). This creates confusion. Add a docstring comment:

```python
# PlaceAnalyzer is geo_infer_space's spatial analyzer (may be None if SPACE not installed)
# For geo_infer_place functionality, use PlaceInterface instead.
```

Or better: don't export it from PLACE's `__all__` at all. It's a SPACE concern. Remove `PlaceAnalyzer`, `DataIntegrator` from `__all__` (keep the try/except import for internal use).

---

## Track 3 — Add Missing Tests (6 files)

### 3a. `tests/conftest.py` (new)

Shared fixtures for all tests:

```python
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def del_norte_bbox():
    return {"west": -124.408, "south": 41.458, "east": -123.536, "north": 42.006}

@pytest.fixture
def sample_h3_cells():
    """5 valid H3 res-8 cells near Del Norte County."""
    return [
        "882aa41503fffff", "882aa41501fffff", "882aa41507fffff",
        "882aa41505fffff", "882aa4150bfffff",
    ]

@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)

@pytest.fixture
def minimal_config(del_norte_bbox):
    return {
        "location": {"bounds": del_norte_bbox},
        "spatial": {"h3_resolution": 8},
        "analyses": {},
    }
```

### 3b. `tests/unit/test_place_interface.py` (new — CRITICAL)

Test the primary API class. Key tests:

```python
class TestPlaceInterfaceInit:
    def test_del_norte_location_valid(self):  # succeeds
    def test_cascadia_location_valid(self):   # succeeds
    def test_unknown_location_raises(self):   # ValueError
    def test_output_dir_created(self, temp_output_dir):

class TestPlaceInterfaceComponents:
    def test_integrator_lazy_init(self):  # first access creates it
    def test_data_manager_lazy_init(self):
    def test_temporal_lazy_init(self):
    def test_get_analyzer_forest_health(self):
    def test_get_analyzer_coastal_resilience(self):
    def test_get_analyzer_fire_risk(self):
    def test_get_analyzer_seismic_hazard(self):
    def test_get_analyzer_unknown_raises(self):  # ValueError
    def test_analyzer_cached_second_call(self):  # same object returned

class TestPlaceInterfaceRunAnalysis:
    def test_run_full_analysis_returns_dict(self, temp_output_dir):
    def test_run_full_analysis_has_required_keys(self, temp_output_dir):
        # keys: location, timestamp, config, analyses, temporal_analysis, data_quality, provenance
    def test_run_full_analysis_saves_json(self, temp_output_dir):
    def test_run_subset_analyzers(self, temp_output_dir):
        # analyzers=["seismic_hazard"] only runs one
    def test_analyzer_failure_doesnt_crash_pipeline(self, temp_output_dir):
        # mock one analyzer to raise, rest should still run

class TestPlaceInterfaceConvenience:
    def test_status_returns_dict(self):
    def test_status_has_required_keys(self):
        # keys: location, location_name, output_dir, data_module_available, etc.
    def test_get_earthquakes_returns_dict(self):  # real or synthetic
    def test_get_fire_perimeters_returns_dict(self):
    def test_get_weather_returns_dict(self):

class TestCreateAnalyzerFactory:
    def test_create_analyzer_del_norte(self):
    def test_create_analyzer_unknown_raises(self):
```

### 3c. `tests/unit/test_unified_backend.py` (new — CRITICAL)

Test `CascadianAgriculturalH3Backend`:

```python
class TestCascadianBackendInit:
    def test_initialization_with_resolution(self, temp_output_dir):
    def test_target_hexagons_property(self):  # returns list
    def test_modules_initially_empty(self):

class TestCascadianBackendH3Operations:
    def test_get_h3_cell_for_coordinate(self):
        # lat/lon in Del Norte → valid H3 cell returned
    def test_export_results_to_geojson(self, temp_output_dir):
    def test_cache_key_deterministic(self):

class TestCascadianBackendSPACEIntegration:
    def test_imports_without_space(self):  # graceful degradation
    def test_cell_to_boundary_returns_polygon(self, sample_h3_cells):
```

### 3d. `tests/unit/test_integration_wrappers.py` (new — HIGH)

Test `_CALFIREWrapper`, `_NOAAWrapper`, `_USGSWrapper` and `DelNorteDataIntegrator`:

```python
class TestCALFIREWrapper:
    def test_get_fire_perimeters_returns_dict(self):  # real or synthetic
    def test_get_fire_perimeters_has_features_key(self):
    def test_synthetic_fallback_has_valid_geojson(self):  # force fallback

class TestNOAAWrapper:
    def test_get_tide_gauge_data_returns_dict(self):
    def test_tide_data_has_series_or_error_key(self):
    def test_get_weather_data_returns_dict(self):

class TestUSGSWrapper:
    def test_get_earthquakes_returns_dict(self):
    def test_earthquakes_has_events_key(self):
    def test_get_cascadia_seismicity_returns_dict(self):

class TestDelNorteDataIntegrator:
    def test_has_all_three_clients(self):
    def test_calfire_client_is_cached_wrapper(self):
    def test_noaa_client_is_cached_wrapper(self):
    def test_usgs_client_is_cached_wrapper(self):
```

### 3e. `tests/unit/test_comprehensive_dashboard.py` (new — HIGH)

Test `DelNorteComprehensiveDashboard`:

```python
class TestDelNorteComprehensiveDashboard:
    def test_initialization(self, temp_output_dir):
    def test_run_analysis_returns_dict(self, temp_output_dir):
    def test_run_analysis_has_sections(self, temp_output_dir):
        # forest_health, coastal_resilience, fire_risk, seismic_hazard present
    def test_cross_domain_integration(self, temp_output_dir):
        # integrated_risk key present
    def test_map_generation(self, temp_output_dir):  # HTML file created
```

### 3f. `tests/unit/test_dashboard_advanced.py` (new — HIGH)

Test `AdvancedDashboard`, `ClimateAnalyzer`, `ZoningAnalyzer`, `AgroEconomicAnalyzer`:

```python
class TestClimateAnalyzer:
    def test_initialization(self):
    def test_run_analysis_returns_dict(self):
    def test_climate_zones_present(self):

class TestZoningAnalyzer:
    def test_initialization(self):
    def test_run_analysis_returns_dict(self):
    def test_zone_breakdown_present(self):

class TestAgroEconomicAnalyzer:
    def test_initialization(self):
    def test_run_analysis_returns_dict(self):

class TestAdvancedDashboard:
    def test_initialization(self, temp_output_dir):
    def test_generate_dashboard_creates_file(self, temp_output_dir):
    def test_layer_config_applied(self):
```

---

## Track 4 — Fix PlaceInterface Extensibility

**File:** `src/geo_infer_place/core/place_interface.py`

### 4a. Extract LOCATION_PRESETS to config

Move the hardcoded dict to `src/geo_infer_place/config/location_presets.yaml` and load it at module init. This allows new locations without modifying core code.

**New file:** `src/geo_infer_place/config/location_presets.yaml`
```yaml
del_norte:
  name: "Del Norte County, California"
  bounds: {west: -124.408, south: 41.458, east: -123.536, north: 42.006}
  h3_resolution: 8
  analyzers: [forest_health, coastal_resilience, fire_risk, seismic_hazard]
  data_sources: [calfire, noaa, usgs]

cascadia:
  name: "Cascadia Bioregion (BC, WA, OR, CA)"
  bounds: {west: -124.8, south: 40.0, east: -114.5, north: 49.0}
  h3_resolution: 7
  analyzers: [seismic_hazard, forest_health]
  data_sources: [usgs, noaa, calfire]
  note: "Full agricultural pipeline via cascadia_main.py"
```

**Updated PlaceInterface:**
```python
import yaml as _yaml

def _load_presets() -> dict:
    _cfg = Path(__file__).parent.parent / "config" / "location_presets.yaml"
    if _cfg.exists():
        with open(_cfg) as f:
            return _yaml.safe_load(f) or {}
    return _FALLBACK_PRESETS  # hardcoded dict as safety net

LOCATION_PRESETS = _load_presets()
```

### 4b. Fix `_create_analyzer()` graceful unknown handling

Currently raises `ValueError` on unknown analyzer names. Cascadia has `salmon_habitat` and `volcanic_hazard` in its analyzer list — these crash `run_full_analysis()`. Fix:

```python
def _create_analyzer(self, name: str) -> Any:
    # ... existing elif chain ...
    else:
        logger.warning("Analyzer '%s' not implemented for location '%s' — skipping", name, self.location)
        return None  # handled in run_full_analysis with None check
```

And in `run_full_analysis()`:
```python
analyzer = self.get_analyzer(name)
if analyzer is None:
    results["analyses"][name] = {"skipped": True, "reason": "not implemented"}
    continue
```

---

## Critical Files

| File | Action | Priority |
|------|--------|----------|
| `README.md` | Full rewrite — document real API | P1 |
| `src/geo_infer_place/__init__.py` | Fix create_analyzer(), complete H3 exports, remove PlaceAnalyzer from __all__ | P1 |
| `tests/conftest.py` | Create shared fixtures | P2 |
| `tests/unit/test_place_interface.py` | Create — PlaceInterface orchestration | P2 |
| `tests/unit/test_unified_backend.py` | Create — CascadianAgriculturalH3Backend | P2 |
| `tests/unit/test_integration_wrappers.py` | Create — API wrapper methods | P2 |
| `tests/unit/test_comprehensive_dashboard.py` | Create — dashboard init+run | P3 |
| `tests/unit/test_dashboard_advanced.py` | Create — AdvancedDashboard + analyzers | P3 |
| `src/geo_infer_place/config/location_presets.yaml` | Create — extracted presets | P3 |
| `src/geo_infer_place/core/place_interface.py` | Fix _create_analyzer() unknown handling; load from yaml | P3 |

---

## Verification

```bash
# 1. Module imports cleanly
python -c "from geo_infer_place import PlaceInterface, latlng_to_cell, cell_to_latlng_boundary, cells_to_geodataframe; print('OK')"

# 2. create_analyzer factory works
python -c "from geo_infer_place import create_analyzer; pi = create_analyzer('del_norte'); print(type(pi).__name__)"
# Expected: PlaceInterface

# 3. Full test suite passes
python -m pytest GEO-INFER-PLACE/tests/ -v --tb=short
# Target: 80+ tests passing (up from ~40)

# 4. PlaceInterface end-to-end smoke test
python << 'EOF'
from geo_infer_place import PlaceInterface
pi = PlaceInterface("del_norte")
s = pi.status()
assert s["location"] == "del_norte"
print("status OK:", s["data_module_available"], s["time_module_available"])
results = pi.run_full_analysis(analyzers=["seismic_hazard"])
assert "seismic_hazard" in results["analyses"]
print("run_full_analysis OK")
EOF

# 5. H3 export completeness
python -c "
from geo_infer_place import (latlng_to_cell, cell_to_latlng, cell_to_latlng_boundary,
    geo_to_cells, polygon_to_cells, grid_disk, grid_distance, grid_ring,
    cell_area, get_resolution, is_valid_cell, are_neighbor_cells,
    cells_to_geodataframe, cell_to_parent, cell_to_children)
print('All 14 H3 exports OK')
"
```

---

## What Is NOT Changing

- Source implementations are solid — no method rewrites needed
- Cascadia standalone pipeline remains separate (too large to merge in one plan)
- `PlaceDataManager` and `PlaceTemporalAnalyzer` graceful degradation patterns are correct
- H3 v4 usage throughout is correct
- API client retry/backoff logic is production quality
- Del Norte analyzer implementations are complete and well-tested
