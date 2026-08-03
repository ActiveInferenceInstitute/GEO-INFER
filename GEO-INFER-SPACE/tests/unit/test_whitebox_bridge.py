"""Tests for the optional WhiteboxTools bridge (item 5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from geo_infer_space.core.whitebox_bridge import (
    HAS_WHITEBOX,
    flow_accumulation,
    whitebox_available,
    whitebox_status,
    whitebox_version,
)


def test_availability_flags_consistent() -> None:
    assert isinstance(HAS_WHITEBOX, bool)
    assert whitebox_available() == HAS_WHITEBOX


def test_version_none_without_whitebox() -> None:
    if not HAS_WHITEBOX:
        assert whitebox_version() is None
    else:
        assert whitebox_version() is not None


def test_status_reports_state() -> None:
    status = whitebox_status()
    if HAS_WHITEBOX:
        assert "available" in status
    else:
        assert "unavailable" in status


def test_flow_accumulation_missing_dep_raises_import_error(tmp_path: Path) -> None:
    """Without whitebox-workflows, the tool fails fast with a clear error."""
    dem = tmp_path / "dem.tif"
    dem.write_bytes(b"not a real raster")
    # In this environment whitebox-workflows is not installed, so the call
    # must raise ImportError (never a silent stub).
    with pytest.raises(ImportError):
        flow_accumulation(dem, tmp_path / "out.tif")


def test_flow_accumulation_missing_dem_file(tmp_path: Path) -> None:
    """The missing-dep check fires before the file check in this env."""
    missing = tmp_path / "missing.tif"
    if HAS_WHITEBOX:
        with pytest.raises(FileNotFoundError):
            flow_accumulation(missing, tmp_path / "out.tif")
    else:
        # whitebox-workflows absent: the require-check runs first and must not
        # fabricate a result even for an invalid DEM path.
        with pytest.raises(ImportError):
            flow_accumulation(missing, tmp_path / "out.tif")
