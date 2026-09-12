"""
Packaged-resource resolution tests for GEO-INFER-OPS.

Ensures default config and Kubernetes manifest resolution works from an
installed package (no repo-relative parent climbs) and that explicit env-var
overrides are honored.
"""

import importlib.resources
from pathlib import Path

import pytest

from geo_infer_ops.core.deployment import DeploymentManager
from geo_infer_ops.utils.config import find_config_file, load_config

PACKAGE_DIR = Path(str(importlib.resources.files("geo_infer_ops")))


def test_default_config_resolves_from_package(tmp_path, monkeypatch):
    """Default config resolution works with an empty cwd (no repo fallback)."""
    monkeypatch.chdir(tmp_path)
    resolved = Path(find_config_file())
    assert resolved.is_file()
    assert resolved == PACKAGE_DIR / "config" / "local.yaml"


def test_load_config_works_from_empty_cwd(tmp_path, monkeypatch):
    """load_config resolves and parses the packaged config from empty cwd."""
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert isinstance(config, dict)
    assert config


def test_config_env_var_override_honored(tmp_path, monkeypatch):
    """GEO_INFER_OPS_CONFIG override wins over the packaged default."""
    override = tmp_path / "custom.yaml"
    override.write_text("logging:\n  level: DEBUG\n")
    monkeypatch.setenv("GEO_INFER_OPS_CONFIG", str(override))
    assert find_config_file() == str(override)


def test_config_env_var_missing_raises(tmp_path, monkeypatch):
    """A set-but-missing GEO_INFER_OPS_CONFIG raises instead of silently falling back."""
    monkeypatch.setenv("GEO_INFER_OPS_CONFIG", str(tmp_path / "missing.yaml"))
    with pytest.raises(FileNotFoundError):
        find_config_file()


def test_default_kube_manifests_resolve_from_package(tmp_path, monkeypatch):
    """Default manifest dir resolves under the installed package, not the repo."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEO_INFER_OPS_KUBE_MANIFESTS", raising=False)
    resolved = Path(DeploymentManager._default_manifest_dir())
    assert resolved == PACKAGE_DIR / "deployment" / "kubernetes"
    assert resolved.is_dir()
    assert (resolved / "deployment.yaml").is_file()


def test_kube_manifest_env_var_override(tmp_path, monkeypatch):
    """GEO_INFER_OPS_KUBE_MANIFESTS drives which manifests get applied."""
    manifest_dir = tmp_path / "kube"
    manifest_dir.mkdir()
    (manifest_dir / "custom.yml").write_text(
        "kind: ConfigMap\nmetadata:\n  name: custom\n"
    )
    monkeypatch.setenv("GEO_INFER_OPS_KUBE_MANIFESTS", str(manifest_dir))
    monkeypatch.chdir(tmp_path)

    applied = []
    manager = DeploymentManager()
    monkeypatch.setattr(
        manager, "_apply_configmap", lambda manifest: applied.append(manifest)
    )

    assert manager.deploy_kubernetes() is True
    assert applied == [{"kind": "ConfigMap", "metadata": {"name": "custom"}}]