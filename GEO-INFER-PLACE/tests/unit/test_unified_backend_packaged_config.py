"""Regression tests: packaged Cascadia config resolution in unified_backend.

GS-023: installed wheels must resolve runtime configs via importlib.resources
from the geo_infer_place package tree — never via repo-relative parent climbs.
The only repo-checkout fallback is the explicit GEO_INFER_PLACE_CASCADIA_CONFIG
environment variable.
"""

from types import SimpleNamespace



def _backend_cls():
    from geo_infer_place.core.unified_backend import (
        CascadianAgriculturalH3Backend,
    )

    return CascadianAgriculturalH3Backend


def test_cascadia_config_resource_lives_in_package_tree() -> None:
    """The packaged resource resolves under the package, not the repo config/ dir."""
    import importlib.resources

    resource = importlib.resources.files("geo_infer_place").joinpath(
        "locations/cascadia/config/cascadia_config.yaml"
    )
    assert resource.is_file()


def test_cascadia_config_resolves_from_package_with_empty_cwd(
    tmp_path, monkeypatch
) -> None:
    """Default resolution works even when cwd is an empty directory."""
    monkeypatch.delenv("GEO_INFER_PLACE_CASCADIA_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)

    config = _backend_cls()._load_cascadia_config(SimpleNamespace())

    assert isinstance(config, dict) and config
    assert "analysis" in config


def test_cascadia_config_env_override_honored(tmp_path, monkeypatch) -> None:
    """The explicit env var override is the only repo-checkout path honored."""
    override = tmp_path / "override_cascadia_config.yaml"
    override.write_text("analysis:\n  h3_resolution: 6\n", encoding="utf-8")
    monkeypatch.setenv("GEO_INFER_PLACE_CASCADIA_CONFIG", str(override))
    monkeypatch.chdir(tmp_path)

    config = _backend_cls()._load_cascadia_config(SimpleNamespace())

    assert config["analysis"]["h3_resolution"] == 6


def test_county_geometries_resolve_from_package_with_empty_cwd(
    tmp_path, monkeypatch
) -> None:
    """County geometry loading reads packaged GeoJSON/YAML, not repo climbs."""
    monkeypatch.delenv("GEO_INFER_PLACE_CASCADIA_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)

    geometries = _backend_cls()._get_county_geometries(
        SimpleNamespace(), {"CA": ["Del Norte", "Lassen"]}
    )

    # The boundary loader keys counties as "<state>_<county>" (e.g. Del_Norte).
    assert set(geometries.get("CA", {})) >= {"Del_Norte", "Lassen"}
    for geometry in geometries["CA"].values():
        assert geometry is not None
