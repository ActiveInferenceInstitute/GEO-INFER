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
├── module_orchestrators/     # Per-module orchestration demos
├── getting_started/          # Beginner walkthroughs
├── agriculture_integration/  # AG + SPACE + RISK workflows
├── climate_integration/      # CLIMATE + SPACE workflows
├── health_integration/       # HEALTH + SPACE workflows
└── iot_radiation_monitoring/ # IOT + DATA + SPACE workflow
```

### Orchestrator Example

```python
from geo_infer_examples.core.module_orchestrator import ModuleOrchestrator

orchestrator = ModuleOrchestrator(monitoring_enabled=False)
workflow_ids = orchestrator.list_workflows()
module_health = orchestrator.get_module_health()
```

## Examples

```python
from geo_infer_examples.core.module_orchestrator import ModuleOrchestrator

# Inspect configured cross-module workflows before execution
orchestrator = ModuleOrchestrator(monitoring_enabled=False)
for workflow_id in orchestrator.list_workflows():
    workflow = orchestrator.get_workflow_definition(workflow_id)
    print(workflow_id, workflow.execution_strategy)
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
- Track new tutorial requests in the root task ledger before adding examples
- Verified runnable examples live under `examples/*/scripts/`
- Test: `uv run python -m pytest GEO-INFER-EXAMPLES/tests/ -v`

### Integrations

- **INTRA** → Documentation hub links to examples
- **All modules** → Examples demonstrate cross-module workflows
- **TEST** → Example code testable as integration tests
