"""
Regression tests for packaged default-config resolution.

The default configuration must resolve from the ``geo_infer_health`` package
tree via ``importlib.resources`` — not from parent-climbing relative to the
module file. An explicit ``GEO_INFER_HEALTH_CONFIG`` environment variable
remains the first-priority override.
"""

import pytest

from geo_infer_health.utils.config import get_default_config_path


@pytest.fixture(autouse=True)
def _clear_default_path_cache():
    """get_default_config_path is lru_cached; clear around each test."""
    get_default_config_path.cache_clear()
    yield
    get_default_config_path.cache_clear()


class TestDefaultConfigPathPackaging:
    """Default config path must come from the package, not the repo tree."""

    def test_default_resolves_to_packaged_resource_from_empty_cwd(
        self, tmp_path, monkeypatch
    ):
        """With an empty cwd and no env override, the packaged resource wins."""
        monkeypatch.delenv("GEO_INFER_HEALTH_CONFIG", raising=False)
        monkeypatch.chdir(tmp_path)

        path = get_default_config_path()

        assert path.is_file()
        assert path.name == "health_config.yaml"
        # Resolved inside the installed package tree, not relative to cwd.
        assert tmp_path not in path.parents
        assert "geo_infer_health" in path.parts

    def test_env_var_override_is_honored_first(self, tmp_path, monkeypatch):
        """An explicit existing GEO_INFER_HEALTH_CONFIG path takes priority."""
        override = tmp_path / "custom_health_config.yaml"
        override.write_text("module:\n  name: custom-override\n")
        monkeypatch.setenv("GEO_INFER_HEALTH_CONFIG", str(override))
        monkeypatch.chdir(tmp_path)

        path = get_default_config_path()

        assert path == override

    def test_env_var_pointing_at_missing_file_falls_back_to_package(
        self, tmp_path, monkeypatch
    ):
        """An env override that does not exist must not break packaged fallback."""
        monkeypatch.setenv(
            "GEO_INFER_HEALTH_CONFIG", str(tmp_path / "missing_config.yaml")
        )
        monkeypatch.chdir(tmp_path)

        path = get_default_config_path()

        assert path.is_file()
        assert path.name == "health_config.yaml"
        assert "geo_infer_health" in path.parts