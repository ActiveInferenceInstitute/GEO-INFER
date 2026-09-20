"""Unit tests for validate_test_contracts.py scan-surface and inventory rules.

Loads the validator script as a module, points its ``ROOT`` at a synthetic
tmp tree, and asserts the contract it exists to enforce: nested test trees
are scanned, conftest files are checked for forbidden controls only, marker
registries include conftest runtime registrations, and GEO-INFER-TEST
inventory docs must match the live test tree in both directions.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "GEO-INFER-TEST"


def _load_script(tmp_path: Path):
    """Load validate_test_contracts.py and repoint ROOT at ``tmp_path``."""
    spec = importlib.util.spec_from_file_location(
        "validate_test_contracts_under_test", SCRIPT_DIR / "validate_test_contracts.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = tmp_path
    return module


def _seed_module(root: Path, name: str) -> Path:
    """Create a minimal conforming module with an empty test inventory."""
    module_dir = root / f"GEO-INFER-{name}"
    (module_dir / "tests").mkdir(parents=True)
    (module_dir / "tests" / "README.md").write_text("# inventory\n", encoding="utf-8")
    return module_dir


def _seed_root(root: Path) -> None:
    """Write the root pyproject the marker registry reads."""
    (root / "pyproject.toml").write_text(
        '[project]\nname = "seed"\n\n[tool.pytest.ini_options]\nmarkers = [\n'
        '    "unit: unit tests",\n'
        "]\n",
        encoding="utf-8",
    )


class TestScanSurface:
    """The validator must scan every tests tree, including nested ones."""

    def test_nested_test_tree_is_scanned(self, tmp_path):
        module = _load_script(tmp_path)
        _seed_root(tmp_path)
        nested = _seed_module(tmp_path, "NEST") / "locations" / "cascadia" / "tests"
        nested.mkdir(parents=True)
        (nested / "test_bad.py").write_text(
            '"""Behavior under test."""\n\nimport pytest\n\n'
            "def test_bad() -> None:\n"
            '    """Uses a forbidden control."""\n'
            "    pytest." + "skip('nope')\n",
            encoding="utf-8",
        )
        errors = module.validate(strict=False)
        assert any("test_bad.py" in error for error in errors)

    def test_conftest_forbidden_control_is_flagged(self, tmp_path):
        module = _load_script(tmp_path)
        _seed_root(tmp_path)
        module_dir = _seed_module(tmp_path, "ACT")
        (module_dir / "tests" / "conftest.py").write_text(
            "import pytest\n\ngpd = pytest.import" + 'orskip("geopandas")\n',
            encoding="utf-8",
        )
        errors = module.validate(strict=False)
        assert any(
            "conftest.py" in error and "forbidden test control" in error
            for error in errors
        )

    def test_conftest_fixtures_are_not_flagged(self, tmp_path):
        module = _load_script(tmp_path)
        _seed_root(tmp_path)
        module_dir = _seed_module(tmp_path, "CLEAN")
        (module_dir / "tests" / "conftest.py").write_text(
            "import pytest\n\n\n"
            '@pytest.fixture\ndef sample():\n'
            '    """Provide shared test data."""\n'
            "    return {}\n",
            encoding="utf-8",
        )
        (module_dir / "tests" / "test_ok.py").write_text(
            '"""Behavior under test."""\n\n'
            "def test_ok() -> None:\n"
            '    """The behavior holds."""\n'
            "    assert True\n",
            encoding="utf-8",
        )
        assert module.validate(strict=True) == []


class TestMarkerRegistry:
    """Marker registries include conftest runtime registrations."""

    def test_conftest_registered_marker_is_known(self, tmp_path):
        module = _load_script(tmp_path)
        _seed_root(tmp_path)
        module_dir = _seed_module(tmp_path, "MARK")
        (module_dir / "tests" / "conftest.py").write_text(
            'def pytest_configure(config):\n'
            '    """Register runtime markers."""\n'
            '    config.addinivalue_line("markers", "temporal: Temporal data tests")\n',
            encoding="utf-8",
        )
        (module_dir / "tests" / "test_marked.py").write_text(
            '"""Behavior under test."""\n\nimport pytest\n\n'
            '@pytest.mark.temporal\n'
            "def test_temporal() -> None:\n"
            '    """The behavior holds."""\n'
            "    assert True\n",
            encoding="utf-8",
        )
        assert "temporal" in module.configured_markers()
        assert module.validate(strict=False) == []

    def test_truly_unknown_marker_is_flagged(self, tmp_path):
        module = _load_script(tmp_path)
        _seed_root(tmp_path)
        module_dir = _seed_module(tmp_path, "UMARK")
        (module_dir / "tests" / "test_marked.py").write_text(
            '"""Behavior under test."""\n\nimport pytest\n\n'
            '@pytest.mark.banana\n'
            "def test_marked() -> None:\n"
            '    """The behavior holds."""\n'
            "    assert True\n",
            encoding="utf-8",
        )
        errors = module.validate(strict=False)
        assert any("unknown marker 'banana'" in error for error in errors)


class TestInventoryParity:
    """GEO-INFER-TEST inventory docs must match the live test tree."""

    def test_listed_but_missing_and_present_but_unlisted(self, tmp_path):
        module = _load_script(tmp_path)
        unit_dir = tmp_path / "GEO-INFER-TEST" / "tests" / "unit"
        unit_dir.mkdir(parents=True)
        (unit_dir / "README.md").write_text("- `test_ghost.py`\n", encoding="utf-8")
        (unit_dir / "test_real.py").write_text(
            '"""Behavior under test."""\n\n'
            "def test_real() -> None:\n"
            '    """The behavior holds."""\n'
            "    assert True\n",
            encoding="utf-8",
        )
        errors = module.inventory_parity_errors()
        assert any("listed but missing: test_ghost.py" in error for error in errors)
        assert any(
            "present but unlisted: test_real.py" in error for error in errors
        )
