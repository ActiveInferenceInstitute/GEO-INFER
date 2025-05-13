"""Unit tests for the CropYieldModel class."""

import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
import tempfile
import os
from shapely.geometry import Polygon
from sklearn.ensemble import RandomForestRegressor

from geo_infer_ag.models.crop_yield import CropYieldModel


class TestCropYieldModel:
    """Test suite for CropYieldModel class."""
    
    def test_initialization(self):
        """Test initialization of CropYieldModel."""
        model = CropYieldModel(crop_type="corn")
        
        assert model.name == "corn_yield_model"
        assert model.crop_type == "corn"
        assert model.model_type == "machine_learning"
        assert model.predictor is None
        assert model.fitted is False
        assert "field_data" in model.required_inputs
        
        # Check metadata
        assert model.metadata["crop_type"] == "corn"
        assert model.metadata["model_type"] == "machine_learning"
        
        # Test with different model type
        model = CropYieldModel(crop_type="wheat", model_type="statistical")
        assert model.model_type == "statistical"
        assert "field_data" in model.required_inputs
        assert "historical_yield_data" in model.required_inputs
        
        # Test with process-based model type
        model = CropYieldModel(crop_type="soybean", model_type="process_based")
        assert model.model_type == "process_based"
        assert "field_data" in model.required_inputs
        assert "weather_data" in model.required_inputs
        assert "soil_data" in model.required_inputs
        assert "management_data" in model.required_inputs
        
        # Test with invalid model type
        with pytest.raises(ValueError):
            CropYieldModel(crop_type="corn", model_type="invalid_type")
    
    def test_fit_machine_learning(self):
        """Test fitting a machine learning model."""
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        
        # Create some test training data
        field_data = gpd.GeoDataFrame(
            {
                "field_id": ["f1", "f2", "f3", "f4", "f5"],
                "area_ha": [10, 5, 7, 12, 8],
                "elevation": [100, 120, 90, 110, 105],
                "slope": [2, 4, 1, 3, 2],
                "soil_quality": [8, 6, 7, 9, 7],
                "yield": [8.5, 6.2, 7.1, 9.3, 7.8],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(5)
                ]
            },
            crs="EPSG:4326"
        )
        
        # Fit the model
        model.fit(
            training_data={"field_data": field_data},
            target_column="yield",
            feature_columns=["area_ha", "elevation", "slope", "soil_quality"]
        )
        
        # Check that the model is fitted
        assert model.fitted is True
        assert model.predictor is not None
        assert isinstance(model.predictor, RandomForestRegressor)
        assert model.feature_columns == ["area_ha", "elevation", "slope", "soil_quality"]
        
        # Test fitting without feature columns specified
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        model.fit(
            training_data={"field_data": field_data},
            target_column="yield"
        )
        
        assert model.fitted is True
        assert set(model.feature_columns) == {"area_ha", "elevation", "slope", "soil_quality"}
        
        # Test fit with missing target column
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        field_data_no_yield = field_data.drop(columns=["yield"])
        
        with pytest.raises(ValueError):
            model.fit(
                training_data={"field_data": field_data_no_yield},
                target_column="yield"
            )
    
    def test_predict_machine_learning(self):
        """Test making predictions with a machine learning model."""
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        
        # Create and fit with training data
        train_fields = gpd.GeoDataFrame(
            {
                "field_id": ["f1", "f2", "f3", "f4", "f5"],
                "area_ha": [10, 5, 7, 12, 8],
                "elevation": [100, 120, 90, 110, 105],
                "soil_quality": [8, 6, 7, 9, 7],
                "yield": [8.5, 6.2, 7.1, 9.3, 7.8],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(5)
                ]
            },
            crs="EPSG:4326"
        )
        
        model.fit(
            training_data={"field_data": train_fields},
            target_column="yield",
            feature_columns=["area_ha", "elevation", "soil_quality"]
        )
        
        # Create test prediction data
        test_fields = gpd.GeoDataFrame(
            {
                "field_id": ["t1", "t2", "t3"],
                "area_ha": [9, 6, 11],
                "elevation": [105, 115, 95],
                "soil_quality": [7, 8, 6],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(3)
                ]
            },
            crs="EPSG:4326"
        )
        
        # Make predictions
        result = model.predict(data={"field_data": test_fields})
        
        # Check that predictions were made
        assert "predictions" in result
        assert len(result["predictions"]) == 3
        assert "spatial_results" in result
        assert "predicted_yield" in result["spatial_results"]
        assert len(result["spatial_results"]["predicted_yield"]) == 3
        assert "metadata" in result
        assert result["metadata"]["crop_type"] == "corn"
        
        # Test with missing feature columns
        test_fields_missing = test_fields.drop(columns=["soil_quality"])
        with pytest.raises(ValueError):
            model.predict(data={"field_data": test_fields_missing})
            
        # Test prediction without fitting
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        with pytest.raises(ValueError):
            model.predict(data={"field_data": test_fields})
    
    def test_predict_statistical(self):
        """Test making predictions with a statistical model."""
        model = CropYieldModel(crop_type="wheat", model_type="statistical")
        
        # For statistical models, we don't need to fit first
        assert model.fitted is False
        
        # Create test prediction data
        test_fields = gpd.GeoDataFrame(
            {
                "field_id": ["t1", "t2", "t3"],
                "area_ha": [9, 6, 11],
                "crop_type": ["wheat", "wheat", "wheat"],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(3)
                ]
            },
            crs="EPSG:4326"
        )
        
        historical_yield_data = pd.DataFrame({
            "year": [2018, 2019, 2020],
            "region": ["A", "A", "A"],
            "wheat_yield": [5.2, 5.8, 5.5]
        })
        
        # Make predictions
        result = model.predict(data={
            "field_data": test_fields,
            "historical_yield_data": historical_yield_data
        })
        
        # Check that predictions were made
        assert "predictions" in result
        assert len(result["predictions"]) == 3
        assert "spatial_results" in result
        assert "predicted_yield" in result["spatial_results"]
        assert len(result["spatial_results"]["predicted_yield"]) == 3
        assert "metadata" in result
        assert result["metadata"]["crop_type"] == "wheat"
        assert "summary" in result
        
        # Test missing required inputs
        with pytest.raises(ValueError):
            model.predict(data={"field_data": test_fields})
    
    def test_predict_process_based(self):
        """Test making predictions with a process-based model."""
        model = CropYieldModel(crop_type="soybean", model_type="process_based")
        
        # For process-based models, we don't need to fit first
        assert model.fitted is False
        
        # Create test prediction data
        test_fields = gpd.GeoDataFrame(
            {
                "field_id": ["t1", "t2"],
                "area_ha": [9, 6],
                "crop_type": ["soybean", "soybean"],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(2)
                ]
            },
            crs="EPSG:4326"
        )
        
        # Create other required data
        weather_data = pd.DataFrame({
            "date": pd.date_range(start="2023-01-01", periods=10),
            "temperature": np.random.uniform(15, 30, 10),
            "precipitation": np.random.uniform(0, 20, 10)
        })
        
        soil_data = gpd.GeoDataFrame(
            {
                "field_id": ["t1", "t2"],
                "organic_matter": [2.5, 3.1],
                "ph": [6.8, 7.2],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(2)
                ]
            },
            crs="EPSG:4326"
        )
        
        management_data = pd.DataFrame({
            "field_id": ["t1", "t2"],
            "planting_date": ["2023-04-15", "2023-04-20"],
            "fertilizer_applied": [200, 180]
        })
        
        # Make predictions
        result = model.predict(data={
            "field_data": test_fields,
            "weather_data": weather_data,
            "soil_data": soil_data,
            "management_data": management_data
        })
        
        # Check that predictions were made
        assert "predictions" in result
        assert len(result["predictions"]) == 2
        assert "spatial_results" in result
        assert "predicted_yield" in result["spatial_results"]
        assert len(result["spatial_results"]["predicted_yield"]) == 2
        assert "metadata" in result
        assert result["metadata"]["crop_type"] == "soybean"
        
        # Test missing required inputs
        with pytest.raises(ValueError):
            model.predict(data={
                "field_data": test_fields,
                "weather_data": weather_data
            })
    
    def test_get_feature_importance(self):
        """Test getting feature importance from a trained model."""
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        
        # Create and fit with training data
        train_fields = gpd.GeoDataFrame(
            {
                "field_id": ["f1", "f2", "f3", "f4", "f5"],
                "area_ha": [10, 5, 7, 12, 8],
                "elevation": [100, 120, 90, 110, 105],
                "rainfall": [800, 700, 850, 780, 820],
                "yield": [8.5, 6.2, 7.1, 9.3, 7.8],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(5)
                ]
            },
            crs="EPSG:4326"
        )
        
        model.fit(
            training_data={"field_data": train_fields},
            target_column="yield",
            feature_columns=["area_ha", "elevation", "rainfall"]
        )
        
        # Get feature importance
        importance = model.get_feature_importance()
        
        # Check that feature importance was calculated
        assert isinstance(importance, dict)
        assert len(importance) == 3
        assert set(importance.keys()) == {"area_ha", "elevation", "rainfall"}
        assert sum(importance.values()) == pytest.approx(1.0)
        
        # Test with unfitted model
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        with pytest.raises(ValueError):
            model.get_feature_importance()
            
        # Test with non-machine learning model
        model = CropYieldModel(crop_type="corn", model_type="statistical")
        with pytest.raises(ValueError):
            model.get_feature_importance()
    
    def test_save_load(self):
        """Test saving and loading a model."""
        # Create and fit a model
        model = CropYieldModel(crop_type="corn", model_type="machine_learning")
        
        train_fields = gpd.GeoDataFrame(
            {
                "field_id": ["f1", "f2", "f3", "f4", "f5"],
                "area_ha": [10, 5, 7, 12, 8],
                "elevation": [100, 120, 90, 110, 105],
                "yield": [8.5, 6.2, 7.1, 9.3, 7.8],
                "geometry": [
                    Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]) for _ in range(5)
                ]
            },
            crs="EPSG:4326"
        )
        
        model.fit(
            training_data={"field_data": train_fields},
            target_column="yield",
            feature_columns=["area_ha", "elevation"]
        )
        
        # Create a temporary file for saving
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as tmp:
            save_path = tmp.name
        
        try:
            # Save the model
            model.save(save_path)
            
            # Load the model
            loaded_model = CropYieldModel.load(save_path)
            
            # Check that the loaded model has the same attributes
            assert loaded_model.name == model.name
            assert loaded_model.crop_type == model.crop_type
            assert loaded_model.model_type == model.model_type
            assert loaded_model.fitted == model.fitted
            assert loaded_model.feature_columns == model.feature_columns
            
            # Try making a prediction with the loaded model
            test_fields = gpd.GeoDataFrame(
                {
                    "field_id": ["t1"],
                    "area_ha": [9],
                    "elevation": [105],
                    "geometry": [Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])]
                },
                crs="EPSG:4326"
            )
            
            result = loaded_model.predict(data={"field_data": test_fields})
            
            # Check that predictions were made
            assert "predictions" in result
            assert len(result["predictions"]) == 1
            
        finally:
            # Clean up the temporary file
            if os.path.exists(save_path):
                os.unlink(save_path) 