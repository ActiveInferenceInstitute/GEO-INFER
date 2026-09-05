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
import platform
import sys

import numpy as np
from geo_infer_act.core.gnn_contract import GNNArtifact, run_gnn_inference


def revision_receipt(root: Path) -> dict:
    """Identify a checkout and expose local modifications in verification receipts."""
    return {
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, timeout=10
        ).strip(),
        "dirty": bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=root, text=True, timeout=10
            ).strip()
        ),
    }


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
        # A non-square Gaussian fixture catches transposed observation/control
        # axes and accidental Euler integration of a discrete transition.
        from geo_infer_act.core.gnn_gaussian_contract import (
            GaussianGNNArtifact,
            run_gaussian_gnn_inference,
        )

        gaussian_source = root / "src/tests/export/gaussian_rectangular.md"
        units_path = Path(temp) / "units.json"
        units_path.write_text(
            json.dumps(
                {
                    "states": ["m", "m/s", "K"],
                    "observations": ["m", "m/s"],
                    "controls": ["N"],
                }
            ),
            encoding="utf-8",
        )
        gaussian_path = Path(temp) / "gaussian.json"
        subprocess.run(
            [
                str(interpreter),
                "-m",
                "export.geo_infer",
                str(gaussian_source),
                str(gaussian_path),
                "--step-seconds",
                "2",
                "--model-type",
                "linear_gaussian",
                "--units",
                str(units_path),
            ],
            cwd=root,
            env=environment,
            check=True,
            timeout=120,
        )
        gaussian = GaussianGNNArtifact.load(gaussian_path)
        assert (
            gaussian.to_dict()["provenance"]["source_sha256"]
            == hashlib.sha256(gaussian_source.read_bytes()).hexdigest()
        )
        gaussian_records = [
            {
                "timestamp": "2026-09-04T00:00:00Z",
                "observation": [1, 2],
                "control": [0.25],
            },
            {
                "timestamp": "2026-09-04T00:00:02Z",
                "observation": [0, 1],
                "control": [0],
            },
        ]
        gaussian_trace = run_gaussian_gnn_inference(gaussian, gaussian_records)
        first_gaussian = gaussian_trace["steps"][0]
        np.testing.assert_allclose(first_gaussian["posterior_mean"], [2 / 3, 4 / 3, 0])
        np.testing.assert_allclose(
            first_gaussian["posterior_covariance"], np.diag([1 / 3, 4 / 3, 9])
        )
        np.testing.assert_allclose(
            first_gaussian["next_prior_mean"], [19 / 12, 11 / 6, 0]
        )
        np.testing.assert_allclose(
            first_gaussian["next_prior_covariance"],
            np.diag([43 / 30, 43 / 30, 47 / 20]),
        )
        assert gaussian_trace == run_gaussian_gnn_inference(gaussian, gaussian_records)
        from geo_infer_act.core.gnn_factored_contract import (
            FactoredGNNArtifact,
            infer_factored_step,
        )

        factored_source = root / "src/tests/export/factored_example.json"
        assert (
            factored_source.read_bytes()
            == (
                Path(__file__).resolve().parents[1]
                / "GEO-INFER-ACT/tests/unit/factored_example.json"
            ).read_bytes()
        )
        factored_path = Path(temp) / "factored.json"
        subprocess.run(
            [
                str(interpreter),
                "-m",
                "export.geo_infer_factored",
                str(factored_source),
                str(factored_path),
                "--step-seconds",
                "60",
            ],
            cwd=root,
            env=environment,
            check=True,
            timeout=120,
        )
        factored = FactoredGNNArtifact.load(factored_path)
        factored_data = factored.to_dict()
        assert (
            factored_data["provenance"]["source_sha256"]
            == hashlib.sha256(factored_source.read_bytes()).hexdigest()
        )
        factored_trace = infer_factored_step(factored, [0, 2])
        a0, a1 = (np.asarray(m["likelihood"]) for m in factored_data["modalities"])
        likelihood = np.array(
            [a0[0, s0] * a1[2, s1, s0] for s0 in range(2) for s1 in range(3)]
        )
        expected = np.asarray(factored_data["initial_joint"]) * likelihood
        expected /= expected.sum()
        np.testing.assert_allclose(factored_trace["posterior"], expected)
        assert len(factored_trace["policy_posterior"]) == len(factored_data["policies"])
        assert factored_trace == infer_factored_step(factored, [0, 2])
        return dict(
            geo=revision_receipt(Path(__file__).resolve().parents[1]),
            gnn=revision_receipt(root),
            python=sys.version,
            platform=platform.platform(),
            gaussian_artifact_sha256=gaussian.digest,
            gaussian_trace=gaussian_trace,
            factored_artifact_sha256=factored.digest,
            factored_trace=factored_trace,
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
