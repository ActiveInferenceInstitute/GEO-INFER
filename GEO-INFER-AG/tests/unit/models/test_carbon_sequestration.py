"""Tests for carbon sequestration model."""

import logging

import numpy as np
import pytest
import pandas as pd
from geo_infer_ag.models.carbon_sequestration import CarbonSequestrationModel


class TestCarbonSequestrationInit:
    """Tests for CarbonSequestrationModel initialization."""

    def test_default_initialization(self) -> None:
        model = CarbonSequestrationModel()
        assert model is not None
        assert model.model_type == "tier1"
        assert model.time_horizon == 20
        assert model.carbon_pools == ["soil_carbon", "biomass_carbon"]
        assert model.fitted is False

    def test_custom_model_type(self) -> None:
        for mt in ["tier1", "tier2", "process_based"]:
            model = CarbonSequestrationModel(model_type=mt)
            assert model.model_type == mt

    def test_invalid_model_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported model type"):
            CarbonSequestrationModel(model_type="invalid")

    def test_custom_time_horizon(self) -> None:
        model = CarbonSequestrationModel(time_horizon=50)
        assert model.time_horizon == 50

    def test_custom_carbon_pools(self) -> None:
        model = CarbonSequestrationModel(carbon_pools=["soil_carbon"])
        assert model.carbon_pools == ["soil_carbon"]

    def test_default_rates_loaded(self) -> None:
        model = CarbonSequestrationModel()
        assert "corn" in model.default_rates
        assert "forest" in model.default_rates
        assert "soil_carbon" in model.default_rates["corn"]

    def test_practice_modifiers_loaded(self) -> None:
        model = CarbonSequestrationModel()
        assert "no_till" in model.practice_modifiers
        assert "cover_crops" in model.practice_modifiers
        assert model.practice_modifiers["no_till"]["soil_carbon"] == 1.3


class TestCarbonSequestrationFit:
    """Tests for CarbonSequestrationModel fit method."""

    def test_tier1_skips_fit(self) -> None:
        model = CarbonSequestrationModel(model_type="tier1")
        model.fit({})
        assert model.fitted is True

    def test_process_based_skips_fit(self) -> None:
        model = CarbonSequestrationModel(model_type="process_based")
        model.fit({})
        assert model.fitted is True

    def test_tier2_requires_field_data(self) -> None:
        model = CarbonSequestrationModel(model_type="tier2")
        with pytest.raises(ValueError, match="Field data required"):
            model.fit({})

    def test_tier2_fit_predict_both_pools_in_total(self) -> None:
        """Tier 2 fit -> predict must include every adequately-trained pool."""
        model = CarbonSequestrationModel(model_type="tier2")
        n = 12
        field_df = pd.DataFrame(
            {
                "soil_ph": np.linspace(5.0, 7.5, n),
                "annual_rainfall": np.linspace(400.0, 900.0, n),
                "soil_carbon_sequestration": np.linspace(0.2, 0.5, n),
                "biomass_carbon_sequestration": np.linspace(0.1, 0.4, n),
            }
        )
        model.fit({"field_data": field_df})
        assert set(model.predictors) == {"soil_carbon", "biomass_carbon"}

        predict_df = pd.DataFrame(
            {
                "crop_type": ["corn", "wheat", "corn"],
                "area_ha": [10.0, 20.0, 30.0],
                "soil_ph": [6.0, 6.5, 7.0],
                "annual_rainfall": [500.0, 600.0, 700.0],
            }
        )
        result = model.predict(
            {
                "field_data": predict_df,
                "soil_data": pd.DataFrame({"soil_type": ["loam"]}),
                "management_data": pd.DataFrame({"practices": [[], []]}),
            }
        )

        assert set(result["sequestration_rates"]) == {
            "soil_carbon",
            "biomass_carbon",
        }
        assert set(result["metadata"]["carbon_pools"]) == {
            "soil_carbon",
            "biomass_carbon",
        }
        # The total must be the sum of both pools, not a single-pool value
        expected_total = (
            result["sequestration_rates"]["soil_carbon"]
            + result["sequestration_rates"]["biomass_carbon"]
        )
        np.testing.assert_allclose(result["total_sequestration_rate"], expected_total)
        assert result["metadata"]["skipped_pools"] == {}

    def test_tier2_fit_warns_and_records_insufficient_pool(self, caplog) -> None:
        """A pool with < 10 training rows must be skipped with a warning."""
        model = CarbonSequestrationModel(model_type="tier2")
        n = 12
        biomass = np.full(n, np.nan)
        biomass[:3] = [0.1, 0.2, 0.3]
        field_df = pd.DataFrame(
            {
                "soil_ph": np.linspace(5.0, 7.5, n),
                "annual_rainfall": np.linspace(400.0, 900.0, n),
                "soil_carbon_sequestration": np.linspace(0.2, 0.5, n),
                "biomass_carbon_sequestration": biomass,
            }
        )

        with caplog.at_level(
            logging.WARNING,
            logger="geo_infer_ag.models.carbon_sequestration",
        ):
            model.fit({"field_data": field_df})

        assert set(model.predictors) == {"soil_carbon"}
        assert model.metadata["skipped_pools"] == {"biomass_carbon": 3}
        assert "biomass_carbon" in caplog.text


