"""Geospatial runner output contracts for ACT H3 and spatial scenarios."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pytest
from PIL import Image

from geo_infer_act.runners import RunConfig, run_scenario


GEOSPATIAL_REQUIRED_FILES = {
    "data/full_history.json",
    "data/step_metrics.csv",
    "data/h3_cells.csv",
    "data/h3_diagnostics.json",
    "data/h3_cells.geojson",
    "analysis/run_summary.json",
    "visualizations/h3_cell_metric_map.png",
    "visualizations/free_energy_evolution.png",
    "visualizations/belief_entropy_coherence.png",
    "visualizations/interactive_h3_map.html",
}


def _assert_visualization_artifact(result, relative_path: str) -> None:
    manifest = json.loads(result.manifest_path.read_text())
    entries = {item["path"]: item for item in manifest["generated_files"]}
    assert relative_path in entries
    entry = entries[relative_path]
    assert entry["artifact_type"] == "visualization"
    assert entry["sha256"]
    assert entry["mime_type"] in {"image/png", "text/html"}
    assert entry["description"]
    assert entry["alt_text"]
    assert entry["data_sources"]
    assert entry["plotted_metrics"]

    figure_path = result.output_dir / relative_path
    metadata_path = result.output_dir / entry["figure_metadata_path"]
    data_path = result.output_dir / entry["figure_data_path"]
    assert figure_path.exists() and figure_path.stat().st_size > 0
    assert metadata_path.exists() and metadata_path.stat().st_size > 0
    assert data_path.exists() and data_path.stat().st_size > 0

    metadata = json.loads(metadata_path.read_text())
    assert metadata["schema_version"] == "geo-infer-act-figure-artifact/v1"
    assert metadata["scenario"] == result.scenario
    assert metadata["figure_path"] == relative_path
    assert metadata["figure_data_path"] == entry["figure_data_path"]
    assert metadata["sha256"] == entry["sha256"]
    assert metadata["data_sources"] == entry["data_sources"]
    assert metadata["plotted_metrics"] == entry["plotted_metrics"]
    for source in metadata["data_sources"]:
        assert (result.output_dir / source).exists(), source

    if relative_path.endswith(".png"):
        with Image.open(figure_path) as image:
            assert image.size[0] > 100 and image.size[1] > 100
            embedded = json.loads(image.info["geo_infer_act_metadata"])
        assert embedded["schema_version"] == metadata["schema_version"]
        assert embedded["scenario"] == metadata["scenario"]
        assert embedded["figure_id"] == metadata["figure_id"]
    elif relative_path.endswith(".html"):
        html = figure_path.read_text()
        assert 'id="geo-infer-act-figure-metadata"' in html
        assert metadata["schema_version"] in html


def _assert_numeric_sidecar(data_path: Path) -> None:
    if data_path.suffix == ".csv":
        with data_path.open() as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        for row in rows:
            for value in row.values():
                try:
                    numeric = float(value)
                except (TypeError, ValueError):
                    continue
                assert math.isfinite(numeric)
    else:
        payload = json.loads(data_path.read_text())
        assert payload


@pytest.mark.parametrize("scenario", ["h3", "spatial"])
def test_geospatial_scenarios_emit_complete_data_and_visualizations(
    scenario: str, tmp_path: Path
) -> None:
    result = run_scenario(
        RunConfig(
            scenario=scenario,
            output_dir=tmp_path / scenario,
            seed=31,
            deterministic=True,
            timesteps=3,
            visualizations=True,
            h3_resolution=8,
            h3_ring_size=1,
        )
    )

    manifest = json.loads(result.manifest_path.read_text())
    generated = {item["path"] for item in manifest["generated_files"]}
    assert manifest["validation"]["status"] == "passed"
    assert GEOSPATIAL_REQUIRED_FILES <= generated

    for relative_path in GEOSPATIAL_REQUIRED_FILES:
        path = result.output_dir / relative_path
        assert path.exists(), relative_path
        assert path.stat().st_size > 0, relative_path

    geojson = json.loads((result.output_dir / "data" / "h3_cells.geojson").read_text())
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == manifest["metrics"]["cell_count"]
    for feature in geojson["features"]:
        assert feature["geometry"]["type"] == "Polygon"
        assert feature["properties"]["h3_cell"]
        assert feature["properties"]["resolution"] == 8

    diagnostics = json.loads(
        (result.output_dir / "data" / "h3_diagnostics.json").read_text()
    )
    assert len(diagnostics) == 3
    for row in diagnostics:
        assert math.isfinite(float(row["aggregate_free_energy"]))
        consistency = row["spatial_consistency"]
        assert math.isfinite(float(consistency["global_coherence"]))
        assert math.isfinite(float(consistency["neighbor_correlations"]))

    with (result.output_dir / "data" / "step_metrics.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    for row in rows:
        assert math.isfinite(float(row["free_energy"]))
        assert math.isfinite(float(row["expected_free_energy"]))
        assert math.isfinite(float(row["belief_entropy"]))
        assert math.isfinite(float(row["coherence"]))


def test_geospatial_manifest_references_only_existing_files(tmp_path: Path) -> None:
    result = run_scenario(
        RunConfig(
            scenario="h3",
            output_dir=tmp_path / "h3",
            seed=9,
            timesteps=2,
            visualizations=True,
        )
    )
    manifest = json.loads(result.manifest_path.read_text())

    for item in manifest["generated_files"]:
        referenced = result.output_dir / item["path"]
        assert referenced.exists(), item["path"]
        assert referenced.stat().st_size == item["size_bytes"]


@pytest.mark.parametrize("scenario", ["h3", "spatial"])
def test_geospatial_visualizations_have_metadata_and_data_sidecars(
    scenario: str, tmp_path: Path
) -> None:
    result = run_scenario(
        RunConfig(
            scenario=scenario,
            output_dir=tmp_path / scenario,
            seed=19,
            deterministic=True,
            timesteps=3,
            visualizations=True,
            h3_resolution=8,
            h3_ring_size=1,
        )
    )
    manifest = json.loads(result.manifest_path.read_text())
    visualizations = [
        item["path"]
        for item in manifest["generated_files"]
        if item["artifact_type"] == "visualization"
    ]
    assert {
        "visualizations/h3_cell_metric_map.png",
        "visualizations/free_energy_evolution.png",
        "visualizations/belief_entropy_coherence.png",
        "visualizations/interactive_h3_map.html",
    } <= set(visualizations)

    for relative_path in visualizations:
        _assert_visualization_artifact(result, relative_path)
        entry = {item["path"]: item for item in manifest["generated_files"]}[
            relative_path
        ]
        _assert_numeric_sidecar(result.output_dir / entry["figure_data_path"])
