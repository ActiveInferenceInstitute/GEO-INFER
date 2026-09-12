"""Regression tests for packaged config resolution in LocationConfigLoader.

Guards GS-023: the default config directory must resolve from the installed
geo_infer_space package (importlib.resources), never from a repo-relative
parent climb of __file__.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path

import pytest
import yaml

from geo_infer_space.utils.config_loader import (
    CONFIG_DIR_ENV_VAR,
    LocationConfigLoader,
)


def test_default_config_dir_resolves_to_package_resource(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Default resolution finds the packaged config even from an empty cwd."""
    monkeypatch.delenv(CONFIG_DIR_ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)

    loader = LocationConfigLoader()

    expected = importlib.resources.files("geo_infer_space").joinpath("config")
    assert Path(loader.config_dir) == Path(str(expected))
    assert (Path(loader.config_dir) / "base.yaml").is_file()


def test_default_config_loads_packaged_base_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The packaged base.yaml merges without changing the in-code defaults."""
    monkeypatch.delenv(CONFIG_DIR_ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)

    config = LocationConfigLoader().load_location_config("nonexistent_location")

    packaged_base = yaml.safe_load(
        (
            importlib.resources.files("geo_infer_space")
            .joinpath("config")
            .joinpath("base.yaml")
            .read_text()
        )
    )
    assert config["spatial"] == packaged_base["spatial"]
    assert config["temporal"] == packaged_base["temporal"]
    assert (
        config["location"]["coordinate_systems"]
        == packaged_base["location"]["coordinate_systems"]
    )


def test_env_var_override_honored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GEO_INFER_SPACE_CONFIG points the loader at an explicit config dir."""
    override_dir = tmp_path / "custom_config"
    override_dir.mkdir()
    (override_dir / "base.yaml").write_text(
        yaml.safe_dump({"spatial": {"h3_resolution": 5}})
    )

    monkeypatch.setenv(CONFIG_DIR_ENV_VAR, str(override_dir))
    monkeypatch.chdir(tmp_path)

    loader = LocationConfigLoader()
    assert loader.config_dir == override_dir

    config = loader.load_location_config("nonexistent_location")
    assert config["spatial"]["h3_resolution"] == 5
