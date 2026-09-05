"""Tests for downscaling methods module."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_climate.core.downscaling import DownscalingMethods


@pytest.fixture
def downscaler():
    return DownscalingMethods()


def _gridded(values: np.ndarray) -> xr.DataArray:
    time = np.arange(values.shape[0])
    lat = np.linspace(30.0, 40.0, values.shape[1])
    lon = np.linspace(-110.0, -100.0, values.shape[2])
    return xr.DataArray(
        values, dims=["time", "lat", "lon"], coords={"time": time, "lat": lat, "lon": lon}
    )


class TestLinearBiasCorrection:
    def test_recovers_observed_mean_and_std(self, downscaler):
        np.random.seed(42)
        observed = _gridded(np.random.normal(10.0, 2.0, (100, 3, 3)))
        model = _gridded(np.random.normal(15.0, 4.0, (100, 3, 3)))

        corrected = downscaler.bias_correction(model, observed, method="linear")

        assert abs(float(corrected.mean()) - float(observed.mean())) < 1e-6
        assert abs(float(corrected.std()) - float(observed.std())) < 1e-4

    def test_constant_model_stays_finite(self, downscaler):
        observed = _gridded(np.random.default_rng(1).normal(10.0, 2.0, (100, 3, 3)))
        model = _gridded(np.full((100, 3, 3), 15.0))

        corrected = downscaler.bias_correction(model, observed, method="linear")

        assert np.isfinite(corrected.values).all()
        # A zero-variance model maps to the observed per-cell mean.
        assert np.allclose(corrected.values, observed.mean("time").values)


class TestQuantileMapping:
    def test_quantile_correction_matches_observed_distribution(self, downscaler):
        np.random.seed(42)
        observed = np.random.normal(10.0, 2.0, 200)
        model_raw = np.random.normal(15.0, 4.0, 200)
        observed_da = xr.DataArray(observed, dims=["time"])
        model_da = xr.DataArray(model_raw, dims=["time"])

        corrected = downscaler.bias_correction(model_da, observed_da, method="quantile")

        assert corrected.shape == model_da.shape
        corrected_vals = corrected.values[np.isfinite(corrected.values)]
        # The corrected sample must follow the observed distribution, not the
        # model's biased one.
        assert abs(np.mean(corrected_vals) - np.mean(observed)) < 1.0
        assert np.mean(corrected_vals) < np.mean(model_raw)

    def test_quantile_mapping_is_monotonic(self, downscaler):
        observed = xr.DataArray(np.linspace(0.0, 10.0, 100), dims=["time"])
        model = xr.DataArray(np.linspace(5.0, 25.0, 100), dims=["time"])

        corrected = downscaler.bias_correction(model, observed, method="quantile")

        assert np.all(np.diff(corrected.values) >= 0)

    def test_unknown_bias_method_raises(self, downscaler):
        model = xr.DataArray(np.arange(10.0), dims=["time"])
        observed = xr.DataArray(np.arange(10.0), dims=["time"])
        with pytest.raises(ValueError):
            downscaler.bias_correction(model, observed, method="delta")


class TestStatisticalDownscaling:
    def test_doubles_grid_resolution(self, downscaler):
        coarse = _gridded(np.random.default_rng(2).normal(10.0, 1.0, (10, 4, 4)))

        fine = downscaler.statistical_downscaling(coarse)

        assert fine.sizes["lat"] == 8
        assert fine.sizes["lon"] == 8
        assert fine.sizes["time"] == 10

    def test_interpolation_preserves_range(self, downscaler):
        coarse = _gridded(np.random.default_rng(3).normal(10.0, 1.0, (10, 4, 4)))

        fine = downscaler.statistical_downscaling(coarse)

        assert float(fine.min()) >= float(coarse.min()) - 1e-6
        assert float(fine.max()) <= float(coarse.max()) + 1e-6

    def test_unknown_method_raises(self, downscaler):
        coarse = _gridded(np.zeros((5, 3, 3)))
        with pytest.raises(ValueError):
            downscaler.statistical_downscaling(coarse, method="rf")
