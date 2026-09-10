"""Behavior tests for the shared ``geo_infer_test.testing`` helper surface.

These tests pin the observable contract that every module's model-contract
tests rely on: finite-array coercion, probability and stochastic-matrix
validation, deterministic-replay comparison, manifest integrity, and the
in-process fixtures.  A regression here silently weakens the whole
per-module test fleet, so the helpers are defended directly.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import urllib.request
from pathlib import Path
import numpy as np
import pytest

from geo_infer_test.testing import (
    LocalService,
    assert_finite,
    assert_model_contract,
    assert_no_nan_statistics,
    assert_probability,
    assert_same_finite_values,
    assert_seed_replay,
    assert_stochastic_matrix,
    assert_visualization_manifest,
    as_finite_array,
)


def test_as_finite_array_coerces_and_rejects_empty_and_nonfinite() -> None:
    """Coercion to a finite float array, with empty and non-finite rejection."""
    array = as_finite_array([1, 2, 3], name="values")
    assert array.dtype == float
    np.testing.assert_array_equal(array, [1.0, 2.0, 3.0])

    with pytest.raises(AssertionError, match="must not be empty"):
        as_finite_array([], name="empty_input")

    with pytest.raises(AssertionError, match="non-finite"):
        as_finite_array([1.0, float("nan")], name="nan_input")

    with pytest.raises(AssertionError, match="non-finite"):
        as_finite_array([1.0, float("inf")], name="inf_input")


def test_assert_finite_walks_nested_containers() -> None:
    """Mappings, homogeneous scalar sequences, and nested arrays all recurse."""
    assert_finite({"matrix": np.array([[1.0, 2.0], [3.0, 4.0]]), "scalars": [1, 2, 3]})

    with pytest.raises(AssertionError, match="non-finite"):
        assert_finite({"row": [1.0, float("nan")], "name": "bad"})

    with pytest.raises(AssertionError, match="non-finite"):
        assert_finite({"nested": {"deep": np.array([float("inf")])}})


def test_assert_probability_enforces_unit_mass() -> None:
    """Valid distributions pass; negative mass and wrong sums are rejected."""
    vector = assert_probability([0.2, 0.3, 0.5], name="dist")
    assert vector.shape == (3,)

    with pytest.raises(AssertionError, match="negative mass"):
        assert_probability([-0.1, 0.6, 0.5], name="neg")

    with pytest.raises(AssertionError, match="sum to one"):
        assert_probability([0.2, 0.3, 0.4], name="short")


def test_assert_stochastic_matrix_axis_and_shape() -> None:
    """Row- and column-stochastic matrices pass; bad shape or sums rejected."""
    matrix = assert_stochastic_matrix([[0.5, 0.5], [1.0, 0.0]], axis=1, name="m")
    assert matrix.shape == (2, 2)

    column = assert_stochastic_matrix([[0.3, 0.7], [0.7, 0.3]], axis=0, name="c")
    assert column.shape == (2, 2)

    with pytest.raises(AssertionError, match="two-dimensional"):
        assert_stochastic_matrix([1.0], name="flat")

    with pytest.raises(AssertionError, match="not stochastic"):
        assert_stochastic_matrix([[0.5, 0.4]], axis=1, name="leaky")


def test_assert_same_finite_values_flags_shape_and_value_drift() -> None:
    """Deterministic replay passes; shape or value drift raises."""
    assert_same_finite_values([1.0, 2.0], [1.0, 2.0])

    with pytest.raises(AssertionError, match="not deterministic"):
        assert_same_finite_values([1.0, 2.0], [1.0, 2.0, 3.0], name="shape")

    with pytest.raises(AssertionError, match="not deterministic"):
        assert_same_finite_values([1.0, 2.0], [1.0, 2.5], name="value")


def test_assert_seed_replay_pins_seeded_factories() -> None:
    """A seeded factory replays identically; an unseeded one drifts."""
    assert_seed_replay(lambda seed: np.random.default_rng(seed).normal(size=4))

    counter = {"n": 0}

    def drifting(seed: int) -> np.ndarray:
        counter["n"] += 1
        return np.full(3, float(counter["n"]))

    with pytest.raises(AssertionError, match="not deterministic"):
        assert_seed_replay(drifting)


def test_assert_no_nan_statistics_recurses_into_sequences() -> None:
    """Scalar leaves, nested mappings, and numeric sequences are all checked."""
    assert_no_nan_statistics({"mean": 0.5, "rows": [1, 2, 3], "nested": {"std": 0.1}})

    with pytest.raises(AssertionError, match="non-finite"):
        assert_no_nan_statistics({"rows": [1, float("nan")]})


def test_assert_model_contract_shape_dtype_probability_matrix() -> None:
    """The composite contract checks every requested dimension of the output."""
    matrix = assert_model_contract(
        [[0.25, 0.75], [0.75, 0.25]],
        shape=(2, 2),
        dtype=float,
        probability=False,
        stochastic_axis=1,
    )
    assert matrix.shape == (2, 2)

    with pytest.raises(AssertionError, match="shape"):
        assert_model_contract([[1.0]], shape=(2, 2))

    with pytest.raises(AssertionError, match="not compatible"):
        assert_model_contract([[1.5]], dtype=int)

    with pytest.raises(AssertionError, match="sum to one"):
        assert_model_contract([[0.5, 0.6]], probability=True)


def test_assert_visualization_manifest_hashes_and_statistics(tmp_path: Path) -> None:
    """Manifest entries must exist, be non-empty, and match their sha256."""
    artifact = tmp_path / "figure.json"
    artifact.write_bytes(json.dumps({"value": 1.0}).encode())
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()

    manifest = {
        "schema_version": "1.0",
        "artifacts": [
            {
                "path": "figure.json",
                "sha256": digest,
                "statistics": {"max": 1.0},
            }
        ],
    }
    assert isinstance(manifest["artifacts"][0], dict)

    assert_visualization_manifest(manifest, root=tmp_path)

    with pytest.raises(AssertionError, match="schema_version"):
        assert_visualization_manifest(
            {"schema_version": "9.9", "artifacts": manifest["artifacts"]},
            root=tmp_path,
        )

    with pytest.raises(AssertionError, match="hash mismatch"):
        broken = {
            "schema_version": "1.0",
            "artifacts": [
                {"path": "figure.json", "sha256": "0" * 64, "statistics": {}}
            ],
        }
        assert_visualization_manifest(broken, root=tmp_path)

    missing = {
        "schema_version": "1.0",
        "artifacts": [{"path": "absent.json", "sha256": digest, "statistics": {}}],
    }
    with pytest.raises(AssertionError, match="missing or empty artifact"):
        assert_visualization_manifest(missing, root=tmp_path)


def test_local_service_records_requests_in_process() -> None:
    """The external-service substitute records payloads without any network."""
    service = LocalService()
    service.record({"route": "probe", "count": 1})
    assert service.requests == [{"route": "probe", "count": 1}]

    named = LocalService(name="payroll")
    named.record({})
    assert named.name == "payroll"


def test_sqlite_database_fixture_commits_and_closes(
    sqlite_database: sqlite3.Connection, tmp_path: Path
) -> None:
    """The transaction-safe fixture yields a usable connection over tmp_path."""
    sqlite_database.execute("CREATE TABLE probe (id INTEGER PRIMARY KEY, label TEXT)")
    sqlite_database.execute("INSERT INTO probe (label) VALUES (?)", ("alpha",))
    sqlite_database.commit()
    row = sqlite_database.execute("SELECT label FROM probe WHERE id = 1").fetchone()
    assert row == ("alpha",)
    assert (tmp_path / "fixture.sqlite3").is_file()


def test_local_http_server_serves_deterministic_json(
    local_http_server: str,
) -> None:
    """The localhost fixture serves the same JSON body on every request."""
    with urllib.request.urlopen(f"{local_http_server}/status") as response:
        payload = json.loads(response.read().decode())
    assert payload == {"status": "ok", "source": "local-fixture"}

    with urllib.request.urlopen(local_http_server) as second:
        assert json.loads(second.read().decode()) == payload


def test_deterministic_rng_fixture_is_seeded(
    deterministic_rng: np.random.Generator,
) -> None:
    """The fixture yields the canonical seed-42 sequence."""
    expected = np.random.default_rng(42).normal(size=5)
    np.testing.assert_array_equal(deterministic_rng.normal(size=5), expected)


def test_local_filesystem_fixture_roots_at_tmp(
    local_filesystem: Path, tmp_path: Path
) -> None:
    """The filesystem fixture is the pytest temp root, not the repo."""
    assert local_filesystem == tmp_path


def test_local_service_fixture_returns_fresh_instance(
    local_service: LocalService,
) -> None:
    """The fixture hands back an empty recorder."""
    assert local_service.requests == []
