"""Regression tests for the public H3 operation helpers."""

import pytest

from geo_infer_space.backends.h3.operations import cell_to_coordinates, coordinate_to_cell


def test_cell_to_coordinates_round_trip() -> None:
    cell = coordinate_to_cell(37.7749, -122.4194, 9)
    latitude, longitude = cell_to_coordinates(cell)

    assert abs(latitude - 37.7749) < 0.01
    assert abs(longitude + 122.4194) < 0.01


def test_cell_to_coordinates_rejects_invalid_cell() -> None:
    with pytest.raises(ValueError):
        cell_to_coordinates("not-an-h3-cell")
