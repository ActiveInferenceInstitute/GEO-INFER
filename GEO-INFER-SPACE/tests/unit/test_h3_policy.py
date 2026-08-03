"""Tests for the H3 grid resolution policy (item: H3 hard-cap guard)."""

from __future__ import annotations

import pytest

from geo_infer_space.core.h3_policy import (
    H3HardCapExceededError,
    check_cell_budget,
    estimate_cell_count,
    suggest_h3_resolution,
    suggest_resolution_with_budget,
)


def test_estimate_cell_count_matches_table() -> None:
    """A 1 km^2 area at resolution 8 (~0.737 km^2/cell) estimates ~1.36 cells."""
    count = estimate_cell_count(1.0, 8)
    assert count == pytest.approx(1.0 / 0.737327598, rel=1e-9)


def test_estimate_cell_count_negative_area_raises() -> None:
    with pytest.raises(ValueError):
        estimate_cell_count(-1.0, 8)


def test_estimate_cell_count_bad_resolution_raises() -> None:
    with pytest.raises(ValueError):
        estimate_cell_count(100.0, 16)


def test_suggest_resolution_finer_for_small_area() -> None:
    """A 10 km^2 area suggests a finer resolution than a 10,000 km^2 area."""
    small = suggest_h3_resolution(10.0)
    large = suggest_h3_resolution(10_000.0)
    assert small["resolution"] > large["resolution"]
    assert small["within_target"] is True
    assert large["within_target"] is True


def test_suggest_resolution_returns_typed_dict() -> None:
    result = suggest_h3_resolution(100.0)
    assert isinstance(result, dict)
    assert set(result) == {"resolution", "estimated_cells", "within_target"}
    assert isinstance(result["resolution"], int)
    assert isinstance(result["estimated_cells"], float)
    assert isinstance(result["within_target"], bool)


def test_suggest_resolution_max_res_bounds() -> None:
    with pytest.raises(ValueError):
        suggest_h3_resolution(100.0, max_res=16)


def test_suggest_resolution_negative_area() -> None:
    with pytest.raises(ValueError):
        suggest_h3_resolution(-5.0)


def test_suggest_resolution_nonpositive_target() -> None:
    with pytest.raises(ValueError):
        suggest_h3_resolution(100.0, target_cells=0)


def test_check_cell_budget_within_cap() -> None:
    # Does not raise.
    check_cell_budget(150_000, hard_cap=200_000)


def test_check_cell_budget_over_cap_raises() -> None:
    with pytest.raises(H3HardCapExceededError):
        check_cell_budget(250_000, hard_cap=200_000)


def test_check_cell_budget_negative_raises() -> None:
    with pytest.raises(ValueError):
        check_cell_budget(-1.0)


def test_suggest_resolution_with_budget_within() -> None:
    result = suggest_resolution_with_budget(100.0)
    assert set(result) == {"resolution", "estimated_cells", "within_target"}
    assert isinstance(result["resolution"], int)


def test_suggest_resolution_with_budget_exceeding() -> None:
    """When reaching the target would exceed the hard cap, raise."""
    # target_cells above the hard cap means the finest resolution that meets
    # the target also exceeds the safety cap -> refused.
    with pytest.raises(H3HardCapExceededError):
        suggest_resolution_with_budget(
            1000.0, target_cells=500_000, hard_cap=200_000
        )
