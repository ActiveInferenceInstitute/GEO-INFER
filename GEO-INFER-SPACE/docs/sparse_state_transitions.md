# Sparse H3 state transitions and resolution transfer

The `geo_infer_space.core.sparse_transition` module transports transition
operators without allocating a dense state-by-state matrix. Its
`geo-infer-space/sparse-transition/1` schema is a SPACE transition-only format.
It is separate from the dense `gnn-geo-infer/1` model artifact: the latter's
consumer does not accept this format as a full generative model.

## Construct, transport and predict

```python
import h3
import numpy as np
from geo_infer_space.core.state_space import H3StateSpace
from geo_infer_space.core.sparse_transition import SparseTransitionArtifact

center = h3.latlng_to_cell(41.75, -124.2, 8)
space = H3StateSpace(sorted(h3.grid_disk(center, 1)))
artifact = SparseTransitionArtifact.from_state_space(space)
transported = SparseTransitionArtifact.from_json(artifact.to_json())
prior = np.zeros(len(space.cells))
prior[space.cells.index(center)] = 1
next_prior = transported.predict(prior, "diffuse")
assert np.isclose(next_prior.sum(), 1)
```

Each JSON artifact contains exactly:

| Field | Meaning |
| --- | --- |
| `schema_version` | `geo-infer-space/sparse-transition/1` |
| `state_ids` | Unique canonical H3 cells at one resolution, in matrix order |
| `action_ids` | Unique nonempty action names, in operator order |
| `boundary` | `reflect` for verified H3 stay/diffuse operators, or `explicit` for caller-defined operators |
| `operators` | One CSC object per action, each with `indptr`, `indices`, `data` |

Every operator has shape `(len(state_ids), len(state_ids))`, indexed
`[next, current]`. Column pointers start at zero, are monotone, and end at the
number of nonzeros. Row indices must be sorted and unique within each column.
Stored entries are finite, strictly positive probabilities; omit exact zeros.
Columns sum to one within absolute tolerance `1e-8`. Ingestion rejects invalid
probabilities without normalizing them or combining duplicate entries.

For `reflect`, action IDs must be `stay` and `diffuse` in that order, and the
actual CSC entries are checked against H3 topology. Diffusion divides mass
equally among the cell's real neighbors. A neighbor outside the represented
domain contributes its share back to the source cell. Pentagon degree comes
from H3. An `explicit` operator remains column stochastic, but can describe any
caller-specified transition graph; action names do not impose dynamics.

The default ingestion caps are 100,000 states, 100 actions, 1,000,000 nonzeros
across all operators, and 32 MiB of UTF-8 JSON. Structural and probability
checks precede SciPy allocation. Generation also enforces its nonzero budget
while constructing columns. `predict` allocates a state vector and a sparse
operator, never a dense square matrix. `from_json` rejects duplicate object
keys, invalid UTF-8 and nonfinite JSON constants. `to_json` returns deterministic
compact JSON; it is not an RFC 8785 canonicalization claim. Returned dictionaries
are copies and cannot change the stored artifact.

## Conservative changes of resolution

```python
from geo_infer_space.core.sparse_transition import h3_resolution_transfer

parent = h3.cell_to_parent(center, 7)
coarse = H3StateSpace([parent])
fine = H3StateSpace(sorted(h3.cell_to_children(parent, 8)))
refinement = h3_resolution_transfer(coarse, fine)
restriction = h3_resolution_transfer(fine, coarse)
fine_mass = refinement @ np.array([1.0])
assert np.allclose(restriction @ fine_mass, [1.0])
```

The returned CSC matrix has shape `(target_states, source_states)`. It preserves
the caller's state order and every column sums to one:

- Restriction sums represented child probabilities into their H3 parent.
  Target cells must be exactly the parents represented by the source. A source
  can contain only some children; aggregation transfers only their represented
  mass, without claiming the omitted cells were observed.
- Refinement divides parent probability equally among **all** children at the
  target resolution. Missing or unrelated children raise. No missing-domain
  mass is discarded or redistributed to a truncated subset. H3 child counts
  are checked against the nonzero budget before enumerating descendants.
- Same-resolution transfer is a permutation and requires identical membership.

These are discrete cell probabilities, not area densities. Equal child weights
are an explicit modeling choice; H3 children do not have identical physical
areas. Refinement followed by restriction is identity on parent mass;
restriction followed by refinement generally loses the original within-parent
distribution. Each state space has one resolution. Mixed-resolution antichains
and full sparse generative-model inference require a separate model contract.

## Verification

```bash
uv run --no-sync python -m pytest \
  GEO-INFER-SPACE/tests/unit/test_sparse_transition.py --no-cov
```

Tests cover JSON round trips, duplicate keys, malformed CSC arrays, strict
probabilities, immutable snapshots, size caps, prediction without `toarray`,
reflecting-topology validation, nonuniform mass across hexagon and pentagon
parents, incomplete coverage rejection, and pre-enumeration refinement bounds.
