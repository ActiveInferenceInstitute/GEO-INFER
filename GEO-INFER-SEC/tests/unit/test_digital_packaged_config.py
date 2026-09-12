"""Packaged threat-indicator resource resolution for DigitalSecurityManager.

Guards against regressions to parent-climbing ``Path(__file__)`` lookups:
default resolution must come from the installed ``geo_infer_sec`` package
(even with cwd pointing nowhere useful), and the only filesystem override is
the explicit ``GEO_INFER_SEC_THREAT_INDICATORS`` environment variable.
"""

import importlib.resources
from pathlib import Path

from geo_infer_sec.core.digital_security import DigitalSecurityManager

PACKAGED_RESOURCE = "config/threat_indicators.yaml"


def _fresh_manager() -> DigitalSecurityManager:
    return DigitalSecurityManager()


def test_default_resolves_packaged_resource_from_empty_cwd(tmp_path, monkeypatch):
    """Default indicator loading works with an empty cwd (no repo fallback)."""
    monkeypatch.chdir(tmp_path)
    assert not list(tmp_path.iterdir())  # cwd is truly empty

    resource = importlib.resources.files("geo_infer_sec").joinpath(
        *PACKAGED_RESOURCE.split("/")
    )
    assert resource.is_file(), f"packaged resource missing: {resource}"

    manager = _fresh_manager()
    assert "suspicious-domain.example" in manager.threat_indicators
    assert manager.blocked_ips == set()
    assert manager.trusted_ips == set()


def test_env_var_override_honored(tmp_path, monkeypatch):
    """GEO_INFER_SEC_THREAT_INDICATORS points resolution at an explicit file."""
    override = tmp_path / "custom_indicators.yaml"
    override.write_text(
        "blocked_ips:\n  - 203.0.113.77\n"
        "threat_indicators:\n  - env-override-indicator.example\n"
        "trusted_ips:\n  - 198.51.100.42\n"
    )
    monkeypatch.chdir(tmp_path.parent)  # cwd must not matter
    monkeypatch.setenv("GEO_INFER_SEC_THREAT_INDICATORS", str(override))

    manager = _fresh_manager()
    assert "203.0.113.77" in manager.blocked_ips
    assert "env-override-indicator.example" in manager.threat_indicators
    assert "198.51.100.42" in manager.trusted_ips
    # Packaged defaults must not leak through when the override is set.
    assert "suspicious-domain.example" not in manager.threat_indicators
    assert Path(str(override)) == override


def test_missing_override_file_starts_empty(tmp_path, monkeypatch):
    """A nonexistent override file logs a warning and starts empty (no silent packaged fallback)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEO_INFER_SEC_THREAT_INDICATORS", str(tmp_path / "nope.yaml"))

    manager = _fresh_manager()
    assert manager.threat_indicators == set()
    assert manager.blocked_ips == set()
    assert manager.trusted_ips == set()
