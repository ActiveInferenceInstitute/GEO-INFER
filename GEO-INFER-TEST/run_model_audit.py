#!/usr/bin/env python3
"""Run model contracts and emit deterministic statistics/visualization artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import numpy as np
from matplotlib.figure import Figure

from geo_infer_act.models.base import CategoricalModel
from geo_infer_act.models.resource import ResourceModel
from geo_infer_test.testing import (
    assert_no_nan_statistics,
    assert_visualization_manifest,
)
from validate_model_contracts import audit_model_contracts


def _digest(path: Path) -> str:
    """Return a stable SHA-256 digest for an artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    """Write canonical, newline-terminated JSON."""
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def run(seed: int, output_dir: Path, *, reproducible: bool = False) -> dict[str, Any]:
    """Run the audit and create machine-verifiable sidecars."""
    output_dir.mkdir(parents=True, exist_ok=True)
    contracts = audit_model_contracts(seed, strict=True)

    categorical = CategoricalModel(state_dim=3, obs_dim=3)
    categorical.update_beliefs(np.array([3.0, 2.0, 1.0]))
    resource = ResourceModel(n_resources=2, n_locations=3, random_seed=seed)
    resource_state, _ = resource.step()
    statistics = {
        "schema_version": "1.0",
        "seed": seed,
        "models_checked": contracts["models_checked"],
        "categorical_posterior": {
            "sum": float(categorical.beliefs.sum()),
            "min": float(categorical.beliefs.min()),
            "max": float(categorical.beliefs.max()),
        },
        "resource_distribution": {
            "shape": list(resource_state["resource_distribution"].shape),
            "mean": float(np.mean(resource_state["resource_distribution"])),
            "min": float(np.min(resource_state["resource_distribution"])),
            "max": float(np.max(resource_state["resource_distribution"])),
        },
    }
    assert_no_nan_statistics(statistics)

    contracts_path = output_dir / "model_contracts.json"
    statistics_path = output_dir / "statistics.json"
    _write_json(contracts_path, contracts)
    _write_json(statistics_path, statistics)

    figure = Figure(figsize=(7, 4), dpi=100)
    axis = figure.subplots()
    axis.bar(["state 0", "state 1", "state 2"], categorical.beliefs, color="#1f77b4")
    axis.set_ylim(0, 1)
    axis.set_ylabel("posterior probability")
    axis.set_title(f"GEO-INFER model audit (seed {seed})")
    figure.tight_layout()
    visualization_path = output_dir / "model_audit.png"
    figure.savefig(
        visualization_path,
        format="png",
        metadata={
            "Software": "GEO-INFER deterministic model audit",
            "Creation Time": None,
        },
    )

    artifacts = []
    for path, kind in (
        (contracts_path, "contracts"),
        (statistics_path, "statistics"),
        (visualization_path, "visualization"),
    ):
        artifacts.append(
            {
                "kind": kind,
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": _digest(path),
                "statistics": (
                    statistics
                    if kind != "contracts"
                    else {"models_checked": contracts["models_checked"]}
                ),
            }
        )
    manifest_core = {"schema_version": "1.0", "seed": seed, "artifacts": artifacts}
    deterministic_hash = hashlib.sha256(
        json.dumps(manifest_core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    manifest = {**manifest_core, "deterministic_hash": deterministic_hash}
    manifest_path = output_dir / "manifest.json"
    _write_json(manifest_path, manifest)
    assert_visualization_manifest(manifest, root=output_dir)

    if reproducible:
        replay = audit_model_contracts(seed, strict=True)
        if replay != contracts:
            raise AssertionError("reproducible model audit replay differed")

    return manifest


def main() -> int:
    """Parse CLI arguments, run the audit, and print its manifest."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".geo-infer-test-results") / "model-audit",
    )
    parser.add_argument("--reproducible", action="store_true")
    args = parser.parse_args()
    manifest = run(args.seed, args.output_dir, reproducible=args.reproducible)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
