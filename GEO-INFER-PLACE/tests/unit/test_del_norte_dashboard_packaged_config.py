"""Regression tests: packaged Del Norte resources (dashboard bounds + intel seed).

GS-023: the Del Norte dashboard and Crescent City intel mapper must resolve
their packaged configs/data via importlib.resources from the
``geo_infer_place`` package tree — never via repo-relative parent climbs. The
only repo-checkout fallbacks are the explicit GEO_INFER_PLACE_DEL_NORTE_CONFIG
and CRESCENT_INTEL_GEO_JSON environment variables.
"""

import importlib.resources
import shutil
from pathlib import Path


def _dashboard_cls():
    from geo_infer_place.locations.del_norte_county.dashboard import AdvancedDashboard

    return AdvancedDashboard


def _bounds_harness():
    """Minimal stand-in exposing only the bounds-loading surface."""
    cls = _dashboard_cls()

    class Harness:
        county_bounds = None
        county_center = None
        _load_location_config_bounds = cls._load_location_config_bounds
        _apply_location_bounds = cls._apply_location_bounds

    return Harness()


def _packaged_analysis_config() -> Path:
    return Path(
        str(
            importlib.resources.files(
                "geo_infer_place.locations.del_norte_county"
            ).joinpath("config/analysis_config.yaml")
        )
    )


def test_location_bounds_resolve_from_package_with_empty_cwd(
    tmp_path, monkeypatch
) -> None:
    """Default resolution works even when cwd is an empty directory."""
    monkeypatch.delenv("GEO_INFER_PLACE_DEL_NORTE_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)

    dummy = _bounds_harness()
    dummy._load_location_config_bounds()

    assert dummy.county_bounds is not None
    assert set(dummy.county_bounds) == {"north", "south", "east", "west"}
    assert dummy.county_center == [
        (dummy.county_bounds["north"] + dummy.county_bounds["south"]) / 2.0,
        (dummy.county_bounds["east"] + dummy.county_bounds["west"]) / 2.0,
    ]


def test_location_bounds_env_override_honored(tmp_path, monkeypatch) -> None:
    """The explicit env var override is the only repo-checkout path honored."""
    override = tmp_path / "analysis_config.yaml"
    override.write_text(
        "location:\n"
        "  bounds:\n"
        "    north: 43.0\n"
        "    south: 42.0\n"
        "    east: -122.0\n"
        "    west: -123.0\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GEO_INFER_PLACE_DEL_NORTE_CONFIG", str(override))
    monkeypatch.chdir(tmp_path)

    dummy = _bounds_harness()
    dummy._load_location_config_bounds()

    assert dummy.county_bounds["north"] == 43.0
    assert dummy.county_center == [42.5, -122.5]


def test_crescent_seed_resolves_from_package_with_empty_cwd(
    tmp_path, monkeypatch
) -> None:
    """The mapper loads the packaged seed even when cwd is an empty directory."""
    from geo_infer_place.locations.del_norte_county.crescent_city_intel import (
        CrescentCityIntelMapper,
    )

    monkeypatch.delenv("CRESCENT_INTEL_GEO_JSON", raising=False)
    monkeypatch.chdir(tmp_path)

    mapper = CrescentCityIntelMapper(seed_path=None)

    assert mapper.loaded is True
    packaged = Path(
        str(
            importlib.resources.files(
                "geo_infer_place.locations.del_norte_county"
            ).joinpath("data/crescent-city-geo-intel.json")
        )
    )
    assert mapper.source_path == packaged


def test_crescent_seed_env_override_honored(tmp_path, monkeypatch) -> None:
    """CRESCENT_INTEL_GEO_JSON remains the explicit override for the seed."""
    from geo_infer_place.locations.del_norte_county.crescent_city_intel import (
        CrescentCityIntelMapper,
    )

    packaged = Path(
        str(
            importlib.resources.files(
                "geo_infer_place.locations.del_norte_county"
            ).joinpath("data/crescent-city-geo-intel.json")
        )
    )
    override = tmp_path / "crescent-city-geo-intel-copy.json"
    shutil.copyfile(packaged, override)
    monkeypatch.setenv("CRESCENT_INTEL_GEO_JSON", str(override))
    monkeypatch.chdir(tmp_path)

    mapper = CrescentCityIntelMapper(seed_path=None)

    assert mapper.loaded is True
    assert mapper.source_path == override
