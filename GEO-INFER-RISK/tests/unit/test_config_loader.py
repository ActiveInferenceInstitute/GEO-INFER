"""Regression and behavioral tests for the RISK configuration loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from geo_infer_risk.utils.config_loader import (
    ConfigurationLoader,
    load_config,
    load_config_with_defaults,
)


def test_default_config_validates_against_schema() -> None:
    config = load_config_with_defaults()

    assert config["hazards"]["hurricane"]["type"] == "tropical_cyclone"
    assert config["vulnerability"]["population"]["classification_scheme"] == "custom"
    assert config["exposure"]["infrastructure"]["value_type"] == "replacement_cost"


def test_default_config_has_all_sections() -> None:
    config = load_config_with_defaults()
    for section in ("general", "risk_model", "hazards", "vulnerability", "exposure"):
        assert section in config
        assert isinstance(config[section], dict)


def test_default_config_has_common_hazards() -> None:
    config = load_config_with_defaults()
    hazards = config["hazards"]
    for hazard in ("flood", "earthquake", "hurricane", "wildfire"):
        assert hazard in hazards, f"missing hazard: {hazard}"


def test_load_config_from_missing_path_raises() -> None:
    missing = Path("/nonexistent/geo_infer_config.yaml")
    with pytest.raises(FileNotFoundError):
        load_config(str(missing))


def test_load_config_from_file_unvalidated(tmp_path: Path) -> None:
    config_file = tmp_path / "risk_config.yaml"
    config_file.write_text(
        "general:\n  name: test\n"
        "hazards:\n  flood:\n    type: riverine\n    return_periods: [10, 50]\n",
        encoding="utf-8",
    )
    config = load_config(str(config_file), validate=False)
    assert config["hazards"]["flood"]["type"] == "riverine"
    assert config["hazards"]["flood"]["return_periods"] == [10, 50]


def test_load_config_accepts_dict_input() -> None:
    config = load_config(
        {"general": {"name": "test"}, "hazards": {"flood": {"type": "riverine"}}},
        validate=False,
    )
    assert config["hazards"]["flood"]["type"] == "riverine"


def test_load_config_returns_dict() -> None:
    config = load_config_with_defaults()
    assert isinstance(config, dict)


def test_config_loader_instance(tmp_path: Path) -> None:
    loader = ConfigurationLoader()
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"general": {"name": "json-test"}, "risk_model": {"class": "test"}}',
        encoding="utf-8",
    )
    config = loader.load_config(str(config_file), validate=False)
    assert config["general"]["name"] == "json-test"
    assert config["risk_model"]["class"] == "test"
