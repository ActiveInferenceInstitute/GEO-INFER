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
    
    def compute_shap_like_values(
        self,
        X: np.ndarray,
        n_samples: int = 100,
        feature_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compute SHAP-like marginal contribution values using a kernel-based
        approximation. For each feature, estimates its contribution to the
        prediction by comparing predictions with and without the feature
        (replaced by its marginal expectation).

        Args:
            X: Feature matrix (n_samples, n_features)
            n_samples: Number of background samples for estimation
            feature_names: Optional feature names

        Returns:
            Dictionary with shap_values matrix and feature-level summaries
        """
        n_obs, n_features = X.shape
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]

        # Use a subsample as background distribution
        bg_size = min(n_samples, n_obs)
        bg_indices = np.random.choice(n_obs, size=bg_size, replace=False)
        X_background = X[bg_indices]

        # Baseline prediction (average prediction on background)
        base_predictions = self.model.predict(X_background)
        base_value = float(np.mean(base_predictions))

        # Compute marginal contributions for each feature
        shap_values = np.zeros((n_obs, n_features))

        for j in range(n_features):
            # Create perturbed copies where feature j is replaced by background values
            for i in range(n_obs):
                X_perturbed = np.tile(X[i], (bg_size, 1))
                X_perturbed[:, j] = X_background[:, j]

                pred_original = self.model.predict(X[i:i+1])[0]
                pred_perturbed_mean = np.mean(self.model.predict(X_perturbed))

                shap_values[i, j] = pred_original - pred_perturbed_mean

        # Feature-level summaries
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        feature_importance_ranking = np.argsort(-mean_abs_shap)

        return {
            'shap_values': shap_values,
            'base_value': base_value,
            'feature_names': feature_names,
            'mean_abs_shap': {
                feature_names[i]: float(mean_abs_shap[i])
                for i in range(n_features)
            },
            'feature_ranking': [
                feature_names[i] for i in feature_importance_ranking
            ],
        }

    def compute_partial_dependence(
        self,
        X: np.ndarray,
        feature_index: int,
        grid_resolution: int = 50,
        feature_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compute partial dependence of the model prediction on a single feature.

        Averages model predictions across all samples while varying the target
        feature over a grid of values.

        Args:
            X: Feature matrix (n_samples, n_features)
            feature_index: Index of the feature to compute PD for
            grid_resolution: Number of grid points
            feature_name: Optional name for the feature

        Returns:
            Dictionary with grid values and average predictions
        """
        if feature_name is None:
            feature_name = f"feature_{feature_index}"

        feature_values = X[:, feature_index]
        grid = np.linspace(
            float(np.min(feature_values)),
            float(np.max(feature_values)),
            grid_resolution,
        )

        avg_predictions = np.zeros(grid_resolution)

        for g_idx, grid_val in enumerate(grid):
            X_modified = X.copy()
            X_modified[:, feature_index] = grid_val
            preds = self.model.predict(X_modified)
            avg_predictions[g_idx] = np.mean(preds)

        return {
            'feature_name': feature_name,
            'feature_index': feature_index,
            'grid_values': grid.tolist(),
            'avg_predictions': avg_predictions.tolist(),
            'feature_range': {
                'min': float(np.min(feature_values)),
                'max': float(np.max(feature_values)),
                'mean': float(np.mean(feature_values)),
            },
        }

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

