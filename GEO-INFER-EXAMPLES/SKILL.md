---
name: geo-infer-examples
description: "Provides runnable code examples and module orchestration patterns for the GEO-INFER framework. Use when wiring GEO-INFER modules together for the first time, finding a working agriculture/climate/health/IoT integration pattern, running a cross-module SPACE-MATH-BAYES pipeline, or adapting a reference implementation to a new geospatial domain."
prerequisites:
  required: []
  recommended: []
difficulty: beginner
estimated_time: 30min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-EXAMPLES

## Instructions

### Step 1: Identify the Example Category

Browse the examples directory to find the pattern that matches your use case:

```text
GEO-INFER-EXAMPLES/examples/
├── module_orchestrators/         # Cross-module coordination pipelines
├── getting_started/              # Beginner walkthroughs
├── agriculture_integration/      # AG + SPACE + RISK workflows
├── climate_integration/          # CLIMATE + TIME + MATH workflows
├── health_integration/           # HEALTH + BAYES + SPACE workflows
├── iot_radiation_monitoring/     # IOT + DATA + SPACE real-time pipelines
└── area_study/                   # Region-specific analysis patterns
```

### Step 2: Run an Example

1. Install required modules for the example (check imports at the top of each script):
   ```bash
   uv pip install -e ./GEO-INFER-SPACE ./GEO-INFER-MATH ./GEO-INFER-BAYES
   ```
2. Verify imports resolve — run `python -c "from geo_infer_space.backends.h3 import H3Backend"` to confirm each module is installed correctly.
3. Execute the example script:
   ```bash
   uv run python GEO-INFER-EXAMPLES/examples/module_orchestrators/orchestrator_demo.py
   ```
4. Check output for convergence status and iteration count to confirm the pipeline ran end-to-end.

### Core Capabilities

- **Module orchestrators**: Chain SPACE, MATH, BAYES, ACT, and other modules into convergent pipelines
- **Domain examples**: Agriculture risk, climate analysis, health mapping, IoT monitoring
- **Active Inference**: End-to-end inference pipelines using ACT + BAYES with free energy minimization
- **Integration patterns**: How modules connect, compose, and exchange data across the framework

## Examples

```python
# Cross-module pipeline: SPACE → MATH → BAYES
from geo_infer_examples.module_orchestrator import ModuleOrchestrator

orchestrator = ModuleOrchestrator(modules=["SPACE", "MATH", "BAYES"])
result = orchestrator.run(data, max_iterations=100)
# Convergence uses numeric relative-change threshold
print(f"Converged in {result.iterations} iterations")
```

```python
# Domain workflow: Agricultural risk assessment
from geo_infer_ag.models.soil_health import SoilHealthModel
from geo_infer_risk.core.risk_engine import RiskEngine
from geo_infer_space.backends.h3 import H3Backend

# 1. Tessellate farm boundary into H3 cells
cells = H3Backend().tessellate(farm_polygon, resolution=9)

# 2. Assess soil health per cell
soil = SoilHealthModel()
health_scores = {cell: soil.assess(cell) for cell in cells}

# 3. Compute spatially-aware risk map
risk = RiskEngine()
risk_map = risk.assess(hazard=drought_index, exposure=health_scores)
```

```python
# Climate integration: temporal trend analysis over spatial grid
from geo_infer_climate.core.trend_analyzer import TrendAnalyzer
from geo_infer_space.backends.h3 import H3Backend
from geo_infer_time.core.temporal_index import TemporalIndex

# 1. Define spatial extent and time range
cells = H3Backend().tessellate(region_polygon, resolution=7)
time_range = TemporalIndex(start="2020-01", end="2025-12", freq="monthly")

# 2. Analyze climate trends per cell over time
analyzer = TrendAnalyzer()
trends = {
    cell: analyzer.fit(climate_data[cell], time_range)
    for cell in cells
}

# 3. Identify cells with statistically significant warming
hotspots = [cell for cell, t in trends.items() if t.p_value < 0.05]
```

## Guidelines

### Running and Testing Examples

- Run all example tests: `uv run python -m pytest GEO-INFER-EXAMPLES/tests/ -v`
- Run a specific example category: `uv run python -m pytest GEO-INFER-EXAMPLES/tests/ -k "agriculture" -v`
- Install module dependencies before running — each example's imports indicate which modules are needed.

### Common Pitfalls

- **Missing module installs**: Examples import from multiple GEO-INFER modules. Install all referenced modules before running, or you will get `ModuleNotFoundError`.
- **H3 version mismatch**: SPACE examples require `h3>=4.0.0` (use `latlng_to_cell`, not the legacy `geo_to_h3` API).
- **Convergence tuning**: The `ModuleOrchestrator` uses numeric relative-change for convergence checks. Adjust `max_iterations` and tolerance based on data complexity.
- End-to-end Active Inference tutorial is planned for v0.4.0.

### Integrations

- **INTRA** → Documentation hub links to these examples for onboarding
- **All modules** → Examples demonstrate cross-module data flow and composition
- **TEST** → Example scripts are testable as integration tests via the unified test runner
