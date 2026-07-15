"""Regression tests for the default RISK configuration contract."""

from geo_infer_risk.utils.config_loader import load_config_with_defaults


def test_default_config_validates_against_schema() -> None:
    config = load_config_with_defaults()

    assert config["hazards"]["hurricane"]["type"] == "tropical_cyclone"
    assert config["vulnerability"]["population"]["classification_scheme"] == "custom"
    assert config["exposure"]["infrastructure"]["value_type"] == "replacement_cost"
