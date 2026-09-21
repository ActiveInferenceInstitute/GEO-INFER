"""Tests for the ortools-dependent optimization utilities in geo_infer_log.

``geo_infer_log.utils.optimization`` guards its ``ortools`` import at module
level: importing the module must succeed with or without the dependency
installed, and the solver entry points must raise a helpful ``ImportError``
when it is absent. The dependency itself is declared in the ``solver``
extra of GEO-INFER-LOG/pyproject.toml.
"""

import pytest

import geo_infer_log.utils.optimization as optimization
from geo_infer_log.utils.optimization import solve_tsp, solve_vrp


def test_module_imports_without_ortools() -> None:
    """The guarded import must never turn module import into a failure."""
    assert hasattr(optimization, "_HAS_ORTOOLS")


def test_solve_tsp_raises_import_error_when_ortools_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With ortools absent, solve_tsp raises ImportError naming the fix."""
    monkeypatch.setattr(optimization, "_HAS_ORTOOLS", False)
    with pytest.raises(ImportError, match="ortools"):
        solve_tsp(points=[(0.0, 0.0), (1.0, 1.0)])


def test_solve_vrp_raises_import_error_when_ortools_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With ortools absent, solve_vrp raises ImportError naming the fix."""
    monkeypatch.setattr(optimization, "_HAS_ORTOOLS", False)
    with pytest.raises(ImportError, match="ortools"):
        solve_vrp(
            depots=[(0.0, 0.0)],
            deliveries=[(1.0, 1.0)],
            num_vehicles=1,
        )