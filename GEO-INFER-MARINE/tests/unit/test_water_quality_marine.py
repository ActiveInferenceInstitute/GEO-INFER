"""Tests for marine water quality module."""

import numpy as np
import pytest
import xarray as xr


from geo_infer_marine.core.water_quality import MarineWaterQuality


@pytest.fixture
def wq():
    return MarineWaterQuality()


class TestDOSaturation:
    def test_do_decreases_with_temperature(self, wq):
        temp_cold = xr.DataArray(np.full((3,), 5.0), dims=("x",))
        temp_warm = xr.DataArray(np.full((3,), 25.0), dims=("x",))
        sal = xr.DataArray(np.full((3,), 35.0), dims=("x",))
        do_cold = wq.calculate_do_saturation(temp_cold, sal)
        do_warm = wq.calculate_do_saturation(temp_warm, sal)
        assert float(do_cold.mean()) > float(do_warm.mean())

    def test_do_positive(self, wq):
        temp = xr.DataArray(np.array([15.0, 20.0, 25.0]), dims=("x",))
        sal = xr.DataArray(np.full((3,), 35.0), dims=("x",))
        do_sat = wq.calculate_do_saturation(temp, sal)
        assert float(do_sat.min()) > 0

    def test_percent_saturation(self, wq):
        temp = xr.DataArray(np.full((3,), 20.0), dims=("x",))
        sal = xr.DataArray(np.full((3,), 35.0), dims=("x",))
        do_sat = wq.calculate_do_saturation(temp, sal)
        measured = do_sat * 0.8
        pct = wq.calculate_do_percent_saturation(measured, temp, sal)
        np.testing.assert_allclose(pct.values, 80.0, atol=1.0)


class TestAcidification:
    def test_no_acidification_at_reference(self, wq):
        ph = xr.DataArray(np.full((5,), 8.1), dims=("x",))
        idx = wq.calculate_ocean_acidification_index(ph)
        np.testing.assert_allclose(idx.values, 0.0, atol=1e-10)

    def test_acidification_increases_with_lower_ph(self, wq):
        ph_high = xr.DataArray(np.full((3,), 8.0), dims=("x",))
        ph_low = xr.DataArray(np.full((3,), 7.8), dims=("x",))
        idx_high = wq.calculate_ocean_acidification_index(ph_high)
        idx_low = wq.calculate_ocean_acidification_index(ph_low)
        assert float(idx_low.mean()) > float(idx_high.mean())


class TestTurbidityScore:
    def test_clear_water_high_score(self, wq):
        turb = xr.DataArray(np.full((3,), 0.5), dims=("x",))
        score = wq.calculate_turbidity_score(turb)
        assert float(score.mean()) > 90

    def test_turbid_water_low_score(self, wq):
        turb = xr.DataArray(np.full((3,), 50.0), dims=("x",))
        score = wq.calculate_turbidity_score(turb)
        assert float(score.mean()) < 20

    def test_score_range(self, wq):
        turb = xr.DataArray(np.linspace(0, 100, 50), dims=("x",))
        score = wq.calculate_turbidity_score(turb)
        assert float(score.min()) >= 0
        assert float(score.max()) <= 100


class TestTrophicState:
    def test_oligotrophic(self, wq):
        chl = xr.DataArray(np.full((3,), 1.0), dims=("x",))
        tsi = wq.calculate_trophic_state_index(chl)
        assert float(tsi.mean()) < 40

    def test_eutrophic(self, wq):
        chl = xr.DataArray(np.full((3,), 20.0), dims=("x",))
        tsi = wq.calculate_trophic_state_index(chl)
        assert float(tsi.mean()) > 50


class TestCompositeWQI:
    def test_excellent_quality(self, wq):
        do = xr.DataArray(np.full((3,), 95.0), dims=("x",))
        ph = xr.DataArray(np.full((3,), 95.0), dims=("x",))
        turb = xr.DataArray(np.full((3,), 95.0), dims=("x",))
        result = wq.composite_marine_wqi(do, ph, turb)
        assert float(result["wqi"].mean()) > 90

    def test_poor_quality(self, wq):
        do = xr.DataArray(np.full((3,), 10.0), dims=("x",))
        ph = xr.DataArray(np.full((3,), 10.0), dims=("x",))
        turb = xr.DataArray(np.full((3,), 10.0), dims=("x",))
        result = wq.composite_marine_wqi(do, ph, turb)
        assert float(result["wqi"].mean()) < 25
