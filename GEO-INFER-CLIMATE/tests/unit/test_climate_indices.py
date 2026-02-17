"""Tests for climate indices calculation module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-CLIMATE/src")

from geo_infer_climate.core.climate_indices import ClimateIndicesCalculator


@pytest.fixture
def calculator():
    return ClimateIndicesCalculator()


class TestSPI:
    def test_spi_normal_distribution(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.exponential(50, 120),
            dims=["time"],
        )
        spi = calculator.calculate_spi(precip, timescale=1, distribution="normal")
        assert spi.shape == (120,)
        assert abs(float(spi.mean())) < 1.0

    def test_spi_gamma_distribution(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.gamma(2, 25, 120),
            dims=["time"],
        )
        spi = calculator.calculate_spi(precip, timescale=1, distribution="gamma")
        assert spi.shape == (120,)

    def test_spi_accumulation_timescale(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.exponential(50, 120),
            dims=["time"],
        )
        spi_1 = calculator.calculate_spi(precip, timescale=1, distribution="normal")
        spi_3 = calculator.calculate_spi(precip, timescale=3, distribution="normal")
        assert spi_1.name == "SPI_1"
        assert spi_3.name == "SPI_3"

    def test_spi_output_range(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.exponential(50, 240),
            dims=["time"],
        )
        spi = calculator.calculate_spi(precip, timescale=1, distribution="normal")
        valid = spi.values[~np.isnan(spi.values)]
        assert float(np.std(valid)) > 0


class TestHeatIndex:
    def test_heat_index_temp_only(self, calculator):
        temp = xr.DataArray(
            np.array([25.0, 30.0, 35.0, 40.0]),
            dims=["time"],
        )
        hi = calculator.calculate_heat_index(temp)
        assert hi.name == "heat_index"
        assert hi.shape == (4,)

    def test_heat_index_with_humidity(self, calculator):
        temp = xr.DataArray(
            np.array([30.0, 35.0, 40.0]),
            dims=["time"],
        )
        rh = xr.DataArray(
            np.array([50.0, 60.0, 70.0]),
            dims=["time"],
        )
        hi = calculator.calculate_heat_index(temp, humidity=rh)
        assert hi.name == "heat_index"
        assert float(hi[2]) > float(hi[0])

    def test_heat_index_high_humidity_increases_apparent(self, calculator):
        temp = xr.DataArray(np.array([35.0, 35.0]), dims=["time"])
        rh_low = xr.DataArray(np.array([30.0, 30.0]), dims=["time"])
        rh_high = xr.DataArray(np.array([80.0, 80.0]), dims=["time"])
        hi_low = calculator.calculate_heat_index(temp, humidity=rh_low)
        hi_high = calculator.calculate_heat_index(temp, humidity=rh_high)
        assert float(hi_high.mean()) > float(hi_low.mean())


class TestExtremeIndices:
    def test_temperature_extremes(self, calculator):
        np.random.seed(42)
        temp = xr.DataArray(
            np.random.normal(20, 8, 365),
            dims=["time"],
        )
        result = calculator.calculate_extreme_indices(temp)
        assert "hot_days" in result
        assert "cold_days" in result
        assert "max_temp" in result
        assert "min_temp" in result
        assert float(result["max_temp"]) > float(result["min_temp"])

    def test_with_precipitation(self, calculator):
        np.random.seed(42)
        temp = xr.DataArray(
            np.random.normal(20, 8, 365),
            dims=["time"],
        )
        precip = xr.DataArray(
            np.random.exponential(5, 365),
            dims=["time"],
        )
        result = calculator.calculate_extreme_indices(temp, precipitation=precip)
        assert "heavy_precip_days" in result
        assert "total_precip" in result

    def test_hot_cold_days_sum(self, calculator):
        np.random.seed(42)
        temp = xr.DataArray(
            np.random.normal(20, 8, 100),
            dims=["time"],
        )
        result = calculator.calculate_extreme_indices(temp)
        hot = int(result["hot_days"].values)
        cold = int(result["cold_days"].values)
        assert hot + cold <= 100


class TestPDSI:
    def test_pdsi_output_range(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.exponential(50, 120),
            dims=["time"],
        )
        temp = xr.DataArray(
            np.random.normal(20, 5, 120),
            dims=["time"],
        )
        pdsi = calculator.calculate_pdsi(precip, temp)
        assert float(pdsi.min()) >= -6.0
        assert float(pdsi.max()) <= 6.0

    def test_pdsi_name(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.exponential(50, 60),
            dims=["time"],
        )
        temp = xr.DataArray(
            np.random.normal(20, 5, 60),
            dims=["time"],
        )
        pdsi = calculator.calculate_pdsi(precip, temp)
        assert pdsi.name == "PDSI"

    def test_pdsi_shape_matches_input(self, calculator):
        np.random.seed(42)
        precip = xr.DataArray(
            np.random.exponential(50, 48),
            dims=["time"],
        )
        temp = xr.DataArray(
            np.random.normal(20, 5, 48),
            dims=["time"],
        )
        pdsi = calculator.calculate_pdsi(precip, temp)
        assert pdsi.shape == (48,)
