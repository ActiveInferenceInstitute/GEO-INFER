"""Physics tests for Green-Ampt infiltration (WATER-01)."""

import numpy as np
import pytest
import xarray as xr

from geo_infer_water import HydrologicalModeler, WaterBalanceModeler


@pytest.fixture
def modeler():
    return HydrologicalModeler()


def make_precip(depths):
    """A (time, y, x) DataArray with the given per-step depths (mm)."""
    data = np.asarray(depths, dtype=float).reshape(-1, 1, 1)
    times = [f"2024-01-{d + 1:02d}T00:00:00" for d in range(data.shape[0])]
    return xr.DataArray(data, dims=("time", "y", "x"), coords={"time": times})


class TestGreenAmptDegenerateCases:
    def test_zero_sorptivity_capacity_is_ks_after_first_contact(self, modeler):
        # S = 0: capacity is Ks once F > 0. The first step is first
        # contact (infinite capacity, all rain infiltrates); every
        # subsequent ponded step infiltrates exactly Ks*dt and the rest
        # runs off.
        precip = make_precip([60.0] * 5)
        result = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.0, dt=1.0
        )
        inf = result["infiltration"].values.ravel()
        assert inf[0] == 60.0
        np.testing.assert_allclose(inf[1:], 10.0)
        np.testing.assert_allclose(result["runoff"].values.ravel()[1:], 50.0)
        assert not bool(result["ponded"].values.ravel()[0])
        assert bool(result["ponded"].values.ravel()[1:].all())


class TestGreenAmptPhysics:
    def test_capacity_declines_toward_ks(self, modeler):
        # Constant heavy rain: the infiltration rate must decrease strictly
        # and approach Ks from above.
        precip = make_precip([100.0] * 60)
        result = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.34, dt=1.0
        )
        rate = result["infiltration_rate"].values[:, 0, 0]
        assert rate[-1] < 10.0 * 1.05
        assert rate[-1] > 10.0

    def test_implicit_equation_residual_is_tiny(self, modeler):
        # Every ponded step must satisfy the implicit Green-Ampt relation
        # F' = F + Ks*dt + S*ln((F'+S)/(F+S)) to numerical precision.
        ks, suction, dtheta, dt = 10.0, 50.0, 0.34, 1.0
        precip = make_precip([80.0] * 30)
        result = modeler.green_ampt_infiltration(
            precip, ks=ks, suction_head=suction, delta_theta=dtheta, dt=dt
        )
        cumulative = result["cumulative_infiltration"].values[:, 0, 0]
        ponded = result["ponded"].values[:, 0, 0]
        s = suction * dtheta
        for k in np.where(ponded)[0]:
            f_old = cumulative[k - 1] if k > 0 else 0.0
            f_new = cumulative[k]
            if f_old == 0.0:
                continue  # first-contact step absorbs the whole depth
            residual = f_new - f_old - ks * dt - s * np.log((f_new + s) / (f_old + s))
            assert abs(residual) < 1e-8 * f_new

    def test_mass_balance_exact(self, modeler):
        precip = make_precip([5.0, 40.0, 80.0, 80.0, 3.0])
        result = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.34, dt=1.0
        )
        np.testing.assert_allclose(
            result["runoff"].values + result["infiltration"].values,
            precip.values,
            atol=1e-9,
        )

    def test_wet_soil_ponds_earlier_than_dry_soil(self, modeler):
        # A drier soil has a larger moisture deficit, hence a larger
        # sorptivity term and more cumulative infiltration under the
        # same rain.
        precip = make_precip([70.0] * 20)
        dry = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.5, dt=1.0
        )
        wet = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.1, dt=1.0
        )
        dry_total = float(dry["infiltration"].sum())
        wet_total = float(wet["infiltration"].sum())
        assert dry_total > wet_total
        assert float(wet["runoff"].sum()) > float(dry["runoff"].sum())

    def test_ponding_flags_track_capacity(self, modeler):
        # Rain [5, 40, 40, 5] with Ks=10: step 0 is first contact (all
        # infiltrates), step 1 stays below the still-large capacity, later
        # heavy steps pond once F has grown.
        precip = make_precip([5.0, 40.0, 40.0, 5.0])
        result = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.34, dt=1.0
        )
        ponded = result["ponded"].values[:, 0, 0]
        assert not ponded[0]
        assert not ponded[3]
        assert ponded[1] or ponded[2]
        # cumulative infiltration never decreases
        cumulative = result["cumulative_infiltration"].values[:, 0, 0]
        assert np.all(np.diff(cumulative) >= 0.0)

    def test_scalar_single_step_first_contact_absorbs_everything(self, modeler):
        precip = make_precip([5000.0])
        result = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.34, dt=1.0
        )
        np.testing.assert_allclose(result["infiltration"].values, 5000.0)
        np.testing.assert_allclose(result["runoff"].values, 0.0)


class TestGreenAmptConsistency:
    def test_runoff_feeds_water_balance_closure_with_zero_residual(self, modeler):
        # The Green-Ampt runoff series must slot into the canonical
        # water-balance owner: with ET = 0 the storage change equals the
        # cumulative infiltration and the closure residual is identically
        # zero.
        precip = make_precip([60.0, 80.0, 5.0])
        result = modeler.green_ampt_infiltration(
            precip, ks=10.0, suction_head=50.0, delta_theta=0.34, dt=1.0
        )
        zero_et = xr.zeros_like(precip)
        closure = WaterBalanceModeler().water_balance_closure(
            precip, zero_et, result["runoff"]
        )
        np.testing.assert_allclose(closure["closure_residual"].values, 0.0, atol=1e-9)
        np.testing.assert_allclose(
            closure["storage_change"].values,
            result["infiltration"].values,
            atol=1e-9,
        )

    def test_invalid_parameters_rejected(self, modeler):
        precip = make_precip([10.0])
        with pytest.raises(ValueError):
            modeler.green_ampt_infiltration(precip, ks=0.0)
        with pytest.raises(ValueError):
            modeler.green_ampt_infiltration(precip, ks=10.0, dt=0.0)
        with pytest.raises(ValueError):
            modeler.green_ampt_infiltration(precip, ks=10.0, delta_theta=-0.1)

    def test_negative_precipitation_rejected(self, modeler):
        with pytest.raises(ValueError):
            modeler.green_ampt_infiltration(make_precip([10.0, -1.0]), ks=10.0)
