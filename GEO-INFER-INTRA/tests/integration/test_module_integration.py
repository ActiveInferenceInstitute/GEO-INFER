"""Integration tests exercising real cross-module public APIs.

These tests import the installed sibling packages (geo_infer_space,
geo_infer_data) and INTRA's own public API, verifying that documented
cross-module usage actually works end to end.
"""

import json
from pathlib import Path

import pytest

import geo_infer_intra
from geo_infer_intra import MODULE_PROFILES, render_svg_card
from geo_infer_intra.utils.config import (
    get_config_value,
    get_schema_path,
    load_config,
    load_default_config,
    validate_config,
)
from geo_infer_intra.utils.geospatial_utils import (
    create_feature,
    create_point,
    is_valid_geojson,
)
from geo_infer_intra.utils.module_discovery import collect_test_modules

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.integration
class TestCrossModuleIntegration:
    """Integration of INTRA with real sibling-module public APIs."""

    def test_module_discovery_finds_sibling_modules(self):
        """collect_test_modules discovers real GEO-INFER sibling modules."""
        modules = collect_test_modules(REPO_ROOT)
        assert len(modules) > 0
        for required in ("geo_infer_space", "geo_infer_data", "geo_infer_intra"):
            assert required in modules, f"Module {required} not found"

    def test_profile_registry_matches_discovered_modules(self):
        """The 45-module preview registry is consistent with the repo layout."""
        modules = collect_test_modules(REPO_ROOT)
        for module_dir in modules.values():
            slug = module_dir.name.replace("GEO-INFER-", "")
            assert slug in MODULE_PROFILES, f"{slug} missing from MODULE_PROFILES"

    def test_space_h3_backend_public_api(self):
        """GEO-INFER-SPACE H3 backend converts coordinates to H3 cells."""
        from geo_infer_space.backends.h3.h3_backend import H3Backend

        backend = H3Backend()
        assert backend.is_available()
        cell = backend.latlng_to_cell(37.7749, -122.4194, 8)
        assert isinstance(cell, str) and len(cell) > 0
        lat, lng = backend.cell_to_latlng(cell)
        assert abs(lat - 37.7749) < 0.5
        assert abs(lng - (-122.4194)) < 0.5

    def test_data_file_connector_lists_written_geojson(self, tmp_path):
        """GEO-INFER-DATA FileConnector discovers a GeoJSON file INTRA built."""
        from geo_infer_data.connectors.file import FileConnector

        feature = create_feature(create_point(-122.4194, 37.7749), {"name": "sf"})
        assert is_valid_geojson(feature)

        geojson_path = tmp_path / "point.geojson"
        geojson_path.write_text(
            json.dumps({"type": "FeatureCollection", "features": [feature]})
        )
        connector = FileConnector(base_path=str(tmp_path))
        found = {p.name for p in connector.list_files(pattern="*.geojson")}
        assert "point.geojson" in found

    def test_config_schema_available_in_installed_layout(self):
        """validate_config resolves the packaged schema (importlib.resources)."""
        schema_path = get_schema_path()
        assert schema_path.is_file()

        is_valid, errors = validate_config(load_default_config())
        assert is_valid, errors

    def test_config_used_with_sibling_module_config(self, tmp_path):
        """INTRA config utilities load and query a sibling-module style config."""
        config_file = tmp_path / "space_config.yaml"
        config_file.write_text(
            "module: geo_infer_space\n"
            "spatial_index: H3\n"
            "coordinate_systems: [WGS84, EPSG:3857]\n"
        )
        cfg = load_config(config_file)
        assert get_config_value(cfg, "spatial_index") == "H3"
        # Missing key with an explicit None default is distinguishable.
        assert get_config_value(cfg, "nonexistent.key", default=None) is None

    def test_preview_rendering_for_all_registered_modules(self):
        """Every registered module renders a deterministic SVG preview card."""
        for module_id in sorted(MODULE_PROFILES):
            svg = render_svg_card(module_id)
            assert f"GEO-INFER-{module_id}" in svg

    def test_package_metadata_consistent(self):
        """Package metadata stays aligned with the module directory name."""
        assert geo_infer_intra.__version__
        assert (REPO_ROOT / "GEO-INFER-INTRA").is_dir()
