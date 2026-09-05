"""Bounded sparse transition artifacts and conservative H3 resolution maps."""

from collections.abc import Mapping
from dataclasses import dataclass
import json
import math

import h3
import numpy as np
from scipy.sparse import csc_matrix

from geo_infer_space.core.state_space import H3StateSpace

SCHEMA_VERSION = "geo-infer-space/sparse-transition/1"


def _positive_integer(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class _CSC:
    indptr: tuple[int, ...]
    indices: tuple[int, ...]
    data: tuple[float, ...]


@dataclass(frozen=True, init=False)
class SparseTransitionArtifact:
    """Immutable JSON-compatible H3 operators indexed [next, current].

    This SPACE format is separate from the dense GNN v1 model contract. It
    describes transitions only, with one canonical CSC operator per action.
    Probabilities are checked, never repaired or normalized on ingestion.
    """

    state_ids: tuple[str, ...]
    action_ids: tuple[str, ...]
    boundary: str
    _operators: tuple[_CSC, ...]

    def __init__(
        self,
        payload: Mapping,
        *,
        max_states: int = 100_000,
        max_actions: int = 100,
        max_nnz: int = 1_000_000,
    ):
        for name, value in (
            ("max_states", max_states),
            ("max_actions", max_actions),
            ("max_nnz", max_nnz),
        ):
            _positive_integer(value, name)
        required = {
            "schema_version",
            "state_ids",
            "action_ids",
            "boundary",
            "operators",
        }
        if not isinstance(payload, Mapping) or set(payload) != required:
            raise ValueError(
                "Sparse artifact requires exactly the declared schema fields"
            )
        if payload["schema_version"] != SCHEMA_VERSION:
            raise ValueError("Unsupported sparse transition schema_version")
        if payload["boundary"] not in ("reflect", "explicit"):
            raise ValueError("boundary must be reflect or explicit")
        states, actions, operators = (
            payload[k] for k in ("state_ids", "action_ids", "operators")
        )
        if not isinstance(states, list) or not 1 <= len(states) <= max_states:
            raise ValueError("state_ids must be a nonempty list within max_states")
        state_space = H3StateSpace(states, max_cells=max_states)
        if (
            not isinstance(actions, list)
            or not 1 <= len(actions) <= max_actions
            or any(not isinstance(a, str) or not a.strip() for a in actions)
            or len(set(actions)) != len(actions)
        ):
            raise ValueError(
                "action_ids must be unique nonempty strings within max_actions"
            )
        if not isinstance(operators, list) or len(operators) != len(actions):
            raise ValueError("Exactly one operator is required per action")
        stored = []
        nnz = 0
        size = len(states)
        for operator in operators:
            if not isinstance(operator, Mapping) or set(operator) != {
                "indptr",
                "indices",
                "data",
            }:
                raise ValueError(
                    "CSC operators require exactly indptr, indices and data"
                )
            indptr, indices, data = (operator[k] for k in ("indptr", "indices", "data"))
            if not all(isinstance(a, list) for a in (indptr, indices, data)):
                raise ValueError("CSC arrays must be lists")
            nnz += len(data)
            if nnz > max_nnz:
                raise ValueError("Sparse artifact exceeds max_nnz")
            if len(indptr) != size + 1 or len(indices) != len(data):
                raise ValueError("CSC array lengths disagree with state count")
            if any(
                isinstance(v, bool) or not isinstance(v, int) for v in indptr + indices
            ):
                raise ValueError("CSC pointers and indices must be integers")
            if (
                indptr[0] != 0
                or indptr[-1] != len(data)
                or any(
                    a > b or a < 0 or b > len(data) for a, b in zip(indptr, indptr[1:])
                )
            ):
                raise ValueError("CSC indptr must be monotone from zero to nnz")
            if any(not 0 <= row < size for row in indices):
                raise ValueError("CSC row index is outside the state space")
            if any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not 0 < v <= 1
                or not math.isfinite(v)
                for v in data
            ):
                raise ValueError("CSC data must contain finite positive probabilities")
            for start, end in zip(indptr, indptr[1:]):
                rows = indices[start:end]
                if any(a >= b for a, b in zip(rows, rows[1:])):
                    raise ValueError(
                        "CSC rows must be sorted and unique within every column"
                    )
                if not math.isclose(
                    math.fsum(data[start:end]), 1.0, rel_tol=0, abs_tol=1e-8
                ):
                    raise ValueError("Each transition column must sum to one")
            stored.append(
                _CSC(tuple(indptr), tuple(indices), tuple(float(v) for v in data))
            )
        if payload["boundary"] == "reflect":
            if actions != ["stay", "diffuse"]:
                raise ValueError(
                    "Reflecting H3 artifacts require stay and diffuse actions"
                )
            expected = self._reflecting_operators(state_space, max_nnz)
            for actual, reference in zip(stored, expected):
                if (
                    actual.indptr != reference.indptr
                    or actual.indices != reference.indices
                    or any(
                        not math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
                        for a, b in zip(actual.data, reference.data)
                    )
                ):
                    raise ValueError(
                        "Reflecting operators disagree with H3 neighbor topology"
                    )
        object.__setattr__(self, "state_ids", state_space.cells)
        object.__setattr__(self, "action_ids", tuple(actions))
        object.__setattr__(self, "boundary", payload["boundary"])
        object.__setattr__(self, "_operators", tuple(stored))

    @classmethod
    def from_dict(cls, payload: Mapping, **budgets: int) -> "SparseTransitionArtifact":
        """Validate bounded CSC lists before constructing any SciPy arrays."""
        return cls(payload, **budgets)

    @classmethod
    def from_json(
        cls, content: str | bytes, *, max_bytes: int = 32 * 1024 * 1024, **budgets: int
    ) -> "SparseTransitionArtifact":
        """Decode bounded UTF-8 JSON, rejecting duplicate keys and nonfinite tokens."""
        _positive_integer(max_bytes, "max_bytes")
        if not isinstance(content, (str, bytes)) or len(content) > max_bytes:
            raise ValueError("JSON input must be str or bytes within max_bytes")
        try:
            encoded = content.encode("utf-8") if isinstance(content, str) else content
            if len(encoded) > max_bytes:
                raise ValueError("JSON input exceeds max_bytes")

            def unique_object(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError(f"Duplicate JSON key: {key}")
                    result[key] = value
                return result

            def invalid_constant(value):
                raise ValueError(f"Nonfinite JSON value: {value}")

            payload = json.loads(
                encoded.decode("utf-8"),
                object_pairs_hook=unique_object,
                parse_constant=invalid_constant,
            )
        except (UnicodeError, RecursionError) as exc:
            raise ValueError("Invalid UTF-8 JSON input") from exc
        return cls(payload, **budgets)

    @classmethod
    def from_state_space(
        cls, space: H3StateSpace, *, max_nnz: int = 1_000_000
    ) -> "SparseTransitionArtifact":
        """Encode stay/diffuse actions using the state's reflecting H3 boundary."""
        _positive_integer(max_nnz, "max_nnz")
        if not isinstance(space, H3StateSpace) or len(space.cells) > 100_000:
            raise ValueError("space must be an H3StateSpace within max_states=100000")
        payload = {
            "schema_version": SCHEMA_VERSION,
            "state_ids": list(space.cells),
            "action_ids": ["stay", "diffuse"],
            "boundary": "reflect",
            "operators": [],
        }
        for operator in cls._reflecting_operators(space, max_nnz):
            payload["operators"].append(
                {
                    "indptr": list(operator.indptr),
                    "indices": list(operator.indices),
                    "data": list(operator.data),
                }
            )
        return cls(payload, max_nnz=max_nnz)

    @staticmethod
    def _reflecting_operators(space: H3StateSpace, max_nnz: int) -> tuple[_CSC, _CSC]:
        size = len(space.cells)
        if 2 * size > max_nnz:
            raise ValueError("Sparse artifact exceeds max_nnz")
        stay = _CSC(tuple(range(size + 1)), tuple(range(size)), (1.0,) * size)
        lookup = {cell: i for i, cell in enumerate(space.cells)}
        indptr, indices, data = [0], [], []
        for column, cell in enumerate(space.cells):
            neighbors = sorted(set(h3.grid_disk(cell, 1)) - {cell}) or [cell]
            weights = {}
            for neighbor in neighbors:
                row = lookup.get(neighbor, column)
                weights[row] = weights.get(row, 0.0) + 1.0 / len(neighbors)
            if size + len(data) + len(weights) > max_nnz:
                raise ValueError("Sparse artifact exceeds max_nnz")
            for row in sorted(weights):
                indices.append(row)
                data.append(weights[row])
            indptr.append(len(data))
        return stay, _CSC(tuple(indptr), tuple(indices), tuple(data))

    def to_dict(self) -> dict:
        """Return an independent serializable snapshot preserving state order."""
        return {
            "schema_version": SCHEMA_VERSION,
            "state_ids": list(self.state_ids),
            "action_ids": list(self.action_ids),
            "boundary": self.boundary,
            "operators": [
                {
                    "indptr": list(op.indptr),
                    "indices": list(op.indices),
                    "data": list(op.data),
                }
                for op in self._operators
            ],
        }

    def to_json(self) -> str:
        """Return deterministic compact JSON suitable for a transport artifact."""
        return json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )

    def predict(self, belief, action: str) -> np.ndarray:
        """Apply one sparse transition to a normalized state probability vector."""
        if not isinstance(action, str) or action not in self.action_ids:
            raise ValueError("Unknown action ID")
        size = len(self.state_ids)
        if isinstance(belief, np.ndarray):
            valid_shape = belief.shape == (size,) and belief.dtype.kind in "iuf"
        elif isinstance(belief, (list, tuple)):
            valid_shape = len(belief) == size and all(
                not isinstance(v, (bool, np.bool_))
                and isinstance(v, (int, float, np.integer, np.floating))
                and 0 <= v <= 1
                for v in belief
            )
        else:
            valid_shape = False
        if not valid_shape:
            raise ValueError("belief must be a numeric vector matching the state count")
        values = np.asarray(belief, dtype=float)
        if (
            values.shape != (size,)
            or not np.all(np.isfinite(values))
            or np.any(values < 0)
            or not np.isclose(values.sum(), 1, rtol=0, atol=1e-8)
        ):
            raise ValueError(
                "belief must be a finite normalized state probability vector"
            )
        operator = self._operators[self.action_ids.index(action)]
        matrix = csc_matrix(
            (operator.data, operator.indices, operator.indptr), shape=(size, size)
        )
        return np.asarray(matrix @ values)


