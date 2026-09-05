"""Sparse interchange and H3 resolution transfer conserve represented mass."""

from copy import deepcopy
import json

import h3
import numpy as np
import pytest
from scipy.sparse import csc_matrix

from geo_infer_space.core.state_space import H3StateSpace
from geo_infer_space.core.sparse_transition import (
    SparseTransitionArtifact,
    h3_resolution_transfer,
)


def artifact():
    center = h3.latlng_to_cell(41.75, -124.2, 8)
    return SparseTransitionArtifact.from_state_space(
        H3StateSpace(sorted(h3.grid_disk(center, 1)))
    )


def test_round_trip_prediction_without_dense_materialization(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Sparse contract must never materialize a dense matrix")

    monkeypatch.setattr(csc_matrix, "toarray", forbidden)
    original = artifact()
    restored = SparseTransitionArtifact.from_dict(
        json.loads(json.dumps(original.to_dict()))
    )
    assert restored.to_dict() == original.to_dict()
    assert (
        SparseTransitionArtifact.from_json(restored.to_json()).to_json()
        == original.to_json()
    )
    assert restored.action_ids == ("stay", "diffuse")
    belief = np.zeros(len(original.state_ids))
    belief[0] = 1
    np.testing.assert_array_equal(restored.predict(belief, "stay"), belief)
    moved = restored.predict(belief, "diffuse")
    assert moved.sum() == pytest.approx(1)
    assert np.count_nonzero(moved) <= 7
    for _ in range(20):
        moved = restored.predict(moved, "diffuse")
    assert moved.sum() == pytest.approx(1)
    assert np.all(moved >= 0)


def test_sparse_domain_exceeds_dense_v1_budget(monkeypatch):
    center = h3.latlng_to_cell(41.75, -124.2, 8)
    space = H3StateSpace(sorted(h3.grid_disk(center, 20)))
    with pytest.raises(ValueError, match="max_entries"):
        space.dense_transition_tensor()

    def forbidden(*args, **kwargs):
        raise AssertionError("Large state space must remain sparse")

    monkeypatch.setattr(csc_matrix, "toarray", forbidden)
    sparse = SparseTransitionArtifact.from_state_space(
        space, max_nnz=8 * len(space.cells)
    )
    prior = np.full(len(space.cells), 1 / len(space.cells))
    prediction = sparse.predict(prior, "diffuse")
    assert prediction.sum() == pytest.approx(1)
    assert sum(len(op["data"]) for op in sparse.to_dict()["operators"]) <= 8 * len(
        space.cells
    )


def test_snapshot_does_not_alias_input_or_output():
    payload = artifact().to_dict()
    stored = SparseTransitionArtifact.from_dict(payload)
    baseline = deepcopy(payload)
    payload["operators"][0]["data"][0] = 0
    stored.to_dict()["operators"][0]["data"][0] = 0
    assert stored.to_dict() == baseline


def test_reflecting_label_must_match_actual_topology():
    payload = artifact().to_dict()
    # A cyclic permutation remains stochastic, but it is not the stay action.
    payload["operators"][0]["indices"] = list(range(1, 7)) + [0]
    with pytest.raises(ValueError, match="topology"):
        SparseTransitionArtifact.from_dict(payload)
    payload["boundary"] = "explicit"
    custom = SparseTransitionArtifact.from_dict(payload)
    np.testing.assert_array_equal(
        custom.predict([1, 0, 0, 0, 0, 0, 0], "stay"), [0, 1, 0, 0, 0, 0, 0]
    )


def test_sparse_generation_enforces_budget_without_matrix_allocation(monkeypatch):
    center = h3.latlng_to_cell(41.75, -124.2, 8)
    space = H3StateSpace(sorted(h3.grid_disk(center, 1)))

    def forbidden(*args, **kwargs):
        raise AssertionError(
            "Generation must apply its budget before allocating matrices"
        )

    monkeypatch.setattr("geo_infer_space.core.sparse_transition.csc_matrix", forbidden)
    for cap in (1, 14, 20):
        with pytest.raises(ValueError, match="max_nnz"):
            SparseTransitionArtifact.from_state_space(space, max_nnz=cap)
    assert SparseTransitionArtifact.from_state_space(space).state_ids == space.cells


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.update(schema_version="unknown"),
        lambda p: p.update(extra=True),
        lambda p: p.update(boundary="normalize"),
        lambda p: p["state_ids"].append(p["state_ids"][0]),
        lambda p: p["action_ids"].append("stay"),
        lambda p: p["operators"][0].update(extra=True),
        lambda p: p["operators"][0]["indptr"].__setitem__(0, 1),
        lambda p: p["operators"][0]["indptr"].__setitem__(1, 99),
        lambda p: p["operators"][0]["indices"].__setitem__(0, -1),
        lambda p: p["operators"][0]["indices"].__setitem__(0, True),
        lambda p: p["operators"][0]["data"].__setitem__(0, float("nan")),
        lambda p: p["operators"][0]["data"].__setitem__(0, -1),
        lambda p: p["operators"][0]["data"].__setitem__(0, 0.5),
        lambda p: p["operators"][0]["data"].__setitem__(0, 10**1000),
    ],
)
def test_invalid_csc_is_rejected_before_scipy_allocation(mutation, monkeypatch):
    payload = artifact().to_dict()
    mutation(payload)

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid payload must fail before sparse allocation")

    monkeypatch.setattr("geo_infer_space.core.sparse_transition.csc_matrix", forbidden)
    with pytest.raises(ValueError):
        SparseTransitionArtifact.from_dict(payload)


