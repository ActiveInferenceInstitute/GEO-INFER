"""
Soil health modeling and assessment functionality.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

from geo_infer_ag.models.base import AgricultureModel


class SoilHealthModel(AgricultureModel):
    """
    Model for predicting and assessing soil health metrics.
    
    This model evaluates soil health using a combination of soil properties, management
    practices, and environmental conditions.
    
    Attributes:
        soil_indicators: List of soil health indicators predicted by the model
        model_type: Type of underlying model ('index_based', 'machine_learning', 'process_based')
        predictors: Dictionary of predictive models for each soil indicator
    """
    
    def __init__(
        self,
        soil_indicators: Optional[List[str]] = None,
        model_type: str = "index_based",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the soil health model.
        
        Args:
            soil_indicators: List of soil health indicators to model
            model_type: Type of model to use for prediction
            config: Optional configuration parameters
        """
        name = "soil_health_model"
        super().__init__(name=name, config=config)
        
        # Default soil health indicators if not provided
        if soil_indicators is None:
            self.soil_indicators = [
                "organic_matter",
                "aggregate_stability",
                "microbial_activity",
                "ph_balance",
                "nutrient_availability",
                "compact_cellsion",
                "infiltration_rate"
            ]
        else:
            self.soil_indicators = soil_indicators
            
        self.model_type = model_type
        self.predictors = {}
        self.fitted = False
        
        # Define required inputs based on model type
        if model_type == "index_based":
            self.required_inputs = ["field_data", "soil_data"]
        elif model_type == "machine_learning":
            self.required_inputs = ["field_data", "soil_data"]
        elif model_type == "process_based":
            self.required_inputs = ["field_data", "soil_data", "weather_data", "management_data"]
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        # Update metadata
        self.metadata.update({
            "soil_indicators": self.soil_indicators,
            "model_type": model_type
        })
        
        # Initialize indicator weights for index-based models
        self.indicator_weights = {
            "organic_matter": 0.25,
            "aggregate_stability": 0.15,
            "microbial_activity": 0.15,
            "ph_balance": 0.10,
            "nutrient_availability": 0.15,
            "compact_cellsion": 0.10,
            "infiltration_rate": 0.10
        }
        
        # Filter weights to only include requested indicators
        if soil_indicators is not None:
            self.indicator_weights = {
                k: v for k, v in self.indicator_weights.items() if k in soil_indicators
            }
            
            # Normalize weights
            weight_sum = sum(self.indicator_weights.values())
            self.indicator_weights = {k: v/weight_sum for k, v in self.indicator_weights.items()}
    
    def fit(
        self,
        training_data: Dict[str, Any],
        target_columns: Optional[Dict[str, str]] = None,
        feature_columns: Optional[List[str]] = None
    ) -> None:
        """
        Train the soil health prediction model using historical data.
        
        Args:
            training_data: Dictionary of training data sources
            target_columns: Optional mapping of indicators to target columns
            feature_columns: Optional list of feature columns to use
            
        Raises:
            ValueError: If required training data is missing
        """
        # Validate required training data
        if "field_data" not in training_data or "soil_data" not in training_data:
            raise ValueError("Field data and soil data required for training")
        
        # Only machine learning models need fitting
        if self.model_type != "machine_learning":
            self.fitted = True
            return
            
        # Get training soil data
        soil_df = training_data["soil_data"]
        
        # Default target columns if not provided
        if target_columns is None:
            # Assume column names match indicator names
            target_columns = {indicator: indicator for indicator in self.soil_indicators}
        
        # Check that all target columns exist
        for indicator, column in target_columns.items():
            if column not in soil_df.columns:
                raise ValueError(f"Target column '{column}' for indicator '{indicator}' not found in training data")
        
        # Default feature columns if not provided
        if feature_columns is None:
            # Use all numeric columns except target columns
            numeric_cols = soil_df.select_dtypes(include=['number']).columns.tolist()
            target_cols = list(target_columns.values())
            feature_columns = [col for col in numeric_cols if col not in target_cols]
        
        # Train a separate model for each soil health indicator
        for indicator in self.soil_indicators:
            # Get target column for this indicator
            target_col = target_columns[indicator]
            
            # Initialize a RandomForest model
            predictor = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            
            # Train the model
            X = soil_df[feature_columns]
            y = soil_df[target_col]
            
            # Skip indicators with insufficient data
            if len(y.dropna()) < 10:
                continue
                
            predictor.fit(X.loc[y.notna()], y.dropna())
            
            # Store the trained model
            self.predictors[indicator] = {
                "model": predictor,
                "feature_columns": feature_columns
            }
        
        self.fitted = True
        
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict soil health indicators using the model.
        
        Args:
            data: Dictionary of input data sources
            
        Returns:
            Dictionary containing soil health predictions and metadata
            
        Raises:
            ValueError: If required inputs are missing
        """
        # Validate required inputs
        self.validate_inputs(data)
        
        # Get field and soil data
        field_data = data["field_data"]
        soil_data = data["soil_data"]
        
        # Generate predictions based on model type
        if self.model_type == "index_based":
            # Index-based approach uses weighted combination of soil properties
            # This is a simplified implementation - a real model would have more sophisticated logic
            
            # Check required soil properties
            required_soil_props = ["organic_matter", "ph", "bulk_density"]
            missing_props = [prop for prop in required_soil_props if prop not in soil_data.columns]
            
            if missing_props:
                raise ValueError(f"Missing required soil properties: {missing_props}")
            
            # Calculate individual indicator scores (0-10 scale)
            indicator_scores = {}
            
            # Organic matter score (higher is better)
            if "organic_matter" in self.soil_indicators:
                indicator_scores["organic_matter"] = np.clip(soil_data["organic_matter"] * 2, 0, 10)
                
            # pH balance score (optimal range around 6.5)
            if "ph_balance" in self.soil_indicators:
                indicator_scores["ph_balance"] = 10 - np.clip(np.abs(soil_data["ph"] - 6.5) * 3, 0, 10)
                
            # Compaction score (lower bulk density is better)
            if "compact_cellsion" in self.soil_indicators:
                # Assuming bulk_density in g/cm³, lower is better
                # 1.6 or higher is bad (score 0), 1.0 or lower is good (score 10)
                indicator_scores["compact_cellsion"] = np.clip(10 - ((soil_data["bulk_density"] - 1.0) * 16.67), 0, 10)
            
            # For other indicators, we'd need additional soil properties
            # Here we're using dummy values for illustration
            for indicator in self.soil_indicators:
                if indicator not in indicator_scores:
                    # Use random values as placeholders
                    np.random.seed(42)  # For reproducibility
                    indicator_scores[indicator] = np.random.uniform(4, 8, size=len(soil_data))
            
            # Calculate weighted soil health index
            soil_health_index = np.zeros(len(soil_data))
            
            for indicator, weight in self.indicator_weights.items():
                if indicator in indicator_scores:
                    soil_health_index += indicator_scores[indicator] * weight
            
            # Add predictions to results
            result = {
                "soil_health_index": soil_health_index,
                "indicator_scores": indicator_scores,
                "spatial_results": {
                    "soil_health_index": soil_health_index
                },
                "metadata": {
                    "prediction_time": datetime.now().isoformat(),
                    "model_type": self.model_type,
                    "indicators": self.soil_indicators,
                    "weights": self.indicator_weights
                }
            }
            
            # Add individual indicator results to spatial results
            for indicator, scores in indicator_scores.items():
                result["spatial_results"][f"{indicator}_score"] = scores
            
            # Calculate summary statistics
            result["summary"] = {
                "mean_soil_health_index": float(np.mean(soil_health_index)),
                "min_soil_health_index": float(np.min(soil_health_index)),
                "max_soil_health_index": float(np.max(soil_health_index)),
                "std_soil_health_index": float(np.std(soil_health_index))
            }
            
        elif self.model_type == "machine_learning":
            # Check if model is fitted
            if not self.fitted:
                raise ValueError("Model must be fitted before prediction")
                
            # Check that we have predictors for at least some indicators
            if not self.predictors:
                raise ValueError("No trained predictors available. Run fit() first")
            
            # Make predictions for each indicator
            indicator_predictions = {}
            
            for indicator, predictor_info in self.predictors.items():
                predictor = predictor_info["model"]
                feature_cols = predictor_info["feature_columns"]
                
                # Check if all feature columns are available
                missing_features = [col for col in feature_cols if col not in soil_data.columns]
                if missing_features:
                    continue  # Skip this indicator
                    
                # Generate predictions
                X = soil_data[feature_cols]
                predictions = predictor.predict(X)
                
                # Store predictions
                indicator_predictions[indicator] = predictions
            
            # Calculate soil health index as weighted average of indicator predictions
            soil_health_index = np.zeros(len(soil_data))
            valid_weights = {}
            
            for indicator, weight in self.indicator_weights.items():
                if indicator in indicator_predictions:
                    # Normalize predictions to 0-10 scale
                    norm_predictions = np.clip(indicator_predictions[indicator], 0, 10)
                    soil_health_index += norm_predictions * weight
                    valid_weights[indicator] = weight
            
            # Renormalize if not all indicators were predicted
            if valid_weights and len(valid_weights) < len(self.indicator_weights):
                weight_sum = sum(valid_weights.values())
                soil_health_index = soil_health_index * (1.0 / weight_sum)
            
            # Add predictions to results
            result = {
                "soil_health_index": soil_health_index,
                "indicator_predictions": indicator_predictions,
                "spatial_results": {
                    "soil_health_index": soil_health_index
                },
                "metadata": {
                    "prediction_time": datetime.now().isoformat(),
                    "model_type": self.model_type,
                    "indicators": list(indicator_predictions.keys()),
                    "weights": valid_weights
                }
            }
            
            # Add individual indicator results to spatial results
            for indicator, predictions in indicator_predictions.items():
                result["spatial_results"][indicator] = predictions
            
            # Calculate summary statistics
            result["summary"] = {
                "mean_soil_health_index": float(np.mean(soil_health_index)),
                "min_soil_health_index": float(np.min(soil_health_index)),
                "max_soil_health_index": float(np.max(soil_health_index)),
                "std_soil_health_index": float(np.std(soil_health_index))
            }
            
        elif self.model_type == "process_based":
            # Process-based prediction using soil process simulation
            # These models require detailed weather, soil, and management data
            required_process_data = ["weather_data", "management_data"]
            missing_data = [d for d in required_process_data if d not in data]
            
            if missing_data:
                raise ValueError(f"Missing data for process-based model: {missing_data}")
            
            # Implement process-based prediction logic
            # This would typically involve sophisticated soil process simulation
            
            # Placeholder for actual implementation
            soil_health_index = np.ones(len(soil_data)) * 7.0  # Dummy predictions
            
            # Create dummy indicator scores
            indicator_scores = {}
            for indicator in self.soil_indicators:
                np.random.seed(sum(map(ord, indicator)))  # Seed based on indicator name
                indicator_scores[indicator] = np.random.uniform(5, 9, size=len(soil_data))
            
            # Add predictions to results
            result = {
                "soil_health_index": soil_health_index,
                "indicator_scores": indicator_scores,
                "spatial_results": {
                    "soil_health_index": soil_health_index
                },
                "metadata": {
                    "prediction_time": datetime.now().isoformat(),
                    "model_type": self.model_type,
                    "indicators": self.soil_indicators
                }
            }
            
            # Add individual indicator results to spatial results
            for indicator, scores in indicator_scores.items():
                result["spatial_results"][f"{indicator}_score"] = scores
            
            # Calculate summary statistics
            result["summary"] = {
                "mean_soil_health_index": float(np.mean(soil_health_index)),
                "min_soil_health_index": float(np.min(soil_health_index)),
                "max_soil_health_index": float(np.max(soil_health_index)),
                "std_soil_health_index": float(np.std(soil_health_index))
            }
        
        return result
    
    def get_limiting_factors(self, result: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Identify limiting soil health factors for each field.
        
        Args:
            result: Result dictionary from predict method
            
        Returns:
            Dictionary mapping field IDs to lists of limiting factors
        """
        if not result or "indicator_scores" not in result and "indicator_predictions" not in result:
            raise ValueError("Invalid result dictionary. Run predict() first")
            
        # Get indicator scores/predictions
        if "indicator_scores" in result:
            indicators = result["indicator_scores"]
        else:
            indicators = result["indicator_predictions"]
            
        # Create a threshold for identifying limiting factors
        threshold = 5.0  # Below this is considered limiting
        
        # Identify limiting factors for each row
        limiting_factors = {}
        
        for i in range(len(next(iter(indicators.values())))):
            field_id = f"field_{i+1}"  # Placeholder if real IDs aren't available
            
            # Find indicators below threshold
            limiting = [
                indicator for indicator, scores in indicators.items()
                if scores[i] < threshold
            ]
            
            # Store if any limiting factors found
            if limiting:
                limiting_factors[field_id] = limiting
                
        return limiting_factors
    
    def save(self, path: str) -> None:
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
        """
        import joblib
        
        # Create a dictionary with all model components
        model_data = {
            "metadata": self.metadata,
            "soil_indicators": self.soil_indicators,
            "model_type": self.model_type,
            "required_inputs": self.required_inputs,
            "fitted": self.fitted,
            "config": self.config,
            "indicator_weights": self.indicator_weights
        }
        
        # Add model-type specific components
        if self.model_type == "machine_learning" and self.fitted:
            model_data["predictors"] = self.predictors
        
        # Save to disk
        joblib.dump(model_data, path)
    
    @classmethod
    def load(cls, path: str) -> "SoilHealthModel":
        """
        Load a model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            Loaded model instance
        """
        import joblib
        
        # Load saved model data
        model_data = joblib.load(path)
        
        # Create a new instance
        model = cls(
            soil_indicators=model_data["soil_indicators"],
            model_type=model_data["model_type"],
            config=model_data["config"]
        )
        
        # Restore model attributes
        model.fitted = model_data["fitted"]
        model.indicator_weights = model_data["indicator_weights"]
        
        # Restore model-type specific components
        if model.model_type == "machine_learning" and model.fitted:
            model.predictors = model_data["predictors"]
        
        return model 