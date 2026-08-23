"""Unit tests for the packaging / wheel-validation contract helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / "GEO-INFER-TEST" / "validate_packaging.py"


def load_packaging_module():
    spec = importlib.util.spec_from_file_location(
        "geo_infer_validate_packaging", VALIDATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _make_pyproject(dir_path: Path) -> Path:
    """Plant a minimal conforming pyproject.toml in a module directory."""
    pyproject = dir_path / "pyproject.toml"
    pyproject.write_text(
        "\n".join(
            [
                "[project]",
                'name = "geo-infer-sample"',
                'version = "0.2.0"',
                "",
                "[tool.setuptools]",
                'package-dir = {"" = "src"}',
                "",
                "[tool.setuptools.package-data]",
                '"*" = ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return pyproject


def test_valid_distribution_namespace_accepts_platform_prefix(tmp_path, monkeypatch):
    packaging = load_packaging_module()
    assert packaging.valid_distribution_namespace("geo-infer-space") is True
    assert packaging.valid_distribution_namespace("geo-infer-test") is True


def test_valid_distribution_namespace_rejects_bad_prefix(tmp_path, monkeypatch):
    packaging = load_packaging_module()
    assert packaging.valid_distribution_namespace("third-party-pkg") is False
    assert packaging.valid_distribution_namespace("geo-infer") is False


def test_wheel_filename_namespace_validation(tmp_path, monkeypatch):
    packaging = load_packaging_module()
    assert packaging.wheel_filename_is_valid("geo_infer_space-0.2.0-py3-none-any.whl", "geo-infer-space")
    assert not packaging.wheel_filename_is_valid("malicious_pkg-0.2.0-py3-none-any.whl", "geo-infer-space")


def test_validate_module_accepts_conforming_package(tmp_path):
    packaging = load_packaging_module()
    module_dir = tmp_path / "GEO-INFER-SAMPLE"
    module_dir.mkdir()
    package_dir = module_dir / "src" / "geo_infer_sample"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("__version__ = '0.2.0'\n")
    _make_pyproject(module_dir)

    report = packaging.ContractReport()
    packaging.validate_module(module_dir, packaging.parse_pyproject(module_dir), report)
    assert report.errors == []


def test_validate_module_rejects_bad_namespace(tmp_path):
    packaging = load_packaging_module()
    module_dir = tmp_path / "GEO-INFER-SAMPLE"
    module_dir.mkdir()
    package_dir = module_dir / "src" / "geo_infer_sample"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("__version__ = '0.2.0'\n")
    pyproject = _make_pyproject(module_dir)
    pyproject.write_text(
        pyproject.read_text().replace('name = "geo-infer-sample"', 'name = "bad-package"'),
        encoding="utf-8",
    )

    report = packaging.ContractReport()
    packaging.validate_module(module_dir, packaging.parse_pyproject(module_dir), report)
    assert any("namespace" in e for e in report.errors)


def test_source_traversal_diagnostics_ignore_test_files(tmp_path):
    packaging = load_packaging_module()
    module_dir = tmp_path / "GEO-INFER-SAMPLE"
    module_dir.mkdir()
    pkg = module_dir / "src" / "geo_infer_sample"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("__version__ = '0.2.0'\n", encoding="utf-8")
    # A source file that climbs parent directories should be flagged; test files skipped.
    (pkg / "loader.py").write_text(
        "from pathlib import Path\nCONFIG = Path(__file__).parent.parent / 'config.yaml'\n",
        encoding="utf-8",
    )
    (pkg / "test_loader.py").write_text(
        "from pathlib import Path\nCONFIG = Path(__file__).parent.parent / 'config.yaml'\n",
        encoding="utf-8",
    )

    report = packaging.ContractReport()
    packaging.validate_source_traversal(module_dir, report)
    assert any("loader.py" in d for d in report.diagnostics)
    assert not any("test_loader.py" in d for d in report.diagnostics)


def test_validate_all_runs_on_live_monorepo():
    packaging = load_packaging_module()
    report = packaging.validate_all()
    # The live monorepo must already conform to the geo-infer-* namespace.
    assert report.errors == []