def test_sparse_budgets_and_noncanonical_entries():
    payload = artifact().to_dict()
    with pytest.raises(ValueError, match="max_states"):
        SparseTransitionArtifact.from_dict(payload, max_states=1)
    with pytest.raises(ValueError, match="max_nnz"):
        SparseTransitionArtifact.from_dict(payload, max_nnz=1)
    duplicate = deepcopy(payload)
    operator = duplicate["operators"][0]
    operator["indices"].insert(0, operator["indices"][0])
    operator["data"][0] = 0.5
    operator["data"].insert(0, 0.5)
    operator["indptr"][1:] = [x + 1 for x in operator["indptr"][1:]]
    with pytest.raises(ValueError, match="sorted|unique"):
        SparseTransitionArtifact.from_dict(duplicate)


@pytest.mark.parametrize("content", ['{"a":1,"a":2}', '{"x":NaN}', b"\xff", "[]"])
def test_json_rejects_ambiguity_and_invalid_encoding(content):
    with pytest.raises(ValueError):
        SparseTransitionArtifact.from_json(content)


def test_json_size_budget_counts_utf8_bytes():
    with pytest.raises(ValueError, match="max_bytes"):
        SparseTransitionArtifact.from_json("é" * 5, max_bytes=5)
    with pytest.raises(ValueError, match="max_bytes"):
        SparseTransitionArtifact.from_json(artifact().to_json(), max_bytes=5)


@pytest.mark.parametrize("keyword", ["max_states", "max_actions", "max_nnz"])
@pytest.mark.parametrize("value", [True, 0, -1, 1.5])
def test_invalid_sparse_budgets(keyword, value):
    with pytest.raises(ValueError):
        SparseTransitionArtifact.from_dict(artifact().to_dict(), **{keyword: value})


@pytest.mark.parametrize(
    "belief,action",
    [
        ([1], "stay"),
        ([float("nan")] * 7, "stay"),
        ([0] * 7, "stay"),
        ([-1, 2, 0, 0, 0, 0, 0], "stay"),
        ([1, 0, 0, 0, 0, 0, 0], "unknown"),
        ([True, False, False, False, False, False, False], "stay"),
        (["1", "0", "0", "0", "0", "0", "0"], "stay"),
        ([[1]] * 7, "stay"),
        ([10**1000, 0, 0, 0, 0, 0, 0], "stay"),
    ],
)
def test_invalid_prediction(belief, action):
    with pytest.raises(ValueError):
        artifact().predict(belief, action)


