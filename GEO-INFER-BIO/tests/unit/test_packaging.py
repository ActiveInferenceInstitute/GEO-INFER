"""Packaging smoke tests for GEO-INFER-BIO subpackage completeness."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

import geo_infer_bio


def src_root() -> Path:
    assert geo_infer_bio.__file__ is not None
    return Path(geo_infer_bio.__file__).resolve().parent


SUBPACKAGES = ("api", "core", "utils")

# The file-existence and find_packages checks walk the source tree under
# src/geo_infer_bio; against a wheel-installed copy there is no such tree,
# so skip rather than fail confusingly.
_SOURCE_LAYOUT = (src_root().parent / "geo_infer_bio").is_dir()
_needs_source_layout = pytest.mark.skipif(
    not _SOURCE_LAYOUT,
    reason="packaging checks walk the source tree; run from a source checkout",
)


@_needs_source_layout
def test_subpackage_dirs_declare_regular_packages() -> None:
    """Every subpackage directory with modules must ship an __init__.py.

    find_packages() only includes directories with __init__.py, so a wheel
    build silently drops any subpackage missing one (SCOPE GS-201).
    """
    for name in SUBPACKAGES:
        pkg_dir = src_root() / name
        assert pkg_dir.is_dir(), f"missing subpackage directory: {name}"
        assert (pkg_dir / "__init__.py").is_file(), (
            f"{name}/ lacks __init__.py; wheel install would drop the subpackage"
        )


def test_subpackages_importable_and_expose_public_api() -> None:
    for name, expected in (
        ("api", {"graphql_app", "rest_app"}),
        ("core", {"SequenceAnalyzer"}),
        ("utils", {"DataValidator", "BioVisualizer"}),
    ):
        module = importlib.import_module(f"geo_infer_bio.{name}")
        for symbol in expected:
            assert hasattr(module, symbol), (
                f"geo_infer_bio.{name} does not re-export {symbol}"
            )
        assert set(getattr(module, "__all__", [])) == expected


@_needs_source_layout
def test_find_packages_selects_all_subpackages() -> None:
    """setuptools.find_packages (the wheel's package selection) must pick up
    every subpackage; this also catches pyproject regressions such as an
    explicit [tool.setuptools] packages list that forgets a subpackage."""
    from setuptools import find_packages

    found = set(find_packages(where=str(src_root().parent)))
    for name in SUBPACKAGES:
        assert f"geo_infer_bio.{name}" in found, (
            f"find_packages(where='src') misses geo_infer_bio.{name}; "
            "the built wheel would drop it"
        )