class TestCarbonSequestrationPredict:
    """Tests for CarbonSequestrationModel predict method."""

    def test_tier1_predict(self) -> None:
        model = CarbonSequestrationModel(model_type="tier1")
        model.fit({})

        field_df = pd.DataFrame(
            {
                "crop_type": ["corn", "wheat", "soybean"],
                "area_ha": [50.0, 30.0, 20.0],
            }
        )
        result = model.predict({"field_data": field_df})

        assert "sequestration_rates" in result
        assert "total_sequestration_rate" in result
        assert "co2e_sequestration" in result
        assert "summary" in result
        assert len(result["total_sequestration_rate"]) == 3
        # Corn default rate is 0.2 (soil) + 0.3 (biomass) = 0.5 t C/ha/yr
        assert result["total_sequestration_rate"][0] == pytest.approx(0.5, rel=0.01)

    def test_tier1_unknown_crop_defaults_to_grassland(self) -> None:
        model = CarbonSequestrationModel(model_type="tier1")
        model.fit({})
        field_df = pd.DataFrame(
            {
                "crop_type": ["unknown_crop"],
                "area_ha": [10.0],
            }
        )
        result = model.predict({"field_data": field_df})
        grassland_rate = (
            model.default_rates["grassland"]["soil_carbon"]
            + model.default_rates["grassland"]["biomass_carbon"]
        )
        assert result["total_sequestration_rate"][0] == pytest.approx(
            grassland_rate, rel=0.01
        )

    def test_co2e_conversion(self) -> None:
        model = CarbonSequestrationModel(model_type="tier1", time_horizon=10)
        model.fit({})
        field_df = pd.DataFrame(
            {
                "crop_type": ["corn"],
                "area_ha": [100.0],
            }
        )
        result = model.predict({"field_data": field_df})
        # CO2e = total_sequestration * time_horizon * 3.67
        total_annual = result["total_sequestration"][0]
        expected_co2e = total_annual * 10 * 3.67
        assert result["co2e_sequestration"][0] == pytest.approx(expected_co2e, rel=0.01)

    def test_missing_crop_type_raises(self) -> None:
        model = CarbonSequestrationModel(model_type="tier1")
        model.fit({})
        field_df = pd.DataFrame({"area_ha": [10.0]})
        with pytest.raises(ValueError, match="crop_type"):
            model.predict({"field_data": field_df})

    def test_process_based_requires_extra_data(self) -> None:
        model = CarbonSequestrationModel(model_type="process_based")
        model.fit({})
        field_df = pd.DataFrame(
            {
                "crop_type": ["corn"],
                "area_ha": [10.0],
            }
        )
        with pytest.raises(ValueError, match="Required input.*is missing"):
            model.predict({"field_data": field_df})


class TestCarbonValue:
    """Tests for carbon value calculation."""

    def test_carbon_value_calculation(self) -> None:
        model = CarbonSequestrationModel(model_type="tier1")
        model.fit({})
        field_df = pd.DataFrame(
            {
                "crop_type": ["corn"],
                "area_ha": [100.0],
            }
        )
        result = model.predict({"field_data": field_df})
        value = model.calculate_carbon_value(result, carbon_price=30.0)
        assert "carbon_value" in value
        assert "total_carbon_value" in value
        assert value["carbon_price"] == 30.0
        assert value["total_carbon_value"] > 0

    def test_carbon_value_missing_data_raises(self) -> None:
        model = CarbonSequestrationModel()
        with pytest.raises(ValueError, match="CO2e sequestration data missing"):
            model.calculate_carbon_value({})


class TestSetTimeHorizon:
    """Tests for set_time_horizon method."""

    def test_set_time_horizon(self) -> None:
        model = CarbonSequestrationModel()
        model.set_time_horizon(50)
        assert model.time_horizon == 50
        assert model.metadata["time_horizon"] == 50

    def test_negative_time_horizon_raises(self) -> None:
        model = CarbonSequestrationModel()
        with pytest.raises(ValueError, match="positive"):
            model.set_time_horizon(-5)

    def test_zero_time_horizon_raises(self) -> None:
        model = CarbonSequestrationModel()
        with pytest.raises(ValueError, match="positive"):
            model.set_time_horizon(0)
