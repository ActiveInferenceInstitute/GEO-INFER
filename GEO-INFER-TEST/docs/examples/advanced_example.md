# Advanced Example: Writing Tests for a New GEO-INFER Module

This example provides a complete walkthrough of adding tests to a new GEO-INFER module. It covers test directory setup, fixture creation, unit tests, integration tests, marker usage, and common patterns.

## Overview

When adding a new module to GEO-INFER, tests are not optional. Every module requires at minimum 4 test files. This guide walks through creating a test suite for a hypothetical `GEO-INFER-WEATHER` module.

## Step 1: Create the Test Directory Structure

Every module follows the standard layout:

```bash
mkdir -p GEO-INFER-WEATHER/tests/unit
mkdir -p GEO-INFER-WEATHER/tests/integration
touch GEO-INFER-WEATHER/tests/__init__.py
touch GEO-INFER-WEATHER/tests/conftest.py
touch GEO-INFER-WEATHER/tests/unit/__init__.py
touch GEO-INFER-WEATHER/tests/unit/test_core.py
touch GEO-INFER-WEATHER/tests/unit/test_models.py
touch GEO-INFER-WEATHER/tests/integration/__init__.py
touch GEO-INFER-WEATHER/tests/integration/test_pipeline.py
touch GEO-INFER-WEATHER/tests/integration/test_api.py
```

Result:

```
GEO-INFER-WEATHER/tests/
  __init__.py
  conftest.py              # Shared fixtures
  unit/
    __init__.py
    test_core.py           # Core functionality
    test_models.py         # Data models
  integration/
    __init__.py
    test_pipeline.py       # End-to-end pipeline
    test_api.py            # API endpoints
```

## Step 2: Create Shared Fixtures in conftest.py

The `conftest.py` file defines test fixtures shared across all test files.

```python
# GEO-INFER-WEATHER/tests/conftest.py
"""Shared test fixtures for GEO-INFER-WEATHER."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime, timedelta


@pytest.fixture
def sample_temperature_grid():
    """Create a sample temperature grid for testing."""
    lat = np.linspace(30, 50, 20)
    lon = np.linspace(-130, -110, 20)
    return xr.DataArray(
        np.random.uniform(-10, 40, (20, 20)),
        dims=["lat", "lon"],
        coords={"lat": lat, "lon": lon},
        attrs={"units": "degrees_C"},
    )


@pytest.fixture
def sample_time_series():
    """Create a sample weather time series for testing."""
    times = [datetime(2025, 1, 1) + timedelta(hours=i) for i in range(168)]
    return xr.DataArray(
        np.random.uniform(0, 30, 168),
        dims=["time"],
        coords={"time": times},
        attrs={"units": "degrees_C"},
    )


@pytest.fixture
def sample_precipitation():
    """Create a sample precipitation dataset."""
    lat = np.linspace(30, 50, 20)
    lon = np.linspace(-130, -110, 20)
    return xr.DataArray(
        np.random.exponential(5, (20, 20)),
        dims=["lat", "lon"],
        coords={"lat": lat, "lon": lon},
        attrs={"units": "mm/day"},
    )


@pytest.fixture
def empty_grid():
    """Create an empty grid for edge case testing."""
    return xr.DataArray(
        np.array([]).reshape(0, 0),
        dims=["lat", "lon"],
    )
```

## Step 3: Write Unit Tests for Core Logic

Unit tests validate individual functions and classes in isolation.

