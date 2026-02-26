# GEO-INFER-AI: Artificial Intelligence Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview

The GEO-INFER-AI module provides machine learning and artificial intelligence capabilities for intelligent agents within the GEO-INFER framework. It enables perception, learning, and decision-making for agents across all domain modules.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational and not yet implemented.

### Currently Implemented

- ✅ **ModelTrainer**: Training and evaluation framework for geospatial ML models
- ✅ **ImageClassifier**: Computer vision for satellite and aerial imagery
- ✅ **SpatialPredictor**: Predictive models for geospatial forecasting
- ✅ **GeospatialFeatureEngineer**: Preprocessing and feature extraction
- ✅ **MLflowPipeline**: MLOps integration with MLflow
- ✅ **ModelExplainer**: Explainable AI techniques

### Aspirational/Planned Features

- 🔮 **AutoML Pipeline**: Automated model selection and hyperparameter tuning
- 🔮 **Federated Learning**: Privacy-preserving distributed training
- 🔮 **Neural Architecture Search**: Automated model architecture optimization

## Technical Capabilities

### Core Classes

#### Model Training

- **`ModelTrainer`**: `ModelTrainer(config: Optional[TrainingConfig] = None)`
  - Training and evaluation framework
  - Methods:
   
- `train(model, X_train, y_train, **kwargs) -> TrainedModel`
   
- `evaluate(model, X_test, y_test, **kwargs) -> Dict[str, float]`
   
- `cross_validate(model, X, y, cv=5, **kwargs) -> Dict[str, Any]`

- **`TrainingConfig`**: `TrainingConfig(batch_size=32, epochs=100, learning_rate=0.001, **kwargs)`
  - Training configuration dataclass

#### Computer Vision

- **`ImageClassifier`**: `ImageClassifier(model_type='resnet50', num_classes=10, input_shape=(256, 256, 3), **kwargs)`
  - Image classification for geospatial imagery
  - Methods:
   
- `fit(X_train, y_train, **kwargs) -> None`
   
- `predict(X, **kwargs) -> np.ndarray`
   
- `predict_proba(X, **kwargs) -> np.ndarray`

#### Predictive Modeling

- **`SpatialPredictor`**: `SpatialPredictor(model_type='random_forest', spatial_features=None, **kwargs)`
  - Predictive models for geospatial forecasting
  - Methods:
   
- `fit(features, targets, **kwargs) -> None`
   
- `predict(features, **kwargs) -> np.ndarray`
   
- `predict_proba(features, **kwargs) -> np.ndarray`

#### Feature Engineering

- **`GeospatialFeatureEngineer`**: `GeospatialFeatureEngineer(**kwargs)`
  - Geospatial feature extraction and preprocessing
  - Methods:
   
- `extract_features(data, **kwargs) -> np.ndarray`
   
- `transform(data, **kwargs) -> np.ndarray`
   
- `fit_transform(data, **kwargs) -> np.ndarray`

#### MLOps

- **`MLflowPipeline`**: `MLflowPipeline(experiment_name='default', **kwargs)`
  - MLflow integration for MLOps
  - Methods:
   
- `log_model(model, model_name, **kwargs) -> None`
   
- `log_metrics(metrics, step=None) -> None`
   
- `log_params(params) -> None`

#### Model Evaluation

- **`GeospatialModelEvaluator`**: `GeospatialModelEvaluator(**kwargs)`
  - Geospatial model evaluation
  - Methods:
   
- `evaluate(model, X, y, **kwargs) -> Dict[str, float]`
   
- `spatial_cross_validate(model, X, y, spatial_folds, **kwargs) -> Dict[str, Any]`

#### Explainability

- **`ModelExplainer`**: `ModelExplainer(model, method='shap', **kwargs)`
  - Model explainability and interpretability
  - Methods:
   
- `explain(X, **kwargs) -> Dict[str, Any]`
   
- `feature_importance(**kwargs) -> np.ndarray`
   
- `plot_explanations(X, output_path, **kwargs) -> None`

## Agent Capabilities Supported

### 1. Perception (Computer Vision)

AI provides visual perception capabilities for agents analyzing geospatial imagery:

```python
from geo_infer_ai import ImageClassifier

# Initialize classifier for agent perception
classifier = ImageClassifier(
    model_type='resnet50',
    num_classes=10, 

# land cover classes
    input_shape=(256, 256, 3))

# Agent uses classifier for environmental perception
predictions = classifier.predict(satellite_images)```

### 2. Learning and Adaptation

AI enables agents to learn from experience and adapt their behavior:

```python
from geo_infer_ai import SpatialPredictor

# Create learning model for agent adaptation
predictor = SpatialPredictor(
    model_type='random_forest',
    spatial_features=['elevation', 'ndvi', 'precipitation'])

# Agent learns spatial patterns
predictor.fit(features=spatial_features, targets=outcomes)

# Agent applies learned knowledge
predictions = predictor.predict(new_features)```

### 3. Decision Support

AI provides predictive capabilities that inform agent decision-making:

```python
from geo_infer_ai import ModelTrainer, TrainingConfig

# Configure model for decision support
config = TrainingConfig(
    batch_size=32,
    epochs=100,
    learning_rate=0.001)

trainer = ModelTrainer(config)

# Train decision model
trainer.train(model=decision_model, X_train=data, y_train=labels)```

## Integration with Agent Framework

### Active Inference Integration

AI models can serve as likelihood functions within Active Inference agents:

- **Observation Models**: CNNs for perception in generative models
- **State Estimation**: Neural networks for belief updating
- **Policy Networks**: Deep RL for action selection

### Multi-Agent Integration

AI supports distributed learning across agent populations:

- **Federated Learning**: Agents share model updates, not raw data
- **Ensemble Methods**: Combining predictions from multiple agent models
- **Transfer Learning**: Agents share learned representations

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Computer Vision** | ✅ Implemented | Image classification, segmentation, detection |
| **Spatial Prediction** | ✅ Implemented | Geospatial forecasting models |
| **Feature Engineering** | ✅ Implemented | Spatial feature extraction |
| **MLOps Pipeline** | ✅ Implemented | MLflow integration |
| **Model Evaluation** | ✅ Implemented | Geospatial model evaluation |
| **Explainability** | ✅ Implemented | XAI techniques |
| **AutoML** | 🔮 Planned | Automated model optimization |
| **Federated Learning** | 🔮 Planned | Distributed training |

---

This AGENTS.md file documents how the GEO-INFER-AI module provides AI/ML capabilities for intelligent agents across the GEO-INFER framework.

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
