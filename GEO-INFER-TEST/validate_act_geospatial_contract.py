#!/usr/bin/env python3
"""Validate GEO-INFER-ACT geospatial Active Inference contracts."""

from __future__ import annotations

import ast
import csv
import importlib
import inspect
import json
import math
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
ACT_ROOT = REPO_ROOT / "GEO-INFER-ACT"
ACT_SRC = ACT_ROOT / "src"
sys.path.insert(0, str(ACT_SRC))

REQUIRED_GEOSPATIAL_FILES = {
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
REQUIRED_FIGURE_METADATA_FIELDS = {
    "schema_version",
    "package",
    "package_version",
    "scenario",
    "figure_id",
    "title",
    "description",
    "alt_text",
    "generated_at",
    "run_config",
    "plotted_metrics",
    "data_sources",
    "figure_path",
    "figure_data_path",
    "sha256",
}

REQUIRED_DOCS = [
    ACT_ROOT / "README.md",
    ACT_ROOT / "docs" / "geospatial_applications.md",
    ACT_ROOT / "docs" / "active_inference_overview.md",
    ACT_ROOT / "docs" / "mathematical_framework.md",
    ACT_ROOT / "docs" / "free_energy_principle.md",
    ACT_ROOT / "examples" / "README.md",
    ACT_ROOT / "src" / "README.md",
    ACT_ROOT / "src" / "geo_infer_act" / "README.md",
]

REQUIRED_MERMAID_HEADINGS = [
    "Geospatial Active Inference Architecture",
    "H3 Perception-Action Sequence",
    "Runner Output Manifest Pipeline",
    "H3 Result and Schema Contracts",
    "Spatial Belief Propagation and Neighbor Diffusion",
    "Multi-Agent H3 Lattice Coordination",
    "Validation Flow",
    "Figure Artifact Metadata Pipeline",
    "Figure Sidecar Traceability",
    "Manifest Visualization Validation",
]

DOCSTRING_TARGETS = [
    ("geo_infer_act.core.generative_model", "GenerativeModel.enable_h3_spatial"),
    ("geo_infer_act.core.generative_model", "GenerativeModel.update_h3_beliefs"),
    ("geo_infer_act.core.active_inference", "ActiveInferenceModel.apply_to_h3"),
    ("geo_infer_act.core.active_inference", "ActiveInferenceModel.infer_over_h3_grid"),
    ("geo_infer_act.core.spatial_agent", "SpatialActiveInferenceAgent"),
    ("geo_infer_act.core.spatial_agent", "SpatialActiveInferenceAgent.step"),
    ("geo_infer_act.models.multi_agent", "MultiAgentModel.enable_h3_spatial"),
    ("geo_infer_act.models.multi_agent", "MultiAgentModel.simulate_h3_lattice"),
    ("geo_infer_act.utils.geospatial_ai", "EnvironmentalActiveInferenceEngine"),
    (
        "geo_infer_act.utils.geospatial_ai",
        "EnvironmentalActiveInferenceEngine.compute_spatial_priors",
    ),
    ("geo_infer_act.utils.geospatial_ai", "H3SpatialGraph"),
    ("geo_infer_act.utils.geospatial_ai", "LevelSpatialGraph"),
    ("geo_infer_act.utils.spatial_diagnostics", "SpatialDiagnostics"),
    ("geo_infer_act.runners.scenarios", "_run_h3_scenario"),
    ("geo_infer_act.runners.scenarios", "_plot_h3_summary"),
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def resolve_attr(module_name: str, dotted_name: str) -> Any:
    obj: Any = importlib.import_module(module_name)
    for part in dotted_name.split("."):
        obj = getattr(obj, part)
    return obj


def validate_docstrings() -> None:
    for module_name, dotted_name in DOCSTRING_TARGETS:
        obj = resolve_attr(module_name, dotted_name)
        if not inspect.getdoc(obj):
            fail(f"Missing docstring: {module_name}.{dotted_name}")

    for path in [
        ACT_SRC / "geo_infer_act" / "utils" / "geospatial_ai.py",
        ACT_SRC / "geo_infer_act" / "runners" / "scenarios.py",
    ]:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                name = node.name.lower()
                if any(key in name for key in ("h3", "spatial", "geo", "plot")):
                    if not ast.get_docstring(node):
                        fail(f"Missing geospatial docstring: {path}:{node.lineno}")


def validate_packaging() -> None:
    setup_text = (ACT_ROOT / "setup.py").read_text()
    pyproject_text = (ACT_ROOT / "pyproject.toml").read_text()
    if "h3>=3.7.0" in setup_text:
        fail("setup.py still advertises h3>=3.7.0")
    if "h3>=4.0.0" not in pyproject_text:
        fail("pyproject.toml does not require h3>=4.0.0")


def validate_geospatial_outputs() -> None:
    from geo_infer_act.runners import RunConfig, run_scenario
    from geo_infer_act.utils.h3_adapter import get_h3_adapter

    adapter = get_h3_adapter()
    with tempfile.TemporaryDirectory() as tmp:
        for scenario in ("h3", "spatial"):
            result = run_scenario(
                RunConfig(
                    scenario=scenario,
                    output_dir=Path(tmp) / scenario,
                    seed=23,
                    deterministic=True,
                    timesteps=3,
                    visualizations=True,
                    h3_resolution=8,
                    h3_ring_size=1,
                )
            )
            manifest = json.loads(result.manifest_path.read_text())
            if manifest["validation"]["status"] != "passed":
                fail(f"{scenario} manifest validation failed: {manifest['validation']}")

            generated = {item["path"] for item in manifest["generated_files"]}
            generated_entries = {
                item["path"]: item for item in manifest["generated_files"]
            }
            missing = sorted(REQUIRED_GEOSPATIAL_FILES - generated)
            if missing:
                fail(f"{scenario} missing geospatial outputs: {missing}")

            geojson_path = result.output_dir / "data" / "h3_cells.geojson"
            geojson = json.loads(geojson_path.read_text())
            if geojson.get("type") != "FeatureCollection":
                fail(f"{scenario} GeoJSON is not a FeatureCollection")
            if len(geojson.get("features", [])) != manifest["metrics"]["cell_count"]:
                fail(f"{scenario} GeoJSON feature count does not match cell_count")
            for feature in geojson["features"]:
                cell = feature["properties"]["h3_cell"]
                if not adapter.is_valid_cell(cell):
                    fail(f"{scenario} GeoJSON contains invalid H3 cell {cell}")
                if feature["geometry"]["type"] != "Polygon":
                    fail(f"{scenario} GeoJSON feature is not a Polygon")

            diagnostics = json.loads(
                (result.output_dir / "data" / "h3_diagnostics.json").read_text()
            )
            for row in diagnostics:
                if not math.isfinite(float(row["aggregate_free_energy"])):
                    fail(f"{scenario} aggregate free energy is not finite")
                consistency = row["spatial_consistency"]
                for key in ("global_coherence", "neighbor_correlations"):
                    if not math.isfinite(float(consistency[key])):
                        fail(f"{scenario} {key} is not finite")

            with (result.output_dir / "data" / "step_metrics.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            if len(rows) != 3:
                fail(f"{scenario} step_metrics.csv has wrong row count")
            for row in rows:
                for key in ("free_energy", "expected_free_energy", "belief_entropy"):
                    if not math.isfinite(float(row[key])):
                        fail(f"{scenario} {key} is not finite")

            validate_visualization_metadata(
                result.output_dir, scenario, generated_entries
            )


def validate_visualization_metadata(
    output_dir: Path, scenario: str, generated_entries: dict[str, dict[str, Any]]
) -> None:
    """Validate manifest-linked sidecars and embedded visualization metadata."""
    visualizations = [
        item
        for item in generated_entries.values()
        if item.get("artifact_type") == "visualization"
    ]
    if not visualizations:
        fail(f"{scenario} did not emit visualization manifest entries")

    for item in visualizations:
        path = item["path"]
        figure_path = output_dir / path
        metadata_rel = item.get("figure_metadata_path")
        data_rel = item.get("figure_data_path")
        if not metadata_rel or not data_rel:
            fail(f"{scenario} visualization missing sidecar fields: {path}")
        metadata_path = output_dir / metadata_rel
        data_path = output_dir / data_rel
        if not metadata_path.exists() or metadata_path.stat().st_size <= 0:
            fail(f"{scenario} missing figure metadata sidecar: {metadata_rel}")
        if not data_path.exists() or data_path.stat().st_size <= 0:
            fail(f"{scenario} missing figure data sidecar: {data_rel}")

        metadata = json.loads(metadata_path.read_text())
        missing_fields = sorted(REQUIRED_FIGURE_METADATA_FIELDS - set(metadata))
        if missing_fields:
            fail(f"{scenario} figure metadata missing {missing_fields}: {metadata_rel}")
        if metadata["schema_version"] != "geo-infer-act-figure-artifact/v1":
            fail(f"{scenario} figure metadata schema is wrong: {metadata_rel}")
        if metadata["scenario"] != scenario:
            fail(f"{scenario} figure metadata scenario mismatch: {metadata_rel}")
        if metadata["figure_path"] != path:
            fail(f"{scenario} figure metadata path mismatch: {metadata_rel}")
        if metadata["figure_data_path"] != data_rel:
            fail(f"{scenario} figure data path mismatch: {metadata_rel}")
        if metadata["sha256"] != item.get("sha256"):
            fail(f"{scenario} figure digest mismatch: {path}")
        if not metadata["data_sources"] or not metadata["plotted_metrics"]:
            fail(
                f"{scenario} figure metadata lacks data source or metric details: {path}"
            )
        for source in metadata["data_sources"]:
            if not (output_dir / source).exists():
                fail(f"{scenario} figure data source does not exist: {source}")

        if path.endswith(".png"):
            with Image.open(figure_path) as image:
                embedded_raw = image.info.get("geo_infer_act_metadata")
            if not embedded_raw:
                fail(f"{scenario} PNG lacks embedded ACT metadata: {path}")
            embedded = json.loads(embedded_raw)
            for key in ("schema_version", "scenario", "figure_id"):
                if embedded.get(key) != metadata.get(key):
                    fail(f"{scenario} PNG embedded metadata mismatch for {key}: {path}")
        elif path.endswith(".html"):
            html = figure_path.read_text()
            if "geo-infer-act-figure-metadata" not in html:
                fail(f"{scenario} HTML lacks embedded ACT metadata: {path}")
            if metadata["schema_version"] not in html:
                fail(f"{scenario} HTML metadata schema not embedded: {path}")

        if data_path.suffix == ".csv":
            with data_path.open() as handle:
                data_rows = list(csv.DictReader(handle))
            if not data_rows:
                fail(f"{scenario} figure data sidecar has no rows: {data_rel}")
            for row in data_rows:
                for value in row.values():
                    try:
                        numeric = float(value)
                    except (TypeError, ValueError):
                        continue
                    if not math.isfinite(numeric):
                        fail(
                            f"{scenario} figure data sidecar has non-finite value: {data_rel}"
                        )
        else:
            if not json.loads(data_path.read_text()):
                fail(f"{scenario} figure data sidecar has no JSON payload: {data_rel}")


def validate_docs() -> None:
    docs_text = "\n".join(path.read_text() for path in REQUIRED_DOCS)
    if docs_text.count("```mermaid") < len(REQUIRED_MERMAID_HEADINGS):
        fail("ACT docs do not contain the required number of Mermaid diagrams")
    for heading in REQUIRED_MERMAID_HEADINGS:
        if heading not in docs_text:
            fail(f"Missing Mermaid section heading: {heading}")
    stale_patterns = [
        r"\bLines?\s+\d+",
        r"\bL\d+",
        r"\bcell_a\b",
        r"\bcell_b\b",
        r"\bcell_c\b",
        r"h3>=3\.7\.0",
    ]
    for pattern in stale_patterns:
        match = re.search(pattern, docs_text)
        if match:
            fail(f"Stale docs pattern found: {match.group(0)}")

    for path in REQUIRED_DOCS:
        text = path.read_text()
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = (path.parent / target.split("#", 1)[0]).resolve()
            if target_path.suffix and not target_path.exists():
                fail(f"Broken local link in {path}: {target}")


def main() -> None:
    validate_docstrings()
    validate_packaging()
    validate_geospatial_outputs()
    validate_docs()
    print("[OK] GEO-INFER-ACT geospatial contract is valid")


if __name__ == "__main__":
    main()
