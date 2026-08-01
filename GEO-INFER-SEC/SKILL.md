---
name: geo-infer-sec
description: Security and threat detection for geospatial systems. Use when implementing spatial access control, anomaly detection on access patterns, geospatial threat assessment, security auditing, or spatial data anonymization.
prerequisites:
  required:
    - geo-infer-api
  recommended: []
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-SEC

## Instructions

### Core Capabilities

- **Access control**: Role-based and spatial-boundary-based authorization (RBAC + SBAC)
- **Threat detection**: Anomaly detection on spatial access patterns, behavioral profiling
- **Confidence scoring**: Dynamic confidence computation (uses real `calculated_confidence`)
- **Audit logging**: Security event tracking with spatial context, chain of evidence
- **Data protection**: Spatial data anonymization, k-anonymity, differential privacy
- **Integrity**: Data integrity verification, tampering detection

### Key Imports

```python
from geo_infer_sec.core.integrated_security import IntegratedSecurityEngine
from geo_infer_sec.core.access_control import SpatialAccessController
from geo_infer_sec.core.threat_detection import ThreatAnalyzer
from geo_infer_sec.core.anonymization import SpatialAnonymizer
```

## Examples

```python
from geo_infer_sec.core.integrated_security import IntegratedSecurityEngine

engine = IntegratedSecurityEngine()
result = engine.assess_threat(
    request=api_request,
    user_context=user_profile,
    spatial_context=request_location
)
print(f"Confidence: {result.confidence_score}")  # Real computed value
```

## Guidelines

- `confidence_score` is computed from calibrated constituent signals (base
  risk weights + correlation bonuses). The weights are heuristics and are
  explicitly documented here — they are not claimed to be empirically
  calibrated.

### Integrations

- Integrates with API for endpoint security
- Test: `uv run python -m pytest GEO-INFER-SEC/tests/ -v`