@pytest.mark.parametrize(
    "parent", [h3.latlng_to_cell(41.75, -124.2, 7), h3.get_pentagons(7)[0]]
)
def test_parent_child_mass_conservation_and_round_trip(parent, monkeypatch):
    coarse = H3StateSpace([parent])
    fine = H3StateSpace(sorted(h3.cell_to_children(parent, 8), reverse=True))

    def forbidden(*args, **kwargs):
        raise AssertionError("Resolution transfer must remain sparse")

    monkeypatch.setattr(csc_matrix, "toarray", forbidden)
    lift = h3_resolution_transfer(coarse, fine)
    restrict = h3_resolution_transfer(fine, coarse)
    child_mass = lift @ np.array([1.0])
    np.testing.assert_allclose(
        child_mass, np.full(len(fine.cells), 1 / len(fine.cells))
    )
    np.testing.assert_allclose(restrict @ child_mass, [1])
    assert lift.nnz == restrict.nnz == len(fine.cells)
    np.testing.assert_allclose(lift.sum(axis=0), 1)
    np.testing.assert_allclose(restrict.sum(axis=0), 1)


def test_resolution_transfer_reorders_and_refuses_incomplete_refinement():
    parent = h3.latlng_to_cell(41.75, -124.2, 7)
    cells = sorted(h3.cell_to_children(parent, 8))
    fine = H3StateSpace(cells)
    reverse = H3StateSpace(reversed(cells))
    weights = np.arange(len(cells), dtype=float)
    np.testing.assert_array_equal(
        h3_resolution_transfer(fine, reverse) @ weights, weights[::-1]
    )
    with pytest.raises(ValueError, match="complete"):
        h3_resolution_transfer(H3StateSpace([parent]), H3StateSpace(cells[:-1]))
    with pytest.raises(ValueError, match="max_nnz"):
        h3_resolution_transfer(H3StateSpace([parent]), fine, max_nnz=1)
    outside = H3StateSpace([h3.latlng_to_cell(0, 0, 7)])
    with pytest.raises(ValueError, match="cover|parent"):
        h3_resolution_transfer(fine, outside)


def test_unequal_child_counts_preserve_nonuniform_parent_probabilities():
    parents = [h3.latlng_to_cell(41.75, -124.2, 7), h3.get_pentagons(7)[0]]
    children = [cell for parent in parents for cell in h3.cell_to_children(parent, 8)]
    coarse = H3StateSpace(parents)
    fine = H3StateSpace(sorted(children))
    lifted = h3_resolution_transfer(coarse, fine) @ np.array([0.25, 0.75])
    for index, cell in enumerate(fine.cells):
        parent = h3.cell_to_parent(cell, 7)
        expected = 0.25 / 7 if parent == parents[0] else 0.75 / 6
        assert lifted[index] == pytest.approx(expected)
    np.testing.assert_allclose(
        h3_resolution_transfer(fine, coarse) @ lifted, [0.25, 0.75]
    )


def test_partial_restriction_sums_only_represented_mass():
    parent = h3.latlng_to_cell(41.75, -124.2, 7)
    child = h3.cell_to_children(parent, 8)[0]
    transfer = h3_resolution_transfer(H3StateSpace([child]), H3StateSpace([parent]))
    np.testing.assert_array_equal(transfer @ [0.4], [0.4])


def test_huge_refinement_refused_without_enumerating_children(monkeypatch):
    parent = h3.latlng_to_cell(41.75, -124.2, 1)
    fine = H3StateSpace([h3.latlng_to_cell(41.75, -124.2, 15)])

    def forbidden(*args, **kwargs):
        raise AssertionError("Must check refinement size before enumerating")

    monkeypatch.setattr(h3, "cell_to_children", forbidden)
    with pytest.raises(ValueError, match="max_nnz|complete"):
        h3_resolution_transfer(H3StateSpace([parent]), fine)
