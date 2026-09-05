"""Tests for canopy analysis module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_forest.core.canopy_analysis import CanopyAnalyzer


@pytest.fixture
def analyzer():
    return CanopyAnalyzer()


@pytest.fixture
def sample_bands():
    np.random.seed(42)
    red = xr.DataArray(np.random.uniform(0.02, 0.15, (10, 10)), dims=("y", "x"))
    nir = xr.DataArray(np.random.uniform(0.3, 0.8, (10, 10)), dims=("y", "x"))
    blue = xr.DataArray(np.random.uniform(0.01, 0.10, (10, 10)), dims=("y", "x"))
    return red, nir, blue


class TestNDVI:
    def test_ndvi_range(self, analyzer, sample_bands):
        red, nir, _ = sample_bands
        ndvi = analyzer.calculate_ndvi(red, nir)
        assert float(ndvi.min()) >= -1.0
        assert float(ndvi.max()) <= 1.0

    def test_ndvi_positive_for_vegetation(self, analyzer):
        red = xr.DataArray(np.full((5, 5), 0.05), dims=("y", "x"))
        nir = xr.DataArray(np.full((5, 5), 0.50), dims=("y", "x"))
        ndvi = analyzer.calculate_ndvi(red, nir)
        assert float(ndvi.mean()) > 0.5

    def test_ndvi_zero_denominator(self, analyzer):
        red = xr.DataArray(np.zeros((3, 3)), dims=("y", "x"))
        nir = xr.DataArray(np.zeros((3, 3)), dims=("y", "x"))
        ndvi = analyzer.calculate_ndvi(red, nir)
        assert np.all(ndvi.values == 0.0)

    def test_ndvi_bare_soil(self, analyzer):
        red = xr.DataArray(np.full((3, 3), 0.3), dims=("y", "x"))
        nir = xr.DataArray(np.full((3, 3), 0.35), dims=("y", "x"))
        ndvi = analyzer.calculate_ndvi(red, nir)
        assert float(ndvi.mean()) < 0.15


class TestEVI:
    def test_evi_range(self, analyzer, sample_bands):
        red, nir, blue = sample_bands
        evi = analyzer.calculate_evi(red, nir, blue)
        assert float(evi.min()) >= -1.0
        assert float(evi.max()) <= 1.0

    def test_evi_shape(self, analyzer, sample_bands):
        red, nir, blue = sample_bands
        evi = analyzer.calculate_evi(red, nir, blue)
        assert evi.shape == red.shape


class TestCanopyCover:
    def test_canopy_cover_range(self, analyzer):
        ndvi = xr.DataArray(np.random.uniform(0.0, 1.0, (10, 10)), dims=("y", "x"))
        cover = analyzer.estimate_canopy_cover(ndvi)
        assert float(cover.min()) >= 0.0
        assert float(cover.max()) <= 100.0

    def test_canopy_cover_dense_forest(self, analyzer):
        ndvi = xr.DataArray(np.full((5, 5), 0.85), dims=("y", "x"))
        cover = analyzer.estimate_canopy_cover(ndvi)
        assert float(cover.mean()) > 80.0

    def test_canopy_cover_squared_method(self, analyzer):
        ndvi = xr.DataArray(np.full((5, 5), 0.5), dims=("y", "x"))
        linear = analyzer.estimate_canopy_cover(ndvi, method="linear")
        squared = analyzer.estimate_canopy_cover(ndvi, method="squared")
        assert float(squared.mean()) < float(linear.mean())


class TestLAI:
    def test_lai_positive(self, analyzer):
        ndvi = xr.DataArray(np.full((5, 5), 0.7), dims=("y", "x"))
        lai = analyzer.estimate_leaf_area_index(ndvi)
        assert float(lai.mean()) > 0.0

    def test_lai_increases_with_ndvi(self, analyzer):
        ndvi_low = xr.DataArray(np.full((3, 3), 0.3), dims=("y", "x"))
        ndvi_high = xr.DataArray(np.full((3, 3), 0.8), dims=("y", "x"))
        lai_low = analyzer.estimate_leaf_area_index(ndvi_low)
        lai_high = analyzer.estimate_leaf_area_index(ndvi_high)
        assert float(lai_high.mean()) > float(lai_low.mean())


class TestCanopyGaps:
    def test_detect_gaps(self, analyzer):
        ndvi = xr.DataArray(np.random.uniform(0.1, 0.8, (10, 10)), dims=("y", "x"))
        result = analyzer.detect_canopy_gaps(ndvi, gap_threshold=0.4)
        assert "gap_mask" in result
        assert result.attrs["gap_fraction"] >= 0.0
        assert result.attrs["gap_fraction"] <= 1.0

    def test_no_gaps_in_dense_forest(self, analyzer):
        ndvi = xr.DataArray(np.full((5, 5), 0.85), dims=("y", "x"))
        result = analyzer.detect_canopy_gaps(ndvi)
        assert result.attrs["gap_pixel_count"] == 0


class TestCanopyDensity:
    def test_classification_categories(self, analyzer):
        ndvi = xr.DataArray(
            np.array([[0.1, 0.3, 0.5], [0.7, 0.85, 0.0]]),
            dims=("y", "x"),
        )
        density = analyzer.classify_canopy_density(ndvi)
        assert int(density.values[0, 0]) == 0  # < 0.2
        assert int(density.values[0, 1]) == 1  # 0.2-0.4
        assert int(density.values[0, 2]) == 2  # 0.4-0.6
        assert int(density.values[1, 0]) == 3  # 0.6-0.8
        assert int(density.values[1, 1]) == 4  # >= 0.8
