"""Tests for deforestation detection module."""

import numpy as np
import pytest
import xarray as xr


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

    def test_intact_forest_has_no_edges(self, detector):
        result = detector.calculate_fragmentation_index(
            xr.DataArray(np.ones((3, 3)), dims=("y", "x"))
        )
        assert result["edge_pixel_count"] == 0
        assert result["core_pixel_count"] == 9
        assert result["edge_density"] == 0.0
        assert result["core_fraction"] == 1.0

    def test_isolated_pixel_is_all_edge(self, detector):
        mask = np.zeros((3, 3))
        mask[1, 1] = 1.0
        result = detector.calculate_fragmentation_index(
            xr.DataArray(mask, dims=("y", "x"))
        )
        assert result["edge_pixel_count"] == 1
        assert result["core_pixel_count"] == 0
        assert result["edge_density"] == 1.0

    def test_image_boundary_alone_is_not_edge(self, detector):
        # Only a non-forest IN-BOUNDS neighbor makes an edge; the map
        # border does not.
        mask = np.zeros((3, 3))
        mask[0, :] = 1.0
        result = detector.calculate_fragmentation_index(
            xr.DataArray(mask, dims=("y", "x"))
        )
        assert result["edge_pixel_count"] == 3

    def test_adjacent_pair_is_core(self, detector):
        result = detector.calculate_fragmentation_index(
            xr.DataArray(np.array([[1.0, 1.0]]), dims=("y", "x"))
        )
        assert result["edge_pixel_count"] == 0
        assert result["core_pixel_count"] == 2

    def test_multilayer_sums_per_layer_edges(self, detector):
        rng = np.random.default_rng(42)
        layers = (rng.random((3, 7, 5)) > 0.5).astype(float)
        stacked = detector.calculate_fragmentation_index(
            xr.DataArray(layers, dims=("time", "y", "x"))
        )
        per_layer = [
            detector.calculate_fragmentation_index(
                xr.DataArray(layers[t], dims=("y", "x"))
            )["edge_pixel_count"]
            for t in range(3)
        ]
        assert stacked["edge_pixel_count"] == sum(per_layer)

    def test_matches_bruteforce_reference(self, detector):
        data = (np.random.default_rng(7).random((8, 9)) > 0.5).astype(float)
        expected = 0
        for i in range(8):
            for j in range(9):
                if data[i, j] > 0:
                    neighbors = [
                        data[ni, nj]
                        for ni, nj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                        if 0 <= ni < 8 and 0 <= nj < 9
                    ]
                    if any(v == 0.0 for v in neighbors):
                        expected += 1
        result = detector.calculate_fragmentation_index(
            xr.DataArray(data, dims=("y", "x"))
        )
        assert result["edge_pixel_count"] == expected
