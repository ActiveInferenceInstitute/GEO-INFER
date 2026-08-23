#!/usr/bin/env python3
"""
Integration tests for Cascadia high-resolution hydrography pipeline and NHDPlus HR flowlines.

Verifies end-to-end:
- GeoInferSurfaceWater analysis execution on real Cascadia H3 hexagonal grids
- Integration of NHDPlus HR vector flowlines with H3 space overlay
- Multi-tributary drainage network routing across the Columbia, Willamette, Snake, Fraser, and Klamath basins
- Downstream-to-outlet travel distance and upstream accumulation metrics
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import geopandas as gpd
import pytest
from shapely.geometry import Point

# Ensure cascadia module is on sys.path
_CASCADIA_DIR = (
    Path(__file__).resolve().parents[2] / "locations" / "cascadia"
)
if str(_CASCADIA_DIR) not in sys.path:
    sys.path.insert(0, str(_CASCADIA_DIR))

from geo_infer_space.utils.h3_utils import (
    latlng_to_cell,
    grid_disk,
)
from src.data_modules.surface_water.flowline_network import (
    CascadiaFlowlineNetwork,
    FlowlineTopologyValidator,
)
from src.data_modules.surface_water.data_sources import (
    CascadianSurfaceWaterDataSources,
)
from src.data_modules.surface_water.geo_infer_surface_water import (
    GeoInferSurfaceWater,
)


class TestCascadiaHydrographyIntegration:
    """Integration test suite for Cascadia regional hydrography and flowline network."""

    @pytest.fixture
    def cascadia_flowlines_network(self) -> CascadiaFlowlineNetwork:
        """Load the tracked Cascadia NHDPlus HR flowline dataset."""
        ds = CascadianSurfaceWaterDataSources()
        return ds.get_flowline_network(min_stream_order=4)

    def test_cascadia_major_basins_represented(
        self, cascadia_flowlines_network: CascadiaFlowlineNetwork
    ):
        """Verify presence of key Pacific Northwest river systems across Cascadia."""
        gdf = cascadia_flowlines_network.flowlines_gdf
        assert not gdf.empty

        names = gdf["gnis_name"].tolist()
        mainstems = gdf["mainstem"].tolist()
        all_names = set(names + mainstems)

        # Check major river systems
        assert any("Columbia" in n for n in all_names)
        assert any("Willamette" in n for n in all_names)
        assert any("Snake" in n for n in all_names)
        assert any("Klamath" in n for n in all_names)
        assert any("Skagit" in n for n in all_names)
        assert any("Fraser" in n for n in all_names)

    def test_columbia_basin_full_downstream_route(
        self, cascadia_flowlines_network: CascadiaFlowlineNetwork
    ):
        """Trace downstream from Clearwater River tributary through Snake to Columbia estuary."""
        clearwater_reach = 17000012
        path = cascadia_flowlines_network.trace_downstream(clearwater_reach)
        assert len(path) >= 4

        path_comids = [e["comid"] for e in path]
        assert path_comids == [17000012, 17000011, 17000010, 17000007, 17000002, 17000001]

        # Total distance from Clearwater to Pacific Ocean estuary outlet
        total_dist = sum(float(e["length_km"]) for e in path)
        assert total_dist > 600.0  # >600 km flow path

    def test_willamette_basin_upstream_accumulation(
        self, cascadia_flowlines_network: CascadiaFlowlineNetwork
    ):
        """Trace upstream from lower Willamette River through McKenzie and Santiam tributaries."""
        lower_willamette = 17000003
        upstream = cascadia_flowlines_network.trace_upstream(lower_willamette)
        assert len(upstream) >= 4

        names = [e.get("gnis_name", "") for e in upstream]
        assert any("Willamette" in n for n in names)
        assert any("Santiam" in n for n in names)
        assert any("McKenzie" in n for n in names)

        total_upstream_length = sum(float(e["length_km"]) for e in upstream)
        assert total_upstream_length > 250.0

    def test_h3_surface_water_grid_overlay(self):
        """Run GeoInferSurfaceWater analysis on target H3 cells covering Portland/Columbia confluence."""
        # Portland / Vancouver confluence area (~45.6, -122.7)
        center_cell = latlng_to_cell(45.6, -122.7, 7)
        assert center_cell is not None
        target_cells = list(grid_disk(center_cell, 1))

        class RealGridBackend:
            h3_resolution = 7
            target_hexagons = target_cells

        sw = GeoInferSurfaceWater(RealGridBackend())  # type: ignore[arg-type]
        results = sw.run_analysis(target_cells)

        assert len(results) == len(target_cells)
        # At least one cell in the disk must intersect the Columbia / Willamette flowlines
        total_flow_km = sum(data["flowline_length_km"] for data in results.values())
        assert total_flow_km > 0.0

        high_order_cells = [
            cid for cid, data in results.items() if data.get("has_high_order_river")
        ]
        assert len(high_order_cells) >= 1

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
