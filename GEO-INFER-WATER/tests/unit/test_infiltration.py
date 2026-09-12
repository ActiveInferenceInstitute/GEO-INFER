"""Tests for Green-Ampt infiltration module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_water.core.infiltration import InfiltrationModeler


@pytest.fixture
def modeler():
    return InfiltrationModeler()


class TestGreenAmptInfiltration:
    def test_mass_conservation_per_step(self, modeler):
        rain = np.array([5.0, 0.0, 25.0, 40.0, 12.0, 3.0, 0.0, 60.0])
        result = modeler.green_ampt_infiltration(rain)
        np.testing.assert_allclose(
            result["infiltration_mm"] + result["runoff_mm"], rain, atol=1e-10
        )
        np.testing.assert_allclose(
            result["cumulative_infiltration_mm"][-1]
            + result["cumulative_runoff_mm"][-1],
            rain.sum(),
            atol=1e-9,
        )

    def test_infiltration_bounded_by_rainfall(self, modeler):
        rain = np.array([2.0, 30.0, 30.0, 3.0])
        result = modeler.green_ampt_infiltration(rain)
        assert np.all(result["infiltration_mm"] <= rain + 1e-12)
        assert np.all(result["runoff_mm"] >= 0.0)
        assert result["cumulative_infiltration_mm"][-1] <= rain.sum() + 1e-12

    def test_output_arrays_match_input_length(self, modeler):
        rain = np.array([3.0, 1.0])
        result = modeler.green_ampt_infiltration(rain)
        assert len(result) == 7
        for values in result.values():
            assert values.shape == (2,)
        np.testing.assert_allclose(result["rainfall_mm"], rain)

    def test_zero_rainfall(self, modeler):
        result = modeler.green_ampt_infiltration(np.zeros(4))
        for values in result.values():
            np.testing.assert_allclose(values, 0.0)

    def test_light_rain_fully_infiltrates(self, modeler):
        # Rain below the Green-Ampt capacity at every step must
        # infiltrate completely with zero runoff.
        rain = np.array([1.0, 2.0, 3.0, 0.5])
        result = modeler.green_ampt_infiltration(
            rain, hydraulic_conductivity_mm_hr=10.0, time_step_hr=1.0
        )
        np.testing.assert_allclose(result["infiltration_mm"], rain)
        np.testing.assert_allclose(result["runoff_mm"], 0.0)

    def test_capacity_declines_under_sustained_rain(self, modeler):
        # Under rain far above capacity the first step is supply-limited
        # (absorbs all rain) and later steps are soil-limited: per-step
        # infiltration decreases monotonically as the wetting front
        # advances, staying above Ks * dt.
        rain = np.full(12, 200.0)
        result = modeler.green_ampt_infiltration(
            rain,
            hydraulic_conductivity_mm_hr=10.0,
            suction_head_mm=100.0,
            saturated_water_content=0.45,
            initial_water_content=0.15,
            time_step_hr=1.0,
        )
        infil = result["infiltration_mm"]
        assert infil[0] == pytest.approx(200.0)
        assert np.all(np.diff(infil[1:]) <= 1e-12)
        assert infil[-1] > 10.0
        assert infil[-1] < infil[1]

    def test_near_saturated_soil_caps_at_conductivity(self, modeler):
        # theta_i -> theta_s makes the capillary drive vanish: per-step
        # infiltration under heavy rain is capped at Ks * dt.
        rain = np.full(10, 100.0)
        result = modeler.green_ampt_infiltration(rain, initial_water_content=0.4499)
        infil = result["infiltration_mm"]
        assert infil[0] == pytest.approx(100.0)
        np.testing.assert_allclose(infil[1:], 10.0, rtol=0.02)

    def test_consistent_with_water_balance_closure(self, modeler):
        # Green-Ampt output must compose with the delivered water-balance
        # closure: storage_change == P - ET - runoff for an arbitrary ET
        # series, and the closure residual is identically zero.
        from geo_infer_water.core.water_balance import WaterBalanceModeler

        rain = np.array([20.0, 5.0, 35.0, 10.0])
        result = modeler.green_ampt_infiltration(rain)
        et = np.array([2.0, 0.0, 5.0, 1.0])
        closure = WaterBalanceModeler().water_balance_closure(
            precipitation=xr.DataArray(rain, dims="t"),
            evapotranspiration=xr.DataArray(et, dims="t"),
            runoff=xr.DataArray(result["runoff_mm"], dims="t"),
        )
        np.testing.assert_allclose(
            closure["storage_change"].values + et, result["infiltration_mm"]
        )
        np.testing.assert_allclose(closure["closure_residual"].values, 0.0)

    def test_dry_soil_infiltrates_more_than_wet_soil(self, modeler):
        rain = np.full(8, 50.0)
        dry = modeler.green_ampt_infiltration(rain, initial_water_content=0.05)
        wet = modeler.green_ampt_infiltration(rain, initial_water_content=0.40)
        assert (
            dry["cumulative_infiltration_mm"][-1]
            > wet["cumulative_infiltration_mm"][-1]
        )
        assert dry["cumulative_runoff_mm"][-1] < wet["cumulative_runoff_mm"][-1]

    def test_defaults_split_rainfall_into_infiltration_and_runoff(self, modeler):
        rain = np.full(6, 30.0)
        result = modeler.green_ampt_infiltration(rain)
        assert result["infiltration_mm"].sum() > 0
        assert result["runoff_mm"].sum() > 0

    def test_wetting_front_depth_consistency(self, modeler):
        rain = np.array([12.0, 8.0, 15.0, 4.0])
        theta_s, theta_i = 0.45, 0.15
        result = modeler.green_ampt_infiltration(
            rain,
            saturated_water_content=theta_s,
            initial_water_content=theta_i,
        )
        expected = result["cumulative_infiltration_mm"] / (theta_s - theta_i)
        np.testing.assert_allclose(result["wetting_front_depth_mm"], expected)

    def test_rate_matches_depth_over_timestep(self, modeler):
        rain = np.array([12.0, 3.0, 30.0])
        result = modeler.green_ampt_infiltration(rain, time_step_hr=0.5)
        np.testing.assert_allclose(
            result["infiltration_rate_mm_hr"], result["infiltration_mm"] / 0.5
        )


class TestGreenAmptValidation:
    def test_rejects_nonpositive_conductivity(self, modeler):
        with pytest.raises(ValueError, match="hydraulic_conductivity"):
            modeler.green_ampt_infiltration(
                np.ones(3), hydraulic_conductivity_mm_hr=0.0
            )
        with pytest.raises(ValueError, match="hydraulic_conductivity"):
            modeler.green_ampt_infiltration(
                np.ones(3), hydraulic_conductivity_mm_hr=-5.0
            )

    def test_rejects_negative_suction_head(self, modeler):
        with pytest.raises(ValueError, match="suction_head"):
            modeler.green_ampt_infiltration(np.ones(3), suction_head_mm=-1.0)

    def test_rejects_saturated_content_outside_unit_interval(self, modeler):
        with pytest.raises(ValueError, match="saturated_water_content"):
            modeler.green_ampt_infiltration(np.ones(3), saturated_water_content=0.0)
        with pytest.raises(ValueError, match="saturated_water_content"):
            modeler.green_ampt_infiltration(np.ones(3), saturated_water_content=1.2)

    def test_rejects_initial_content_at_or_above_saturation(self, modeler):
        with pytest.raises(ValueError, match="initial_water_content"):
            modeler.green_ampt_infiltration(
                np.ones(3),
                saturated_water_content=0.45,
                initial_water_content=0.45,
            )
        with pytest.raises(ValueError, match="initial_water_content"):
            modeler.green_ampt_infiltration(
                np.ones(3),
                saturated_water_content=0.45,
                initial_water_content=0.6,
            )
        with pytest.raises(ValueError, match="initial_water_content"):
            modeler.green_ampt_infiltration(np.ones(3), initial_water_content=-0.1)

    def test_rejects_nonpositive_time_step(self, modeler):
        with pytest.raises(ValueError, match="time_step"):
            modeler.green_ampt_infiltration(np.ones(3), time_step_hr=0.0)
        with pytest.raises(ValueError, match="time_step"):
            modeler.green_ampt_infiltration(np.ones(3), time_step_hr=-1.0)

    def test_rejects_negative_rainfall(self, modeler):
        with pytest.raises(ValueError, match="rainfall_mm"):
            modeler.green_ampt_infiltration(np.array([1.0, -0.5, 2.0]))

    def test_rejects_nonfinite_rainfall(self, modeler):
        with pytest.raises(ValueError, match="finite"):
            modeler.green_ampt_infiltration(np.array([1.0, np.nan]))
        with pytest.raises(ValueError, match="finite"):
            modeler.green_ampt_infiltration(np.array([1.0, np.inf]))

    def test_cross_model_green_ampt_consistency(self, modeler):
        # The raster variant (HydrologicalModeler, implicit Newton ponding
        # solver) and this point-scale variant must stay numerically
        # consistent: they implement the same physics, differing only in
        # the documented ponding approximation (start-of-step capacity
        # here vs mid-step implicit resolution there). Divergence is
        # bounded to ~1% on cumulative infiltration and ~5% per step;
        # both partitions stay mass exact. This pins GS-163: changing one
        # implementation's numerics without the other fails here.
        from geo_infer_water import HydrologicalModeler

        rain = np.array([60.0, 5.0, 40.0, 80.0, 80.0, 3.0, 200.0, 0.0, 30.0])
        point = modeler.green_ampt_infiltration(
            rain,
            hydraulic_conductivity_mm_hr=10.0,
            suction_head_mm=100.0,
            saturated_water_content=0.45,
            initial_water_content=0.15,
            time_step_hr=1.0,
        )
        raster = HydrologicalModeler().green_ampt_infiltration(
            xr.DataArray(rain, dims="time"),
            ks=10.0,
            suction_head=100.0,
            delta_theta=0.30,
            dt=1.0,
        )
        np.testing.assert_allclose(
            point["infiltration_mm"], raster["infiltration"].values, rtol=0.05
        )
        np.testing.assert_allclose(
            point["cumulative_infiltration_mm"][-1],
            float(raster["cumulative_infiltration"].values[-1]),
            rtol=0.02,
        )
        np.testing.assert_allclose(
            point["infiltration_mm"] + point["runoff_mm"], rain, atol=1e-9
        )
        np.testing.assert_allclose(
            raster["runoff"].values + raster["infiltration"].values,
            rain,
            atol=1e-9,
        )