def h3_resolution_transfer(
    source: H3StateSpace, target: H3StateSpace, *, max_nnz: int = 1_000_000
) -> csc_matrix:
    """Return a conservative sparse map indexed [target state, source state].

    Restriction sums represented child mass at its parent. Refinement splits
    each parent's mass equally among ALL its H3 children at target resolution;
    a truncated target domain raises instead of redistributing excluded mass.
    These are probabilities per discrete cell, not area densities. Same-level
    transfer is an exact reorder and requires identical cell membership.
    """
    _positive_integer(max_nnz, "max_nnz")
    if not isinstance(source, H3StateSpace) or not isinstance(target, H3StateSpace):
        raise ValueError("source and target must be H3StateSpace instances")
    source_res = h3.get_resolution(source.cells[0])
    target_res = h3.get_resolution(target.cells[0])
    target_index = {cell: i for i, cell in enumerate(target.cells)}
    rows, columns, values = [], [], []
    if source_res >= target_res:
        if len(source.cells) > max_nnz:
            raise ValueError("Resolution transfer exceeds max_nnz")
        parents = [h3.cell_to_parent(cell, target_res) for cell in source.cells]
        if set(parents) != set(target.cells):
            raise ValueError(
                "Target states must exactly cover represented source parents"
            )
        for column, parent in enumerate(parents):
            rows.append(target_index[parent])
            columns.append(column)
            values.append(1.0)
    else:
        counts = [h3.cell_to_children_size(cell, target_res) for cell in source.cells]
        total = sum(counts)
        if total > max_nnz:
            raise ValueError("Resolution transfer exceeds max_nnz")
        if total != len(target.cells):
            raise ValueError("Refinement requires complete child coverage")
        source_set = set(source.cells)
        if any(
            h3.cell_to_parent(cell, source_res) not in source_set
            for cell in target.cells
        ):
            raise ValueError(
                "Refinement target includes a child outside source parents"
            )
        for column, (parent, count) in enumerate(zip(source.cells, counts)):
            for child in h3.cell_to_children(parent, target_res):
                rows.append(target_index[child])
                columns.append(column)
                values.append(1.0 / count)
    return csc_matrix(
        (values, (rows, columns)), shape=(len(target.cells), len(source.cells))
    )
