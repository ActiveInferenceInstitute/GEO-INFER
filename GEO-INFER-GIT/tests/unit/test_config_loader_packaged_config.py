"""Regression tests: packaged config resolution for GEO-INFER-GIT.

Default ConfigLoader resolution must come from importlib.resources inside the
installed ``geo_infer_git`` package — never from repo-relative parent climbs —
with an explicit ``GEO_INFER_GIT_CONFIG`` env-var override honored when set.
"""

import importlib.resources
from pathlib import Path

import pytest

from geo_infer_git.utils.config_loader import (
    CloneConfig,
    ConfigLoader,
    load_clone_config,
)


def test_packaged_default_resolves_from_empty_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Default resolution must find packaged YAML even with an empty cwd."""
    monkeypatch.delenv("GEO_INFER_GIT_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)  # empty directory: no repo fallback available

    loader = ConfigLoader()
    assert loader.config_dir is not None

    packaged_config_dir = importlib.resources.files("geo_infer_git") / "config"
    assert loader.config_dir == packaged_config_dir

    # example.yaml and both target lists resolve from the package tree;
    # truthy content proves the packaged files are really there (a missing
    # file would silently fall back to [] / default CloneConfig)
    example = loader.load_yaml_config("example.yaml")
    assert "api" in example

    target_repos = loader.load_target_repos_config()
    assert len(target_repos) == 20

    target_users = loader.load_target_users_config()
    assert len(target_users) == 23
    assert isinstance(target_users, list)

    # Convenience constructor follows the same packaged default
    clone_config = load_clone_config()
    assert isinstance(clone_config, CloneConfig)


def test_env_var_override_honored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Explicit GEO_INFER_GIT_CONFIG env var overrides the packaged default."""
    override_dir = tmp_path / "checkout-config"
    override_dir.mkdir()
    (override_dir / "example.yaml").write_text(
        "general:\n"
        "  output_dir: /tmp/override-output\n"
        "github:\n"
        "  api_url: https://override.example.invalid\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GEO_INFER_GIT_CONFIG", str(override_dir))
    monkeypatch.chdir(tmp_path)

    loader = ConfigLoader()
    assert loader.config_dir == override_dir

    clone_config = loader.load_clone_config()
    assert clone_config.output_dir == "/tmp/override-output"
    assert clone_config.github_api_url == "https://override.example.invalid"
