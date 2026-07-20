"""Tests for hazard model."""

import pytest
from datetime import datetime
import numpy as np
from geo_infer_risk.core.hazard_model import EnhancedHazardModel


class TestEnhancedHazardModel:
    """Tests for the enhanced hazard model."""

    def setup_method(self) -> None:
        self.model = EnhancedHazardModel(
            hazard_type="flood",
            params={
                "return_periods": [10, 50, 100],
                "include_climate_change": False,
                "spatial_resolution": 9,
            },
        )

    def test_initialization(self) -> None:
        assert self.model.hazard_type == "flood"
        assert self.model.return_periods == [10, 50, 100]
        assert self.model.is_fitted is False

    def test_different_hazard_types(self) -> None:
        for htype in ["earthquake", "hurricane", "wildfire", "flood"]:
            m = EnhancedHazardModel(hazard_type=htype, params={})
            assert m.hazard_type == htype

    def test_default_parameters(self) -> None:
        m = EnhancedHazardModel(hazard_type="generic", params={})
        assert m.return_periods == [10, 25, 50, 100, 500]
        assert m.spatial_resolution == 9

    def test_climate_change_flag(self) -> None:
        m = EnhancedHazardModel(
            hazard_type="flood", params={"include_climate_change": True}
        )
        assert m.include_climate_change is True

    def test_seeded_event_generation_is_reproducible(self) -> None:
        params = {
            "random_seed": 13,
            "reference_time": "2020-01-01T00:00:00",
        }
        first = EnhancedHazardModel("flood", params).generate_events(
            4,
            time_period=(datetime(2020, 1, 1), datetime(2020, 1, 2)),
        )
        second = EnhancedHazardModel("flood", params).generate_events(
            4,
            time_period=(datetime(2020, 1, 1), datetime(2020, 1, 2)),
        )

        assert first == second

    def test_event_generation_rejects_invalid_count_and_interval(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            self.model.generate_events(-1)
        with pytest.raises(ValueError, match="after"):
            self.model.generate_events(
                1, time_period=(datetime(2020, 1, 2), datetime(2020, 1, 1))
            )

    def test_return_period_intensity_requires_calibrated_model(self) -> None:
        with pytest.raises(ValueError, match="must be fitted"):
            self.model._get_return_period_intensity(10, 0.0, 0.0)

        self.model.is_fitted = True
        self.model.model_parameters = {
            "mean_intensity": 4.0,
            "std_intensity": 1.0,
        }
        value = self.model._get_return_period_intensity(100, 0.0, 0.0)
        assert np.isfinite(value)
        assert value > 4.0

    def test_return_period_intensity_rejects_invalid_period(self) -> None:
        self.model.is_fitted = True
        self.model.model_parameters = {
            "mean_intensity": 4.0,
            "std_intensity": 1.0,
        }
        with pytest.raises(ValueError, match="greater than one"):
            self.model._get_return_period_intensity(1, 0.0, 0.0)
