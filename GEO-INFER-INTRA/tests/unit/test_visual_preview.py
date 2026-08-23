"""Unit and contract tests for spatial visual preview helpers (DOCS-01)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from geo_infer_intra.core.documentation.visual_preview import (
    MODULE_PROFILES,
    SpatialPreviewArtifacts,
    generate_all_module_previews,
    generate_module_preview_suite,
    render_leaflet_html,
    render_png_card,
    render_svg_card,
)


@pytest.mark.unit
@pytest.mark.geospatial
class TestVisualPreviewContract:
    """Test suite verifying reproducible spatial widget preview cards."""

    def test_all_44_modules_registered(self) -> None:
        """Verify all 44 GEO-INFER modules are configured in the profile registry."""
        expected_modules = {
            "ACT", "AG", "AGENT", "AI", "ANT", "API", "APP", "ART",
            "BAYES", "BIO", "CIV", "CLIMATE", "COG", "COMMS", "DATA",
            "ECON", "EDU", "EMERGENCY", "ENERGY", "EXAMPLES", "FOREST",
            "GIT", "HEALTH", "INTRA", "IOT", "LOG", "MARINE", "MATH",
            "METAGOV", "NORMS", "OPS", "ORG", "PEP", "PLACE", "REQ",
            "RISK", "SEC", "SIM", "SPACE", "SPM", "TEST", "TIME",
            "TRANSPORT", "WATER",
        }
        assert set(MODULE_PROFILES.keys()) == expected_modules
        assert len(MODULE_PROFILES) == 44

    def test_module_profiles_have_valid_spatial_attributes(self) -> None:
        """Ensure each module profile defines valid coordinates, colors, and features."""
        for mod_id, profile in MODULE_PROFILES.items():
            assert "name" in profile
            assert "description" in profile
            assert "category" in profile
            assert "center" in profile
            lat, lng = profile["center"]
            assert -90.0 <= lat <= 90.0
            assert -180.0 <= lng <= 180.0
            assert "zoom" in profile
            assert 1 <= profile["zoom"] <= 20
            assert profile["primary_color"].startswith("#")
            assert len(profile["primary_color"]) == 7
            assert profile["secondary_color"].startswith("#")
            assert len(profile["secondary_color"]) == 7
            assert isinstance(profile["features"], list)
            assert len(profile["features"]) >= 3

    def test_render_leaflet_html_contract(self, tmp_path: Path) -> None:
        """Verify Leaflet HTML generation produces valid, self-contained HTML."""
        out_file = tmp_path / "test_act_map.html"
        html_str = render_leaflet_html("ACT", out_file)

        assert out_file.exists()
        assert out_file.read_text(encoding="utf-8") == html_str
        assert "<!doctype html>" in html_str.lower() or "<html" in html_str.lower()
        assert "GEO-INFER-ACT" in html_str
        assert "Active Inference Engine" in html_str
        assert len(html_str) > 500

    def test_render_svg_card_contract(self, tmp_path: Path) -> None:
        """Verify SVG card rendering produces valid vector XML with hex polygons."""
        out_file = tmp_path / "test_space_card.svg"
        svg_str = render_svg_card("SPACE", out_file)

        assert out_file.exists()
        assert out_file.read_text(encoding="utf-8") == svg_str
        assert svg_str.startswith("<svg")
        assert svg_str.endswith("</svg>")
        assert 'viewBox="0 0 700 380"' in svg_str
        assert "GEO-INFER-SPACE" in svg_str
        assert "<polygon" in svg_str
        assert "<circle" in svg_str

    def test_render_png_card_contract(self, tmp_path: Path) -> None:
        """Verify PNG rendering produces a valid PNG binary with PNG header and IEND."""
        out_file = tmp_path / "test_water_card.png"
        png_bytes = render_png_card("WATER", out_file)

        assert out_file.exists()
        assert out_file.read_bytes() == png_bytes
        # Standard PNG Magic Header: 89 50 4E 47 0D 0A 1A 0A
        assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")
        assert b"IHDR" in png_bytes
        assert b"IDAT" in png_bytes
        assert b"IEND" in png_bytes
        assert len(png_bytes) > 200

    def test_generate_module_preview_suite(self, tmp_path: Path) -> None:
        """Verify the full artifact bundle generation and receipt verification."""
        artifacts = generate_module_preview_suite("BIO", tmp_path)

        assert isinstance(artifacts, SpatialPreviewArtifacts)
        assert artifacts.module_id == "BIO"
        assert artifacts.html_path.exists()
        assert artifacts.svg_path.exists()
        assert artifacts.png_path.exists()
        assert artifacts.manifest_path.exists()

        manifest = json.loads(artifacts.manifest_path.read_text(encoding="utf-8"))
        assert manifest["schema_version"] == "geo-infer-intra-visual-preview/v1"
        assert manifest["module_id"] == "GEO-INFER-BIO"
        assert manifest["name"] == "Biological Systems"
        assert len(manifest["artifacts"]) == 3
        assert manifest["accessibility"]["has_title"] is True
        assert manifest["accessibility"]["has_svg_viewbox"] is True
        assert manifest["accessibility"]["has_png_metadata"] is True

    def test_unknown_module_raises(self, tmp_path: Path) -> None:
        """Verify unknown module identifiers raise ValueError."""
        with pytest.raises(ValueError, match="Unknown module ID"):
            render_leaflet_html("INVALID_MODULE", tmp_path / "fail.html")

        with pytest.raises(ValueError, match="Unknown module ID"):
            render_svg_card("INVALID_MODULE", tmp_path / "fail.svg")

        with pytest.raises(ValueError, match="Unknown module ID"):
            render_png_card("INVALID_MODULE", tmp_path / "fail.png")

    def test_generate_all_module_previews(self, tmp_path: Path) -> None:
        """Verify batch emission produces bundles for all 44 modules deterministically."""
        all_bundles = generate_all_module_previews(tmp_path)
        assert len(all_bundles) == 44
        for mod_id, bundle in all_bundles.items():
            assert bundle.module_id == mod_id
            assert bundle.html_path.exists()
            assert bundle.svg_path.exists()
            assert bundle.png_path.exists()
            assert bundle.manifest_path.exists()
            assert bundle.html_bytes > 0
            assert bundle.svg_bytes > 0
            assert bundle.png_bytes > 0
