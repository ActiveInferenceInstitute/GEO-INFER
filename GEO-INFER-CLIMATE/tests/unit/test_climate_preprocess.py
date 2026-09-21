"""Behavioral tests for ClimateDataProcessor.preprocess_dataset/load_dataset (GS19-58).

Covers the four supported preprocessing operations, the ValueError contract
for unsupported operations (previously silently ignored), and the documented
failure modes of load_dataset.
"""

import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from geo_infer_climate.core.climate_data import ClimateDataProcessor


def _dataset() -> xr.Dataset:
    return xr.Dataset(
        {
            "temperature": (
                ("time",),
                np.array([0.0, 1.0, 2.0, 3.0]),
                {"units": "celsius"},
            )
        },
        coords={"time": pd.date_range("2024-01-01", periods=4, freq="D")},
    )


def test_default_operations_leave_sorted_dataset_identical():
    processor = ClimateDataProcessor()
    result = processor.preprocess_dataset(_dataset())
    xr.testing.assert_identical(result, _dataset())


def test_sort_time_orders_unsorted_series():
    shuffled = _dataset().isel(time=[2, 0, 3, 1])
    result = ClimateDataProcessor().preprocess_dataset(shuffled, ["sort_time"])
    expected = pd.date_range("2024-01-01", periods=4, freq="D").values
    assert np.array_equal(result["time"].values, expected)


def test_standardize_coords_renames_lat_lon():
    ds = xr.Dataset(
        {"temperature": (("latitude", "longitude"), np.zeros((2, 3)))},
        coords={
            "latitude": np.array([10.0, 20.0]),
            "longitude": np.array([1.0, 2.0, 3.0]),
        },
    )
    result = ClimateDataProcessor().preprocess_dataset(ds, ["standardize_coords"])
    assert "lat" in result.coords
    assert "lon" in result.coords


def test_detrend_removes_linear_trend():
    result = ClimateDataProcessor().preprocess_dataset(_dataset(), ["detrend"])
    assert np.allclose(result["temperature"].values, 0.0, atol=1e-9)


def test_remove_outliers_masks_zscore_extremes():
    data = np.array([0.0] * 10 + [100.0])
    ds = xr.Dataset(
        {"temperature": (("time",), data)},
        coords={"time": pd.date_range("2024-01-01", periods=11, freq="D")},
    )
    result = ClimateDataProcessor().preprocess_dataset(ds, ["remove_outliers"])
    values = result["temperature"].values
    assert np.isnan(values[-1])
    assert np.isfinite(values[:-1]).all()


def test_unsupported_operation_raises():
    with pytest.raises(ValueError, match="bogus_op"):
        ClimateDataProcessor().preprocess_dataset(_dataset(), ["bogus_op"])


def test_resample_is_not_silently_ignored():
    """The formerly silent no-op for 'resample' now raises."""
    with pytest.raises(ValueError, match="resample"):
        ClimateDataProcessor().preprocess_dataset(_dataset(), ["resample"])


def test_load_dataset_rejects_unsupported_dataset_type():
    with pytest.raises(ValueError, match="Unsupported dataset type"):
        ClimateDataProcessor().load_dataset("/tmp/irrelevant.nc", "bogus")


def test_load_dataset_missing_file_raises():
    # Engine discovery may emit environment-specific RuntimeWarnings (e.g.
    # cfgrib/ecCodes absence) before the missing file is reported.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(FileNotFoundError):
            ClimateDataProcessor().load_dataset("/nonexistent/path/file.nc", "era5")
