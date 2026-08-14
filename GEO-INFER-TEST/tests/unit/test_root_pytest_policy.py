"""Regression tests for process-global cleanup in the root pytest policy."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_root_policy():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_root_pytest_policy", REPO_ROOT / "conftest.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cleanup_closes_figures_without_importing_optional_backend(monkeypatch):
    policy = load_root_policy()
    close_calls: list[str] = []
    pyplot = SimpleNamespace(close=close_calls.append)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", pyplot)

    policy._close_imported_matplotlib_figures()

    assert close_calls == ["all"]


def test_cleanup_does_not_import_pyplot(monkeypatch):
    policy = load_root_policy()
    monkeypatch.delitem(sys.modules, "matplotlib.pyplot", raising=False)

    policy._close_imported_matplotlib_figures()

    assert "matplotlib.pyplot" not in sys.modules
