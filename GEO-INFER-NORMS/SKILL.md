---
name: geo-infer-norms
description: Normative inference and compliance tracking for geospatial governance. Use when evaluating spatial policy compliance, tracking governance metrics, computing normative content influence (Jaccard similarity), or managing multi-criteria regulatory frameworks.
prerequisites:
  required:
    - geo-infer-data
  recommended:
    - geo-infer-api
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-NORMS

## Instructions

### Core Capabilities

- **Compliance tracking**: Threshold, range, and boolean evaluation with weighted scoring
- **Normative inference**: Content influence measurement via Jaccard similarity
- **Policy evaluation**: Multi-criteria governance assessment with configurable metrics
- **Regulatory frameworks**: Spatial regulation management, jurisdiction tracking

### Key Imports

```python
from geo_infer_norms.core.compliance_tracking import compliance_tracking
from geo_infer_norms.core.normative_inference import NormativeInference
from geo_infer_norms.models.metrics import Metric, ComplianceResult
```

## Examples

```python
from geo_infer_norms.core.compliance_tracking import compliance_tracking
from geo_infer_norms.models.metrics import Metric

metrics = [
    Metric(name="air_quality", value=42, threshold=50, type="threshold"),
    Metric(name="noise_level", value=65, range=(0, 70), type="range"),
    Metric(name="green_space", value=True, type="boolean"),
]
result = compliance_tracking(metrics)
print(f"Overall compliance: {result.score:.1%}")
```

## Guidelines

- Content influence uses Jaccard similarity (real implementation)
- Compliance evaluation handles threshold/range/boolean types correctly

### Integrations

- Integrates with METAGOV for governance compliance monitoring
- Integrates with REQ for requirements compliance tracking
- Test: `uv run python -m pytest GEO-INFER-NORMS/tests/ -v`
