"""Topology, ordering and allocation contracts for H3 state spaces."""

import h3
import numpy as np
import pytest
from geo_infer_space.core.state_space import H3StateSpace


@pytest.mark.parametrize(
    "center", [h3.latlng_to_cell(41.75, -124.2, 8), h3.get_pentagons(8)[0]]
)
def test_probability_conservation_and_order(center):
    cells = sorted(h3.grid_disk(center, 1), reverse=True)
    space = H3StateSpace(cells)
    assert space.cells == tuple(cells)
    stay, diffuse = space.transitions()
    np.testing.assert_allclose(diffuse.sum(axis=0), 1)
    np.testing.assert_array_equal(stay.toarray(), np.eye(len(cells)))
    degree = len(cells) - 1
    column = diffuse.toarray()[:, cells.index(center)]
    assert column[cells.index(center)] == 0
    np.testing.assert_allclose(column[column > 0], 1 / degree)
    assert diffuse.nnz <= 7 * len(cells)
    assert space.locate(*h3.cell_to_latlng(center)) == cells.index(center)


def test_isolated_boundary_and_dense_cap():
    cell = h3.latlng_to_cell(41.75, -124.2, 8)
    space = H3StateSpace([cell])
    np.testing.assert_allclose(
        space.dense_transition_tensor(), np.ones((1, 1, 2)), rtol=0, atol=1e-15
    )
    with pytest.raises(ValueError, match="max_entries"):
        space.dense_transition_tensor(max_entries=1)
    with pytest.raises(ValueError, match="outside"):
        space.locate(0, 0)


def test_invalid_and_duplicate_cells_rejected():
    cell = h3.latlng_to_cell(41.75, -124.2, 8)
    for values in (
        [],
        [cell, cell],
        [cell, h3.cell_to_parent(cell)],
        ["invalid"],
        [cell.upper()],
    ):
        with pytest.raises(ValueError):
            H3StateSpace(values)
    with pytest.raises(ValueError):
        H3StateSpace(iter([cell, cell]), max_cells=1)
