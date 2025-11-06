"""
Model evaluation module for geospatial AI models.

Provides geospatial-specific evaluation metrics and validation methods.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

logger = logging.getLogger(__name__)


class GeospatialModelEvaluator:
    """
    Evaluate geospatial AI models with spatial-specific metrics.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize model evaluator."""
        self.config = config or {}
    
    def evaluate_classification(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        labels: Optional[List] = None
    ) -> Dict[str, float]:
        """
        Evaluate classification model.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Optional label names
            
        Returns:
            Evaluation metrics
        """
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        }
        
        return metrics
    
    def evaluate_regression(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate regression model.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Evaluation metrics
        """
        metrics = {
            'mae': float(mean_absolute_error(y_true, y_pred)),
            'mse': float(mean_squared_error(y_true, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'r2': float(r2_score(y_true, y_pred))
        }
        
        return metrics
    
    def evaluate_spatial_accuracy(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        coordinates: np.ndarray,
        buffer_distance: float = 100.0
    ) -> Dict[str, float]:
        """
        Evaluate spatial accuracy (location-based metrics).
        
        Args:
            y_true: True values
            y_pred: Predicted values
            coordinates: Spatial coordinates
            buffer_distance: Buffer distance for spatial matching (meters)
            
        Returns:
            Spatial accuracy metrics
        """
        # Simplified spatial accuracy calculation
        # In practice, would use actual distance calculations
        
        # Calculate prediction errors
        errors = np.abs(y_true - y_pred)
        
        # Spatial error statistics
        spatial_metrics = {
            'mean_spatial_error': float(np.mean(errors)),
            'median_spatial_error': float(np.median(errors)),
            'max_spatial_error': float(np.max(errors)),
            'spatial_error_std': float(np.std(errors))
        }
        
        # Percentage within buffer
        within_buffer = np.sum(errors <= buffer_distance) / len(errors) * 100
        spatial_metrics['within_buffer_percentage'] = float(within_buffer)
        
        return spatial_metrics
    
    def cross_validate_spatial(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        coordinates: np.ndarray,
        n_splits: int = 5
    ) -> Dict[str, float]:
        """
        Perform spatial cross-validation.
        
        Args:
            model: Model to evaluate
            X: Feature matrix
            y: Target values
            coordinates: Spatial coordinates
            n_splits: Number of spatial folds
            
        Returns:
            Cross-validation results
        """
        # Simplified spatial CV - would implement proper spatial blocking
        from sklearn.model_selection import KFold
        
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        scores = []
        
        for train_idx, test_idx in kf.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            if len(np.unique(y)) > 10:  # Regression
                score = r2_score(y_test, y_pred)
            else:  # Classification
                score = accuracy_score(y_test, y_pred)
            
            scores.append(score)
        
        return {
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'scores': [float(s) for s in scores]
        }

