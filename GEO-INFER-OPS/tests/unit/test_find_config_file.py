"""Explicit-config-path contract tests for find_config_file (GS19-78).

A provided-but-missing explicit path must raise FileNotFoundError instead of
being silently ignored in favour of the environment/default candidates.
"""

import pytest

from geo_infer_ops.utils.config import find_config_file


def test_missing_explicit_path_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="absent.yaml"):
        find_config_file(str(tmp_path / "absent.yaml"))


def test_existing_explicit_path_returned(tmp_path):
    config = tmp_path / "ops.yaml"
    config.write_text("environment: development\n", encoding="utf-8")
    assert find_config_file(str(config)) == str(config)


def test_missing_env_path_still_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("GEO_INFER_OPS_CONFIG", str(tmp_path / "absent.yaml"))
    with pytest.raises(FileNotFoundError):
        find_config_file()
