"""Regression tests for the geo_infer_ant package __init__ surface (GS-268, GS-269)."""

import json

import geo_infer_ant
from geo_infer_ant.utils.integration import IntegrationManager


def test_setup_ant_module_returns_configured_integration_manager(tmp_path):
    config_path = tmp_path / "ant_config.json"
    config_path.write_text(
        json.dumps(
            {
                "simulation": {"name": "test", "description": "test", "version": "1.0.0"},
                "agents": {},
                "environment": {},
                "integrations": {"geo_infer_space": {"enabled": True}},
            }
        )
    )
    config = geo_infer_ant.setup_ant_module(str(config_path))

    manager = config["integration_manager"]
    assert isinstance(manager, IntegrationManager)
    assert manager.is_enabled("geo_infer_space") is True
    assert manager.is_enabled("geo_infer_act") is False


def test_setup_ant_module_defaults_expose_disabled_manager():
    """With no config file the returned manager reports integrations disabled."""
    config = geo_infer_ant.setup_ant_module()

    assert isinstance(config["integration_manager"], IntegrationManager)
    assert config["integration_manager"].is_enabled("anything") is False


def test_setup_ant_module_invalid_config_falls_back_to_defaults(tmp_path):
    """A bad config file logs the failure and still returns a usable manager."""
    bad = tmp_path / "broken.json"
    bad.write_text("{not json")

    config = geo_infer_ant.setup_ant_module(str(bad))

    assert isinstance(config["integration_manager"], IntegrationManager)
    assert config["integration_manager"].is_enabled("anything") is False


def test_get_available_components_covers_full_export_surface():
    """Every __all__ export (minus metadata) appears in the components report, and vice versa."""
    metadata = {"__version__", "__author__", "__description__"}

    reported = set()
    for names in geo_infer_ant.get_available_components().values():
        reported.update(names)

    expected = {name for name in geo_infer_ant.__all__ if name not in metadata}

    assert reported == expected
    assert reported  # sanity: the surface is non-empty


def test_get_available_components_groups_match_defining_subpackages():
    """Derived grouping follows each export's defining subpackage."""
    components = geo_infer_ant.get_available_components()

    assert "SwarmAgent" in components["core"]
    assert "AntColonyOptimization" in components["algorithms"]
    assert "EnvironmentalMonitoringSwarm" in components["applications"]
    assert "SwarmPatternAnalyzer" in components["analysis"]
    assert "load_config" in components["utils"]
    assert set(components) == {"core", "algorithms", "applications", "analysis", "utils"}