"""Tests for forest health monitoring module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_forest.core.forest_health import ForestHealthMonitor


@pytest.fixture
def monitor():
    return ForestHealthMonitor()


class TestForestHealth:
    def test_health_index_range(self, monitor):
        ndvi = xr.DataArray(np.random.uniform(0.2, 0.9, (10, 10)), dims=("y", "x"))
        result = monitor.assess_forest_health(ndvi)
        assert float(result["health_index"].min()) >= 0.0
        assert float(result["health_index"].max()) <= 1.0

    def test_with_temperature(self, monitor):
        ndvi = xr.DataArray(np.full((5, 5), 0.7), dims=("y", "x"))
        temp = xr.DataArray(np.full((5, 5), 35.0), dims=("y", "x"))
        result = monitor.assess_forest_health(ndvi, temperature=temp)
        assert "temperature_stress" in result

    def test_with_precipitation(self, monitor):
        ndvi = xr.DataArray(np.full((5, 5), 0.7), dims=("y", "x"))
        precip = xr.DataArray(np.full((5, 5), 200.0), dims=("y", "x"))
        result = monitor.assess_forest_health(ndvi, precipitation=precip)
        assert "water_stress" in result



    def test_temperature_stress_clamped(self, monitor):
        ndvi = xr.DataArray(np.full((5, 5), 0.7), dims=("y", "x"))
        temp = xr.DataArray(np.full((5, 5), 45.0), dims=("y", "x"))  # 25 deg over optimum
        result = monitor.assess_forest_health(ndvi, temperature=temp)
        stress = result["temperature_stress"]
        assert float(stress.max()) == 1.0  # would be 25/20 unclamped
        assert float(stress.min()) >= 0.0

    def test_water_stress_clamped(self, monitor):
        ndvi = xr.DataArray(np.full((5, 5), 0.7), dims=("y", "x"))
        precip = xr.DataArray(np.full((5, 5), 5000.0), dims=("y", "x"))  # 5x optimal
        result = monitor.assess_forest_health(ndvi, precipitation=precip)
        assert float(result["water_stress"].max()) == 1.0

    def test_optimal_temperature_configurable(self):
        monitor = ForestHealthMonitor(config={"optimal_temperature_c": 30.0})
        ndvi = xr.DataArray(np.full((2, 2), 0.7), dims=("y", "x"))
        at_optimum = monitor.assess_forest_health(ndvi, temperature=xr.DataArray(np.full((2, 2), 30.0), dims=("y", "x")))
        assert float(at_optimum["temperature_stress"].max()) == 0.0

    def test_optimal_precipitation_configurable(self):
        monitor = ForestHealthMonitor(config={"optimal_precipitation_mm": 500.0})
        ndvi = xr.DataArray(np.full((2, 2), 0.7), dims=("y", "x"))
        at_optimum = monitor.assess_forest_health(ndvi, precipitation=xr.DataArray(np.full((2, 2), 500.0), dims=("y", "x")))
        assert float(at_optimum["water_stress"].max()) == 0.0

class TestDeforestationDetection:
    def test_detects_loss(self, monitor):
        cover = xr.DataArray(
            np.array([[[0.8] * 5] * 5, [[0.3] * 5] * 5]),
            dims=("time", "y", "x"),
            coords={"time": [0, 1]},
        )
        result = monitor.detect_deforestation(cover)
        assert bool(result["deforestation"].any())

    def test_stable_forest(self, monitor):
        cover = xr.DataArray(
            np.full((3, 5, 5), 0.8),
            dims=("time", "y", "x"),
            coords={"time": [0, 1, 2]},
        )
        result = monitor.detect_deforestation(cover)
        assert not bool(result["deforestation"].any())

    def test_custom_threshold(self, monitor):
        cover = xr.DataArray(
            np.array([[[0.8] * 5] * 5, [[0.75] * 5] * 5]),
            dims=("time", "y", "x"),
            coords={"time": [0, 1]},
        )
        result_loose = monitor.detect_deforestation(cover, threshold=0.1)
        result_tight = monitor.detect_deforestation(cover, threshold=0.01)
        assert float(result_tight["deforestation"].sum()) >= float(
            result_loose["deforestation"].sum()
        )
