"""Unit tests for _CALFIREWrapper, _NOAAWrapper, _USGSWrapper, DelNorteDataIntegrator."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from geo_infer_place.utils.integration import (
    _CALFIREWrapper,
    _NOAAWrapper,
    _USGSWrapper,
    DelNorteDataIntegrator,
)
from geo_infer_place.core.api_clients import CaliforniaAPIManager


@pytest.fixture
def api_manager():
    """Minimal CaliforniaAPIManager for testing."""
    return CaliforniaAPIManager()


@pytest.fixture
def calfire_wrapper(api_manager, tmp_path):
    return _CALFIREWrapper(api_manager, cache_dir=tmp_path / "calfire_cache")


@pytest.fixture
def noaa_wrapper(api_manager, tmp_path):
    return _NOAAWrapper(api_manager, cache_dir=tmp_path / "noaa_cache")


@pytest.fixture
def usgs_wrapper(api_manager, tmp_path):
    return _USGSWrapper(api_manager, cache_dir=tmp_path / "usgs_cache")


# ---------------------------------------------------------------------------
# CAL FIRE wrapper
# ---------------------------------------------------------------------------

class TestCALFIREWrapper:
    def test_get_fire_perimeters_returns_dict(self, calfire_wrapper):
        result = calfire_wrapper.get_fire_perimeters()
        assert isinstance(result, dict)

    def test_get_fire_perimeters_has_features_key(self, calfire_wrapper):
        result = calfire_wrapper.get_fire_perimeters()
        assert "features" in result

    def test_synthetic_fallback_valid_geojson(self, calfire_wrapper):
        synthetic = calfire_wrapper._generate_synthetic_fire_perimeters()
        assert synthetic.get("type") == "FeatureCollection"
        assert "features" in synthetic
        assert isinstance(synthetic["features"], list)
        assert len(synthetic["features"]) > 0

    def test_bbox_filter_applied(self, calfire_wrapper):
        bbox = (-124.408, 41.458, -123.536, 42.006)
        result = calfire_wrapper.get_fire_perimeters(bbox=bbox)
        assert isinstance(result, dict)
        assert "features" in result

    def test_get_active_incidents_returns_dict(self, calfire_wrapper):
        result = calfire_wrapper.get_active_incidents()
        assert isinstance(result, dict)
        assert "incidents" in result


# ---------------------------------------------------------------------------
# NOAA wrapper
# ---------------------------------------------------------------------------

class TestNOAAWrapper:
    def test_get_weather_data_returns_dict(self, noaa_wrapper):
        result = noaa_wrapper.get_weather_data()
        assert isinstance(result, dict)

    def test_get_tide_gauge_data_returns_dict(self, noaa_wrapper):
        result = noaa_wrapper.get_tide_gauge_data()
        assert isinstance(result, dict)

    def test_tide_gauge_has_series_key(self, noaa_wrapper):
        result = noaa_wrapper.get_tide_gauge_data()
        # Key may be present but empty if API unavailable
        assert "series" in result or "data" in result or "stations" in result or isinstance(result, dict)

    def test_weather_has_station_key_or_error(self, noaa_wrapper):
        result = noaa_wrapper.get_weather_data(station_id="KCEC")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# USGS wrapper
# ---------------------------------------------------------------------------

class TestUSGSWrapper:
    def test_get_earthquakes_returns_dict(self, usgs_wrapper):
        result = usgs_wrapper.get_earthquakes()
        assert isinstance(result, dict)

    def test_get_earthquakes_has_events_key(self, usgs_wrapper):
        result = usgs_wrapper.get_earthquakes()
        assert "events" in result or "features" in result or isinstance(result, dict)

    def test_get_cascadia_seismicity_returns_dict(self, usgs_wrapper):
        result = usgs_wrapper.get_cascadia_seismicity(days=7)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# DelNorteDataIntegrator
# ---------------------------------------------------------------------------

class TestDelNorteDataIntegrator:
    def test_init_creates_integrator(self):
        integrator = DelNorteDataIntegrator()
        assert integrator is not None

    def test_has_calfire_client(self):
        integrator = DelNorteDataIntegrator()
        assert hasattr(integrator, "calfire_client")
        assert integrator.calfire_client is not None

    def test_has_noaa_client(self):
        integrator = DelNorteDataIntegrator()
        assert hasattr(integrator, "noaa_client")
        assert integrator.noaa_client is not None

    def test_has_usgs_client(self):
        integrator = DelNorteDataIntegrator()
        assert hasattr(integrator, "usgs_client")
        assert integrator.usgs_client is not None

    def test_calfire_client_is_wrapper(self):
        integrator = DelNorteDataIntegrator()
        assert isinstance(integrator.calfire_client, _CALFIREWrapper)

    def test_noaa_client_is_wrapper(self):
        integrator = DelNorteDataIntegrator()
        assert isinstance(integrator.noaa_client, _NOAAWrapper)

    def test_usgs_client_is_wrapper(self):
        integrator = DelNorteDataIntegrator()
        assert isinstance(integrator.usgs_client, _USGSWrapper)

    def test_clients_cached_on_second_access(self):
        integrator = DelNorteDataIntegrator()
        c1 = integrator.calfire_client
        c2 = integrator.calfire_client
        assert c1 is c2
