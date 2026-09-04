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


def _synthetic_regional_network() -> gpd.GeoDataFrame:
    """Deterministic NHDPlus-HR-style regional flowline network for the PNW.

    The former ``cascadia_nhdplus_flowlines.geojson`` extract was never
    committed; these tests run against this synthetic dataset instead, which
    preserves upstream regression topology cases, not measured regional coverage (COMIDs 17000001-17000012,
    major-basin names, Strahler orders, distances).
    """
    from shapely.geometry import LineString

    reaches = [
        # Columbia trunk: Clearwater -> Snake -> lower Columbia -> estuary.
        (
            17000001,
            "Columbia River Estuary Reach",
            "Columbia River",
            8,
            "N6",
            "N7",
            70.0,
            [(-123.95, 46.25), (-124.05, 46.3)],
        ),
        (
            17000002,
            "Columbia River Lower Reach",
            "Columbia River",
            8,
            "N5",
            "N6",
            90.0,
            [(-122.75, 45.62), (-123.35, 45.62)],
        ),
        (
            17000007,
            "Snake River Lower Reach",
            "Snake River",
            8,
            "N4",
            "N5",
            100.0,
            [(-119.8, 46.1), (-121.0, 45.9)],
        ),
        (
            17000010,
            "Snake River Middle Reach",
            "Snake River",
            8,
            "N3",
            "N4",
            150.0,
            [(-118.5, 46.2), (-119.8, 46.1)],
        ),
        (
            17000011,
            "Snake River Upper Reach",
            "Snake River",
            8,
            "N2",
            "N3",
            120.0,
            [(-117.2, 46.4), (-118.5, 46.2)],
        ),
        (
            17000012,
            "Clearwater River Reach",
            "Clearwater River",
            6,
            "N1",
            "N2",
            80.0,
            [(-116.9, 46.4), (-117.2, 46.4)],
        ),
        # Willamette system joining the Columbia at the Portland confluence.
        (
            17000003,
            "Willamette River Lower Reach",
            "Willamette River",
            7,
            "W3",
            "N5",
            70.0,
            [(-122.67, 45.52), (-122.72, 45.6)],
        ),
        (
            17000004,
            "Willamette River Middle Reach",
            "Willamette River",
            6,
            "W2",
            "W3",
            80.0,
            [(-122.6, 45.0), (-122.67, 45.5)],
        ),
        (
            17000005,
            "McKenzie River Reach",
            "McKenzie River",
            5,
            "W1",
            "W2",
            60.0,
            [(-122.0, 44.2), (-122.6, 45.0)],
        ),
        (
            17000006,
            "Santiam River Reach",
            "Santiam River",
            5,
            "S1",
            "W3",
            50.0,
            [(-122.3, 44.7), (-122.6, 45.0)],
        ),
        # Independent coastal basin trunks.
        (
            17090001,
            "Klamath River Upper Reach",
            "Klamath River",
            5,
            "K1",
            "K2",
            60.0,
            [(-121.8, 42.4), (-122.3, 42.1)],
        ),
        (
            17090002,
            "Klamath River Lower Reach",
            "Klamath River",
            6,
            "K2",
            "K3",
            40.0,
            [(-122.3, 42.1), (-123.0, 41.8)],
        ),
        (
            17110001,
            "Skagit River Upper Reach",
            "Skagit River",
            5,
            "G1",
            "G2",
            50.0,
            [(-121.4, 48.5), (-121.8, 48.45)],
        ),
        (
            17110002,
            "Skagit River Lower Reach",
            "Skagit River",
            6,
            "G2",
            "G3",
            30.0,
            [(-121.8, 48.45), (-122.3, 48.4)],
        ),
        (
            17080001,
            "Fraser River Upper Reach",
            "Fraser River",
            6,
            "F1",
            "F2",
            80.0,
            [(-121.6, 49.4), (-122.0, 49.2)],
        ),
        (
            17080002,
            "Fraser River Lower Reach",
            "Fraser River",
            7,
            "F2",
            "F3",
            60.0,
            [(-122.0, 49.2), (-122.8, 49.1)],
        ),
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
            comid,
            name,
            mainstem,
            order,
            from_node,
            to_node,
            length_km,
            coords,
        ) in reaches
    ]
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def test_constructed_regional_branching_retains_upstream_regressions(
    tmp_path, monkeypatch
):
    """Preserve upstream routing/accumulation coverage with declared constructed data."""
    frame = _synthetic_regional_network()
    path = tmp_path / "constructed-network.geojson"
    frame.to_file(path, driver="GeoJSON")
    monkeypatch.setenv("GEO_INFER_CASCADIA_FLOWLINES_PATH", str(path))
    monkeypatch.setenv("GEO_INFER_SURFACE_WATER_OFFLINE", "1")
    source = CascadianSurfaceWaterDataSources()
    network = source.get_flowline_network(4)
    downstream = network.trace_downstream(17000012)
    assert [reach["comid"] for reach in downstream] == [
        17000012,
        17000011,
        17000010,
        17000007,
        17000002,
        17000001,
    ]
    assert sum(reach["length_km"] for reach in downstream) == pytest.approx(610.0)
    upstream = network.trace_upstream(17000003)
    assert {reach["comid"] for reach in upstream} == {
        17000003,
        17000004,
        17000005,
        17000006,
    }
    assert sum(reach["length_km"] for reach in upstream) == pytest.approx(260.0)
    assert network.graph.number_of_edges() == 16
    assert network.validate()["component_count"] == 4
    center = latlng_to_cell(45.6, -122.7, 7)
    targets = list(grid_disk(center, 1))

    class Backend:
        h3_resolution = 7
        target_hexagons = targets

    result = GeoInferSurfaceWater(Backend(), data_source=source).run_analysis(targets)
    assert sum(row["flowline_length_km"] for row in result.values()) > 0
    assert any(row["has_high_order_river"] for row in result.values())


def test_projection_fallback_requires_opt_in_and_records_degradation(
    tmp_path, monkeypatch
):
    """A failed projection raises by default; opted-in raw output advertises it."""
    from pyproj.exceptions import CRSError

    monkeypatch.chdir(tmp_path)

    class Backend:
        h3_resolution = 7
        target_hexagons = list(grid_disk(latlng_to_cell(41.92, -124.20, 7), 1))

    source = CascadianSurfaceWaterDataSources(flowlines=sample_flowlines())
    strict = GeoInferSurfaceWater(Backend(), data_source=source)
    fallback = GeoInferSurfaceWater(
        Backend(), data_source=source, allow_projection_fallback=True
    )

    def reject_projection(*args, **kwargs):
        raise CRSError("Constructed projection failure")

    monkeypatch.setattr(gpd.GeoDataFrame, "to_crs", reject_projection)
    with pytest.raises(CRSError, match="Constructed projection failure"):
        strict.acquire_raw_data()
    assert not strict.projection_degraded
    assert not (tmp_path / "output/data/raw_surface_water_data.geojson").exists()
    path = fallback.acquire_raw_data()
    assert fallback.projection_degraded
    frame = gpd.read_file(path)
    assert frame["projection_degraded"].all()
    assert frame.geom_type.isin(["LineString", "MultiLineString"]).all()
