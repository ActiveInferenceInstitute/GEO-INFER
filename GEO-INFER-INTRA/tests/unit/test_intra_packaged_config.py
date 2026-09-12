"""Regression tests for packaged default-config resolution.

Ensures ``get_default_config_path`` resolves the example config from the
installed ``geo_infer_intra`` package via ``importlib.resources`` (no
parent-climbing ``Path(__file__)`` lookups) and honors the explicit
``GEO_INFER_INTRA_CONFIG`` override.
"""

from pathlib import Path

import pytest

from geo_infer_intra.utils import config


class TestPackagedDefaultConfig:
    """Tests for packaged default config resolution."""

    def test_default_resolution_uses_packaged_resource(self, tmp_path, monkeypatch):
        """Default resolution finds a packaged config with cwd set to an empty dir."""
        monkeypatch.chdir(tmp_path)
        # Neutralize any user/home and explicit overrides so only the packaged
        # resource can satisfy the lookup.
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("GEO_INFER_INTRA_CONFIG", raising=False)

        resolved = config.get_default_config_path()

        assert Path(resolved).is_file()
        assert Path(resolved).name == "example.yaml"
        # Must come from inside the package tree, not a repo-relative config/ dir.
        assert "geo_infer_intra" in Path(resolved).parts
        assert Path(resolved).parent.name == "config"

    def test_env_var_override_honored(self, tmp_path, monkeypatch):
        """An explicitly set GEO_INFER_INTRA_CONFIG wins over the packaged default."""
        override = tmp_path / "custom.yaml"
        override.write_text("general:\n  log_level: DEBUG\n")
        monkeypatch.setenv("GEO_INFER_INTRA_CONFIG", str(override))

        resolved = config.get_default_config_path()

        assert Path(resolved) == override

    def test_env_var_override_missing_file_raises(self, tmp_path, monkeypatch):
        """A set-but-invalid GEO_INFER_INTRA_CONFIG errors instead of silently falling back."""
        monkeypatch.setenv("GEO_INFER_INTRA_CONFIG", str(tmp_path / "missing.yaml"))

        with pytest.raises(FileNotFoundError):
            config.get_default_config_path()
