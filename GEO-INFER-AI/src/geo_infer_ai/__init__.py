"""
GEO-INFER-AI: Artificial Intelligence and Machine Learning for Geospatial Workflows

This module provides comprehensive AI and machine learning capabilities for geospatial
data processing, pattern recognition, and predictive modeling.

Key Features:
- Computer vision for satellite and aerial imagery
- Predictive ML models for geospatial forecasting
- MLOps integration with MLflow
- Geospatial data preprocessing and feature engineering
- Model repository and pre-trained models
- Explainable AI (XAI) techniques
"""

__version__ = "0.2.0"
__author__ = "GEO-INFER Development Team"

from geo_infer_ai.core.training import ModelTrainer, TrainingConfig
from geo_infer_ai.core.explainability import ModelExplainer
from geo_infer_ai.core.model_evaluation import GeospatialModelEvaluator
from geo_infer_ai.models.cv.image_classifier import ImageClassifier
from geo_infer_ai.models.predictive.spatial_predictor import (
    IDWInterpolator,
    OrdinaryKriging,
    SpatialPredictor,
)
from geo_infer_ai.models.predictive.geospatial_ai import (
    EnvironmentalActiveInferenceEngine,
    EnvironmentalState,
    H3SpatialGraph,
    LevelSpatialGraph,
    MultiScaleHierarchicalAnalyzer,
    ResourceAllocation,
    SpatialPrediction,
    analyze_multi_scale_patterns,
)
from geo_infer_ai.preprocessing.feature_engineering import GeospatialFeatureEngineer
from geo_infer_ai.pipelines.mlflow_integration import MLflowPipeline

__all__ = [
    "ModelTrainer",
    "TrainingConfig",
    "ModelExplainer",
    "GeospatialModelEvaluator",
    "ImageClassifier",
    "IDWInterpolator",
    "OrdinaryKriging",
    "SpatialPredictor",
    "GeospatialFeatureEngineer",
    "MLflowPipeline",
    "EnvironmentalActiveInferenceEngine",
    "EnvironmentalState",
    "H3SpatialGraph",
    "LevelSpatialGraph",
    "MultiScaleHierarchicalAnalyzer",
    "ResourceAllocation",
    "SpatialPrediction",
    "analyze_multi_scale_patterns",
]
