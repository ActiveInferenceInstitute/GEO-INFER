---
title: "GEO-INFER-SIM: Simulation Framework"
description: "Agent-based modeling, discrete event simulation, and scenario analysis"
purpose: "Provide simulation capabilities for spatial systems and agent behavior"
module_type: "Core Analysis"
status: "Beta"
last_updated: "2026-02-25"
dependencies: ["SPACE", "TIME", "ACT"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-ACT"]
tags: ["simulation", "abm", "modeling", "scenarios", "monte-carlo"]
difficulty: "Advanced"
estimated_time: "50"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-SIM: Simulation Framework

## Overview

**GEO-INFER-SIM** provides simulation capabilities:

- **Agent-Based Models**: Spatial ABM simulations
- **Discrete Event**: Event-driven simulations
- **Scenario Analysis**: What-if comparisons
- **Monte Carlo**: Probabilistic analysis

## Features

### Agent-Based Modeling

```python
from geo_infer_sim import ABMSimulator

# Create ABM simulation
simulator = ABMSimulator()

model = simulator.create(
    environment=city_grid,
    agents=pedestrian_agents,
    rules=movement_rules
)

results = model.run(steps=1000)
print(f"Emergent patterns: {results.patterns}")
```

### Discrete Event Simulation

```python
from geo_infer_sim import DiscreteEventSim

# Event-driven simulation
des = DiscreteEventSim()

sim = des.create(
    model=logistics_model,
    events=["arrival", "processing"]
)

results = sim.run(duration_hours=24)
print(f"Throughput: {results.throughput}")
```

### Scenario Analysis

```python
from geo_infer_sim import ScenarioAnalyzer

# Compare scenarios
analyzer = ScenarioAnalyzer()

comparison = analyzer.compare(
    base=current_state,
    alternatives=[scenario_a, scenario_b],
    metrics=["cost", "coverage"]
)

print(f"Best scenario: {comparison.best}")
```

### Monte Carlo

```python
from geo_infer_sim import MonteCarloSim

# Probabilistic analysis
mc = MonteCarloSim()

analysis = mc.run(
    model=risk_model,
    iterations=10000
)

print(f"95% CI: {analysis.ci_95}")
```

## Simulation Types

| Type | Application |
|------|-------------|
| **ABM** | Social behavior |
| **DES** | Logistics, queues |
| **SD** | System dynamics |
| **MC** | Risk analysis |

## Installation

```bash
uv pip install -e "./GEO-INFER-SIM"
```

---

**Status**: Beta

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
