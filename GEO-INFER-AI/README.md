---
title: "GEO-INFER-AI: Artificial Intelligence and Machine Learning"
description: "ML models, deep learning, and AI capabilities for geospatial analysis"
purpose: "Provide AI/ML tools for spatial pattern recognition and prediction"
module_type: "Core Intelligence"
status: "Beta"
last_updated: "2026-04-16"
dependencies: ["DATA", "SPACE", "MATH"]
compatibility: ["GEO-INFER-DATA", "GEO-INFER-SPACE", "GEO-INFER-ACT", "GEO-INFER-BAYES"]
tags: ["ai", "machine-learning", "deep-learning", "prediction", "classification"]
difficulty: "Advanced"
estimated_time: "50"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> •
  <a href="../README.md#-module-overview">Module Index</a> •
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-AI: Artificial Intelligence and Machine Learning

## Overview

**GEO-INFER-AI** provides machine-learning capabilities for geospatial workflows: model training with MLflow integration, satellite/aerial image classification, spatial prediction (incl. IDW and Ordinary Kriging), geospatial feature engineering, and model explainability. Estimators follow the scikit-learn API (`fit`/`predict`) for interoperability with the wider Python ML ecosystem.

## Core Capabilities

- **Training infrastructure**: `ModelTrainer` + `TrainingConfig` for reproducible training runs
- **Computer vision**: `ImageClassifier` for satellite/aerial imagery (CNN backbone)
- **Spatial prediction**: `SpatialPredictor`, `IDWInterpolator`, `OrdinaryKriging` for regression over coordinates
- **Feature engineering**: `GeospatialFeatureEngineer` — distance, density, adjacency, H3 indicator features
- **MLOps**: `MLflowPipeline` for experiment tracking, model registry, and deployment artifacts
- **Explainability**: `ModelExplainer` — SHAP-style feature attribution for spatial models
- **Evaluation**: `GeospatialModelEvaluator` — spatial-aware CV, Moran's I of residuals, block-holdout metrics

## Features

### Spatial Prediction with Kriging

```python
from geo_infer_ai import SpatialPredictor
from geo_infer_ai.models.predictive.spatial_predictor import OrdinaryKriging
import numpy as np

coords = np.array([[-122.4, 37.7], [-122.3, 37.8], [-122.5, 37.6]])
values = np.array([10.0, 15.0, 12.0])

kriging = OrdinaryKriging(variogram_model="spherical")
kriging.fit(coords, values)

preds, variances = kriging.predict(np.array([[-122.35, 37.75]]), return_variance=True)
```

### Image Classification

```python
from geo_infer_ai import ImageClassifier

clf = ImageClassifier(num_classes=10)
clf.fit(X_train_imagery, y_train_labels)
predictions = clf.predict(X_test_imagery)
```

### Feature Engineering

```python
from geo_infer_ai import GeospatialFeatureEngineer

fe = GeospatialFeatureEngineer(h3_resolution=9)
features = fe.transform(geo_dataframe)  # distance, density, H3 indicators
```

### MLflow Pipeline

```python
from geo_infer_ai import MLflowPipeline, ModelTrainer, TrainingConfig

pipeline = MLflowPipeline(experiment_name="land-use-classification")
config = TrainingConfig(model_type="random_forest", cv_folds=5, random_state=42)

trainer = ModelTrainer(config=config, pipeline=pipeline)
trainer.train(X, y)
```

### Explainability

```python
from geo_infer_ai import ModelExplainer

explainer = ModelExplainer(model=trained_model)
attributions = explainer.explain(X_sample, method="shap")
```

## API Reference

| Class | Purpose |
|-------|---------|
| `ModelTrainer(config, pipeline=None)` | Trains sklearn-compatible models with optional MLflow tracking |
| `TrainingConfig(model_type, cv_folds, random_state, ...)` | Dataclass for reproducible training configuration |
| `ImageClassifier(num_classes, ...)` | CNN-backed classifier for satellite/aerial imagery |
| `SpatialPredictor(method, ...)` | Regressor for spatial prediction with multiple backends |
| `IDWInterpolator(power=2, k_neighbors=None)` | Inverse-distance-weighted interpolation |
| `OrdinaryKriging(variogram_model, ...)` | Geostatistical kriging with fitted variogram |
| `GeospatialFeatureEngineer(h3_resolution, ...)` | Extracts spatial features from GeoDataFrames |
| `MLflowPipeline(experiment_name, ...)` | MLflow experiment + model-registry wrapper |
| `ModelExplainer(model)` | Feature attribution (SHAP / permutation / partial dependence) |
| `GeospatialModelEvaluator(...)` | Spatial-aware evaluation with block-holdout and residual autocorrelation |

## Available Model Backends

| Backend | Use | Estimator |
|---------|-----|-----------|
| scikit-learn | Tabular / spatial features | RandomForest, GradientBoosting, LinearModels |
| XGBoost (optional) | Gradient boosting | `ModelTrainer(model_type="xgboost")` |
| PyTorch (optional) | Deep learning | `ImageClassifier`, custom CNN heads |
| PyKrige (optional) | Geostatistics | Semivariogram fitting for `OrdinaryKriging` |

Optional dependencies are guarded with `try/except` imports; missing backends raise an actionable `RuntimeError` at call time.

## Integration

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-DATA** | AI ← DATA | Training datasets, raster/vector sources |
| **GEO-INFER-SPACE** | AI ← SPACE | H3 indexing for spatial feature engineering |
| **GEO-INFER-MATH** | AI ← MATH | Variogram models, distance metrics, kernels |
| **GEO-INFER-BAYES** | AI ↔ BAYES | Hybrid Bayesian-ML workflows |
| **GEO-INFER-ACT** | AI → ACT | Learned perception models for active-inference agents |

## Installation

```bash
uv pip install -e "./GEO-INFER-AI"

# Optional extras
uv pip install -e "./GEO-INFER-AI[gpu]"    # PyTorch with CUDA
uv pip install -e "./GEO-INFER-AI[geostats]"  # PyKrige
```

## Testing

```bash
uv run python -m pytest GEO-INFER-AI/tests/ -v
uv run python -m pytest GEO-INFER-AI/tests/ --cov=GEO-INFER-AI/src --cov-report=html
```

## Documentation Hub

Full framework documentation is in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation and quick-start |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | Cross-module workflows |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards |

---

**Status**: Beta

**Last Updated**: 2026-04-16
