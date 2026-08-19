"""Behavior tests for the H3 smoke-check entrypoint."""

import importlib.util
from pathlib import Path

import pytest


def load_module(module_filename: str):
    tools_dir = Path(__file__).parents[2] / "src" / "geo_infer_space" / "tools"
    spec = importlib.util.spec_from_file_location(
        "_run_h3_tests_simple", tools_dir / module_filename
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module


@pytest.fixture(name="mod")
def _mod():
    return load_module("run_h3_tests_simple.py")


def test_main_returns_zero_when_every_check_passes(mod):
    """A healthy H3 install makes main() report success."""
    assert mod.main() == 0


def test_every_registered_check_passes_against_real_h3(mod):
    """Each named check runs against the installed h3 without raising."""
    import h3
    assert mod.CHECKS, "no H3 checks are registered"
    for name, check in mod.CHECKS:
        check(h3)  # must not raise
        assert isinstance(name, str) and name


def test_round_trip_check_rejects_a_broken_h3(mod):
    """A cell that does not round trip is reported, not silently accepted."""

    class BrokenH3:
        @staticmethod
        def latlng_to_cell(lat, lng, resolution):
            return "89283082803ffff"

        @staticmethod
        def is_valid_cell(cell):
            return True

        @staticmethod
        def get_resolution(cell):
            return 9

        @staticmethod
        def cell_to_latlng(cell):
            return (0.0, 0.0)

    with pytest.raises(ValueError):
        mod._check_round_trip(BrokenH3())


def test_main_reports_failure_when_a_check_raises(mod, monkeypatch):
    """main() returns 1 when any registered check fails."""

    def exploding_check(_h3):
        raise ValueError("induced failure")

    monkeypatch.setattr(mod, "CHECKS", (("induced", exploding_check),))
    assert mod.main() == 1
