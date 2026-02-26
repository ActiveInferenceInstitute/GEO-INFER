"""Tests for water usage model."""

import pytest
import numpy as np
import pandas as pd
from geo_infer_ag.models.water_usage import WaterUsageModel


class TestWaterUsageModelInit:
    """Tests for WaterUsageModel initialization."""

    def test_default_initialization(self) -> None:
        model = WaterUsageModel()
        assert model is not None
        assert model.model_type == "reference_et"
        assert model.crop_type is None
        assert model.fitted is False
        assert model.predictor is None

    def test_with_crop_type(self) -> None:
        model = WaterUsageModel(crop_type="corn")
        assert model.crop_type == "corn"
        assert model.name == "corn_water_usage_model"

    def test_model_types(self) -> None:
        for mt in ["reference_et", "statistical", "process_based"]:
            model = WaterUsageModel(model_type=mt)
            assert model.model_type == mt

    def test_invalid_model_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported model type"):
            WaterUsageModel(model_type="invalid")

    def test_default_water_balance_components(self) -> None:
        model = WaterUsageModel()
        assert "evapotranspiration" in model.water_balance_components
        assert "precipitation" in model.water_balance_components
        assert "irrigation" in model.water_balance_components
        assert len(model.water_balance_components) == 5

    def test_custom_water_balance_components(self) -> None:
        model = WaterUsageModel(water_balance_components=["et", "precip"])
        assert model.water_balance_components == ["et", "precip"]

    def test_crop_coefficients_loaded(self) -> None:
        model = WaterUsageModel()
        assert "corn" in model.crop_coefficients
        assert "wheat" in model.crop_coefficients
        assert "generic" in model.crop_coefficients
        assert "mid" in model.crop_coefficients["corn"]


class TestWaterUsageModelFit:
    """Tests for WaterUsageModel fit method."""

    def test_reference_et_skips_fit(self) -> None:
        model = WaterUsageModel(model_type="reference_et")
        model.fit({})
        assert model.fitted is True

    def test_statistical_requires_field_data(self) -> None:
        model = WaterUsageModel(model_type="statistical")
        with pytest.raises(ValueError, match="Field data and weather data required"):
            model.fit({"weather_data": pd.DataFrame()})

    def test_statistical_fit(self) -> None:
        model = WaterUsageModel(model_type="statistical")
        np.random.seed(42)
        field_df = pd.DataFrame({
            "temperature": np.random.uniform(15, 35, 50),
            "rainfall": np.random.uniform(0, 10, 50),
            "area_ha": np.random.uniform(1, 100, 50),
            "water_usage": np.random.uniform(200, 600, 50),
        })
        weather_df = pd.DataFrame({"temp": [25]})
        model.fit(
            {"field_data": field_df, "weather_data": weather_df},
            target_column="water_usage",
        )
        assert model.fitted is True
        assert model.predictor is not None


class TestWaterUsageModelPredict:
    """Tests for WaterUsageModel predict method."""

    def test_reference_et_predict(self) -> None:
        model = WaterUsageModel(crop_type="corn", model_type="reference_et")
        model.fit({})

        field_df = pd.DataFrame({
            "area_ha": [10.0, 20.0, 15.0],
            "field_id": ["f1", "f2", "f3"],
        })
        weather_df = pd.DataFrame({
            "temperature": [25.0, 28.0, 22.0],
            "solar_radiation": [20.0, 22.0, 18.0],
            "humidity": [60.0, 55.0, 70.0],
            "wind_speed": [3.0, 4.0, 2.0],
            "precipitation": [5.0, 2.0, 8.0],
        })
        result = model.predict({"field_data": field_df, "weather_data": weather_df})
        assert "water_requirement_mm" in result
        assert "irrigation_requirement_mm" in result
        assert "summary" in result
        assert len(result["water_requirement_mm"]) == 3

    def test_reference_et_missing_weather_raises(self) -> None:
        model = WaterUsageModel(model_type="reference_et")
        model.fit({})
        field_df = pd.DataFrame({"area_ha": [10.0]})
        weather_df = pd.DataFrame({"temperature": [25.0]})
        with pytest.raises(ValueError, match="Missing required weather variables"):
            model.predict({"field_data": field_df, "weather_data": weather_df})

    def test_process_based_predict(self) -> None:
        model = WaterUsageModel(model_type="process_based")
        model.fit({})

        field_df = pd.DataFrame({"area_ha": [10.0, 20.0]})
        weather_df = pd.DataFrame({
            "temperature": [25.0],
            "solar_radiation": [20.0],
            "humidity": [60.0],
            "wind_speed": [3.0],
        })
        soil_df = pd.DataFrame({"clay": [30]})
        mgmt_df = pd.DataFrame({"practice": ["no_till"]})

        result = model.predict({
            "field_data": field_df,
            "weather_data": weather_df,
            "soil_data": soil_df,
            "management_data": mgmt_df,
        })
        assert "water_balance" in result
        assert "evapotranspiration" in result["water_balance"]
        assert result["water_requirement_mm"][0] > 0.0


class TestWaterUsageModelFootprint:
    """Tests for water footprint calculation."""

    def test_water_footprint_basic(self) -> None:
        model = WaterUsageModel()
        result_data = {
            "water_requirement_mm": np.array([400.0, 500.0]),
            "irrigation_requirement_mm": np.array([200.0, 300.0]),
            "effective_rainfall_mm": np.array([200.0, 200.0]),
        }
        footprint = model.calculate_water_footprint(result_data)
        assert "water_footprint_mm" in footprint
        assert "blue_water_mm" in footprint
        assert "green_water_mm" in footprint
        assert np.allclose(footprint["blue_water_mm"], [200.0, 300.0])

    def test_water_footprint_with_yield(self) -> None:
        model = WaterUsageModel()
        result_data = {
            "water_requirement_mm": np.array([400.0]),
            "irrigation_requirement_mm": np.array([200.0]),
            "effective_rainfall_mm": np.array([200.0]),
        }
        yield_data = pd.Series([8.0])
        footprint = model.calculate_water_footprint(result_data, yield_data=yield_data)
        assert "water_footprint_m3_per_ton" in footprint

    def test_water_footprint_missing_data_raises(self) -> None:
        model = WaterUsageModel()
        with pytest.raises(ValueError, match="Water requirement data missing"):
            model.calculate_water_footprint({})
