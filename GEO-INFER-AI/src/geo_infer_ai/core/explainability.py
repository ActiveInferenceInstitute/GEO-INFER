"""
Explainable AI (XAI) module for geospatial models.

Provides interpretability and explainability tools for understanding
geospatial AI model predictions.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


class ModelExplainer:
    """
    Explain geospatial AI model predictions.
    
    Provides feature importance, SHAP-like explanations, and
    spatial interpretability for geospatial models.
    """
    
    def __init__(self, model: Any, config: Optional[Dict] = None):
        """
        Initialize model explainer.
        
        Args:
            model: Trained model to explain
            config: Configuration dictionary
        """
        self.model = model
        self.config = config or {}
    
    def calculate_feature_importance(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        method: str = 'permutation'
    ) -> Dict[str, float]:
        """
        Calculate feature importance.
        
        Args:
            X: Feature matrix
            y: Target values
            feature_names: Optional feature names
            method: Method ('permutation' or 'coefficient')
            
        Returns:
            Dictionary of feature importances
        """
        if method == 'permutation':
            # Permutation importance
            result = permutation_importance(
                self.model, X, y,
                n_repeats=10,
                random_state=42,
                n_jobs=-1
            )
            importances = result.importances_mean
        elif method == 'coefficient':
            # For linear models, use coefficients
            if hasattr(self.model, 'coef_'):
                importances = np.abs(self.model.coef_)
            elif hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            else:
                raise ValueError("Model does not support coefficient-based importance")
        else:
            raise ValueError(f"Unknown method: {method}")
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(importances))]
        
        return dict(zip(feature_names, importances))
    
    def explain_prediction(
        self,
        X: np.ndarray,
        prediction: float,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Explain a single prediction.
        
        Args:
            X: Feature vector for prediction
            y: Predicted value
            feature_names: Optional feature names
            
        Returns:
            Explanation dictionary
        """
        # Simplified explanation using feature contributions
        if hasattr(self.model, 'predict_proba'):
            # For classification
            proba = self.model.predict_proba(X.reshape(1, -1))[0]
            explanation = {
                'prediction': prediction,
                'probabilities': proba.tolist(),
                'confidence': proba.max()
            }
        else:
            # For regression
            explanation = {
                'prediction': prediction,
                'feature_values': X.tolist()
            }
        
        if feature_names:
            explanation['feature_names'] = feature_names
        
        return explanation
    
    def generate_spatial_explanation(
        self,
        spatial_features: np.ndarray,
        predictions: np.ndarray,
        coordinates: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Generate spatial explanation for geospatial predictions.
        
        Args:
            spatial_features: Spatial feature matrix
            predictions: Model predictions
            coordinates: Optional spatial coordinates
            
        Returns:
            Spatial explanation
        """
        # Calculate spatial patterns in predictions
        prediction_mean = np.mean(predictions)
        prediction_std = np.std(predictions)
        
        # Identify spatial clusters of high/low predictions
        high_predictions = predictions > (prediction_mean + prediction_std)
        low_predictions = predictions < (prediction_mean - prediction_std)
        
        explanation = {
            'prediction_statistics': {
                'mean': float(prediction_mean),
                'std': float(prediction_std),
                'min': float(np.min(predictions)),
                'max': float(np.max(predictions))
            },
            'spatial_patterns': {
                'high_prediction_areas': int(np.sum(high_predictions)),
                'low_prediction_areas': int(np.sum(low_predictions))
            }
        }
        
        if coordinates is not None:
            explanation['spatial_extent'] = {
                'lat_range': [float(np.min(coordinates[:, 0])), float(np.max(coordinates[:, 0]))],
                'lon_range': [float(np.min(coordinates[:, 1])), float(np.max(coordinates[:, 1]))]
            }
        
        return explanation

