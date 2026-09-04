#!/usr/bin/env python3
"""
Integration tests for Cascadia high-resolution hydrography pipeline and NHDPlus HR flowlines.

Verifies end-to-end:
- GeoInferSurfaceWater analysis execution on real Cascadia H3 hexagonal grids
- Integration of NHDPlus HR vector flowlines with H3 space overlay
- Native topology preservation and within-excerpt routing for measured Smith River reaches
- Explicit distinction between sampled extent boundaries and basin outlets
"""

from __future__ import annotations


import geopandas as gpd
import pytest

from geo_infer_space.utils.h3_utils import latlng_to_cell, grid_disk
from geo_infer_place.hydrography import (
    CascadiaFlowlineNetwork,
    CascadianSurfaceWaterDataSources,
    GeoInferSurfaceWater,
    sample_flowlines,
)


class TestCascadiaHydrographyIntegration:
    """Integration test suite for Cascadia regional hydrography and flowline network."""

    def test_smith_river_excerpt_preserves_source_ids_and_topology(self):
        """Actual USGS sample proves native attributes survive package loading."""
        gdf = sample_flowlines()
        assert len(gdf) == 34
        assert all(gdf["reachcode"].str.startswith("18010101"))
        assert "Smith River" in set(gdf["gnis_name"])
        assert set(gdf["comid"]) == set(gdf["nhdplusid"])
        net = CascadiaFlowlineNetwork(gdf)
        assert net.graph.number_of_edges() == len(gdf)
        assert net.validate()["dag_validation"]["is_dag"]
        # Trace an actual connected path within this bounded excerpt, not to a
        # claimed basin outlet outside the retrieved extent.
        paths = [net.trace_downstream(int(c)) for c in gdf["comid"]]
        longest = max(paths, key=len)
        assert len(longest) >= 3
        for upstream, downstream in zip(longest, longest[1:]):
            assert upstream["to_node"] == downstream["from_node"]
        assert sum(r["length_km"] for r in longest) > 0

    def test_h3_surface_water_grid_overlay(self):
        """Run GeoInferSurfaceWater analysis on target H3 cells covering the lower Smith River."""
        # Lower Smith River excerpt center
        center_cell = latlng_to_cell(41.92, -124.20, 7)
        assert center_cell is not None
        target_cells = list(grid_disk(center_cell, 1))

        class RealGridBackend:
            h3_resolution = 7
            target_hexagons = target_cells

        sw = GeoInferSurfaceWater(
            RealGridBackend(),
            data_source=CascadianSurfaceWaterDataSources(flowlines=sample_flowlines()),
        )  # type: ignore[arg-type]
        results = sw.run_analysis(target_cells)

        assert len(results) == len(target_cells)
        # At least one cell in the disk must intersect the Smith River flowlines
        total_flow_km = sum(data["flowline_length_km"] for data in results.values())
        assert total_flow_km > 0.0

        high_order_cells = [
            cid for cid, data in results.items() if data.get("has_high_order_river")
        ]
        assert len(high_order_cells) >= 1
        assert all(row["water_body_area_sqkm"] is None for row in results.values())

    def test_run_final_analysis_flowline_feature_aggregation(self):
        """Verify run_final_analysis summarizes stream order and flowline counts."""

        class DummyBackend:
            h3_resolution = 8
            target_hexagons = []

        sw = GeoInferSurfaceWater(DummyBackend())  # type: ignore[arg-type]

        sample_h3_data = {
            "8828308281fffff": [
                {
                    "layer": "flowlines",
                    "gnis_name": "Columbia River",
                    "stream_order": 8,
                },
                {
                    "layer": "waterbodies",
                    "gnis_name": "Columbia Estuary",
                    "stream_order": 0,
                },
            ],
            "8828308283fffff": [
                {
                    "layer": "flowlines",
                    "gnis_name": "Unnamed Creek",
                    "stream_order": 2,
                }
            ],
            "8828308285fffff": [],
        }

        summary = sw.run_final_analysis(sample_h3_data)
        assert summary["8828308281fffff"]["has_water"] is True
        assert summary["8828308281fffff"]["flowline_feature_count"] == 1
        assert summary["8828308281fffff"]["waterbody_feature_count"] == 1
        assert summary["8828308281fffff"]["max_stream_order"] == 8
        assert summary["8828308281fffff"]["has_high_order_river"] is True

        assert summary["8828308283fffff"]["has_water"] is True
        assert summary["8828308283fffff"]["max_stream_order"] == 2
        assert summary["8828308283fffff"]["has_high_order_river"] is False

        assert summary["8828308285fffff"]["has_water"] is False
        assert summary["8828308285fffff"]["max_stream_order"] == 0


def test_acquire_raw_data_accepts_real_geodataframes(tmp_path, monkeypatch):
    """Regression for ambiguous GeoDataFrame truth-value in acquisition."""
    monkeypatch.chdir(tmp_path)

    class Backend:
        h3_resolution = 7
        target_hexagons = list(grid_disk(latlng_to_cell(41.92, -124.20, 7), 1))

    source = CascadianSurfaceWaterDataSources(flowlines=sample_flowlines())
    sw = GeoInferSurfaceWater(Backend(), data_source=source)
    path = sw.acquire_raw_data()
    data = gpd.read_file(path)
    assert len(data) > 0
    assert set(data["layer"]) == {"flowlines"}


def test_empty_target_does_not_trigger_regional_download():
    class Backend:
        target_hexagons = []

    sw = GeoInferSurfaceWater(Backend())
    assert sw.run_analysis([]) == {}
    with pytest.raises(ValueError, match="Explicit"):
        sw.acquire_raw_data()
