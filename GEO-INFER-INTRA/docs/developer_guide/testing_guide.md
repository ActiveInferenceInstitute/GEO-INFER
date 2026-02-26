# GEO-INFER Testing Guide

> Complete reference for writing, running, and maintaining tests across the GEO-INFER framework.

This guide covers the full testing lifecycle for all 44 GEO-INFER modules: from
environment setup through unit, integration, property-based, and performance tests,
to CI integration and troubleshooting. All examples use real patterns from the
codebase, not hypothetical stubs.

## Table of Contents

- [1. Testing Philosophy](#1-testing-philosophy)
- [2. Test Environment Setup](#2-test-environment-setup)
- [3. Module Test Structure](#3-module-test-structure)
- [4. Standard conftest.py Pattern](#4-standard-conftestpy-pattern)
- [5. Unit Test Patterns](#5-unit-test-patterns)
- [6. Integration Test Patterns](#6-integration-test-patterns)
- [7. H3 v4 Test Patterns](#7-h3-v4-test-patterns)
- [8. Property-Based Testing with Hypothesis](#8-property-based-testing-with-hypothesis)
- [9. Performance Testing](#9-performance-testing)
- [10. Coverage Configuration](#10-coverage-configuration)
- [11. Running Tests](#11-running-tests)
- [12. CI Integration](#12-ci-integration)
- [13. Troubleshooting](#13-troubleshooting)

---

## 1. Testing Philosophy

GEO-INFER tests exist to verify that geospatial inference operations produce
mathematically correct results under realistic conditions. The following
principles govern all test code in the framework.

### Real Implementations Only

Every test must exercise actual logic. If a module function computes Moran's I,
the test must verify the computed value against a known reference, not against a
mocked return value. Never mock the module under test.

```python
# CORRECT: test exercises real computation
def test_morans_i_positive_autocorrelation():
    """Clustered spatial data must produce positive Moran's I."""
    weights = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    values = np.array([10.0, 10.5, 9.8])  # clustered values
    result = spatial_statistics.morans_i(values, weights)
    assert result > 0.0, "Clustered data must yield positive spatial autocorrelation"

# WRONG: test passes trivially regardless of implementation
def test_morans_i_placeholder():
    result = spatial_statistics.morans_i([], [])
    assert result is not None  # tells us nothing
```

### No Placeholder Tests

If a function is not implemented, do not write a test that passes trivially.
A test that asserts `result is not None` or `isinstance(result, dict)` without
checking contents is a placeholder. Write tests that will catch regressions.

### Active Inference Alignment

Mathematical correctness tests are as important as functional tests. For Active
Inference modules (ACT, BAYES, COG, AGENT), verify:

- Free energy is non-negative (F >= 0)
- Posterior variance is less than prior variance after observing data
- Belief distributions sum to 1.0
- KL divergence is non-negative

### Coverage Targets

| Test Category   | Target |
|-----------------|--------|
| Unit tests      | >= 80% |
| Integration     | >= 70% |
| Module overall  | >= 75% |

### Test Isolation

Each test function must be independent. Use fixtures for shared setup. Never
rely on test execution order or shared mutable state between tests.

---

## 2. Test Environment Setup

### Installing Dev Dependencies

Each module declares its test dependencies in `pyproject.toml` under the `[dev]`
extra. Install with:

```bash
# Install a single module in editable mode with dev dependencies
uv pip install -e "./GEO-INFER-MATH[dev]"

# Install multiple modules for cross-module integration testing
uv pip install -e "./GEO-INFER-MATH[dev]" -e "./GEO-INFER-SPACE[dev]" -e "./GEO-INFER-ACT[dev]"

# Install the full framework with quality/testing tools
uv pip install -e ".[quality]"
```

### pytest Configuration

The root `pyproject.toml` contains the shared pytest configuration. All modules
inherit these settings automatically:

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = [
    "GEO-INFER-*/tests",
    "tests",
]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "performance: marks tests as performance tests",
]
```

The `--strict-markers` flag ensures that any marker used in tests must be
registered. The `--strict-config` flag catches configuration errors early.

### Pytest Markers Reference

The following markers are available across the framework. Register any new
markers in the root `pyproject.toml` before using them.

| Marker | Description |
|--------|-------------|
| `unit` | Unit tests exercising a single function or class |
| `integration` | Tests spanning multiple modules or external services |
| `system` | Full system tests covering end-to-end workflows |
| `performance` | Benchmark and timing tests |
| `geospatial` | Tests requiring geospatial libraries (geopandas, h3, shapely) |
| `api` | Tests for REST/HTTP API endpoints |
| `slow` | Tests taking more than 10 seconds (excluded by default in dev) |
| `fast` | Tests completing in under 1 second |
| `bayesian` | Tests for Bayesian inference operations (BAYES module) |
| `active_inference` | Tests for Active Inference computations (ACT module) |
| `spatial` | Tests for spatial indexing, joins, and overlays |
| `temporal` | Tests for time series and temporal analysis |
| `h3` | Tests using the H3 hexagonal indexing system |
| `visualization` | Tests for chart, map, and plot generation |
| `cli` | Tests for command-line interfaces |
| `security` | Tests for authentication, authorization, encryption |
| `data_quality` | Tests for data validation and cleaning operations |
| `regression` | Tests that guard against specific past bugs |
| `smoke` | Quick sanity checks that core imports work |
| `parametrize` | Parametrized tests covering multiple input combinations |
| `serial` | Tests that must not run in parallel |
| `parallel` | Tests safe for parallel execution |
| `network` | Tests requiring network access |
| `gpu` | Tests requiring GPU hardware (CUDA/Metal) |
| `memory_intensive` | Tests requiring more than 2GB RAM |

Usage:

```python
import pytest

@pytest.mark.unit
@pytest.mark.spatial
def test_point_in_polygon():
    ...

@pytest.mark.slow
@pytest.mark.integration
def test_full_pipeline():
    ...
```

### Import Mode

The framework uses `importlib` import mode to avoid `sys.path` manipulation
issues. If you encounter import problems, verify the module is installed:

```bash
uv pip install -e ./GEO-INFER-MODULE
```

---

## 3. Module Test Structure

Every module follows a standard directory layout. This consistency enables the
unified test runner to discover and execute tests across all 44 modules.

```
GEO-INFER-MODULE/
├── tests/
│   ├── conftest.py              # Shared fixtures for this module
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_core.py         # Core algorithm tests
│   │   ├── test_models.py       # Data model tests
│   │   └── test_utils.py        # Utility function tests
│   └── integration/
│       ├── __init__.py
│       ├── test_pipeline.py     # Multi-component pipeline tests
│       └── test_cross_module.py # Tests with other GEO-INFER modules
├── src/geo_infer_module/
│   ├── __init__.py
│   ├── core/
│   ├── models/
│   ├── api/
│   └── utils/
└── pyproject.toml
```

### File Naming Conventions

- Test files: `test_<component>.py` (prefix, not suffix)
- Test classes: `Test<ComponentName>` (optional; function-style is preferred)
- Test functions: `test_<behavior_description>()`
- Fixtures: descriptive nouns (`sample_geodataframe`, `active_inference_state`)

### Test Discovery Rules

pytest discovers tests by:

1. Scanning directories listed in `testpaths` (all `GEO-INFER-*/tests` directories)
2. Matching files named `test_*.py` or `*_test.py`
3. Matching classes named `Test*` (no `__init__` method)
4. Matching functions named `test_*`

### Class vs Function Style

Function-style tests are preferred for most cases. Use classes only when tests
share significant setup or when testing a stateful object:

```python
# PREFERRED: function-style for stateless operations
def test_haversine_distance_zero_for_same_point():
    assert haversine(47.6, -122.3, 47.6, -122.3) == pytest.approx(0.0)

def test_haversine_distance_seattle_to_portland():
    dist = haversine(47.6062, -122.3321, 45.5152, -122.6784)
    assert 230 < dist < 280  # approximately 274 km


# ACCEPTABLE: class-style when tests share a complex fixture
class TestGaussianProcess:
    @pytest.fixture(autouse=True)
    def setup_gp(self):
        self.gp = GaussianProcess(kernel="rbf", length_scale=1.0)
        self.X_train = np.array([[0.0], [1.0], [2.0]])
        self.y_train = np.array([0.0, 1.0, 0.5])
        self.gp.fit(self.X_train, self.y_train)

    def test_posterior_mean_at_training_points(self):
        mean, _ = self.gp.predict(self.X_train)
        np.testing.assert_allclose(mean, self.y_train, atol=1e-6)

    def test_posterior_variance_less_than_prior(self):
        _, var = self.gp.predict(self.X_train)
        assert np.all(var < 1.0), "Posterior variance must be less than prior at training points"
```

---

## 4. Standard conftest.py Pattern

Every module should have a `tests/conftest.py` file providing shared fixtures.
A complete template is available at:

```
GEO-INFER-INTRA/docs/developer_guide/conftest_template.py
```

Copy it to your module and customize the module-specific section. The standard
fixtures provided are:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `sample_coordinates` | session | 10 (lat, lng) tuples across diverse US locations |
| `sample_h3_cells` | session | Resolution 8 H3 cells from `sample_coordinates` |
| `sample_geodataframe` | function | GeoDataFrame with points, CRS, and attributes |
| `sample_time_series` | function | 365-day Pandas Series with sinusoidal + noise |
| `sample_raster` | session | 100x100 numpy array with CRS metadata dict |
| `active_inference_state` | function | Generative model state for Active Inference tests |
| `tmp_spatial_dir` | function | Temp directory with .geojson and .csv sample files |

### Fixture Scoping

- **session**: Expensive objects that are read-only (coordinate lists, H3 cells,
  raster data). Created once per test session.
- **module**: Objects shared across a single test file. Rarely needed.
- **function** (default): Mutable objects that tests may modify
  (GeoDataFrames, dicts, time series). Fresh copy per test.

```python
@pytest.fixture(scope="session")
def sample_coordinates():
    """Session-scoped: created once, shared read-only across all tests."""
    return [(47.6062, -122.3321), (37.7749, -122.4194)]

@pytest.fixture(scope="function")
def sample_geodataframe():
    """Function-scoped: fresh GeoDataFrame for each test that requests it."""
    return gpd.GeoDataFrame(...)
```

See the full template file for complete implementations of all fixtures.

---

## 5. Unit Test Patterns

### MATH Module: Spatial Statistics

Testing Moran's I spatial autocorrelation. The key invariant: clustered data
produces positive autocorrelation, dispersed data produces negative.

```python
import numpy as np
import pytest
from geo_infer_math.core.spatial_statistics import morans_i, spatial_weights_matrix


class TestMoransI:
    """Test Moran's I spatial autocorrelation statistic."""

    def test_positive_autocorrelation(self):
        """Spatially clustered values must produce Moran's I > 0."""
        coords = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        values = np.array([10.0, 10.2, 9.8, 10.1])  # similar nearby
        W = spatial_weights_matrix(coords, method="knn", k=2)
        I = morans_i(values, W)
        assert I > 0.0, f"Expected positive autocorrelation, got I={I}"

    def test_negative_autocorrelation(self):
        """Checkerboard pattern must produce Moran's I < 0."""
        coords = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        values = np.array([10.0, 0.0, 0.0, 10.0])  # checkerboard
        W = spatial_weights_matrix(coords, method="knn", k=2)
        I = morans_i(values, W)
        assert I < 0.0, f"Expected negative autocorrelation, got I={I}"

    def test_range_bounds(self):
        """Moran's I is bounded approximately by [-1, 1]."""
        coords = np.array([[i, j] for i in range(5) for j in range(5)])
        values = np.random.uniform(0, 100, len(coords))
        W = spatial_weights_matrix(coords, method="knn", k=4)
        I = morans_i(values, W)
        assert -1.5 <= I <= 1.5, f"Moran's I out of expected range: {I}"

    @pytest.mark.parametrize("n_points", [10, 50, 100, 500])
    def test_scales_with_data_size(self, n_points):
        """Moran's I must compute without error for various data sizes."""
        coords = np.random.uniform(0, 100, (n_points, 2))
        values = np.random.normal(50, 10, n_points)
        W = spatial_weights_matrix(coords, method="knn", k=4)
        I = morans_i(values, W)
        assert np.isfinite(I), f"Non-finite result for n={n_points}"
```

### ACT Module: Free Energy Computation

Free energy F must always be non-negative. Belief updates must produce valid
probability distributions.

```python
import numpy as np
import pytest
from geo_infer_act.core.free_energy import compute_free_energy, update_beliefs


class TestFreeEnergy:
    """Test variational free energy computation."""

    def test_free_energy_non_negative(self, active_inference_state):
        """Variational free energy must be >= 0 for any valid state."""
        state = active_inference_state
        F = compute_free_energy(
            beliefs=state["beliefs"],
            observations=state["observations"],
            A=state["A"],
            B=state["B"],
        )
        assert F >= 0.0, f"Free energy must be non-negative, got F={F}"

    def test_free_energy_decreases_after_update(self, active_inference_state):
        """Belief updating must reduce free energy (or leave it unchanged)."""
        state = active_inference_state
        # Set an observation
        obs = np.zeros(state["n_obs"])
        obs[0] = 1.0
        state["observations"] = obs

        F_before = compute_free_energy(
            beliefs=state["beliefs"],
            observations=obs,
            A=state["A"],
            B=state["B"],
        )

        updated_beliefs = update_beliefs(
            prior=state["beliefs"],
            observation=obs,
            A=state["A"],
        )

        F_after = compute_free_energy(
            beliefs=updated_beliefs,
            observations=obs,
            A=state["A"],
            B=state["B"],
        )

        assert F_after <= F_before + 1e-10, (
            f"Free energy must not increase after belief update: "
            f"F_before={F_before}, F_after={F_after}"
        )

    def test_updated_beliefs_sum_to_one(self, active_inference_state):
        """Updated beliefs must be a valid probability distribution."""
        state = active_inference_state
        obs = np.zeros(state["n_obs"])
        obs[0] = 1.0

        updated = update_beliefs(
            prior=state["beliefs"],
            observation=obs,
            A=state["A"],
        )

        assert np.all(updated >= 0), "Beliefs must be non-negative"
        np.testing.assert_allclose(
            np.sum(updated), 1.0, atol=1e-10,
            err_msg="Beliefs must sum to 1.0"
        )
```

### BAYES Module: Gaussian Process Prediction

Posterior variance must be less than prior variance at training points. Posterior
mean must interpolate training data (up to numerical tolerance).

```python
import numpy as np
import pytest
from geo_infer_bayes.core.gaussian_process import GaussianProcess


class TestGaussianProcess:
    """Test GP prediction with Cholesky-based implementation."""

    @pytest.fixture
    def trained_gp(self):
        """GP fitted on a simple 1D function."""
        gp = GaussianProcess(kernel="rbf", length_scale=1.0, noise=1e-6)
        X_train = np.linspace(0, 5, 10).reshape(-1, 1)
        y_train = np.sin(X_train.ravel())
        gp.fit(X_train, y_train)
        return gp, X_train, y_train

    def test_posterior_mean_at_training_points(self, trained_gp):
        """Posterior mean must match training targets at training locations."""
        gp, X_train, y_train = trained_gp
        mean, _ = gp.predict(X_train)
        np.testing.assert_allclose(
            mean, y_train, atol=1e-4,
            err_msg="Posterior mean must interpolate training data"
        )

    def test_posterior_variance_less_than_prior(self, trained_gp):
        """Posterior variance must be reduced relative to prior at training points."""
        gp, X_train, _ = trained_gp
        _, variance = gp.predict(X_train)
        prior_variance = gp.kernel_variance  # prior signal variance
        assert np.all(variance < prior_variance), (
            "Posterior variance must be less than prior variance at training points"
        )

    def test_variance_increases_away_from_data(self, trained_gp):
        """Variance at distant test points must exceed variance at training points."""
        gp, X_train, _ = trained_gp
        _, var_at_data = gp.predict(X_train)
        X_far = np.array([[100.0]])
        _, var_far = gp.predict(X_far)
        assert var_far[0] > np.mean(var_at_data), (
            "Variance far from training data must exceed variance at training points"
        )

    @pytest.mark.parametrize("kernel", ["rbf", "matern32", "matern52"])
    def test_kernel_variants(self, kernel):
        """GP must train and predict with all supported kernels."""
        gp = GaussianProcess(kernel=kernel, length_scale=1.0, noise=1e-6)
        X = np.array([[0.0], [1.0], [2.0]])
        y = np.array([0.0, 1.0, 0.5])
        gp.fit(X, y)
        mean, var = gp.predict(X)
        assert mean.shape == (3,)
        assert var.shape == (3,)
        assert np.all(np.isfinite(mean))
        assert np.all(var >= 0)
```

### SPACE Module: H3 Hexagonal Indexing

Round-trip through H3: encoding a lat/lng to a cell and decoding the cell center
must return a point within the same cell.

```python
import pytest

try:
    import h3
    HAS_H3 = True
except ImportError:
    HAS_H3 = False


@pytest.mark.h3
@pytest.mark.skipif(not HAS_H3, reason="h3 not installed")
class TestH3Indexing:
    """Test H3 v4 spatial indexing operations."""

    @pytest.mark.parametrize("resolution", [4, 8, 12])
    def test_round_trip_encoding(self, resolution):
        """Encoding lat/lng to cell and back must return a point in the same cell."""
        lat, lng = 47.6062, -122.3321
        cell = h3.latlng_to_cell(lat, lng, resolution)
        center_lat, center_lng = h3.cell_to_latlng(cell)
        # The center of the cell must map back to the same cell
        assert h3.latlng_to_cell(center_lat, center_lng, resolution) == cell

    def test_cell_is_valid_string(self):
        """H3 cell index must be a 15-character hexadecimal string."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        assert isinstance(cell, str)
        assert len(cell) == 15

    def test_grid_disk_contains_origin(self):
        """grid_disk(cell, k) must include the origin cell."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        disk = h3.grid_disk(cell, k=1)
        assert cell in disk

    def test_grid_disk_size(self):
        """grid_disk(cell, k=1) must return exactly 7 cells (origin + 6 neighbors)."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        disk = h3.grid_disk(cell, k=1)
        assert len(disk) == 7

    def test_resolution_hierarchy(self):
        """Child cell at resolution r+1 must have parent at resolution r."""
        cell_r8 = h3.latlng_to_cell(47.6062, -122.3321, 8)
        parent = h3.cell_to_parent(cell_r8, 7)
        children = h3.cell_to_children(parent, 8)
        assert cell_r8 in children

    def test_cell_boundary_is_polygon(self):
        """cell_to_boundary must return a sequence of (lat, lng) pairs forming a ring."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        boundary = h3.cell_to_boundary(cell)
        assert len(boundary) >= 5  # hexagons have 6 vertices (can be 5 for pentagons)
        for vertex in boundary:
            assert len(vertex) == 2
            lat, lng = vertex
            assert -90 <= lat <= 90
            assert -180 <= lng <= 180
```

### Numerical Tolerance Patterns

Use `np.testing.assert_allclose` for floating-point comparisons, not bare
`assert ==`:

```python
import numpy as np

# CORRECT: use tolerance-aware comparison
np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-8)

# CORRECT: pytest.approx for scalar comparisons
assert result == pytest.approx(3.14159, rel=1e-5)

# WRONG: exact float comparison (will fail due to floating-point arithmetic)
# assert result == 3.14159265358979
```

### Parametrize Decorator Usage

Use `@pytest.mark.parametrize` to test multiple inputs without code duplication:

```python
@pytest.mark.parametrize("lat,lng,expected_continent", [
    (47.6062, -122.3321, "North America"),
    (51.5074, -0.1278, "Europe"),
    (-33.8688, 151.2093, "Oceania"),
    (35.6762, 139.6503, "Asia"),
])
def test_reverse_geocode_continent(lat, lng, expected_continent):
    result = reverse_geocode(lat, lng)
    assert result.continent == expected_continent
```

---

## 6. Integration Test Patterns

Integration tests verify that multiple modules work together correctly. They
are more expensive to run and may require multiple modules to be installed.

### SPACE + TIME + DATA Pipeline

```python
import pytest
import numpy as np
import pandas as pd

pytest.importorskip("geo_infer_space")
pytest.importorskip("geo_infer_time")
pytest.importorskip("geo_infer_data")


@pytest.mark.integration
class TestSpatioTemporalPipeline:
    """Integration test for the SPACE -> TIME -> DATA pipeline."""

    def test_spatial_temporal_aggregation(self, sample_geodataframe, sample_time_series):
        """Data indexed spatially and temporally must produce valid aggregates."""
        from geo_infer_space.core.indexing import spatial_index
        from geo_infer_time.core.temporal import temporal_resample
        from geo_infer_data.core.pipeline import DataPipeline

        # Step 1: spatial indexing
        indexed = spatial_index(sample_geodataframe, resolution=8)
        assert "h3_cell" in indexed.columns

        # Step 2: temporal resampling
        monthly = temporal_resample(sample_time_series, freq="ME")
        assert len(monthly) == 12

        # Step 3: pipeline joins spatial and temporal
        pipeline = DataPipeline()
        result = pipeline.join_spatiotemporal(indexed, monthly)
        assert not result.empty
        assert "h3_cell" in result.columns
        assert "timestamp" in result.columns
```

### BAYES + ACT Pipeline

```python
import pytest
import numpy as np

pytest.importorskip("geo_infer_bayes")
pytest.importorskip("geo_infer_act")


@pytest.mark.integration
@pytest.mark.active_inference
def test_bayesian_active_inference_loop():
    """Bayesian posterior feeds into Active Inference free energy computation."""
    from geo_infer_bayes.core.gaussian_process import GaussianProcess
    from geo_infer_act.core.free_energy import compute_free_energy

    # Train GP on spatial data
    gp = GaussianProcess(kernel="rbf", length_scale=1.0, noise=1e-4)
    X_train = np.array([[0.0], [1.0], [2.0], [3.0]])
    y_train = np.array([0.0, 1.0, 0.5, 0.2])
    gp.fit(X_train, y_train)

    # Get posterior as beliefs
    X_test = np.array([[1.5]])
    mean, variance = gp.predict(X_test)

    # Construct belief state for ACT module
    n_states = 3
    beliefs = np.array([variance[0], 1.0 - variance[0], 0.0])
    beliefs = np.abs(beliefs) / np.sum(np.abs(beliefs))  # normalize

    # Compute free energy using GP-derived beliefs
    n_obs = 4
    A = np.random.dirichlet(np.ones(n_states), n_obs)
    B = np.stack([
        np.random.dirichlet(np.ones(n_states), n_states)
        for _ in range(2)
    ])
    observations = np.zeros(n_obs)
    observations[0] = 1.0

    F = compute_free_energy(
        beliefs=beliefs,
        observations=observations,
        A=A,
        B=B,
    )
    assert F >= 0.0, f"Free energy from GP-derived beliefs must be non-negative: {F}"
    assert np.isfinite(F), "Free energy must be finite"
```

### Handling Module Import Failures

Use `pytest.importorskip` at the top of integration test files to gracefully
skip when a dependency is not installed:

```python
import pytest

# Skip the entire module if dependencies are missing
geo_infer_space = pytest.importorskip("geo_infer_space")
geo_infer_time = pytest.importorskip("geo_infer_time")


@pytest.mark.integration
def test_cross_module_workflow():
    """This test only runs when both SPACE and TIME are installed."""
    from geo_infer_space.core.indexing import spatial_index
    from geo_infer_time.core.temporal import temporal_resample
    # ... test logic ...
```

For individual tests within a file, use `skipif`:

```python
import importlib

HAS_BAYES = importlib.util.find_spec("geo_infer_bayes") is not None

@pytest.mark.skipif(not HAS_BAYES, reason="geo_infer_bayes not installed")
def test_bayesian_spatial_analysis():
    from geo_infer_bayes.core.gaussian_process import GaussianProcess
    # ... test logic ...
```

### Multi-Module End-to-End Pattern

```python
import pytest
import numpy as np

# Declare all required modules upfront
modules = {}
for mod_name in ["geo_infer_math", "geo_infer_space", "geo_infer_bayes", "geo_infer_act"]:
    try:
        modules[mod_name] = pytest.importorskip(mod_name)
    except pytest.skip.Exception:
        pytest.skip(f"Required module {mod_name} not installed", allow_module_level=True)


@pytest.mark.integration
@pytest.mark.system
def test_full_geospatial_inference_pipeline(sample_coordinates):
    """End-to-end: coordinates -> H3 cells -> spatial stats -> Bayesian -> Active Inference."""
    from geo_infer_math.core.spatial_statistics import morans_i, spatial_weights_matrix
    from geo_infer_space.core.indexing import spatial_index
    from geo_infer_bayes.core.gaussian_process import GaussianProcess
    from geo_infer_act.core.free_energy import compute_free_energy

    # 1. Spatial indexing
    coords = np.array(sample_coordinates)

    # 2. Compute spatial statistics
    values = np.random.normal(50, 10, len(coords))
    W = spatial_weights_matrix(coords, method="knn", k=3)
    I = morans_i(values, W)
    assert np.isfinite(I)

    # 3. Bayesian modeling
    gp = GaussianProcess(kernel="rbf", length_scale=1.0)
    gp.fit(coords[:, :1], values)  # use latitude as predictor
    mean, var = gp.predict(coords[:, :1])

    # 4. Active Inference
    beliefs = np.abs(mean[:3])
    beliefs = beliefs / beliefs.sum()
    n_obs = 4
    A = np.random.dirichlet(np.ones(3), n_obs)
    B = np.stack([np.eye(3) for _ in range(2)])
    F = compute_free_energy(beliefs=beliefs, observations=np.zeros(n_obs), A=A, B=B)
    assert F >= 0.0
```

---

## 7. H3 v4 Test Patterns

GEO-INFER requires H3 v4 (`h3>=4.0.0`). The v4 API uses different function
names than v3. Using the wrong API will cause `AttributeError` at runtime.

### API Reference: v3 vs v4

| Operation | v3 (WRONG) | v4 (CORRECT) |
|-----------|-----------|--------------|
| Lat/lng to cell | `h3.geo_to_h3(lat, lng, res)` | `h3.latlng_to_cell(lat, lng, res)` |
| Cell to lat/lng | `h3.h3_to_geo(cell)` | `h3.cell_to_latlng(cell)` |
| Cell to boundary | `h3.h3_to_geo_boundary(cell)` | `h3.cell_to_boundary(cell)` |
| Neighbors | `h3.k_ring(cell, k)` | `h3.grid_disk(cell, k)` |
| Resolution | `h3.h3_get_resolution(cell)` | `h3.get_resolution(cell)` |
| Parent cell | `h3.h3_to_parent(cell, res)` | `h3.cell_to_parent(cell, res)` |
| Children | `h3.h3_to_children(cell, res)` | `h3.cell_to_children(cell, res)` |
| Valid check | `h3.h3_is_valid(cell)` | `h3.is_valid_cell(cell)` |
| Distance | `h3.h3_distance(a, b)` | `h3.grid_distance(a, b)` |

### Complete H3 Test Example

```python
import pytest

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False


@pytest.mark.h3
@pytest.mark.skipif(not H3_AVAILABLE, reason="h3 not installed")
class TestH3V4Operations:
    """Verify all H3 v4 operations used across GEO-INFER."""

    def test_latlng_to_cell_type(self):
        """latlng_to_cell returns a string cell index."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, resolution=8)
        assert isinstance(cell, str)

    def test_cell_to_latlng_returns_tuple(self):
        """cell_to_latlng returns a (lat, lng) tuple of floats."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        result = h3.cell_to_latlng(cell)
        assert len(result) == 2
        lat, lng = result
        assert isinstance(lat, float)
        assert isinstance(lng, float)
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180

    def test_round_trip_same_cell(self):
        """Encoding, decoding, re-encoding must return the same cell."""
        original_cell = h3.latlng_to_cell(47.6062, -122.3321, 8)
        lat, lng = h3.cell_to_latlng(original_cell)
        recovered_cell = h3.latlng_to_cell(lat, lng, 8)
        assert recovered_cell == original_cell

    def test_grid_disk_increasing_k(self):
        """grid_disk with increasing k must return increasing cell counts."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        prev_count = 0
        for k in range(5):
            disk = h3.grid_disk(cell, k)
            assert len(disk) > prev_count
            prev_count = len(disk)

    def test_grid_distance_symmetry(self):
        """Grid distance must be symmetric: d(a,b) == d(b,a)."""
        a = h3.latlng_to_cell(37.7749, -122.4194, 8)
        b = h3.latlng_to_cell(37.7849, -122.4094, 8)
        assert h3.grid_distance(a, b) == h3.grid_distance(b, a)

    def test_get_resolution(self):
        """get_resolution must return the resolution used to create the cell."""
        for res in [0, 4, 8, 12, 15]:
            cell = h3.latlng_to_cell(47.6062, -122.3321, res)
            assert h3.get_resolution(cell) == res

    def test_is_valid_cell(self):
        """is_valid_cell must return True for valid cells, False for garbage."""
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        assert h3.is_valid_cell(cell) is True
        assert h3.is_valid_cell("not_a_cell") is False
```

---

## 8. Property-Based Testing with Hypothesis

Property-based testing generates many random inputs to find edge cases that
example-based tests miss. Use the `hypothesis` library (included in the
`[quality]` extra).

### H3 Round-Trip Property

```python
import pytest
from hypothesis import given, strategies as st, assume, settings

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False


@pytest.mark.skipif(not H3_AVAILABLE, reason="h3 not installed")
@given(
    lat=st.floats(min_value=-89.99, max_value=89.99, allow_nan=False, allow_infinity=False),
    lng=st.floats(min_value=-179.99, max_value=179.99, allow_nan=False, allow_infinity=False),
    resolution=st.integers(min_value=0, max_value=15),
)
@settings(max_examples=200)
def test_h3_round_trip_property(lat, lng, resolution):
    """For any valid lat/lng, encoding to cell and decoding the center stays in the same cell."""
    cell = h3.latlng_to_cell(lat, lng, resolution)
    center_lat, center_lng = h3.cell_to_latlng(cell)
    assert h3.latlng_to_cell(center_lat, center_lng, resolution) == cell
```

### Numpy Array Strategies

```python
from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np


@given(
    values=arrays(
        dtype=np.float64,
        shape=st.integers(min_value=3, max_value=100),
        elements=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
    )
)
def test_spatial_mean_is_bounded(values):
    """Spatial mean must lie within the range [min(values), max(values)]."""
    mean = np.mean(values)
    assert np.min(values) <= mean <= np.max(values)
```

### GeoDataFrame Generation Strategy

```python
from hypothesis import given, strategies as st
import geopandas as gpd
from shapely.geometry import Point
import numpy as np


@st.composite
def geodataframes(draw, min_rows=3, max_rows=50):
    """Strategy that generates valid GeoDataFrames with point geometries."""
    n = draw(st.integers(min_value=min_rows, max_value=max_rows))
    lats = [draw(st.floats(min_value=-85, max_value=85, allow_nan=False)) for _ in range(n)]
    lngs = [draw(st.floats(min_value=-179, max_value=179, allow_nan=False)) for _ in range(n)]
    values = [draw(st.floats(min_value=0, max_value=1000, allow_nan=False)) for _ in range(n)]
    geometry = [Point(lng, lat) for lat, lng in zip(lats, lngs)]
    return gpd.GeoDataFrame(
        {"value": values, "geometry": geometry},
        crs="EPSG:4326",
    )


@given(gdf=geodataframes())
def test_geodataframe_has_valid_crs(gdf):
    """Generated GeoDataFrame must have a valid CRS."""
    assert gdf.crs is not None
    assert gdf.crs.to_epsg() == 4326


@given(gdf=geodataframes(min_rows=5))
def test_spatial_bounds_contain_all_points(gdf):
    """GeoDataFrame bounds must contain all geometries."""
    minx, miny, maxx, maxy = gdf.total_bounds
    for geom in gdf.geometry:
        assert minx <= geom.x <= maxx
        assert miny <= geom.y <= maxy
```

### Time Series Strategy

```python
import pandas as pd
from hypothesis import given, strategies as st


@st.composite
def time_series_data(draw, min_length=10, max_length=500):
    """Strategy for generating time series with DatetimeIndex."""
    n = draw(st.integers(min_value=min_length, max_value=max_length))
    freq = draw(st.sampled_from(["h", "D", "W", "ME"]))
    values = [draw(st.floats(min_value=-100, max_value=100, allow_nan=False)) for _ in range(n)]
    index = pd.date_range("2020-01-01", periods=n, freq=freq, tz="UTC")
    return pd.Series(values, index=index, name="measurement")


@given(ts=time_series_data())
def test_time_series_index_is_monotonic(ts):
    """Generated time series must have a monotonically increasing DatetimeIndex."""
    assert ts.index.is_monotonic_increasing
```

---

## 9. Performance Testing

Performance tests use `pytest-benchmark` to measure execution time and detect
regressions. Install with `uv pip install pytest-benchmark`.

### Basic Benchmark

```python
import pytest

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False


@pytest.mark.performance
@pytest.mark.skipif(not H3_AVAILABLE, reason="h3 not installed")
def test_h3_indexing_performance(benchmark):
    """Benchmark H3 cell encoding for 1000 coordinates."""
    coords = [(37.77 + i * 0.001, -122.41 + i * 0.001) for i in range(1000)]

    def encode_all():
        return [h3.latlng_to_cell(lat, lng, 8) for lat, lng in coords]

    result = benchmark(encode_all)
    assert len(result) == 1000
```

### Benchmark with Assertions

```python
@pytest.mark.performance
def test_spatial_join_performance(benchmark, sample_geodataframe):
    """Spatial join of 10-point GeoDataFrame must complete within 100ms."""
    import geopandas as gpd
    from shapely.geometry import box

    # Create a bounding box to join against
    bbox = gpd.GeoDataFrame(
        {"region": ["test"]},
        geometry=[box(-123, 47, -122, 48)],
        crs="EPSG:4326",
    )

    def spatial_join():
        return gpd.sjoin(sample_geodataframe, bbox, how="inner", predicate="within")

    result = benchmark(spatial_join)
    # Verify correctness alongside performance
    assert not result.empty
```

### Regression Thresholds

To fail a test when performance degrades beyond a threshold:

```python
@pytest.mark.performance
def test_matrix_operations_regression(benchmark):
    """Matrix multiplication of 500x500 must stay under 50ms."""
    import numpy as np
    A = np.random.rand(500, 500)
    B = np.random.rand(500, 500)

    result = benchmark(lambda: A @ B)

    # Verify the benchmark stats
    assert benchmark.stats.stats.mean < 0.05, (
        f"Matrix multiplication regression: {benchmark.stats.stats.mean:.3f}s > 0.05s"
    )
```

### Running Performance Tests

```bash
# Run only performance tests
uv run python -m pytest -m performance GEO-INFER-MATH/tests/ -v

# With benchmark comparison (saves baseline)
uv run python -m pytest -m performance --benchmark-save=baseline

# Compare against baseline
uv run python -m pytest -m performance --benchmark-compare=baseline

# Disable benchmarks during regular development
uv run python -m pytest --benchmark-disable
```

---

## 10. Coverage Configuration

### Root Configuration

The root `pyproject.toml` contains the shared coverage configuration:

```toml
[tool.coverage.run]
source = ["GEO-INFER-*/src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/env/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

### Module-Specific Coverage

For a single module, override `source` to target just that module:

```toml
# In GEO-INFER-MATH/pyproject.toml or a setup.cfg
[tool.coverage.run]
source = ["src"]
omit = ["*/__init__.py", "*/tests/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Running Coverage

```bash
# Coverage for a single module (HTML + terminal report)
uv run python -m pytest GEO-INFER-MATH/tests/ \
    --cov=GEO-INFER-MATH/src \
    --cov-report=html \
    --cov-report=term-missing

# Coverage with fail-under threshold
uv run python -m pytest GEO-INFER-MATH/tests/ \
    --cov=GEO-INFER-MATH/src \
    --cov-fail-under=80

# Multi-module coverage
uv run python -m pytest GEO-INFER-MATH/tests/ GEO-INFER-SPACE/tests/ \
    --cov=GEO-INFER-MATH/src \
    --cov=GEO-INFER-SPACE/src \
    --cov-report=html

# Coverage report only (no test re-run, uses .coverage file)
uv run python -m coverage report --show-missing
uv run python -m coverage html
```

The HTML report is generated in `htmlcov/` by default. Open `htmlcov/index.html`
to browse file-by-file coverage.

---

## 11. Running Tests

### Unified Test Runner

The unified test runner (`GEO-INFER-TEST/run_unified_tests.py`) discovers and
executes tests across all 44 modules.

```bash
# Run all module tests
uv run python GEO-INFER-TEST/run_unified_tests.py

# Run tests for a specific module (use short name without GEO-INFER- prefix)
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH

# Run by test category
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration

# JSON output for programmatic consumption
uv run python GEO-INFER-TEST/run_unified_tests.py --output json

# JUnit XML for CI systems
uv run python GEO-INFER-TEST/run_unified_tests.py --output junit
```

### Direct pytest Usage

For faster iteration during development, run pytest directly:

```bash
# All tests in a module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Specific test file
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v

# Specific test function
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py::test_morans_i -v

# Specific test class and method
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py::TestMoransI::test_positive -v
```

### Marker-Based Selection

```bash
# Only unit tests
uv run python -m pytest -m unit GEO-INFER-MATH/tests/

# Only integration tests
uv run python -m pytest -m integration GEO-INFER-MATH/tests/

# Spatial unit tests
uv run python -m pytest -m "unit and spatial" GEO-INFER-SPACE/tests/

# Geospatial but not slow
uv run python -m pytest -m "geospatial and not slow" GEO-INFER-SPACE/tests/

# Everything except performance
uv run python -m pytest -m "not performance" GEO-INFER-MATH/tests/

# H3-specific tests across all modules
uv run python -m pytest -m h3 GEO-INFER-SPACE/tests/ GEO-INFER-PLACE/tests/
```

### Useful pytest Flags

| Flag | Purpose |
|------|---------|
| `-v` | Verbose output (show each test name) |
| `-vv` | Extra verbose (show assertion details) |
| `-x` | Stop on first failure |
| `--lf` | Re-run only last-failed tests |
| `--ff` | Run failed tests first, then the rest |
| `-k "pattern"` | Run tests matching name pattern |
| `-s` | Show print() output (disable capture) |
| `--tb=short` | Shorter tracebacks |
| `--tb=no` | No tracebacks (just pass/fail) |
| `-n auto` | Parallel execution (requires pytest-xdist) |
| `--durations=10` | Show 10 slowest tests |

### Development Workflow

During active development, use this progression:

```bash
# 1. Run only the specific test you're writing
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py::TestMoransI -v

# 2. Run the full test file
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v

# 3. Run all unit tests for the module
uv run python -m pytest -m unit GEO-INFER-MATH/tests/ -v

# 4. Run all tests for the module (including integration)
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# 5. Run with coverage before submitting
uv run python -m pytest GEO-INFER-MATH/tests/ --cov=GEO-INFER-MATH/src --cov-report=term-missing
```

---

## 12. CI Integration

### JUnit XML Output

Most CI systems (GitHub Actions, GitLab CI, Jenkins) parse JUnit XML for test
result reporting:

```bash
# Generate JUnit XML
uv run python -m pytest GEO-INFER-MATH/tests/ --junitxml=test-results/math-junit.xml -v

# With the unified runner
uv run python GEO-INFER-TEST/run_unified_tests.py --output junit
```

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          uv pip install -e ".[quality]"
          uv pip install -e ./GEO-INFER-MATH -e ./GEO-INFER-SPACE -e ./GEO-INFER-ACT

      - name: Run tests
        run: |
          uv run python -m pytest GEO-INFER-MATH/tests/ \
            --junitxml=test-results/junit.xml \
            --cov=GEO-INFER-MATH/src \
            --cov-report=xml:test-results/coverage.xml \
            -v

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.python-version }}
          path: test-results/

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: test-results/coverage.xml
```

### Unified Runner Aggregation

The unified test runner (`run_unified_tests.py`) executes tests across all 44
modules and aggregates results:

```
Module              Tests   Pass   Fail   Skip   Duration
------------------------------------------------------------
MATH                  87     85      0      2      4.2s
SPACE                 62     60      1      1      6.8s
ACT                   45     45      0      0      2.1s
BAYES                 38     36      0      2      3.4s
...
------------------------------------------------------------
TOTAL               3042   2980     12     50     94.3s
```

JSON output (`--output json`) provides machine-readable results:

```json
{
  "timestamp": "2026-02-25T10:30:00Z",
  "total_modules": 44,
  "total_tests": 3042,
  "passed": 2980,
  "failed": 12,
  "skipped": 50,
  "duration_seconds": 94.3,
  "modules": {
    "MATH": {"tests": 87, "passed": 85, "failed": 0, "skipped": 2},
    "SPACE": {"tests": 62, "passed": 60, "failed": 1, "skipped": 1}
  }
}
```

### Coverage Badge Generation

Generate coverage badges for the README using `coverage-badge`:

```bash
# Install badge generator
uv pip install coverage-badge

# Generate badge after running coverage
uv run python -m pytest --cov=GEO-INFER-MATH/src --cov-report=xml
uv run python -m coverage_badge -o coverage-badge.svg
```

---

## 13. Troubleshooting

### ModuleNotFoundError: No module named 'geo_infer_module'

**Cause**: The module is not installed in the current environment.

**Fix**:

```bash
uv pip install -e ./GEO-INFER-MODULE
```

If testing multiple modules, install all required modules:

```bash
uv pip install -e ./GEO-INFER-MATH -e ./GEO-INFER-SPACE -e ./GEO-INFER-ACT
```

### ImportError: libgdal.so not found (or similar GDAL errors)

**Cause**: GDAL system libraries are not installed. Python packages like
`rasterio` and `fiona` require GDAL C libraries.

**Fix**:

```bash
# macOS
brew install gdal

# Ubuntu/Debian
sudo apt-get install libgdal-dev gdal-bin

# Verify
gdal-config --version
```

### AttributeError: module 'h3' has no attribute 'geo_to_h3'

**Cause**: Using H3 v3 API function names with H3 v4 installed. GEO-INFER
requires `h3>=4.0.0`.

**Fix**: Replace all v3 function calls with v4 equivalents:

```python
# WRONG (v3 API)
cell = h3.geo_to_h3(lat, lng, resolution)
lat, lng = h3.h3_to_geo(cell)
neighbors = h3.k_ring(cell, k)

# CORRECT (v4 API)
cell = h3.latlng_to_cell(lat, lng, resolution)
lat, lng = h3.cell_to_latlng(cell)
neighbors = h3.grid_disk(cell, k)
```

Verify your installed version:

```bash
uv run python -c "import h3; print(h3.__version__)"
# Must print 4.x.x
```

### conftest.py: fixture not found

**Cause**: The fixture is defined in a `conftest.py` that is not in the test's
ancestor directory, or the fixture name is misspelled.

**Fix**:

1. Verify `conftest.py` is in `tests/` (not `tests/unit/` or `tests/integration/`)
   if the fixture should be shared across subdirectories.
2. Check spelling: the fixture parameter name in the test function must exactly
   match the `@pytest.fixture` function name.
3. Verify scope: a `session`-scoped fixture cannot depend on a `function`-scoped
   fixture.

```python
# conftest.py at tests/ level
@pytest.fixture(scope="session")
def sample_coordinates():
    return [(47.6, -122.3)]

# tests/unit/test_example.py
def test_something(sample_coordinates):  # name must match exactly
    assert len(sample_coordinates) == 1
```

### TypeError in spatial operations

**Cause**: The geometry column is not set as the active geometry in a
GeoDataFrame, or the CRS is missing.

**Fix**:

```python
import geopandas as gpd
from shapely.geometry import Point

# Ensure geometry column is set
gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")

# If geometry column has a different name, set it explicitly
gdf = gdf.set_geometry("my_geom_column")

# Verify
assert gdf.geometry.name == "geometry"  # or your column name
assert gdf.crs is not None
```

### Slow tests blocking development

**Cause**: Performance, integration, or data-heavy tests run during every
test invocation.

**Fix**: Mark slow tests and exclude them during development:

```python
@pytest.mark.slow
def test_process_large_dataset():
    """This test processes 1M rows and takes 30+ seconds."""
    ...
```

```bash
# Exclude slow tests during development
uv run python -m pytest -m "not slow" GEO-INFER-MODULE/tests/ -v

# Run slow tests only (before CI push)
uv run python -m pytest -m slow GEO-INFER-MODULE/tests/ -v
```

### pytest-benchmark not found

**Cause**: `pytest-benchmark` is not installed.

**Fix**:

```bash
uv pip install pytest-benchmark
```

Performance tests using the `benchmark` fixture will be skipped automatically
if `pytest-benchmark` is not installed, so this only matters when you want to
run performance tests.

### Tests pass locally but fail in CI

Common causes:

1. **Missing system dependencies**: CI may not have GDAL, HDF5, or other C
   libraries. Add them to your CI configuration.
2. **Import order**: Tests depend on modules being installed in a specific
   order. Use `pytest.importorskip()` to handle missing dependencies.
3. **File system paths**: Avoid hardcoded absolute paths. Use `tmp_path` or
   `tmp_path_factory` fixtures.
4. **Timezone differences**: Always use timezone-aware datetimes in tests.
   Use `tz="UTC"` in `pd.date_range()`.
5. **Random seed**: Set `np.random.seed()` or use `np.random.default_rng(42)`
   for reproducible tests.

```python
def test_reproducible_result():
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, 100)
    result = compute_something(data)
    assert result == pytest.approx(expected_value, rel=1e-6)
```

### Circular import errors

**Cause**: Module A imports from Module B which imports from Module A.

**Fix**: Use lazy imports inside functions rather than at module level:

```python
# WRONG: top-level circular import
from geo_infer_space.core.indexing import spatial_index  # may cause circular import

# CORRECT: lazy import inside the function that needs it
def test_cross_module():
    from geo_infer_space.core.indexing import spatial_index
    result = spatial_index(data)
    ...
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Install module for testing | `uv pip install -e "./GEO-INFER-MODULE[dev]"` |
| Run all tests | `uv run python GEO-INFER-TEST/run_unified_tests.py` |
| Run module tests | `uv run python -m pytest GEO-INFER-MODULE/tests/ -v` |
| Run by marker | `uv run python -m pytest -m "unit and not slow"` |
| Run with coverage | `uv run python -m pytest --cov=MODULE/src --cov-report=html` |
| Run last failed | `uv run python -m pytest --lf` |
| Show slowest tests | `uv run python -m pytest --durations=10` |
| Generate JUnit XML | `uv run python -m pytest --junitxml=results.xml` |

---

*This guide is maintained as part of the GEO-INFER-INTRA documentation hub.
For module-specific testing details, see the SKILL.md file in each module.*
