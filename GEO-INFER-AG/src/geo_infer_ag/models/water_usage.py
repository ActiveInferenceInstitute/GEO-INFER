"""
Agricultural water usage modeling functionality.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

from geo_infer_ag.models.base import AgricultureModel


class WaterUsageModel(AgricultureModel):
    """
    Model for predicting agricultural water usage and requirements.
    
    This model predicts crop water requirements, irrigation needs, water efficiency,
    and other water-related metrics for agricultural fields.
    
    Attributes:
        crop_type: Type of crop for water usage prediction
        model_type: Type of underlying model ('reference_et', 'statistical', 'process_based')
        water_balance_components: List of water balance components to model
    """
    
    def __init__(
        self,
        crop_type: Optional[str] = None,
        model_type: str = "reference_et",
        water_balance_components: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the water usage model.
        
        Args:
            crop_type: Optional crop type (can be used for crop-specific models)
            model_type: Type of model to use for prediction
            water_balance_components: Optional list of water balance components to model
            config: Optional configuration parameters
        """
        name = "water_usage_model"
        if crop_type:
            name = f"{crop_type}_water_usage_model"
            
        super().__init__(name=name, config=config)
        
        self.crop_type = crop_type
        self.model_type = model_type
        self.predictor = None
        self.fitted = False
        
        # Default water balance components if not provided
        if water_balance_components is None:
            self.water_balance_components = [
                "evapotranspiration", 
                "precipitation", 
                "irrigation", 
                "runoff", 
                "drainage"
            ]
        else:
            self.water_balance_components = water_balance_components
            
        # Define required inputs based on model type
        if model_type == "reference_et":
            self.required_inputs = ["field_data", "weather_data"]
        elif model_type == "statistical":
            self.required_inputs = ["field_data", "weather_data"]
        elif model_type == "process_based":
            self.required_inputs = ["field_data", "weather_data", "soil_data", "management_data"]
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        # Update metadata
        self.metadata.update({
            "crop_type": crop_type,
            "model_type": model_type,
            "water_balance_components": self.water_balance_components
        })
        
        # Initialize crop coefficients for ET-based methods
        self.crop_coefficients = {
            "corn": {"initial": 0.3, "mid": 1.2, "end": 0.6, "length_days": [30, 40, 50, 30]},
            "wheat": {"initial": 0.3, "mid": 1.15, "end": 0.4, "length_days": [20, 30, 60, 30]},
            "rice": {"initial": 1.05, "mid": 1.2, "end": 0.9, "length_days": [30, 30, 60, 30]},
            "soybean": {"initial": 0.4, "mid": 1.15, "end": 0.5, "length_days": [20, 30, 60, 30]},
            "cotton": {"initial": 0.35, "mid": 1.2, "end": 0.6, "length_days": [30, 50, 60, 50]},
            "alfalfa": {"initial": 0.4, "mid": 0.95, "end": 0.9, "length_days": [10, 30, 150, 30]},
            "generic": {"initial": 0.3, "mid": 1.0, "end": 0.5, "length_days": [25, 35, 50, 25]}
        }
    
    def fit(
        self,
        training_data: Dict[str, Any],
        target_column: str = "water_usage",
        feature_columns: Optional[List[str]] = None
    ) -> None:
        """
        Train the water usage prediction model using historical data.
        
        Args:
            training_data: Dictionary of training data sources
            target_column: Column name containing water usage values
            feature_columns: Optional list of feature columns to use
            
        Raises:
            ValueError: If required training data is missing
        """
        # Only statistical models require fitting
        if self.model_type not in ["statistical"]:
            self.fitted = True
            return
            
        # Validate required training data
        if "field_data" not in training_data or "weather_data" not in training_data:
            raise ValueError("Field data and weather data required for training")
            
        # Combine field and weather data for training
        field_data = training_data["field_data"]
        weather_data = training_data["weather_data"]
        
        # This is a simplification - in a real model, you would need to properly join
        # and align the field data with weather data, potentially using time series
        # aggregation and spatial joins
        
        # For simplicity, assume field_data already has the target_column
        train_df = field_data
        
        # Ensure target column exists
        if target_column not in train_df.columns:
            raise ValueError(f"Target column '{target_column}' not found in training data")
        
        # Default feature columns if not provided
        if feature_columns is None:
            # Use all numeric columns except the target
            numeric_cols = train_df.select_dtypes(include=['number']).columns.tolist()
            feature_columns = [col for col in numeric_cols if col != target_column]
        
        # Initialize and train a RandomForest model for statistical prediction
        self.predictor = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        # Train the model
        X = train_df[feature_columns]
        y = train_df[target_column]
        
        self.predictor.fit(X, y)
        self.feature_columns = feature_columns
            
        self.fitted = True
        
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict water usage metrics using the model.
        
        Args:
            data: Dictionary of input data sources
            
        Returns:
            Dictionary containing water usage predictions and metadata
            
        Raises:
            ValueError: If required inputs are missing
        """
        # Validate required inputs
        self.validate_inputs(data)
        
        # Get field and weather data
        field_data = data["field_data"]
        weather_data = data["weather_data"]
        
        # Check if weather data is properly formatted
        required_weather_vars = ["temperature", "solar_radiation", "humidity", "wind_speed"]
        missing_vars = [var for var in required_weather_vars if var not in weather_data.columns]
        
        if missing_vars and self.model_type in ["reference_et", "process_based"]:
            raise ValueError(f"Missing required weather variables: {missing_vars}")
            
        # Generate predictions based on model type
        if self.model_type == "reference_et":
            # Reference ET approach calculates crop water requirements based on
            # reference evapotranspiration and crop coefficients
            
            # Calculate reference ET (using simplified Penman-Monteith equation)
            # Normally this would use a more complex implementation
            reference_et = self._calculate_reference_et(weather_data)
            
            # Get crop coefficients for the crop type (or use generic)
            crop_type = self.crop_type or "generic"
            crop_coeffs = self.crop_coefficients.get(
                crop_type.lower(), 
                self.crop_coefficients["generic"]
            )
            
            # For simplification, use the mid-season coefficient
            # In a real model, you would determine growth stage and use the appropriate coefficient
            kc = crop_coeffs["mid"]
            
            # Calculate crop ET (crop water requirement)
            crop_et = reference_et * kc
            
            # Calculate irrigation requirement (simplified)
            # In reality, this would account for effective rainfall, soil moisture, etc.
            effective_rainfall = weather_data["precipitation"] * 0.7  # Assume 70% effectiveness
            irrigation_requirement = np.maximum(0, crop_et - effective_rainfall)
            
            # Calculate water metrics for each field
            num_fields = len(field_data)
            
            # Aggregate daily values to seasonal totals
            # This is simplistic - a real model would account for crop calendars
            seasonal_et = crop_et.sum() if isinstance(crop_et, pd.Series) else crop_et
            seasonal_rainfall = effective_rainfall.sum() if isinstance(effective_rainfall, pd.Series) else effective_rainfall
            seasonal_irrigation = irrigation_requirement.sum() if isinstance(irrigation_requirement, pd.Series) else irrigation_requirement
            
            # Create field-level predictions
            # For simplicity, we're applying the same values to all fields
            # In practice, you would account for spatial variations
            water_requirement = np.full(num_fields, seasonal_et)
            water_requirement_m3 = water_requirement * field_data["area_ha"] * 10  # mm * ha * 10 = m³
            
            irrigation_requirement_values = np.full(num_fields, seasonal_irrigation)
            irrigation_m3 = irrigation_requirement_values * field_data["area_ha"] * 10
            
            effective_rainfall_values = np.full(num_fields, seasonal_rainfall)
            rainfall_m3 = effective_rainfall_values * field_data["area_ha"] * 10
            
            # Calculate water efficiency metrics
            water_productivity = 1.0  # Yield (t/ha) / water use (mm) - placeholder value
            if "yield" in field_data.columns:
                # If yield data is available, calculate actual water productivity
                water_productivity = field_data["yield"] / water_requirement
            
            # Add predictions to results
            result = {
                "water_requirement_mm": water_requirement,
                "water_requirement_m3": water_requirement_m3,
                "irrigation_requirement_mm": irrigation_requirement_values,
                "irrigation_requirement_m3": irrigation_m3,
                "effective_rainfall_mm": effective_rainfall_values,
                "effective_rainfall_m3": rainfall_m3,
                "water_productivity": water_productivity,
                "spatial_results": {
                    "water_requirement_mm": water_requirement,
                    "irrigation_requirement_mm": irrigation_requirement_values,
                    "effective_rainfall_mm": effective_rainfall_values,
                    "water_productivity": water_productivity
                },
                "metadata": {
                    "prediction_time": datetime.now().isoformat(),
                    "model_type": self.model_type,
                    "crop_type": self.crop_type,
                    "reference_et_method": "simplified_penman_monteith"
                }
            }
            
            # Calculate summary statistics
            result["summary"] = {
                "mean_water_requirement_mm": float(np.mean(water_requirement)),
                "total_water_requirement_m3": float(np.sum(water_requirement_m3)),
                "mean_irrigation_requirement_mm": float(np.mean(irrigation_requirement_values)),
                "total_irrigation_requirement_m3": float(np.sum(irrigation_m3))
            }
            
        elif self.model_type == "statistical":
            # Check if model is fitted
            if not self.fitted:
                raise ValueError("Statistical model must be fitted before prediction")
                
            # Check if all feature columns are available
            missing_features = [col for col in self.feature_columns if col not in field_data.columns]
            if missing_features:
                raise ValueError(f"Missing feature columns: {missing_features}")
                
            # Generate predictions
            X = field_data[self.feature_columns]
            water_usage_predictions = self.predictor.predict(X)
            
            # Calculate water metrics based on predictions
            # Here we assume water_usage_predictions are in mm of water per growing season
            water_requirement = water_usage_predictions
            water_requirement_m3 = water_requirement * field_data["area_ha"] * 10
            
            # Simplified estimation of irrigation requirement
            # In practice, this would be more complex and depend on rainfall
            rainfall_factor = 0.3  # Assume 30% of water comes from rainfall
            irrigation_requirement = water_requirement * (1 - rainfall_factor)
            irrigation_m3 = irrigation_requirement * field_data["area_ha"] * 10
            
            # Add predictions to results
            result = {
                "water_requirement_mm": water_requirement,
                "water_requirement_m3": water_requirement_m3,
                "irrigation_requirement_mm": irrigation_requirement,
                "irrigation_requirement_m3": irrigation_m3,
                "spatial_results": {
                    "water_requirement_mm": water_requirement,
                    "irrigation_requirement_mm": irrigation_requirement
                },
                "metadata": {
                    "prediction_time": datetime.now().isoformat(),
                    "model_type": self.model_type,
                    "crop_type": self.crop_type
                }
            }
            
            # Calculate summary statistics
            result["summary"] = {
                "mean_water_requirement_mm": float(np.mean(water_requirement)),
                "total_water_requirement_m3": float(np.sum(water_requirement_m3)),
                "mean_irrigation_requirement_mm": float(np.mean(irrigation_requirement)),
                "total_irrigation_requirement_m3": float(np.sum(irrigation_m3))
            }
            
        elif self.model_type == "process_based":
            # Process-based prediction using water balance simulation
            # These models require detailed soil, weather, and crop data
            required_process_data = ["soil_data", "management_data"]
            missing_data = [d for d in required_process_data if d not in data]
            
            if missing_data:
                raise ValueError(f"Missing data for process-based model: {missing_data}")
                
            soil_data = data["soil_data"]
            management_data = data["management_data"]
            
            # Implement process-based water balance model
            # This would typically involve a sophisticated simulation of the soil-plant-atmosphere system
            
            # Placeholder for actual implementation
            num_fields = len(field_data)
            water_requirement = np.ones(num_fields) * 500.0  # Dummy values in mm per season
            water_requirement_m3 = water_requirement * field_data["area_ha"] * 10
            
            # Create dummy water balance components
            water_balance = {}
            for component in self.water_balance_components:
                if component == "evapotranspiration":
                    water_balance[component] = water_requirement
                elif component == "precipitation":
                    water_balance[component] = np.ones(num_fields) * 300.0
                elif component == "irrigation":
                    water_balance[component] = np.maximum(0, water_requirement - 300.0)
                elif component == "runoff":
                    water_balance[component] = np.ones(num_fields) * 50.0
                elif component == "drainage":
                    water_balance[component] = np.ones(num_fields) * 70.0
            
            # Add predictions to results
            result = {
                "water_requirement_mm": water_requirement,
                "water_requirement_m3": water_requirement_m3,
                "water_balance": water_balance,
                "spatial_results": {
                    "water_requirement_mm": water_requirement
                },
                "metadata": {
                    "prediction_time": datetime.now().isoformat(),
                    "model_type": self.model_type,
                    "crop_type": self.crop_type,
                    "water_balance_components": self.water_balance_components
                }
            }
            
            # Add water balance components to spatial results
            for component, values in water_balance.items():
                result["spatial_results"][f"{component}_mm"] = values
            
            # Calculate summary statistics
            result["summary"] = {
                "mean_water_requirement_mm": float(np.mean(water_requirement)),
                "total_water_requirement_m3": float(np.sum(water_requirement_m3))
            }
            
            # Add water balance summary
            for component, values in water_balance.items():
                result["summary"][f"mean_{component}_mm"] = float(np.mean(values))
        
        return result
    
    def _calculate_reference_et(self, weather_data: pd.DataFrame) -> Union[float, np.ndarray, pd.Series]:
        """
        Calculate reference evapotranspiration using simplified Penman-Monteith.
        
        Args:
            weather_data: DataFrame with required weather variables
            
        Returns:
            Reference ET values
            
        Note:
            This is a simplified implementation. A real model would use the full
            FAO-56 Penman-Monteith equation and properly handle all required inputs.
        """
        # Extract required variables
        temp = weather_data["temperature"]  # Mean temperature in °C
        solar = weather_data["solar_radiation"]  # Solar radiation in MJ/m²/day
        humidity = weather_data["humidity"]  # Relative humidity in %
        wind = weather_data["wind_speed"]  # Wind speed in m/s
        
        # Simplified ET calculation
        # In reality, this would be the full FAO-56 Penman-Monteith equation
        # This is a very basic approximation
        reference_et = 0.0023 * (temp + 17.8) * np.sqrt(temp) * solar * 0.408
        
        # Apply wind and humidity adjustments
        # These are highly simplified approximations
        wind_factor = 0.8 + 0.2 * np.clip(wind / 5.0, 0, 1)
        humidity_factor = 0.6 + 0.4 * (1 - np.clip(humidity / 100.0, 0, 1))
        
        reference_et = reference_et * wind_factor * humidity_factor
        
        return reference_et
    
    def calculate_water_footprint(
        self, 
        result: Dict[str, Any], 
        yield_data: Optional[pd.Series] = None
    ) -> Dict[str, Union[float, np.ndarray, pd.Series]]:
        """
        Calculate water footprint metrics from water usage results.
        
        Args:
            result: Result dictionary from predict method
            yield_data: Optional crop yield data (t/ha)
            
        Returns:
            Dictionary of water footprint metrics
        """
        if "water_requirement_mm" not in result:
            raise ValueError("Water requirement data missing from results")
            
        # Get water requirement components
        water_requirement = result["water_requirement_mm"]
        
        # Get rainfall and irrigation if available
        blue_water = None
        green_water = None
        
        if "irrigation_requirement_mm" in result:
            # Blue water is irrigation water
            blue_water = result["irrigation_requirement_mm"]
            
        if "effective_rainfall_mm" in result:
            # Green water is rainfall
            green_water = result["effective_rainfall_mm"]
            
        # If components aren't available, estimate them
        if blue_water is None and green_water is None:
            # Assume 60% green water (rainfall), 40% blue water (irrigation)
            # This is a simplification - actual values would depend on climate and crop
            green_water = water_requirement * 0.6
            blue_water = water_requirement * 0.4
            
        # Calculate total water footprint (m³/ha)
        water_footprint_volumetric = blue_water + green_water
        
        # Calculate water footprint per unit yield (m³/t) if yield data is available
        water_footprint_yield = None
        
        if yield_data is not None:
            # Convert mm to m³/ha (1 mm over 1 ha = 10 m³)
            water_footprint_yield = water_footprint_volumetric * 10 / yield_data
            
        # Prepare water footprint results
        footprint_results = {
            "water_footprint_mm": water_footprint_volumetric,
            "blue_water_mm": blue_water,
            "green_water_mm": green_water,
            "blue_water_fraction": blue_water / water_footprint_volumetric
        }
        
        if water_footprint_yield is not None:
            footprint_results["water_footprint_m3_per_ton"] = water_footprint_yield
            
        return footprint_results
    
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
            "crop_type": self.crop_type,
            "model_type": self.model_type,
            "water_balance_components": self.water_balance_components,
            "required_inputs": self.required_inputs,
            "fitted": self.fitted,
            "config": self.config,
            "crop_coefficients": self.crop_coefficients
        }
        
        # Add model-type specific components
        if self.model_type == "statistical" and self.fitted:
            model_data["predictor"] = self.predictor
            model_data["feature_columns"] = self.feature_columns
        
        # Save to disk
        joblib.dump(model_data, path)
    
    @classmethod
    def load(cls, path: str) -> "WaterUsageModel":
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
            crop_type=model_data["crop_type"],
            model_type=model_data["model_type"],
            water_balance_components=model_data["water_balance_components"],
            config=model_data["config"]
        )
        
        # Restore model attributes
        model.fitted = model_data["fitted"]
        model.crop_coefficients = model_data["crop_coefficients"]
        
        # Restore model-type specific components
        if model.model_type == "statistical" and model.fitted:
            model.predictor = model_data["predictor"]
            model.feature_columns = model_data["feature_columns"]
        
        return model 