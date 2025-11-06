"""
Predictive ML models for geospatial forecasting and regression.

This module provides machine learning models specifically designed for
geospatial prediction tasks including land use change, climate impacts,
and resource forecasting.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge

logger = logging.getLogger(__name__)


class SpatialPredictor(BaseEstimator, RegressorMixin):
    """
    Spatial predictor for geospatial regression and forecasting tasks.

    Supports multiple regression algorithms optimized for spatial data
    with consideration of spatial autocorrelation and geographic features.
    """

    def __init__(
        self,
        model_type: str = "random_forest",
        include_spatial_features: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the spatial predictor.

        Args:
            model_type: Type of model ("linear", "ridge", "random_forest", "gradient_boosting")
            include_spatial_features: Whether to automatically include spatial features
            **kwargs: Additional arguments passed to the underlying model
        """
        self.model_type = model_type
        self.include_spatial_features = include_spatial_features
        self.model: Optional[Any] = None
        self.feature_names_: Optional[List[str]] = None
        self._initialize_model(**kwargs)

    def _initialize_model(self, **kwargs: Any) -> None:
        """Initialize the underlying regression model."""
        if self.model_type == "linear":
            default_params = {"fit_intercept": True}
            default_params.update(kwargs)
            self.model = LinearRegression(**default_params)
        elif self.model_type == "ridge":
            default_params = {"alpha": 1.0, "fit_intercept": True}
            default_params.update(kwargs)
            self.model = Ridge(**default_params)
        elif self.model_type == "random_forest":
            default_params = {
                "n_estimators": 100,
                "max_depth": 20,
                "random_state": 42,
                "n_jobs": -1,
            }
            default_params.update(kwargs)
            self.model = RandomForestRegressor(**default_params)
        elif self.model_type == "gradient_boosting":
            default_params = {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 5,
                "random_state": 42,
            }
            default_params.update(kwargs)
            self.model = GradientBoostingRegressor(**default_params)
        else:
            raise ValueError(
                f"Unknown model_type: {self.model_type}. "
                "Must be 'linear', 'ridge', 'random_forest', or 'gradient_boosting'"
            )

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        coordinates: Optional[np.ndarray] = None,
    ) -> "SpatialPredictor":
        """
        Train the spatial predictor.

        Args:
            X: Training features (n_samples, n_features)
            y: Training targets (n_samples,)
            sample_weight: Optional sample weights
            coordinates: Optional spatial coordinates (n_samples, 2) for spatial features

        Returns:
            Self for method chaining
        """
        logger.info(
            f"Training {self.model_type} predictor on {len(X)} samples "
            f"with {X.shape[1] if hasattr(X, 'shape') else len(X.columns)} features"
        )

        # Convert to numpy if pandas DataFrame
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = list(X.columns)
            X = X.values
        else:
            self.feature_names_ = [f"feature_{i}" for i in range(X.shape[1])]

        # Add spatial features if requested and coordinates provided
        if self.include_spatial_features and coordinates is not None:
            X = self._add_spatial_features(X, coordinates)

        # Train the model
        if sample_weight is not None:
            self.model.fit(X, y, sample_weight=sample_weight)
        else:
            self.model.fit(X, y)

        logger.info("Training completed")
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame], coordinates: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Features for prediction (n_samples, n_features)
            coordinates: Optional spatial coordinates for spatial features

        Returns:
            Predicted values (n_samples,)
        """
        if self.model is None or not hasattr(self.model, 'predict'):
            raise ValueError("Model must be trained before prediction")

        # Convert to numpy if pandas DataFrame
        if isinstance(X, pd.DataFrame):
            X = X.values

        # Add spatial features if requested and coordinates provided
        if self.include_spatial_features and coordinates is not None:
            X = self._add_spatial_features(X, coordinates)

        predictions = self.model.predict(X)
        return predictions

    def _add_spatial_features(
        self, X: np.ndarray, coordinates: np.ndarray
    ) -> np.ndarray:
        """
        Add spatial features to the feature matrix.

        Args:
            X: Original features (n_samples, n_features)
            coordinates: Spatial coordinates (n_samples, 2) [lon, lat]

        Returns:
            Enhanced feature matrix with spatial features
        """
        # Calculate spatial features
        lon = coordinates[:, 0]
        lat = coordinates[:, 1]

        # Add coordinate features
        spatial_features = np.column_stack([lon, lat])

        # Add distance from origin (centroid)
        centroid_lon = np.mean(lon)
        centroid_lat = np.mean(lat)
        distances = np.sqrt(
            (lon - centroid_lon) ** 2 + (lat - centroid_lat) ** 2
        )
        spatial_features = np.column_stack([spatial_features, distances])

        # Combine with original features
        X_enhanced = np.column_stack([X, spatial_features])
        return X_enhanced

    def get_feature_importance(self) -> Optional[np.ndarray]:
        """
        Get feature importance scores (for tree-based models).

        Returns:
            Feature importance array or None if not available
        """
        if hasattr(self.model, "feature_importances_"):
            return self.model.feature_importances_
        elif hasattr(self.model, "coef_"):
            # For linear models, use absolute coefficients as importance
            return np.abs(self.model.coef_)
        return None

    def get_feature_names(self) -> Optional[List[str]]:
        """
        Get feature names.

        Returns:
            List of feature names or None
        """
        return self.feature_names_

