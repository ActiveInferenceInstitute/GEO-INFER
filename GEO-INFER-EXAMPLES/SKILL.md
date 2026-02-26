---
name: geo-infer-examples
description: Working examples and module orchestration patterns. Use when looking for usage examples, cross-module orchestration patterns, end-to-end workflows, or reference implementations of GEO-INFER capabilities.
prerequisites:
  required: []
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-EXAMPLES

## Instructions

### Core Capabilities

- **Module orchestrators**: Cross-module workflow examples
- **Domain examples**: Per-domain analysis workflows
- **Active Inference**: End-to-end inference pipeline examples
- **Integration patterns**: How modules connect and compose

### Key Directories

```text
GEO-INFER-EXAMPLES/examples/
├── module_orchestrator.py    # Cross-module coordination
├── spatial_analysis/         # SPACE + MATH examples
├── active_inference/         # ACT + BAYES examples
└── domain/                   # Domain-specific examples
```

### Orchestrator Example

```python
from geo_infer_examples.module_orchestrator import ModuleOrchestrator

orchestrator = ModuleOrchestrator(modules=["SPACE", "MATH", "BAYES"])
result = orchestrator.run(data, max_iterations=100)
# Convergence uses numeric relative-change (not placeholder)
```

## Examples

```python
from geo_infer_examples.module_orchestrator import ModuleOrchestrator

# Cross-module pipeline: SPACE → MATH → BAYES
orchestrator = ModuleOrchestrator(modules=["SPACE", "MATH", "BAYES"])
result = orchestrator.run(data, max_iterations=100)
# Convergence uses numeric relative-change (not placeholder)
print(f"Converged in {result.iterations} iterations")
```

```python
# Domain workflow: Agricultural risk assessment
from geo_infer_ag.models.soil_health import SoilHealthModel
from geo_infer_risk.core.risk_engine import RiskEngine
from geo_infer_space.backends.h3 import H3Backend

# 1. Tessellate farm boundary
cells = H3Backend().tessellate(farm_polygon, resolution=9)

# 2. Assess soil health per cell
soil = SoilHealthModel()
health_scores = {cell: soil.assess(cell) for cell in cells}

# 3. Compute risk
risk = RiskEngine()
risk_map = risk.assess(hazard=drought_index, exposure=health_scores)
```

## Guidelines

- `module_orchestrator.py` convergence check uses numeric relative-change
- Missing end-to-end Active Inference tutorial (planned for v0.4.0)
- Test: `uv run python -m pytest GEO-INFER-EXAMPLES/tests/ -v`

### Integrations

- **INTRA** → Documentation hub links to examples
- **All modules** → Examples demonstrate cross-module workflows
- **TEST** → Example code testable as integration tests