```python
# GEO-INFER-WEATHER/tests/unit/test_core.py
"""Unit tests for weather analysis core functionality."""

import pytest
import numpy as np
import xarray as xr


class TestWeatherAnalyzer:
    """Tests for the WeatherAnalyzer class."""

    def setup_method(self):
        """Create fresh analyzer for each test."""
        from geo_infer_weather.core.analyzer import WeatherAnalyzer
        self.analyzer = WeatherAnalyzer()

    @pytest.mark.unit
    def test_init_default_config(self):
        """Verify default configuration is applied."""
        assert self.analyzer.config is not None
        assert isinstance(self.analyzer.config, dict)

    @pytest.mark.unit
    def test_compute_heat_index(self):
        """Verify heat index calculation matches NOAA formula."""
        # Known test case: 90F, 65% humidity -> ~105F heat index
        temp_f = 90.0
        humidity = 65.0
        result = self.analyzer.compute_heat_index(temp_f, humidity)
        assert isinstance(result, float)
        assert 100 < result < 115  # Expected range for this input

    @pytest.mark.unit
    def test_compute_heat_index_low_temp(self):
        """Verify heat index returns temperature when below threshold."""
        result = self.analyzer.compute_heat_index(70.0, 50.0)
        assert result == pytest.approx(70.0, abs=5.0)

    @pytest.mark.unit
    def test_spatial_interpolation(self, sample_temperature_grid):
        """Verify spatial interpolation produces valid output."""
        result = self.analyzer.interpolate(
            sample_temperature_grid,
            method="linear",
            target_resolution=0.5,
        )
        assert result is not None
        assert not np.isnan(result.values).all()

    @pytest.mark.unit
    def test_anomaly_detection(self, sample_time_series):
        """Verify anomaly detection identifies outliers."""
        # Inject an obvious anomaly
        data = sample_time_series.copy()
        data[50] = 100.0  # Way above normal range

        anomalies = self.analyzer.detect_anomalies(data, threshold=3.0)
        assert len(anomalies) > 0
        assert 50 in anomalies

    @pytest.mark.unit
    @pytest.mark.fast
    def test_wind_chill_calculation(self):
        """Verify wind chill calculation."""
        # At 0F and 15 mph wind, wind chill should be well below zero
        result = self.analyzer.compute_wind_chill(
            temperature_f=0.0,
            wind_speed_mph=15.0,
        )
        assert result < 0.0

    @pytest.mark.unit
    def test_empty_input_handling(self, empty_grid):
        """Verify graceful handling of empty input."""
        result = self.analyzer.interpolate(empty_grid)
        assert result is not None
```

## Step 4: Write Data Model Tests

```python
# GEO-INFER-WEATHER/tests/unit/test_models.py
"""Unit tests for weather data models."""

import pytest
from datetime import datetime


class TestWeatherObservation:
    """Tests for WeatherObservation data class."""

    @pytest.mark.unit
    def test_create_observation(self):
        """Verify observation creation with valid data."""
        from geo_infer_weather.models.observation import WeatherObservation

        obs = WeatherObservation(
            station_id="KCEC",
            timestamp=datetime(2025, 6, 15, 12, 0),
            temperature_c=18.5,
            humidity_pct=72.0,
            wind_speed_ms=4.2,
        )

        assert obs.station_id == "KCEC"
        assert obs.temperature_c == 18.5
        assert obs.humidity_pct == 72.0

    @pytest.mark.unit
    def test_observation_validation(self):
        """Verify invalid data is rejected."""
        from geo_infer_weather.models.observation import WeatherObservation

        with pytest.raises(ValueError):
            WeatherObservation(
                station_id="KCEC",
                timestamp=datetime(2025, 6, 15, 12, 0),
                temperature_c=18.5,
                humidity_pct=150.0,  # Invalid: > 100%
                wind_speed_ms=4.2,
            )

    @pytest.mark.unit
    def test_observation_to_dict(self):
        """Verify serialization to dictionary."""
        from geo_infer_weather.models.observation import WeatherObservation

        obs = WeatherObservation(
            station_id="KCEC",
            timestamp=datetime(2025, 6, 15, 12, 0),
            temperature_c=18.5,
            humidity_pct=72.0,
            wind_speed_ms=4.2,
        )

        d = obs.to_dict()
        assert isinstance(d, dict)
        assert d["station_id"] == "KCEC"
        assert "timestamp" in d
```

## Step 5: Write Integration Tests

Integration tests verify that components work together correctly.

