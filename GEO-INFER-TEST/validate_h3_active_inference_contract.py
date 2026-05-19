#!/usr/bin/env python3
"""
Validate the GEO-INFER H3 + Active Inference runtime contract.

This check is intentionally executable: it uses real H3 v4 cells through
GEO-INFER-SPACE, runs the canonical ACT H3 paths, and verifies normalized
beliefs plus finite free-energy and spatial diagnostics.
"""

from __future__ import annotations

import ast
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parent.parent
ACT_SRC = REPO_ROOT / "GEO-INFER-ACT" / "src"
SPACE_SRC = REPO_ROOT / "GEO-INFER-SPACE" / "src"
ACT_PACKAGE = ACT_SRC / "geo_infer_act"
SPACE_PACKAGE = SPACE_SRC / "geo_infer_space"

RUNTIME_SOURCE_ROOTS = [ACT_PACKAGE, SPACE_PACKAGE]
TARGETED_H3_FILES = [
    ACT_PACKAGE / "core" / "active_inference.py",
    ACT_PACKAGE / "core" / "generative_model.py",
    ACT_PACKAGE / "core" / "spatial_agent.py",
    ACT_PACKAGE / "models" / "multi_agent.py",
    ACT_PACKAGE / "utils" / "h3_adapter.py",
    SPACE_PACKAGE / "core" / "spatial_indexing.py",
    SPACE_PACKAGE / "backends" / "h3" / "h3_backend.py",
    SPACE_PACKAGE / "backends" / "h3" / "operations.py",
]
DOC_FILES = [
    REPO_ROOT / "GEO-INFER-ACT" / "README.md",
    REPO_ROOT / "GEO-INFER-ACT" / "SKILL.md",
    REPO_ROOT / "GEO-INFER-ACT" / "docs" / "mathematical_framework.md",
]
H3_V3_API_CALLS = [
    "h3.geo_to_h3(",
    "h3.h3_to_geo(",
    "h3.k_ring(",
    "h3.hex_ring(",
    "h3.polyfill(",
    "h3.h3_to_parent(",
    "h3.h3_to_children(",
    "h3.h3_to_geo_boundary(",
    "h3.h3_set_to_multi_polygon(",
]


def _ensure_import_path() -> None:
    for src in (str(ACT_SRC), str(SPACE_SRC)):
        if src not in sys.path:
            sys.path.insert(0, src)


def _is_runtime_file(path: Path) -> bool:
    parts = set(path.parts)
    if "tools" in parts:
        return False
    if path.name == "h3_v3_to_v4_upgrade.py":
        return False
    return path.suffix == ".py"


def _validate_no_h3_v3_calls() -> None:
    offenders: list[str] = []
    for root in RUNTIME_SOURCE_ROOTS:
        for path in sorted(root.rglob("*.py")):
            if not _is_runtime_file(path):
                continue
            text = path.read_text()
            for pattern in H3_V3_API_CALLS:
                if pattern in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: {pattern}")
    for path in DOC_FILES:
        if not path.exists():
            continue
        text = path.read_text()
        for pattern in H3_V3_API_CALLS:
            if pattern in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {pattern}")
    assert not offenders, "H3 v3 API calls found:\n" + "\n".join(offenders)


def _validate_no_inert_h3_methods() -> None:
    offenders: list[str] = []
    for path in TARGETED_H3_FILES:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Pass):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}: pass")
            if isinstance(node, ast.Raise):
                text = ast.get_source_segment(path.read_text(), node) or ""
                if "NotImplemented" in text:
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {text.strip()}"
                    )
    assert not offenders, "Inert H3 method bodies found:\n" + "\n".join(offenders)


def _validate_public_h3_docstrings() -> None:
    missing: list[str] = []
    for path in TARGETED_H3_FILES:
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name.startswith("_"):
                continue
            name = node.name.lower()
            if "h3" not in name and "cell" not in name and "spatial" not in name:
                continue
            if not ast.get_docstring(node):
                missing.append(
                    f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {node.name}"
                )
    assert not missing, "Public H3 methods missing docstrings:\n" + "\n".join(missing)


def _as_array(value: Any) -> np.ndarray:
    if isinstance(value, dict) and "states" in value:
        value = value["states"]
    return np.asarray(value, dtype=float).reshape(-1)


def _assert_probability_vector(value: Any, label: str) -> None:
    array = _as_array(value)
    assert array.size > 0, f"{label} is empty"
    assert np.all(np.isfinite(array)), f"{label} contains non-finite values"
    assert np.all(array >= -1e-12), f"{label} contains negative values"
    assert np.isclose(
        np.sum(array), 1.0, atol=1e-6
    ), f"{label} is not normalized: sum={np.sum(array)}"


def _assert_finite(value: Any, label: str) -> None:
    assert math.isfinite(float(value)), f"{label} is not finite: {value!r}"


