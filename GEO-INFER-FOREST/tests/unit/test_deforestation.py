"""Tests for deforestation detection module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-FOREST/src")

from geo_infer_forest.core.deforestation import DeforestationDetector


@pytest.fixture
def detector():
    return DeforestationDetector()


class TestTwoDateChange:
    def test_detects_loss(self, detector):
        before = xr.DataArray(np.full((10, 10), 0.8), dims=("y", "x"))
        after = xr.DataArray(np.full((10, 10), 0.2), dims=("y", "x"))
        result = detector.detect_change_two_date(before, after)
        assert float(result["deforestation_mask"].sum()) == 100

    def test_no_change(self, detector):
        data = xr.DataArray(np.full((10, 10), 0.7), dims=("y", "x"))
        result = detector.detect_change_two_date(data, data)
        assert float(result["deforestation_mask"].sum()) == 0

    def test_change_magnitude(self, detector):
        before = xr.DataArray(np.full((5, 5), 0.8), dims=("y", "x"))
        after = xr.DataArray(np.full((5, 5), 0.5), dims=("y", "x"))
        result = detector.detect_change_two_date(before, after)
        np.testing.assert_allclose(result["change_magnitude"].values, 0.3, atol=1e-10)

    def test_threshold_sensitivity(self, detector):
        before = xr.DataArray(np.full((5, 5), 0.8), dims=("y", "x"))
        after = xr.DataArray(np.full((5, 5), 0.7), dims=("y", "x"))
        result_tight = detector.detect_change_two_date(before, after, threshold=0.05)
        result_loose = detector.detect_change_two_date(before, after, threshold=0.15)
        assert float(result_tight["deforestation_mask"].sum()) >= float(
            result_loose["deforestation_mask"].sum()
        )


class TestTimeSeriesChange:
    def test_detects_break(self, detector):
        values = np.concatenate([np.full(10, 0.8), np.full(10, 0.3)])
        series = xr.DataArray(values, dims=("time",))
        result = detector.detect_change_time_series(series, window_size=5)
        assert "z_score" in result
        assert "significant_decrease" in result

    def test_stable_series(self, detector):
        values = np.full(20, 0.7)
        series = xr.DataArray(values, dims=("time",))
        result = detector.detect_change_time_series(series, window_size=3)
        assert float(result["cumulative_loss"].min()) <= 0


class TestAnnualRate:
    def test_zero_loss(self, detector):
        cover = xr.DataArray(
            np.full(5, 80.0),
            dims=("time",),
            coords={"time": range(5)},
        )
        result = detector.calculate_annual_deforestation_rate(cover)
        assert abs(result["annual_rate_pct"]) < 1e-10

    def test_significant_loss(self, detector):
        cover = xr.DataArray(
            np.linspace(80, 40, 10),
            dims=("time",),
            coords={"time": range(10)},
        )
        result = detector.calculate_annual_deforestation_rate(cover)
        assert result["annual_rate_pct"] > 0
        assert result["total_loss_pct"] > 0


class TestFragmentation:
    def test_intact_forest(self, detector):
        mask = xr.DataArray(np.ones((10, 10)), dims=("y", "x"))
        result = detector.calculate_fragmentation_index(mask)
        assert result["forest_fraction"] == 1.0
        assert result["core_fraction"] > 0

    def test_no_forest(self, detector):
        mask = xr.DataArray(np.zeros((10, 10)), dims=("y", "x"))
        result = detector.calculate_fragmentation_index(mask)
        assert result["forest_fraction"] == 0.0
        assert result["fragmentation_index"] == 1.0

    def test_fragmented_checkerboard(self, detector):
        mask_data = np.zeros((6, 6))
        mask_data[::2, ::2] = 1
        mask = xr.DataArray(mask_data, dims=("y", "x"))
        result = detector.calculate_fragmentation_index(mask)
        assert result["edge_density"] > 0.5
