#!/usr/bin/env python3
"""Exercise a real GNN exporter in its own environment and consume in GEO-INFER."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from geo_infer_act.core.gnn_contract import GNNArtifact, run_gnn_inference


def validate_interchange(gnn_repo: Path, gnn_python: Path) -> dict:
    """Export the tracked gridworld, validate provenance, and verify real replay."""
    root = gnn_repo.resolve(strict=True)
    interpreter = gnn_python.absolute()
    if not interpreter.is_file():
        raise ValueError("GNN interpreter must be an existing file")
    source = root / "input/gnn_files/pomdp_gridworld/pomdp_gridworld_3x3.md"
    with tempfile.TemporaryDirectory(prefix="gnn-geo-contract-") as temp:
        artifact_path = Path(temp) / "model.json"
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(root / "src")
        subprocess.run(
            [
                str(interpreter),
                "-m",
                "export.geo_infer",
                str(source),
                str(artifact_path),
                "--step-seconds",
                "60",
            ],
            cwd=root,
            env=environment,
            check=True,
            timeout=120,
        )
        artifact = GNNArtifact.load(artifact_path)
        assert (
            artifact.to_dict()["provenance"]["source_sha256"]
            == hashlib.sha256(source.read_bytes()).hexdigest()
        )
        records = [
            dict(timestamp=f"2026-01-01T00:0{i}:00Z", observation=i) for i in range(3)
        ]
        first = run_gnn_inference(artifact, records, random_seed=42)
        assert first == run_gnn_inference(artifact, records, random_seed=42)
        matrices = {k: np.asarray(v) for k, v in artifact.to_dict()["matrices"].items()}
        for index, step in enumerate(first["steps"]):
            prior = (
                matrices["D"]
                if index == 0
                else np.asarray(first["steps"][index - 1]["next_prior"])
            )
            likelihood = matrices["A"][records[index]["observation"]]
            posterior = prior * likelihood / np.sum(prior * likelihood)
            np.testing.assert_allclose(step["posterior"], posterior)
            np.testing.assert_allclose(
                step["next_prior"], matrices["B"][:, :, step["action"]] @ posterior
            )
        # Compile a genuine H3 stay/diffuse operator into GNN source, then
        # export in the GNN environment and consume again without reordering.
        import h3
        from geo_infer_space.core.state_space import H3StateSpace

        center = h3.latlng_to_cell(41.75, -124.2, 8)
        cells = sorted(h3.grid_disk(center, 1), reverse=True)
        space = H3StateSpace(cells)
        n = len(cells)
        expected_B = space.dense_transition_tensor()
        parameters = dict(
            A=np.eye(n).tolist(),
            B=expected_B.tolist(),
            C=[0.0] * n,
            D=[1 / n] * n,
            E=[0.25, 0.75],
        )
        source_text = (
            f"""# GNN model
## GNNVersionAndFlags
GNN v1.0
## ModelName
H3 stay and diffuse
## StateSpaceBlock
s[{n},1,type=int]
o[{n},1,type=int]
u[1,type=int]
π[2,type=float]
A[{n},{n},type=float]
B[{n},{n},2,type=float]
C[{n},type=float]
D[{n},type=float]
E[2,type=float]
## Connections
D>s
s>A
o>A
s>B
u>B
E>π
## InitialParameterization
"""
            + "\n".join(f"{key}={value!r}" for key, value in parameters.items())
            + f"""
## ModelParameters
num_states={n}
num_observations={n}
num_actions=2
num_timesteps=2
b_tensor_order=next_state_previous_state_action
## Time
Dynamic
DiscreteTime=t
"""
        )
        h3_source = Path(temp) / "h3.md"
        h3_source.write_text(source_text, encoding="utf-8")
        ids_path = Path(temp) / "state_ids.json"
        ids_path.write_text(json.dumps(cells), encoding="utf-8")
        spatial_path = Path(temp) / "h3.json"
        subprocess.run(
            [
                str(interpreter),
                "-m",
                "export.geo_infer",
                str(h3_source),
                str(spatial_path),
                "--step-seconds",
                "60",
                "--space-kind",
                "h3",
                "--state-ids",
                str(ids_path),
            ],
            cwd=root,
            env=environment,
            check=True,
            timeout=120,
        )
        spatial = GNNArtifact.load(spatial_path)
        assert spatial.to_dict()["space"]["state_ids"] == cells
        np.testing.assert_array_equal(spatial.to_dict()["matrices"]["B"], expected_B)
        spatial_trace = run_gnn_inference(spatial, records[:2], random_seed=42)
        return dict(
            h3_state_count=n,
            h3_artifact_sha256=spatial.digest,
            h3_trace=spatial_trace,
            contract=artifact.to_dict()["schema_version"],
            artifact_sha256=artifact.digest,
            source_sha256=artifact.to_dict()["provenance"]["source_sha256"],
            steps=len(first["steps"]),
            deterministic_replay=True,
            trace=first,
        )


def main() -> int:
    """Validate two explicitly selected environments and print a JSON receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gnn-repo", type=Path, required=True)
    parser.add_argument("--gnn-python", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            validate_interchange(args.gnn_repo, args.gnn_python),
            indent=2,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
