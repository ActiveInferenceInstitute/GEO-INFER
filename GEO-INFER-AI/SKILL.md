---
name: geo-infer-ai
description: Machine learning pipelines and model selection for geospatial AI. Use when training spatial ML models, building prediction pipelines, performing feature engineering on geographic data, or selecting between ML approaches for spatial problems.
prerequisites:
  required:
    - geo-infer-act
    - geo-infer-bayes
  recommended:
    - geo-infer-space
    - geo-infer-data
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-AI

## Instructions

### Core Capabilities

- **ML pipelines**: End-to-end spatial feature engineering → training → evaluation
- **Model selection**: Cross-validation, hyperparameter optimization
- **Spatial features**: H3-based feature extraction, proximity features
- **Deep learning**: Spatial neural networks, graph neural networks
- **Transfer learning**: Pre-trained geospatial embeddings

### Key Imports

```python
from geo_infer_ai.core.pipeline import SpatialPipeline
from geo_infer_ai.core.model_selection import ModelSelector
from geo_infer_ai.core.feature_engineering import SpatialFeatureExtractor
```

## Examples

```python
from geo_infer_ai.core.pipeline import SpatialPipeline

pipeline = SpatialPipeline(
    features=["h3_resolution", "proximity", "density"],
    model="random_forest"
)
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

## Guidelines


### Integrations

- Integrates with SPACE module for H3-based feature extraction
- Depends on MATH for spatial statistics features
- Optional deps: scikit-learn, torch, tensorflow — graceful degradation
- Test: `uv run python -m pytest GEO-INFER-AI/tests/ -v`
