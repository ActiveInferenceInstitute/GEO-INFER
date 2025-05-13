"""Unit tests for the Agricultural Analysis core functionality."""

import pytest
import numpy as np
import pandas as pd
import geopandas as gpd

from geo_infer_ag.core.agricultural_analysis import AgriculturalAnalysis, AgriculturalResults
from geo_infer_ag.models.crop_yield import CropYieldModel


class TestAgriculturalAnalysis:
    """Test suite for AgriculturalAnalysis class."""

    def test_initialization(self):
        """Test initialization of AgriculturalAnalysis."""
        model = CropYieldModel(crop_type="corn")
        analyzer = AgriculturalAnalysis(model=model)
        
        assert analyzer.model == model
        assert isinstance(analyzer.config, dict)
        assert analyzer.results is None

    def test_validation(self, sample_field_data):
        """Test input validation."""
        model = CropYieldModel(crop_type="corn")
        analyzer = AgriculturalAnalysis(model=model)
        
        # Test valid input
        analyzer._validate_inputs(sample_field_data)
        
        # Test invalid input (not a GeoDataFrame)
        with pytest.raises(ValueError):
            analyzer._validate_inputs(pd.DataFrame())
        
        # Test with specific required inputs
        model.required_inputs = ["weather"]
        analyzer = AgriculturalAnalysis(model=model)
        
        with pytest.raises(ValueError):
            analyzer._validate_inputs(sample_field_data)

    def test_prepare_data(self, sample_field_data, sample_weather_data, sample_soil_data):
        """Test data preparation for model input."""
        model = CropYieldModel(crop_type="corn")
        analyzer = AgriculturalAnalysis(model=model)
        
        prepared_data = analyzer._prepare_data(
            sample_field_data,
            sample_weather_data,
            sample_soil_data
        )
        
        assert "field_data" in prepared_data
        assert prepared_data["field_data"] is sample_field_data
        assert "weather_data" in prepared_data
        assert prepared_data["weather_data"] is sample_weather_data
        assert "soil_data" in prepared_data
        assert prepared_data["soil_data"] is sample_soil_data

    def test_run_analysis(self, sample_field_data, sample_weather_data, mocker):
        """Test running the agricultural analysis."""
        # Create a mock model
        mock_model = mocker.Mock()
        mock_model.required_inputs = []
        mock_model.predict.return_value = {
            "predictions": [5.0, 6.0, 7.0],
            "spatial_results": {
                "predicted_yield": [5.0, 6.0, 7.0]
            },
            "metadata": {
                "name": "test_model",
                "crop_type": "corn"
            }
        }
        mock_model.metadata = {"name": "test_model"}
        
        # Create the analyzer
        analyzer = AgriculturalAnalysis(model=mock_model)
        
        # Run the analysis
        results = analyzer.run(
            field_data=sample_field_data,
            weather_data=sample_weather_data
        )
        
        # Check that the model was called with the right data
        mock_model.predict.assert_called_once()
        
        # Check results
        assert isinstance(results, AgriculturalResults)
        assert analyzer.results is results
        assert "predicted_yield" in results.field_data.columns
        
        # Check that spatial results were merged with field data
        assert results.field_data["predicted_yield"].tolist() == [5.0, 6.0, 7.0]


class TestAgriculturalResults:
    """Test suite for AgriculturalResults class."""

    def test_initialization(self, sample_field_data):
        """Test initialization of AgriculturalResults."""
        model_results = {
            "predictions": [5.0, 6.0, 7.0],
            "spatial_results": {
                "predicted_yield": [5.0, 6.0, 7.0]
            }
        }
        model_metadata = {"name": "test_model"}
        
        results = AgriculturalResults(
            model_results=model_results,
            field_data=sample_field_data,
            model_metadata=model_metadata
        )
        
        assert results.results == model_results
        assert isinstance(results.field_data, gpd.GeoDataFrame)
        assert "predicted_yield" in results.field_data.columns
        assert "timestamp" in results.metadata
        assert results.metadata["model"] == model_metadata

    def test_merge_results(self, sample_field_data):
        """Test merging results with field data."""
        # Create results without spatial_results
        model_results = {
            "predictions": [5.0, 6.0, 7.0]
        }
        model_metadata = {"name": "test_model"}
        
        results = AgriculturalResults(
            model_results=model_results,
            field_data=sample_field_data,
            model_metadata=model_metadata
        )
        
        # No spatial_results should not modify field_data
        assert "predicted_yield" not in results.field_data.columns
        
        # Create results with spatial_results
        model_results = {
            "predictions": [5.0, 6.0, 7.0],
            "spatial_results": {
                "predicted_yield": [5.0, 6.0, 7.0],
                "confidence": [0.8, 0.9, 0.7]
            }
        }
        
        results = AgriculturalResults(
            model_results=model_results,
            field_data=sample_field_data,
            model_metadata=model_metadata
        )
        
        assert "predicted_yield" in results.field_data.columns
        assert "confidence" in results.field_data.columns
        assert results.field_data["predicted_yield"].tolist() == [5.0, 6.0, 7.0]
        assert results.field_data["confidence"].tolist() == [0.8, 0.9, 0.7]

    def test_get_metric(self, sample_field_data):
        """Test getting metrics from results."""
        model_results = {
            "predictions": [5.0, 6.0, 7.0],
            "mean_yield": 6.0,
            "spatial_results": {
                "predicted_yield": [5.0, 6.0, 7.0]
            }
        }
        model_metadata = {"name": "test_model"}
        
        results = AgriculturalResults(
            model_results=model_results,
            field_data=sample_field_data,
            model_metadata=model_metadata
        )
        
        assert results.get_metric("mean_yield") == 6.0
        assert results.get_metric("predictions") == [5.0, 6.0, 7.0]
        
        with pytest.raises(KeyError):
            results.get_metric("nonexistent_metric")

    def test_summary(self, sample_field_data):
        """Test generating summary statistics."""
        model_results = {
            "predictions": [5.0, 6.0, 7.0],
            "spatial_results": {
                "predicted_yield": [5.0, 6.0, 7.0]
            }
        }
        model_metadata = {"name": "test_model"}
        
        results = AgriculturalResults(
            model_results=model_results,
            field_data=sample_field_data,
            model_metadata=model_metadata
        )
        
        summary = results.summary()
        
        assert "timestamp" in summary
        assert "model_name" in summary
        assert summary["field_count"] == 3
        assert "predicted_yield_mean" in summary
        assert summary["predicted_yield_mean"] == 6.0 