```python
# GEO-INFER-WEATHER/tests/integration/test_pipeline.py
"""Integration tests for weather analysis pipeline."""

import pytest
import numpy as np
import xarray as xr


class TestWeatherPipeline:
    """Test the full weather analysis pipeline."""

    @pytest.mark.integration
    def test_end_to_end_analysis(self, sample_temperature_grid, sample_precipitation):
        """Verify complete pipeline from data to results."""
        from geo_infer_weather.core.analyzer import WeatherAnalyzer

        analyzer = WeatherAnalyzer()

        # Step 1: Ingest data
        analyzer.load_data(
            temperature=sample_temperature_grid,
            precipitation=sample_precipitation,
        )

        # Step 2: Run analysis
        results = analyzer.run_analysis()

        # Step 3: Verify output structure
        assert "temperature_stats" in results
        assert "precipitation_stats" in results
        assert results["temperature_stats"]["mean"] is not None

    @pytest.mark.integration
    def test_multi_module_integration(self, sample_temperature_grid):
        """Verify integration with GEO-INFER-SPACE."""
        try:
            from geo_infer_space import SpatialAnalyzer
            has_space = True
        except ImportError:
            has_space = False

        if not has_space:
            pytest.skip("GEO-INFER-SPACE not installed")

        from geo_infer_weather.core.analyzer import WeatherAnalyzer

        analyzer = WeatherAnalyzer()
        # Test that spatial integration works when available
        result = analyzer.spatial_aggregate(
            sample_temperature_grid,
            h3_resolution=7,
        )
        assert result is not None

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_pipeline(self):
        """Verify pipeline handles large datasets."""
        from geo_infer_weather.core.analyzer import WeatherAnalyzer

        # Create large dataset
        lat = np.linspace(-90, 90, 500)
        lon = np.linspace(-180, 180, 500)
        data = xr.DataArray(
            np.random.random((500, 500)),
            dims=["lat", "lon"],
            coords={"lat": lat, "lon": lon},
        )

        analyzer = WeatherAnalyzer()
        analyzer.load_data(temperature=data)
        results = analyzer.run_analysis()

        assert results is not None
```

## Step 6: Write API Tests

```python
# GEO-INFER-WEATHER/tests/integration/test_api.py
"""Integration tests for weather API endpoints."""

import pytest


class TestWeatherAPI:
    """Test weather REST API endpoints."""

    @pytest.mark.api
    def test_health_endpoint(self, client):
        """Verify API health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    @pytest.mark.api
    def test_forecast_endpoint(self, client):
        """Verify forecast endpoint returns valid JSON."""
        response = client.post("/forecast", json={
            "latitude": 42.0,
            "longitude": -124.0,
            "hours": 24,
        })
        assert response.status_code == 200
        data = response.json()
        assert "forecasts" in data
        assert len(data["forecasts"]) == 24
```

## Step 7: Verify Tests Are Discovered

```bash
# List all tests without running them
uv run python -m pytest GEO-INFER-WEATHER/tests/ --co

# Expected:
# <Module tests/unit/test_core.py>
#   <Class TestWeatherAnalyzer>
#     <Function test_init_default_config>
#     <Function test_compute_heat_index>
#     ...
# <Module tests/unit/test_models.py>
#   <Class TestWeatherObservation>
#     ...

# Run only unit tests
uv run python -m pytest GEO-INFER-WEATHER/tests/ -m unit -v

# Run only integration tests
uv run python -m pytest GEO-INFER-WEATHER/tests/ -m integration -v
```

## Step 8: Run Through Unified Runner

Verify the unified runner discovers the new module:

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module WEATHER
```

## Key Patterns to Follow

1. **Fixtures in conftest.py**: Share data creation across tests. Avoid duplicating setup code.
2. **One assertion per test**: Each test verifies one specific behavior. Multiple assertions are acceptable when validating a single logical outcome.
3. **Mark every test**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, etc. This enables category-based filtering.
4. **Test edge cases**: Empty inputs, zero-length arrays, NaN values, out-of-range parameters.
5. **Skip gracefully**: Use `pytest.skip()` when optional dependencies are missing.
6. **No mocks for external data**: Use real (but small) test datasets. Mocks hide integration bugs.
7. **Class-based organization**: Group related tests in classes. Use `setup_method` for per-test initialization.

## Checklist for New Module Tests

- [ ] `tests/` directory exists with `__init__.py`
- [ ] `tests/conftest.py` with shared fixtures
- [ ] `tests/unit/test_core.py` -- core functionality (3+ tests)
- [ ] `tests/unit/test_models.py` -- data models (3+ tests)
- [ ] `tests/integration/test_pipeline.py` -- end-to-end (2+ tests)
- [ ] `tests/integration/test_api.py` -- API endpoints (2+ tests)
- [ ] All tests have pytest markers
- [ ] Edge cases covered (empty, NaN, out-of-range)
- [ ] Tests pass: `uv run python -m pytest GEO-INFER-WEATHER/tests/ -v`
- [ ] Unified runner discovers module: `--module WEATHER`

## Next Steps

- Read the [API Reference](../api_reference.md) for validator details to add validation checks.
- Use the validators from GEO-INFER-TEST within your integration tests.
- Set up coverage targets and add to the CI pipeline.
