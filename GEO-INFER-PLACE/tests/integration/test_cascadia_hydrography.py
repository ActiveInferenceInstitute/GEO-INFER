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

from pathlib import Path
from typing import Any, Dict, List

import geopandas as gpd
import pytest
from shapely.geometry import Point


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


def _synthetic_regional_network() -> gpd.GeoDataFrame:
    """Deterministic NHDPlus-HR-style regional flowline network for the PNW.

    The tracked ``cascadia_nhdplus_flowlines.geojson`` extract was never
    committed; these tests run against this synthetic dataset instead, which
    preserves the documented topology contract (COMIDs 17000001-17000012,
    major-basin names, Strahler orders, distances).
    """
    from shapely.geometry import LineString

    reaches = [
        # Columbia trunk: Clearwater -> Snake -> lower Columbia -> estuary.
        (17000001, "Columbia River Estuary Reach", "Columbia River", 8,
         "N6", "N7", 70.0, [(-123.95, 46.25), (-124.05, 46.3)]),
        (17000002, "Columbia River Lower Reach", "Columbia River", 8,
         "N5", "N6", 90.0, [(-122.75, 45.62), (-123.35, 45.62)]),
        (17000007, "Snake River Lower Reach", "Snake River", 8,
         "N4", "N5", 100.0, [(-119.8, 46.1), (-121.0, 45.9)]),
        (17000010, "Snake River Middle Reach", "Snake River", 8,
         "N3", "N4", 150.0, [(-118.5, 46.2), (-119.8, 46.1)]),
        (17000011, "Snake River Upper Reach", "Snake River", 8,
         "N2", "N3", 120.0, [(-117.2, 46.4), (-118.5, 46.2)]),
        (17000012, "Clearwater River Reach", "Clearwater River", 6,
         "N1", "N2", 80.0, [(-116.9, 46.4), (-117.2, 46.4)]),
        # Willamette system joining the Columbia at the Portland confluence.
        (17000003, "Willamette River Lower Reach", "Willamette River", 7,
         "W3", "N5", 70.0, [(-122.67, 45.52), (-122.72, 45.6)]),
        (17000004, "Willamette River Middle Reach", "Willamette River", 6,
         "W2", "W3", 80.0, [(-122.6, 45.0), (-122.67, 45.5)]),
        (17000005, "McKenzie River Reach", "McKenzie River", 5,
         "W1", "W2", 60.0, [(-122.0, 44.2), (-122.6, 45.0)]),
        (17000006, "Santiam River Reach", "Santiam River", 5,
         "S1", "W3", 50.0, [(-122.3, 44.7), (-122.6, 45.0)]),
        # Independent coastal basin trunks.
        (17090001, "Klamath River Upper Reach", "Klamath River", 5,
         "K1", "K2", 60.0, [(-121.8, 42.4), (-122.3, 42.1)]),
        (17090002, "Klamath River Lower Reach", "Klamath River", 6,
         "K2", "K3", 40.0, [(-122.3, 42.1), (-123.0, 41.8)]),
        (17110001, "Skagit River Upper Reach", "Skagit River", 5,
         "G1", "G2", 50.0, [(-121.4, 48.5), (-121.8, 48.45)]),
        (17110002, "Skagit River Lower Reach", "Skagit River", 6,
         "G2", "G3", 30.0, [(-121.8, 48.45), (-122.3, 48.4)]),
        (17080001, "Fraser River Upper Reach", "Fraser River", 6,
         "F1", "F2", 80.0, [(-121.6, 49.4), (-122.0, 49.2)]),
        (17080002, "Fraser River Lower Reach", "Fraser River", 7,
         "F2", "F3", 60.0, [(-122.0, 49.2), (-122.8, 49.1)]),
    ]
    records = [
        {
            "comid": comid,
            "gnis_name": name,
            "mainstem": mainstem,
            "basin": f"{mainstem} Basin",
            "reachcode": f"17{comid:09d}",
            "stream_order": order,
            "from_node": from_node,
            "to_node": to_node,
            "length_km": length_km,
            "geometry": LineString(coords),
        }
        for (
            comid, name, mainstem, order, from_node, to_node, length_km, coords
        ) in reaches
    ]
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


@pytest.fixture
def pnw_flowlines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> CascadiaFlowlineNetwork:
    """Point the surface-water data source at the synthetic regional network."""
    geojson_path = tmp_path / "cascadia_nhdplus_flowlines.geojson"
    _synthetic_regional_network().to_file(geojson_path, driver="GeoJSON")
    monkeypatch.setenv("GEO_INFER_CASCADIA_FLOWLINES_PATH", str(geojson_path))
    monkeypatch.setenv("GEO_INFER_SURFACE_WATER_OFFLINE", "1")
    ds = CascadianSurfaceWaterDataSources()
    return ds.get_flowline_network(min_stream_order=4)


class TestCascadiaHydrographyIntegration:
    """Integration test suite for Cascadia regional hydrography and flowline network."""

    def test_cascadia_major_basins_represented(
        self, pnw_flowlines: CascadiaFlowlineNetwork
    ):
        """Verify presence of key Pacific Northwest river systems across Cascadia."""
        gdf = pnw_flowlines.flowlines_gdf
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
        self, pnw_flowlines: CascadiaFlowlineNetwork
    ):
        """Trace downstream from Clearwater River tributary through Snake to Columbia estuary."""
        clearwater_reach = 17000012
        path = pnw_flowlines.trace_downstream(clearwater_reach)
        assert len(path) >= 4

        path_comids = [e["comid"] for e in path]
        assert path_comids == [17000012, 17000011, 17000010, 17000007, 17000002, 17000001]

        # Total distance from Clearwater to Pacific Ocean estuary outlet
        total_dist = sum(float(e["length_km"]) for e in path)
        assert total_dist > 600.0  # >600 km flow path

    def test_willamette_basin_upstream_accumulation(
        self, pnw_flowlines: CascadiaFlowlineNetwork
    ):
        """Trace upstream from lower Willamette River through McKenzie and Santiam tributaries."""
        lower_willamette = 17000003
        upstream = pnw_flowlines.trace_upstream(lower_willamette)
        assert len(upstream) >= 4

        names = [e.get("gnis_name", "") for e in upstream]
        assert any("Willamette" in n for n in names)
        assert any("Santiam" in n for n in names)
        assert any("McKenzie" in n for n in names)

        total_upstream_length = sum(float(e["length_km"]) for e in upstream)
        assert total_upstream_length > 250.0

    def test_h3_surface_water_grid_overlay(
        self, pnw_flowlines: CascadiaFlowlineNetwork
    ):
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
