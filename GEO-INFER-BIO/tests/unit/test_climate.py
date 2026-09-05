"""Tests for climate data processing."""

import pytest
from geo_infer_bio.climate import ClimateDataProcessor, ClimateDataset


def _two_variable_dataset() -> ClimateDataset:
    data = {
        "bio1": {
            "variable": "bio1",
            "description": "Annual Mean Temperature",
            "units": "°C * 10",
            "coordinates": [
                {"latitude": 37.7, "longitude": -122.4, "value": 15.0},
                {"latitude": 38.0, "longitude": -122.0, "value": 14.0},
            ],
        },
        "bio12": {
            "variable": "bio12",
            "description": "Annual Precipitation",
            "units": "mm",
            "coordinates": [
                {"latitude": 37.7, "longitude": -122.4, "value": 600.0},
                {"latitude": 38.0, "longitude": -122.0, "value": 550.0},
            ],
        },
    }
    return ClimateDataset(data=data, coordinates=[(37.7, -122.4), (38.0, -122.0)])


class TestClimateDataProcessor:
    """Tests for climate data processing."""

    def test_initialization(self) -> None:
        processor = ClimateDataProcessor()
        assert processor.cache_dir.exists()

    def test_worldclim_variables(self) -> None:
        processor = ClimateDataProcessor()
        variables = processor.worldclim_config["variables"]
        assert "bio1" in variables
        assert "bio12" in variables
        assert len(variables) == 19

    def test_worldclim_resolutions(self) -> None:
        processor = ClimateDataProcessor()
        resolutions = processor.worldclim_config["resolutions"]
        assert "30s" in resolutions
        assert "10m" in resolutions

    def test_bbox_with_buffer(self) -> None:
        processor = ClimateDataProcessor()
        bbox = processor._calculate_bbox_with_buffer(
            [(37.7, -122.4), (38.0, -122.0)], buffer_km=11.1
        )
        # 11.1 km ≈ 0.1 degrees
        assert bbox == (-122.5, 37.6, -121.9, 38.1)

    def test_bbox_requires_coordinates(self) -> None:
        processor = ClimateDataProcessor()
        with pytest.raises(ValueError, match="No coordinates"):
            processor._calculate_bbox_with_buffer([], buffer_km=1.0)

    def test_worldclim_requires_data_path(self) -> None:
        processor = ClimateDataProcessor()
        with pytest.raises(ValueError, match="data_path"):
            processor.load_worldclim_data(
                variables=["bio1"], coordinates=[(37.7, -122.4)]
            )

    def test_worldclim_rejects_unknown_variable(self, tmp_path) -> None:
        processor = ClimateDataProcessor()
        with pytest.raises(FileNotFoundError, match="WorldClim raster"):
            processor.load_worldclim_data(
                variables=["bio1"],
                coordinates=[(37.7, -122.4)],
                data_path=str(tmp_path),
            )


class TestClimateDataset:
    """Behavior tests for the climate dataset container."""

    def test_get_variables(self) -> None:
        dataset = _two_variable_dataset()
        assert dataset.get_variables() == ["bio1", "bio12"]

    def test_get_variable_data(self) -> None:
        dataset = _two_variable_dataset()
        df = dataset.get_variable_data("bio1")
        assert list(df.columns) == ["latitude", "longitude", "value", "variable", "units"]
        assert len(df) == 2
        assert (df["variable"] == "bio1").all()
        assert (df["units"] == "°C * 10").all()

    def test_get_variable_data_unknown_variable(self) -> None:
        dataset = _two_variable_dataset()
        with pytest.raises(ValueError, match="not found"):
            dataset.get_variable_data("bio99")

    def test_get_all_variables_dataframe_merges_on_coordinates(self) -> None:
        dataset = _two_variable_dataset()
        merged = dataset.get_all_variables_dataframe()
        # One row per location, one column per variable
        assert list(merged.columns) == ["latitude", "longitude", "bio1", "bio12"]
        assert len(merged) == 2
        row = merged[
            (merged["latitude"] == 37.7) & (merged["longitude"] == -122.4)
        ]
        assert row["bio1"].iloc[0] == 15.0
        assert row["bio12"].iloc[0] == 600.0

    def test_export_for_h3_integration(self) -> None:
        dataset = _two_variable_dataset()
        export = dataset.export_for_h3_integration()
        assert export["coordinates"] == [(37.7, -122.4), (38.0, -122.0)]
        assert set(export["climate_variables"]) == {"bio1", "bio12"}
        assert len(export["climate_data"]) == 2

    def test_empty_dataset_renders_empty_dataframe(self) -> None:
        dataset = ClimateDataset(data={}, coordinates=[])
        assert dataset.get_all_variables_dataframe().empty
