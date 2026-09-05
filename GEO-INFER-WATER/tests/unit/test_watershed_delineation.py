"""Tests for watershed delineation module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_water.core.watershed_delineation import WatershedDelineator


@pytest.fixture
def delineator():
    return WatershedDelineator()


@pytest.fixture
def simple_dem():
    """Create a simple V-shaped valley DEM."""
    dem = np.array(
        [
            [9, 8, 7, 8, 9],
            [8, 7, 5, 7, 8],
            [7, 5, 3, 5, 7],
            [8, 6, 4, 6, 8],
            [9, 7, 5, 7, 9],
        ],
        dtype=float,
    )
    return dem


class TestFlowDirection:
    def test_flow_direction_shape(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        assert flow_dir.shape == simple_dem.shape

    def test_flow_toward_lowest(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        assert flow_dir[2, 2] == 0  # Pit cell, lowest point

    def test_non_negative_values(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        assert np.all(flow_dir >= 0)


class TestFlowAccumulation:
    def test_accumulation_shape(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        accum = delineator.calculate_flow_accumulation(flow_dir)
        assert accum.shape == simple_dem.shape

    def test_minimum_accumulation_is_one(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        accum = delineator.calculate_flow_accumulation(flow_dir)
        assert float(np.min(accum)) >= 1.0

    def test_outlet_has_highest_accumulation(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        accum = delineator.calculate_flow_accumulation(flow_dir)
        assert accum[2, 2] == float(np.max(accum))


class TestBasinDelineation:
    def test_basin_includes_outlet(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        basin = delineator.delineate_basin(flow_dir, 2, 2)
        assert basin[2, 2] == 1

    def test_basin_binary(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        basin = delineator.delineate_basin(flow_dir, 2, 2)
        unique_vals = np.unique(basin)
        assert set(unique_vals).issubset({0, 1})

    def test_basin_contains_multiple_cells(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        basin = delineator.delineate_basin(flow_dir, 2, 2)
        assert int(np.sum(basin)) > 1


class TestStreamNetwork:
    def test_stream_extraction(self, delineator):
        accum = np.array([[1, 2, 3], [5, 50, 200], [10, 100, 500]], dtype=float)
        streams = delineator.extract_stream_network(accum, threshold=100)
        assert streams[1, 2] == 1
        assert streams[2, 1] == 1
        assert streams[2, 2] == 1
        assert streams[0, 0] == 0


class TestSlope:
    def test_flat_terrain(self, delineator):
        flat = np.ones((5, 5), dtype=float)
        slope = delineator.calculate_slope(flat)
        np.testing.assert_allclose(slope, 0.0, atol=1e-10)

    def test_slope_positive_on_gradient(self, delineator, simple_dem):
        slope = delineator.calculate_slope(simple_dem, cell_size=30.0)
        assert float(np.max(slope)) > 0


class TestFullDelineation:
    def test_full_pipeline(self, delineator, simple_dem):
        dem_da = xr.DataArray(simple_dem, dims=("y", "x"))
        result = delineator.full_delineation(dem_da, outlet=(2, 2))
        assert "flow_direction" in result
        assert "flow_accumulation" in result
        assert "basin_mask" in result
        assert "stream_network" in result
        assert "slope_degrees" in result
        assert result.attrs["basin_area_cells"] > 0

    def test_full_pipeline_area_attribute(self, delineator, simple_dem):
        dem_da = xr.DataArray(simple_dem, dims=("y", "x"))
        result = delineator.full_delineation(dem_da, outlet=(2, 2), cell_size=500.0)
        # Area is basin_cells * cell_size^2 / 1e6 km2.
        expected_km2 = result.attrs["basin_area_cells"] * (500.0 ** 2) / 1e6
        assert result.attrs["basin_area_km2"] == pytest.approx(expected_km2)

    def test_full_pipeline_outlet_in_basin(self, delineator, simple_dem):
        dem_da = xr.DataArray(simple_dem, dims=("y", "x"))
        result = delineator.full_delineation(dem_da, outlet=(2, 2))
        # The outlet cell must be inside the delineated basin.
        assert int(result["basin_mask"].values[2, 2]) == 1
        # Flow accumulation at the outlet is the maximum (everything
        # drains to the lowest point of the V-valley).
        accum = result["flow_accumulation"].values
        assert accum[2, 2] == float(np.max(accum))

    def test_delineate_basin_traces_upstream(self, delineator, simple_dem):
        flow_dir = delineator.calculate_flow_direction_d8(simple_dem)
        basin = delineator.delineate_basin(flow_dir, 2, 2)
        # The basin is a boolean mask that includes the outlet.
        assert basin[2, 2] == 1
        # Upstream cells draining to the outlet are part of the basin.
        assert int(np.sum(basin)) > 1
