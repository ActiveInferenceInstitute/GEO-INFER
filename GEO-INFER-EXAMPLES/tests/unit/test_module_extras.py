"""Unit coverage: missing-dependency hints name real install targets.

The orchestrator engine's ``requires`` field must resolve to an extra that
actually exists in the target module's ``pyproject.toml`` (GS-300: the old
``full`` default existed only in GEO-INFER-PLACE).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

_LIB_PATH = (
    _REPO_ROOT / "GEO-INFER-EXAMPLES" / "examples" / "module_orchestrators" / "_lib.py"
)
_spec = importlib.util.spec_from_file_location("_gs300_lib", _LIB_PATH)
assert _spec is not None and _spec.loader is not None
_lib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lib)
MODULE_EXTRAS = _lib.MODULE_EXTRAS
run_module_orchestrator = _lib.run_module_orchestrator


def test_module_extras_values_exist_in_module_pyprojects() -> None:
    """Every mapped extra is a real optional-dependency group of its module."""
    orchestrator_dirs = {
        p.name
        for p in (
            _REPO_ROOT / "GEO-INFER-EXAMPLES" / "examples" / "module_orchestrators"
        ).iterdir()
        if p.is_dir() and p.name.isupper()
    }
    assert set(MODULE_EXTRAS) == orchestrator_dirs, (
        "MODULE_EXTRAS must cover exactly the orchestrator module directories"
    )

    for module, extra in MODULE_EXTRAS.items():
        pyproject = _REPO_ROOT / f"GEO-INFER-{module}" / "pyproject.toml"
        assert pyproject.is_file(), f"missing {pyproject}"
        groups = tomllib.loads(pyproject.read_text())["project"].get(
            "optional-dependencies", {}
        )
        if extra is None:
            assert not groups, f"{module}: expected no extras, found {sorted(groups)}"
        else:
            assert extra in groups, (
                f"{module}: MODULE_EXTRAS advertises extra {extra!r} which is "
                f"not in pyproject groups {sorted(groups)}"
            )


def test_missing_dependency_hint_uses_verified_extra() -> None:
    """The engine emits the mapped extra (or plain package when unmapped)."""

    def _broken() -> dict:
        raise ModuleNotFoundError("simulated missing dependency")

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = run_module_orchestrator("SPACE", _broken)
    assert rc == 2
    payload = json.loads(buf.getvalue())
    assert payload["status"] == "missing-dependency"
    assert payload["requires"] == "geo-infer-space[dev]"

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = run_module_orchestrator("MARINE", _broken)
    assert rc == 2
    payload = json.loads(buf.getvalue())
    assert payload["requires"] == "geo-infer-marine"
