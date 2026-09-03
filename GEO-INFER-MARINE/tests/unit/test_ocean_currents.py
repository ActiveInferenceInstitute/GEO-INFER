"""Tests for ocean current modeling module."""

import numpy as np
import pytest
import xarray as xr

import sys
sys.path.insert(0, "GEO-INFER-MARINE/src")

from geo_infer_marine.core.ocean_currents import OceanCurrentModeler


@pytest.fixture
def modeler():
    return OceanCurrentModeler()


class TestCoriolisParameter:
    def test_positive_in_northern_hemisphere(self, modeler):
        f = modeler.coriolis_parameter(45.0)
        assert f > 0

    def test_negative_in_southern_hemisphere(self, modeler):
        f = modeler.coriolis_parameter(-45.0)
        assert f < 0

    def test_near_equator_minimum(self, modeler):
        f = modeler.coriolis_parameter(0.1)
        assert abs(f) >= 1e-5

    def test_maximum_at_pole(self, modeler):
        f_45 = modeler.coriolis_parameter(45.0)
        f_90 = modeler.coriolis_parameter(90.0)
        assert f_90 > f_45


class TestEkmanTransport:
    def test_transport_perpendicular_to_wind(self, modeler):
        lats = np.array([30.0, 40.0, 50.0])
        wind_x = xr.DataArray(np.array([0.1, 0.1, 0.1]), dims=("y",))
        wind_y = xr.DataArray(np.zeros(3), dims=("y",))
        lat = xr.DataArray(lats, dims=("y",))
        result = modeler.calculate_ekman_transport(wind_x, wind_y, lat)
        assert "ekman_transport_x" in result
        assert "ekman_transport_y" in result
        assert "ekman_transport_magnitude" in result

    def test_zero_wind(self, modeler):
        wind_x = xr.DataArray(np.zeros(3), dims=("y",))
        wind_y = xr.DataArray(np.zeros(3), dims=("y",))
        lat = xr.DataArray(np.array([30.0, 40.0, 50.0]), dims=("y",))
        result = modeler.calculate_ekman_transport(wind_x, wind_y, lat)
        np.testing.assert_allclose(
            result["ekman_transport_magnitude"].values, 0.0, atol=1e-10
        )


class TestGeostrophicCurrent:
    def test_returns_velocity_components(self, modeler):
        ssh = xr.DataArray(
            np.random.uniform(0, 0.1, (5, 5)),
            dims=("lat", "lon"),
            coords={"lat": np.arange(5), "lon": np.arange(5)},
        )
        lat = xr.DataArray(
            np.full((5, 5), 35.0),
            dims=("lat", "lon"),
            coords={"lat": np.arange(5), "lon": np.arange(5)},
        )
        result = modeler.calculate_geostrophic_current(ssh, lat)
        assert "u_geostrophic" in result
        assert "v_geostrophic" in result
        assert "geostrophic_speed" in result

    def test_flat_ssh_no_current(self, modeler):
        ssh = xr.DataArray(
            np.full((5, 5), 0.5),
            dims=("lat", "lon"),
            coords={"lat": np.arange(5), "lon": np.arange(5)},
        )
        lat = xr.DataArray(
            np.full((5, 5), 35.0),
            dims=("lat", "lon"),
            coords={"lat": np.arange(5), "lon": np.arange(5)},
        )
        result = modeler.calculate_geostrophic_current(ssh, lat)
        assert float(result["geostrophic_speed"].max()) < 1e-6


class TestMixedLayerDepth:
    def test_shallow_thermocline(self, modeler):
        depths = xr.DataArray(np.arange(0, 200, 10, dtype=float), dims=("depth",))
        temp_profile = xr.DataArray(
            np.concatenate([np.full(5, 25.0), np.linspace(25, 10, 15)]),
            dims=("depth",),
            coords={"depth": depths},
        )
        mld = modeler.calculate_mixed_layer_depth(temp_profile, depths, delta_t=0.2)
        assert float(mld) > 0
        assert float(mld) < 200

    def test_uniform_profile_deep_mld(self, modeler):
        depths = xr.DataArray(np.arange(0, 100, 10, dtype=float), dims=("depth",))
        temp_profile = xr.DataArray(
            np.full(10, 20.0),
            dims=("depth",),
            coords={"depth": depths},
        )
        mld = modeler.calculate_mixed_layer_depth(temp_profile, depths)
        assert float(mld) == float(depths.max())


class TestEquatorGuardSignPreserving:
    """The 1e-5 equator guard must not flip the sign of small |f|."""

    def test_negative_f_stays_negative(self, modeler):
        # Latitude whose Coriolis parameter is -1e-6 (inside the guard band).
        lat = np.degrees(np.arcsin(-1e-6 / (2 * 7.2921e-5)))
        lats = xr.DataArray(np.array([lat]), dims=("y",))
        tau_y = xr.DataArray(np.array([1.0]), dims=("y",))
        tau_x = xr.DataArray(np.array([0.0]), dims=("y",))
        result = modeler.calculate_ekman_transport(tau_x, tau_y, lats)
        # transport_x = tau_y / f with f clamped to -1e-5, so negative.
        assert float(result["ekman_transport_x"].values[0]) < 0

    def test_zero_f_clamps_positive(self, modeler):
        lats = xr.DataArray(np.array([0.0]), dims=("y",))
        tau_y = xr.DataArray(np.array([1.0]), dims=("y",))
        tau_x = xr.DataArray(np.array([0.0]), dims=("y",))
        result = modeler.calculate_ekman_transport(tau_x, tau_y, lats)
        # f == 0 clamps to +1e-5, so transport_x = 1 / 1e-5.
        assert float(result["ekman_transport_x"].values[0]) == pytest.approx(1e5)

    def test_positive_f_stays_positive(self, modeler):
        lat = np.degrees(np.arcsin(1e-6 / (2 * 7.2921e-5)))
        lats = xr.DataArray(np.array([lat]), dims=("y",))
        tau_y = xr.DataArray(np.array([1.0]), dims=("y",))
        tau_x = xr.DataArray(np.array([0.0]), dims=("y",))
        result = modeler.calculate_ekman_transport(tau_x, tau_y, lats)
        assert float(result["ekman_transport_x"].values[0]) > 0