def _validate_space_indexing_contract() -> list[str]:
    from geo_infer_space.core.spatial_indexing import (  # noqa: PLC0415
        SpatialIndexingInterface,
    )

    indexer = SpatialIndexingInterface(backend="h3")
    center = indexer.latlng_to_cell(37.7749, -122.4194, 8)
    lat, lng = indexer.cell_to_latlng(center)
    assert 37.0 < lat < 38.5
    assert -123.5 < lng < -121.5

    boundary = {
        "coordinates": [
            [
                [-122.42, 37.77],
                [-122.42, 37.79],
                [-122.39, 37.79],
                [-122.39, 37.77],
                [-122.42, 37.77],
            ]
        ]
    }
    cells = indexer.polygon_to_cells(boundary, 8)
    if len(cells) < 2:
        cells = indexer.get_cell_neighbors(center, 1)[:6] + [center]
    cells = sorted(set(cells))
    assert len(cells) >= 2, "SPACE H3 indexing did not produce enough cells"

    parent = indexer.get_cell_parent(cells[0], 7)
    children = indexer.get_cell_children(parent, 8)
    assert cells[0] in children
    assert indexer.get_cell_resolution(cells[0]) == 8
    assert indexer.get_cell_ring(cells[0], 1)
    assert indexer.get_cell_boundary(cells[0])
    assert indexer.get_cell_area(cells[0]) > 0
    compacted = indexer.compact_cells(children)
    uncompacted = indexer.uncompact_cells(compacted, 8)
    assert set(children).issubset(set(uncompacted))
    multipolygon = indexer.cells_to_multipolygon(cells[:2])
    assert multipolygon["type"] == "MultiPolygon"
    return cells


def _validate_act_h3_runtime(cells: list[str]) -> None:
    from geo_infer_act import (  # noqa: PLC0415
        ActiveInferenceModel,
        ActiveInferenceStepResult,
        GenerativeModel,
        H3BeliefUpdateResult,
        H3GridInferenceResult,
        H3SpatialConsistency,
        SpatialActiveInferenceAgent,
    )
    from geo_infer_act.models.multi_agent import MultiAgentModel  # noqa: PLC0415

    boundary = {
        "coordinates": [
            [
                [-122.42, 37.77],
                [-122.42, 37.79],
                [-122.39, 37.79],
                [-122.39, 37.77],
                [-122.42, 37.77],
            ]
        ]
    }

    gen = GenerativeModel("categorical", {"state_dim": 3, "obs_dim": 3})
    gen.enable_h3_spatial(8, boundary)
    selected_cells = gen.h3_cells[: max(2, min(4, len(gen.h3_cells)))]
    observations = {
        cell: np.eye(3)[index % 3] for index, cell in enumerate(selected_cells)
    }

    belief_result = gen.update_h3_beliefs(observations, return_result=True)
    assert isinstance(belief_result, H3BeliefUpdateResult)
    assert isinstance(belief_result.spatial_consistency, H3SpatialConsistency)
    _assert_finite(belief_result.aggregate_free_energy, "H3 belief aggregate FE")
    _assert_finite(
        belief_result.spatial_consistency.global_coherence,
        "H3 belief coherence",
    )
    _assert_finite(
        belief_result.spatial_consistency.neighbor_correlations,
        "H3 neighbor correlation",
    )
    for cell, belief in belief_result.h3_beliefs.items():
        _assert_probability_vector(belief, f"belief[{cell}]")
    _assert_probability_vector(belief_result.average, "average H3 belief")

    try:
        gen.update_h3_beliefs({"not-a-real-h3-cell": np.array([1.0, 0.0, 0.0])})
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid H3 cell did not fail clearly")

    model = ActiveInferenceModel(
        model_type="categorical",
        policy_selection_mode="deterministic",
        random_seed=11,
    )
    model.set_generative_model(gen)
    grid_result = model.infer_over_h3_grid(observations, return_result=True)
    assert isinstance(grid_result, H3GridInferenceResult)
    _assert_finite(grid_result.aggregate_free_energy, "H3 grid aggregate FE")
    _assert_finite(
        grid_result.spatial_consistency.global_coherence,
        "H3 grid coherence",
    )
    assert grid_result.spatial_consistency.cell_count == len(observations)
    for cell, step_result in grid_result.cell_results.items():
        assert isinstance(step_result, ActiveInferenceStepResult)
        _assert_finite(step_result.free_energy, f"step FE[{cell}]")
        _assert_finite(step_result.expected_free_energy, f"step EFE[{cell}]")
        _assert_probability_vector(step_result.beliefs, f"step belief[{cell}]")

    spatial_agent = SpatialActiveInferenceAgent(
        initial_cells=selected_cells,
        state_dim=3,
        obs_dim=3,
        h3_resolution=8,
        enable_logging=False,
    )
    agent_result = spatial_agent.step(observations, return_result=True)
    assert isinstance(agent_result, H3GridInferenceResult)
    _assert_finite(agent_result.aggregate_free_energy, "spatial-agent aggregate FE")
    assert agent_result.spatial_consistency.cell_count == len(selected_cells)
    for cell, step_result in agent_result.cell_results.items():
        _assert_probability_vector(step_result.beliefs, f"spatial-agent belief[{cell}]")

    multi = MultiAgentModel(n_agents=2)
    multi.enable_h3_spatial(8, boundary)
    history = multi.simulate_h3_lattice(2, lambda _cell: np.array([1.0, 0.0, 0.0, 0.0]))
    assert len(history) == 2
    for timestep in history:
        assert timestep
        for cell, payload in timestep.items():
            _assert_probability_vector(
                payload["beliefs"], f"multi-agent belief[{cell}]"
            )
            _assert_finite(payload["free_energy"], f"multi-agent FE[{cell}]")

    coordination = multi.coordinate_agents()
    assert "coordination_matrix" in coordination
    assert np.all(np.isfinite(coordination["coordination_matrix"]))

    assert set(selected_cells).issubset(set(cells) | set(gen.h3_cells))


def main() -> int:
    _ensure_import_path()

    _validate_no_h3_v3_calls()
    _validate_no_inert_h3_methods()
    _validate_public_h3_docstrings()
    cells = _validate_space_indexing_contract()
    _validate_act_h3_runtime(cells)

    print("H3 Active Inference contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
