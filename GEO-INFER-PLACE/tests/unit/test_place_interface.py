"""Unit tests for PlaceInterface and create_analyzer factory."""
import pytest
from pathlib import Path
from typing import Any

from geo_infer_place.core.place_interface import PlaceInterface, LOCATION_PRESETS
from geo_infer_place import create_analyzer, get_supported_locations


# ---------------------------------------------------------------------------
# PlaceInterface initialisation
# ---------------------------------------------------------------------------

class TestPlaceInterfaceInit:
    def test_valid_location_del_norte(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        assert pi.location == "del_norte"

    def test_valid_location_cascadia(self, temp_output_dir):
        pi = PlaceInterface("cascadia", output_dir=str(temp_output_dir))
        assert pi.location == "cascadia"

    def test_unknown_location_raises(self, temp_output_dir):
        with pytest.raises(ValueError, match="Unknown location"):
            PlaceInterface("atlantis", output_dir=str(temp_output_dir))

    def test_output_dir_created(self, tmp_path):
        new_dir = tmp_path / "new_output"
        assert not new_dir.exists()
        PlaceInterface("del_norte", output_dir=str(new_dir))
        assert new_dir.exists()

    def test_location_name_set(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        assert "Del Norte" in pi.location_name

    def test_custom_config_applied(self, temp_output_dir, minimal_config):
        pi = PlaceInterface("del_norte", config=minimal_config, output_dir=str(temp_output_dir))
        assert pi.config is minimal_config


# ---------------------------------------------------------------------------
# Component accessors (lazy init)
# ---------------------------------------------------------------------------

class TestPlaceInterfaceComponents:
    def test_integrator_lazy_init(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        assert pi._integrator is None
        integrator = pi.integrator
        assert integrator is not None
        # Second call returns cached
        assert pi.integrator is integrator

    def test_data_manager_lazy_init(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        assert pi._data_manager is None
        dm = pi.data_manager
        assert dm is not None
        assert pi.data_manager is dm

    def test_temporal_lazy_init(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        assert pi._temporal is None
        ta = pi.temporal
        assert ta is not None
        assert pi.temporal is ta

    def test_get_analyzer_forest_health(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        analyzer = pi.get_analyzer("forest_health")
        assert analyzer is not None

    def test_get_analyzer_coastal_resilience(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        analyzer = pi.get_analyzer("coastal_resilience")
        assert analyzer is not None

    def test_get_analyzer_fire_risk(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        analyzer = pi.get_analyzer("fire_risk")
        assert analyzer is not None

    def test_get_analyzer_seismic_hazard(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        analyzer = pi.get_analyzer("seismic_hazard")
        assert analyzer is not None

    def test_get_analyzer_unknown_returns_none(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        result = pi.get_analyzer("nonexistent_analyzer")
        assert result is None

    def test_get_analyzer_cached_on_second_call(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        a1 = pi.get_analyzer("seismic_hazard")
        a2 = pi.get_analyzer("seismic_hazard")
        assert a1 is a2


# ---------------------------------------------------------------------------
# Full analysis pipeline
# ---------------------------------------------------------------------------

class TestPlaceInterfaceRunAnalysis:
    def test_returns_dict_with_required_keys(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        results = pi.run_full_analysis(analyzers=["seismic_hazard"], include_temporal=False)
        assert isinstance(results, dict)
        for key in ("location", "timestamp", "config", "analyses", "temporal_analysis",
                    "data_quality", "provenance"):
            assert key in results, f"Missing key: {key}"

    def test_analyses_dict_has_requested_analyzer(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        results = pi.run_full_analysis(analyzers=["seismic_hazard"], include_temporal=False)
        assert "seismic_hazard" in results["analyses"]

    def test_subset_analyzers(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        results = pi.run_full_analysis(
            analyzers=["seismic_hazard", "fire_risk"],
            include_temporal=False,
        )
        assert "seismic_hazard" in results["analyses"]
        assert "fire_risk" in results["analyses"]
        assert "forest_health" not in results["analyses"]

    def test_saves_json_output_file(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        pi.run_full_analysis(analyzers=["seismic_hazard"], include_temporal=False)
        json_files = list(temp_output_dir.glob("*.json"))
        assert len(json_files) >= 1

    def test_analyzer_failure_does_not_crash_pipeline(self, temp_output_dir, monkeypatch):
        """If one analyzer raises, pipeline continues and records error."""
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))

        def _bad_create(name):
            if name == "seismic_hazard":
                raise RuntimeError("injected failure")
            return pi._create_analyzer.__wrapped__(pi, name) if hasattr(
                pi._create_analyzer, "__wrapped__"
            ) else None

        monkeypatch.setattr(pi, "_create_analyzer", _bad_create)
        results = pi.run_full_analysis(
            analyzers=["seismic_hazard"], include_temporal=False
        )
        analysis = results["analyses"].get("seismic_hazard", {})
        assert "error" in analysis or analysis.get("success") is False or analysis.get("skipped")


# ---------------------------------------------------------------------------
# Convenience methods
# ---------------------------------------------------------------------------

class TestPlaceInterfaceConvenience:
    def test_status_keys(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        s = pi.status()
        for key in ("location", "location_name", "output_dir", "available_analyzers"):
            assert key in s, f"Missing key: {key}"

    def test_status_location_correct(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        assert pi.status()["location"] == "del_norte"

    def test_get_earthquakes_returns_dict(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        result = pi.get_earthquakes()
        assert isinstance(result, dict)

    def test_get_fire_perimeters_returns_dict(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        result = pi.get_fire_perimeters()
        assert isinstance(result, dict)

    def test_get_weather_returns_dict(self, temp_output_dir):
        pi = PlaceInterface("del_norte", output_dir=str(temp_output_dir))
        result = pi.get_weather()
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# create_analyzer factory
# ---------------------------------------------------------------------------

class TestCreateAnalyzerFactory:
    def test_del_norte_returns_place_interface(self, temp_output_dir):
        # Factory is module-level, uses default output dir
        pi = create_analyzer("del_norte")
        assert isinstance(pi, PlaceInterface)

    def test_cascadia_returns_place_interface(self):
        pi = create_analyzer("cascadia")
        assert isinstance(pi, PlaceInterface)

    def test_unknown_raises_value_error(self):
        with pytest.raises(ValueError, match="not supported"):
            create_analyzer("atlantis")

    def test_does_not_raise_import_error(self):
        """Should never raise ImportError regardless of optional deps."""
        try:
            create_analyzer("del_norte")
        except ImportError as exc:
            pytest.fail(f"create_analyzer raised ImportError: {exc}")

    def test_get_supported_locations_returns_list(self):
        locations = get_supported_locations()
        assert isinstance(locations, list)
        assert "del_norte" in locations
        assert "cascadia" in locations

    def test_get_supported_locations_no_county_suffix(self):
        """Keys must not include '_county' suffix."""
        locations = get_supported_locations()
        assert "del_norte_county" not in locations
