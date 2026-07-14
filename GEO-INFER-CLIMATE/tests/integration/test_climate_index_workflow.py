"""Integration coverage for climate statistics and finite-value contracts."""

import numpy as np
import pandas as pd
import xarray as xr

from geo_infer_climate.core.climate_indices import ClimateIndicesCalculator


def test_spi_workflow_returns_finite_index_values() -> None:
    """Calculate SPI from deterministic positive precipitation observations."""
    precipitation = xr.DataArray(
        np.linspace(10.0, 40.0, 24),
        dims=["time"],
        coords={"time": pd.date_range("2024-01-01", periods=24, freq="ME")},
    )

    spi = ClimateIndicesCalculator().calculate_spi(precipitation, timescale=3)

    assert spi.name == "SPI_3"
    assert spi.shape == precipitation.shape
    assert np.isfinite(spi.values[3:]).all()
