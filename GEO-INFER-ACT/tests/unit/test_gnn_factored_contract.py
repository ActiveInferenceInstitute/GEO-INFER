"""Exact joint filtering and finite-horizon policy contract regressions."""

import copy
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pytest

from geo_infer_act.core.gnn_factored_contract import (
    CONTRACT_VERSION,
    FactoredGNNArtifact,
    infer_factored_step,
)


def _data():
    text = Path(__file__).with_name("factored_example.json").read_text()
    return {
        **json.loads(text),
        "schema_version": CONTRACT_VERSION,
        "model_type": "categorical_factored",
        "time": {"step_seconds": 60},
        "provenance": {
            "producer": "GNN explicit factored JSON exporter",
            "source_kind": "explicit_factored_json",
            "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
        },
    }


def _entropy(q):
    return -sum(p * np.log(p) for p in q if p > 0)


def test_two_factor_filter_and_two_step_information_match_history_enumeration():
    """Use the entropy chain rule as an independent two-step EFE oracle."""
    data = _data()
    artifact = FactoredGNNArtifact.from_dict(data)
    result = infer_factored_step(artifact, [0, 2])
    states = list(itertools.product(range(2), range(3)))
    outcomes = list(itertools.product(range(2), range(4)))
    a0, a1 = (np.asarray(m["likelihood"]) for m in data["modalities"])
    emissions = np.array(
        [[a0[o0, s0] * a1[o1, s1, s0] for s0, s1 in states] for o0, o1 in outcomes]
    )
    prior = np.asarray(data["initial_joint"])
    likelihood = emissions[outcomes.index((0, 2))]
    evidence = likelihood @ prior
    posterior = likelihood * prior / evidence
    np.testing.assert_allclose(result["posterior"], posterior, atol=1e-12)
    assert result["evidence"] == pytest.approx(evidence)
    assert result["free_energy"] == pytest.approx(-np.log(evidence))
    # The initial joint distribution is correlated, not a product of marginals.
    joint = posterior.reshape(2, 3)
    assert not np.allclose(joint, np.outer(joint.sum(axis=1), joint.sum(axis=0)))
    expected_efe = []
    utility = np.array(
        [
            data["modalities"][0]["preferences"][o0]
            + data["modalities"][1]["preferences"][o1]
            for o0, o1 in outcomes
        ]
    )
    for policy in data["policies"]:
        # Deterministic bijections in this fixture let us keep original state
        # coordinates while enumerating the complete future observation pair.
        first = [(s0 ^ policy[0][0], (s1 + 1) % 3) for s0, s1 in states]
        second = [(s0 ^ policy[1][0], (s1 + 1) % 3) for s0, s1 in first]
        first_a = emissions[:, [states.index(s) for s in first]]
        second_a = emissions[:, [states.index(s) for s in second]]
        history_entropy = 0.0
        for o1, o2 in itertools.product(range(8), repeat=2):
            joint_probability = posterior * first_a[o1] * second_a[o2]
            mass = joint_probability.sum()
            if mass > 0:
                history_entropy += mass * _entropy(joint_probability / mass)
        information = _entropy(posterior) - history_entropy
        expected_utility = utility @ (first_a @ posterior + second_a @ posterior)
        expected_efe.append(-information - expected_utility)
    np.testing.assert_allclose(result["expected_free_energy"], expected_efe, atol=1e-12)
    weights = np.exp(-np.asarray(expected_efe)) * data["policy_prior"]
    np.testing.assert_allclose(
        result["policy_posterior"], weights / weights.sum(), atol=1e-12
    )
    next_prior = np.zeros(6)
    action = result["selected_action"][0]
    for index, (s0, s1) in enumerate(states):
        next_prior[states.index((s0 ^ action, (s1 + 1) % 3))] += posterior[index]
    np.testing.assert_allclose(result["next_prior"], next_prior, atol=1e-12)


def test_artifact_snapshot_provenance_and_prior_override(tmp_path):
    data = _data()
    artifact = FactoredGNNArtifact.from_dict(data)
    digest = artifact.digest
    data["initial_joint"][0] = 0.9
    assert artifact.digest == digest
    stored = tmp_path / "factored.json"
    stored.write_text(json.dumps(artifact.to_dict()))
    assert FactoredGNNArtifact.load(stored).digest == digest
    result = infer_factored_step(artifact, [1, 0], prior=[1, 0, 0, 0, 0, 0])
    assert result["posterior"] == [1, 0, 0, 0, 0, 0]


