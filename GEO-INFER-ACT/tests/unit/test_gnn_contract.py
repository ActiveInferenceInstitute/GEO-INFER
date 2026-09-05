"""Data-boundary rejection, policy-prior and sequential inference regressions."""

import numpy as np
import pytest
from geo_infer_act.core.gnn_contract import GNNArtifact, run_gnn_inference


def artifact_data():
    return dict(
        schema_version="gnn-geo-infer/1",
        model_type="categorical",
        model_name="two states",
        dimensions=dict(states=2, observations=2, actions=2),
        matrices=dict(
            A=[[0.8, 0.2], [0.2, 0.8]],
            B=[[[1, 0], [0, 1]], [[0, 1], [1, 0]]],
            C=[0, 0],
            D=[0.5, 0.5],
            E=[0.01, 0.99],
        ),
        space=dict(kind="categorical", state_ids=["west", "east"]),
        time=dict(step_seconds=60),
        provenance=dict(producer="test fixture", source_sha256="0" * 64),
    )


def test_snapshot_and_roundtrip(tmp_path):
    data = artifact_data()
    model = GNNArtifact.from_dict(data)
    data["matrices"]["D"][0] = 99
    path = tmp_path / "model.json"
    model.write(path)
    assert GNNArtifact.load(path).digest == model.digest
    assert model.to_dict()["matrices"]["D"] == [0.5, 0.5]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(schema_version="future"),
        lambda d: d.update(model_type="continuous"),
        lambda d: d["matrices"].update(A=[[1, 1], [1, 1]]),
        lambda d: d["matrices"].update(B=np.eye(2).tolist()),
        lambda d: d["matrices"].update(C=["0", "0"]),
        lambda d: d["matrices"].update(D=[-1, 2]),
        lambda d: d["matrices"].update(E=[1]),
        lambda d: d["dimensions"].update(states=True),
        lambda d: d["dimensions"].update(states=1000000),
        lambda d: d["space"].update(state_ids=["same", "same"]),
        lambda d: d["space"].update(kind="h3"),
        lambda d: d["time"].update(step_seconds=0),
        lambda d: d["provenance"].update(source_sha256="invalid"),
        lambda d: d.update(executable="raise RuntimeError()"),
    ],
)
def test_invalid_artifacts(mutate):
    data = artifact_data()
    mutate(data)
    with pytest.raises(ValueError):
        GNNArtifact.from_dict(data)


def test_duplicate_keys_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version":"x","schema_version":"y"}')
    with pytest.raises(ValueError, match="Duplicate"):
        GNNArtifact.load(path)


def test_actual_pymdp_prior_and_sequential_alignment():
    model = GNNArtifact.from_dict(artifact_data())
    observations = [
        dict(timestamp="2026-01-01T00:00:00Z", observation=0),
        dict(timestamp="2026-01-01T00:01:00Z", observation=1),
    ]
    result = run_gnn_inference(model, observations, random_seed=4)
    assert result == run_gnn_inference(model, observations, random_seed=4)
    first, second = result["steps"]
    assert first["action"] == 1
    assert first["policy_posterior"][1] == pytest.approx(0.99, abs=1e-5)
    np.testing.assert_allclose(first["posterior"], [0.8, 0.2])
    np.testing.assert_allclose(second["prior"], [0.2, 0.8])
    np.testing.assert_allclose(second["posterior"], [1 / 17, 16 / 17])
    assert first["free_energy"] == pytest.approx(-np.log(0.5))


def test_impossible_observation_is_not_smoothed():
    data = artifact_data()
    data["matrices"]["A"] = [[1, 1], [0, 0]]
    with pytest.raises(ValueError, match="zero probability"):
        run_gnn_inference(
            GNNArtifact.from_dict(data),
            [dict(timestamp="2026-01-01T00:00:00Z", observation=1)],
        )


def test_temporal_and_index_errors_rejected_before_inference():
    model = GNNArtifact.from_dict(artifact_data())
    for value in [-1, 2, True, 0.1]:
        with pytest.raises(ValueError, match="out of range"):
            run_gnn_inference(
                model, [dict(timestamp="2026-01-01T00:00:00Z", observation=value)]
            )
    with pytest.raises(ValueError, match="timezone"):
        run_gnn_inference(model, [dict(timestamp="2026-01-01", observation=0)])


def test_shape_is_rejected_before_numpy_allocation(monkeypatch):
    """Malformed input cannot allocate a dense array outside declared dimensions."""
    import geo_infer_act.core.gnn_contract as contract

    data = artifact_data()
    data["matrices"]["A"] = [[0.0] * 100]

    def forbidden_conversion(*args, **kwargs):
        raise AssertionError("Array allocated before shape validation")

    monkeypatch.setattr(contract.np, "asarray", forbidden_conversion)
    with pytest.raises(ValueError, match="shape"):
        GNNArtifact.from_dict(data)
