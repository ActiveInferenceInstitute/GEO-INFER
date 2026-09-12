"""Regression tests for the collapsed visual_preview import surface (GS-299)."""

from __future__ import annotations

import importlib

import pytest

EXPECTED_PREVIEW_SYMBOLS = (
    "MODULE_PROFILES",
    "SpatialPreviewArtifacts",
    "generate_all_module_previews",
    "generate_module_preview_suite",
    "render_leaflet_html",
    "render_png_card",
    "render_svg_card",
)


def test_utils_reexports_preview_symbols_from_core_documentation() -> None:
    """geo_infer_intra.utils exposes preview symbols without a shim module."""
    import geo_infer_intra.core.documentation.visual_preview as core_preview
    import geo_infer_intra.utils as utils_pkg

    for symbol in EXPECTED_PREVIEW_SYMBOLS:
        assert getattr(utils_pkg, symbol) is getattr(core_preview, symbol)
        assert symbol in utils_pkg.__all__


def test_package_level_preview_reexport_is_stable() -> None:
    """Top-level package still re-exports the six preview symbols."""
    import geo_infer_intra

    for symbol in EXPECTED_PREVIEW_SYMBOLS:
        assert hasattr(geo_infer_intra, symbol)


def test_utils_visual_preview_shim_is_gone() -> None:
    """The weightless utils.visual_preview shim must not be importable."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("geo_infer_intra.utils.visual_preview")