@pytest.mark.parametrize(
    "mutation, match",
    [
        (lambda d: d["modalities"][1].update(dependencies=[0, 1]), "shape"),
        (lambda d: d["transitions"][0].update(dependencies=[1, 1]), "unique"),
        (lambda d: d.update(policy_prior=[0.5, 0.5]), "shape"),
        (lambda d: d["policies"][0].append([0, 0]), "same horizon"),
        (lambda d: d["policies"][0][0].__setitem__(0, True), "integer"),
        (lambda d: d["policies"].__setitem__(1, d["policies"][0]), "unique"),
        (lambda d: d["transitions"][1].update(control_factor=2), "integer"),
        (
            lambda d: d["modalities"][0].update(likelihood=[[0.9, 0.3], [0.2, 0.7]]),
            "stochastic",
        ),
        (lambda d: d["time"].update(step_seconds=False), "positive"),
    ],
)
def test_invalid_axes_policies_and_probabilities_are_rejected(mutation, match):
    data = copy.deepcopy(_data())
    mutation(data)
    with pytest.raises(ValueError, match=match):
        FactoredGNNArtifact.from_dict(data)


def test_budget_and_shapes_fail_before_numpy_allocation(monkeypatch):
    import geo_infer_act.core.gnn_factored_contract as contract

    def forbidden(*args, **kwargs):
        raise AssertionError("Numerical allocation occurred before validation")

    monkeypatch.setattr(contract.np, "asarray", forbidden)
    data = _data()
    data["policies"] = [[[0, 0]] * 8]
    data["policy_prior"] = [1]
    with pytest.raises(ValueError, match="work budget"):
        FactoredGNNArtifact.from_dict(data)
    data = _data()
    data["modalities"][1]["likelihood"] = [1]
    with pytest.raises(ValueError, match="shape"):
        FactoredGNNArtifact.from_dict(data)


def test_zero_evidence_and_invalid_observations_are_rejected():
    data = _data()
    data["modalities"][0]["likelihood"] = [[1, 1], [0, 0]]
    artifact = FactoredGNNArtifact.from_dict(data)
    with pytest.raises(ValueError, match="zero evidence"):
        infer_factored_step(artifact, [1, 0])
    for observation in ([0], [False, 0], [0, 4]):
        with pytest.raises(ValueError):
            infer_factored_step(artifact, observation)


def test_zero_policy_prior_preserves_excluded_policies():
    data = _data()
    data["policy_prior"] = [0, 0, 1, 0]
    result = infer_factored_step(FactoredGNNArtifact.from_dict(data), [0, 0])
    assert result["policy_posterior"] == [0, 0, 1, 0]
    assert result["selected_policy"] == 2


def test_external_prior_shape_is_bounded_before_conversion(monkeypatch):
    import geo_infer_act.core.gnn_factored_contract as contract

    artifact = FactoredGNNArtifact.from_dict(_data())

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid prior reached NumPy conversion")

    monkeypatch.setattr(contract.np, "asarray", forbidden)
    with pytest.raises(ValueError, match="prior.*shape"):
        infer_factored_step(artifact, [0, 0], prior=[0.1] * 1000)


@pytest.mark.parametrize("scale, modalities", [(1e308, 2), (1e308, 1), (-1e308, 1)])
def test_extreme_finite_preferences_fail_before_nonfinite_policy_result(
    scale, modalities
):
    data = _data()
    for index, modality in enumerate(data["modalities"]):
        modality["preferences"] = [scale if index < modalities else 0.0] * len(
            modality["outcomes"]
        )
    artifact = FactoredGNNArtifact.from_dict(data)
    with pytest.raises(ValueError, match="finite numeric range"):
        infer_factored_step(artifact, [0, 0])


def test_excluded_low_cost_policy_cannot_destroy_supported_policy_mass():
    data = _data()
    data["modalities"][0]["preferences"] = [10000, -10000]
    data["policy_prior"] = [1, 0, 0, 0]
    result = infer_factored_step(FactoredGNNArtifact.from_dict(data), [1, 0])
    assert (
        min(result["expected_free_energy"][1:])
        < result["expected_free_energy"][0] - 1000
    )
    assert result["policy_posterior"] == [1, 0, 0, 0]
    assert result["selected_policy"] == 0
