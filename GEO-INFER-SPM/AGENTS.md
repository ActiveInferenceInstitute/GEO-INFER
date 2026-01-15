# GEO-INFER-SPM: Spatial Project Management

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-SPM module provides statistical and probabilistic mapping capabilities enabling agents to create uncertainty-aware spatial predictions and probability surfaces.

## Implementation Status

### Currently Implemented

- ✅ **ProbabilisticMapper**: Uncertainty-aware mapping
- ✅ **GeostatisticalModeler**: Kriging and spatial interpolation
- ✅ **UncertaintySurfaceGenerator**: Probability surfaces
- ✅ **SpatialPredictionValidator**: Validation tools

### Aspirational/Planned Features

- 🔮 **AdaptiveSamplingAgent**: Optimal sampling decisions
- 🔮 **UncertaintyReductionAgent**: Targeted uncertainty reduction

## Agent Capabilities Supported

### 1. Probabilistic Mapping

```python
from geo_infer_spm import ProbabilisticMapper

# Agent creates probabilistic map
mapper = ProbabilisticMapper()
prob_map = mapper.map(
    observations=sample_data,
    method='gaussian_process',
    uncertainty=True
)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Probabilistic Mapping** | ✅ Ready | Uncertainty-aware maps |
| **Geostatistics** | ✅ Ready | Kriging and interpolation |
| **Uncertainty Surfaces** | ✅ Ready | Probability generation |
| **Validation** | ✅ Ready | Prediction validation |
| **Sampling Agent** | 🔮 Planned | Optimal sampling |

---

This AGENTS.md documents how GEO-INFER-SPM provides statistical mapping capabilities.
