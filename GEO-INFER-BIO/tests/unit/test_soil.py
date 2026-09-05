"""Tests for soil data integration."""

import inspect
import pytest
from geo_infer_bio.soil import SoilDataIntegrator, SoilDataset


def _soil_dataset() -> SoilDataset:
    data = {
        "phh2o_0-5cm": {
            "property": "phh2o",
            "depth": "0-5cm",
            "units": "SoilGrids mapped units",
            "coordinates": [
                {"latitude": 37.7, "longitude": -122.4, "value": 6.5, "depth": "0-5cm"},
                {"latitude": 38.0, "longitude": -122.0, "value": 7.5, "depth": "0-5cm"},
            ],
        },
        "soc_0-5cm": {
            "property": "soc",
            "depth": "0-5cm",
            "units": "SoilGrids mapped units",
            "coordinates": [
                {"latitude": 37.7, "longitude": -122.4, "value": 15.0, "depth": "0-5cm"},
                {"latitude": 38.0, "longitude": -122.0, "value": 3.0, "depth": "0-5cm"},
            ],
        },
    }
    return SoilDataset(data=data, coordinates=[(37.7, -122.4), (38.0, -122.0)])


class TestSoilDataIntegrator:
    """Tests for soil data integration."""

    def test_initialization(self) -> None:
        integrator = SoilDataIntegrator()
        assert integrator.cache_dir.exists()

    def test_soilgrids_properties(self) -> None:
        integrator = SoilDataIntegrator()
        props = integrator.soilgrids_config["properties"]
        assert "phh2o" in props
        assert "clay" in props
        assert "sand" in props

    def test_soilgrids_depths(self) -> None:
        integrator = SoilDataIntegrator()
        depths = integrator.soilgrids_config["depths"]
        assert "0-5cm" in depths

    def test_soilgrids_depth_argument_is_not_mutable_default(self) -> None:
        parameter = inspect.signature(
            SoilDataIntegrator.load_soilgrids_data
        ).parameters["depths"]
        assert parameter.default is None

    def test_load_soilgrids_data_validates_inputs(self) -> None:
        integrator = SoilDataIntegrator()
        with pytest.raises(ValueError, match="coordinates must not be empty"):
            integrator.load_soilgrids_data(coordinates=[], properties=["phh2o"])
        with pytest.raises(ValueError, match="properties must not be empty"):
            integrator.load_soilgrids_data(coordinates=[(37.7, -122.4)], properties=[])
        with pytest.raises(ValueError, match="Unknown SoilGrids properties"):
            integrator.load_soilgrids_data(
                coordinates=[(37.7, -122.4)], properties=["bogus"]
            )
        with pytest.raises(ValueError, match="Unknown SoilGrids depths"):
            integrator.load_soilgrids_data(
                coordinates=[(37.7, -122.4)], properties=["phh2o"], depths=["99m"]
            )


class TestSoilDataset:
    """Behavior tests for the soil dataset container."""

    def test_parses_properties_and_depths(self) -> None:
        dataset = _soil_dataset()
        assert dataset.get_properties() == ["phh2o", "soc"]
        assert dataset.get_depths() == ["0-5cm"]

    def test_get_property_data_single_depth(self) -> None:
        dataset = _soil_dataset()
        df = dataset.get_property_data("phh2o", "0-5cm")
        assert (df["property"] == "phh2o").all()
        assert len(df) == 2
        assert sorted(df["value"]) == [6.5, 7.5]

    def test_get_property_data_all_depths(self) -> None:
        dataset = _soil_dataset()
        df = dataset.get_property_data("phh2o")
        assert len(df) == 2  # one depth present

    def test_get_property_data_unknown_depth_raises(self) -> None:
        dataset = _soil_dataset()
        with pytest.raises(ValueError, match="not found"):
            dataset.get_property_data("phh2o", "100-200cm")

    def test_get_soil_profile_with_tolerance(self) -> None:
        dataset = _soil_dataset()
        profile = dataset.get_soil_profile(37.71, -122.41, tolerance=0.01)
        assert set(profile["property"]) == {"phh2o", "soc"}
        assert (profile["depth"] == "0-5cm").all()

    def test_calculate_soil_health_indicators(self) -> None:
        dataset = _soil_dataset()
        indicators = dataset.calculate_soil_health_indicators()
        by_location = indicators.set_index(["latitude", "longitude"])
        # pH 6.5 is inside the optimal range -> perfect score
        assert by_location.loc[(37.7, -122.4), "ph_health_score"] == 1.0
        # pH 7.5 -> 1 - |7.5 - 6.5|/2 = 0.5
        assert by_location.loc[(38.0, -122.0), "ph_health_score"] == 0.5
        assert by_location.loc[(37.7, -122.4), "organic_carbon_score"] == 0.5
        assert by_location.loc[(38.0, -122.0), "organic_carbon_score"] == 0.1

    def test_export_for_h3_integration(self) -> None:
        dataset = _soil_dataset()
        export = dataset.export_for_h3_integration()
        assert export["coordinates"] == [(37.7, -122.4), (38.0, -122.0)]
        assert set(export["soil_properties"]) == {"phh2o", "soc"}
        assert export["depths"] == ["0-5cm"]
        assert export["soil_data"] == dataset.data
