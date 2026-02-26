---
name: geo-infer-req
description: Requirements engineering and traceability for geospatial projects. Use when managing spatial project requirements, building traceability matrices, implementing P3IF frameworks (Purpose, People, Process, Infrastructure, Finance), or tracking requirement coverage and verification.
prerequisites:
  required: []
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-REQ

## Instructions

### Core Capabilities

- **Requirements management**: Spatial project requirement CRUD and lifecycle tracking
- **Traceability**: Bidirectional requirement-to-implementation mapping
- **P3IF framework**: Purpose, People, Process, Infrastructure, Finance analysis
- **Coverage analysis**: Requirements coverage verification and gap detection
- **Change management**: Requirement change impact analysis

### Key Imports

```python
from geo_infer_req.core.requirements import RequirementsManager
from geo_infer_req.core.traceability import TraceabilityMatrix
from geo_infer_req.core.p3if import P3IFFramework
from geo_infer_req.core.coverage import CoverageAnalyzer
```

## Examples

```python
from geo_infer_req.core.traceability import TraceabilityMatrix

matrix = TraceabilityMatrix()
matrix.add_requirement("REQ-001", "System shall support H3 v4 indexing")
matrix.link("REQ-001", implementation="geo_infer_space/backends/h3.py")
matrix.link("REQ-001", test="test_h3_backend.py")
report = matrix.coverage_report()
print(f"Coverage: {report.coverage_percent:.0f}%")
```

## Guidelines

- P3IF framework partially implemented (Alpha)

### Integrations

- Integrates with NORMS for compliance requirement tracking
- Test: `uv run python -m pytest GEO-INFER-REQ/tests/ -v`
