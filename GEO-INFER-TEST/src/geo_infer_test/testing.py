"""Reusable deterministic assertions and fixtures for GEO-INFER tests."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import http.server
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

import numpy as np
import pytest


def as_finite_array(value: Any, *, name: str = "value") -> np.ndarray:
    """Convert a value to a non-empty finite floating-point array."""
    array = np.asarray(value, dtype=float)
    if array.size == 0:
        raise AssertionError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise AssertionError(f"{name} contains non-finite values: {array!r}")
    return array


def assert_finite(value: Any, *, name: str = "value") -> None:
    """Recursively assert that numpy-rich values contain only finite numbers."""
    if isinstance(value, Mapping):
        for key, item in value.items():
            assert_finite(item, name=f"{name}[{key!r}]")
        return
    if isinstance(value, (list, tuple)) and value:
        if all(np.isscalar(item) for item in value):
            as_finite_array(value, name=name)
        else:
            for index, item in enumerate(value):
                assert_finite(item, name=f"{name}[{index}]")
        return
    if isinstance(value, (np.ndarray, np.number, float, int)):
        if isinstance(value, np.ndarray) and value.dtype == object:
            for index, item in enumerate(value.flat):
                assert_finite(item, name=f"{name}[{index}]")
            return
        as_finite_array(value, name=name)


def assert_probability(
    values: Any, *, name: str = "probability", atol: float = 1e-8
) -> np.ndarray:
    """Assert a finite non-negative vector sums to one and return it."""
    array = as_finite_array(values, name=name).reshape(-1)
    if np.any(array < -atol):
        raise AssertionError(f"{name} contains negative mass: {array!r}")
    if not np.isclose(float(array.sum()), 1.0, atol=atol, rtol=0.0):
        raise AssertionError(f"{name} does not sum to one: {array.sum()!r}")
    return array


def assert_stochastic_matrix(
    matrix: Any, *, axis: int = 0, name: str = "matrix", atol: float = 1e-8
) -> np.ndarray:
    """Assert a finite non-negative matrix has unit sums along ``axis``."""
    array = as_finite_array(matrix, name=name)
    if array.ndim != 2:
        raise AssertionError(f"{name} must be two-dimensional, got {array.shape}")
    if np.any(array < -atol):
        raise AssertionError(f"{name} contains negative entries")
    sums = np.sum(array, axis=axis)
    if not np.allclose(sums, 1.0, atol=atol, rtol=0.0):
        raise AssertionError(f"{name} is not stochastic along axis {axis}: {sums!r}")
    return array


def assert_same_finite_values(
    first: Any, second: Any, *, name: str = "values", atol: float = 1e-10
) -> None:
    """Assert two numeric outputs have equal shape and deterministic values."""
    first_array = as_finite_array(first, name=f"{name}.first")
    second_array = as_finite_array(second, name=f"{name}.second")
    if first_array.shape != second_array.shape or not np.allclose(
        first_array, second_array, atol=atol, rtol=0.0
    ):
        raise AssertionError(f"{name} is not deterministic")


def assert_no_nan_statistics(values: Mapping[str, Any]) -> None:
    """Assert scalar statistics are finite and mappings are recursively valid."""
    for key, value in values.items():
        if isinstance(value, Mapping):
            assert_no_nan_statistics(value)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            assert_finite(value, name=str(key))
        elif isinstance(value, (int, float, np.number)):
            as_finite_array(value, name=str(key))


def assert_model_contract(
    output: Any,
    *,
    shape: tuple[int, ...] | None = None,
    dtype: np.dtype | type | None = None,
    probability: bool = False,
    stochastic_axis: int | None = None,
) -> np.ndarray:
    """Validate the common finite/shape/dtype contract for model outputs."""
    array = as_finite_array(output, name="model_output")
    if shape is not None and array.shape != shape:
        raise AssertionError(f"model_output has shape {array.shape}, expected {shape}")
    if dtype is not None and not np.can_cast(array.dtype, dtype, casting="safe"):
        raise AssertionError(
            f"model_output dtype {array.dtype} is not compatible with {dtype}"
        )
    if probability:
        assert_probability(array, name="model_probability")
    if stochastic_axis is not None:
        assert_stochastic_matrix(array, axis=stochastic_axis, name="model_matrix")
    return array


def assert_seed_replay(factory: Any, *, seed: int = 42) -> None:
    """Assert that a seeded model factory produces the same finite output twice."""
    first = factory(seed=seed)
    second = factory(seed=seed)
    assert_same_finite_values(first, second, name="seeded_model_output")


def assert_visualization_manifest(
    manifest: Mapping[str, Any], *, root: Path | str
) -> None:
    """Validate artifact paths, hashes, finite statistics, and schema metadata."""
    if manifest.get("schema_version") != "1.0":
        raise AssertionError("visualization manifest schema_version must be 1.0")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise AssertionError("visualization manifest must contain artifacts")
    root_path = Path(root)
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            raise AssertionError("manifest artifact entries must be mappings")
        relative_path = artifact.get("path")
        expected_hash = artifact.get("sha256")
        if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
            raise AssertionError("manifest artifact requires path and sha256")
        path = root_path / relative_path
        if not path.is_file() or path.stat().st_size == 0:
            raise AssertionError(f"missing or empty artifact: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise AssertionError(f"artifact hash mismatch: {path}")
        assert_no_nan_statistics(artifact.get("statistics", {}))


@dataclass
class LocalService:
    """Small deterministic service state object for integration tests."""

    name: str = "local-service"
    requests: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.requests is None:
            self.requests = []

    def record(self, payload: Mapping[str, Any]) -> None:
        """Record a request without contacting an external service."""
        assert self.requests is not None
        self.requests.append(dict(payload))


@pytest.fixture
def deterministic_rng() -> np.random.Generator:
    """Provide a fresh deterministic NumPy generator for each test."""
    return np.random.default_rng(42)


@pytest.fixture
def local_filesystem(tmp_path: Path) -> Path:
    """Provide an isolated filesystem fixture rooted at pytest's temp path."""
    return tmp_path


@pytest.fixture
def sqlite_database(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    """Provide a transaction-safe local SQLite database for integration tests."""
    connection = sqlite3.connect(tmp_path / "fixture.sqlite3")
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def local_http_server() -> Iterator[str]:
    """Serve deterministic JSON over localhost without external network access."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib protocol name
            body = json.dumps({"status": "ok", "source": "local-fixture"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: Any) -> None:
            return

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


@pytest.fixture
def local_service() -> LocalService:
    """Provide a deterministic in-process external-service substitute."""
    return LocalService()


__all__ = [
    "as_finite_array",
    "assert_finite",
    "assert_no_nan_statistics",
    "assert_model_contract",
    "assert_probability",
    "assert_seed_replay",
    "assert_same_finite_values",
    "assert_stochastic_matrix",
    "assert_visualization_manifest",
    "LocalService",
    "deterministic_rng",
    "local_filesystem",
    "local_http_server",
    "local_service",
    "sqlite_database",
]
