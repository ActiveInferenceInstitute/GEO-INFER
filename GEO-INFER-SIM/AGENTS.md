# GEO-INFER-SIM: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-SIM** module provides simulation capabilities for agents, enabling agent-based modeling, discrete event simulation, and scenario analysis.

## Agent Capabilities

### 1. Agent-Based Modeling

```python
from geo_infer_sim import ABMSimulator

# Run agent-based simulation
simulator = ABMSimulator()

simulation = simulator.create(
    environment=city_grid,
    agents=pedestrian_agents,
    rules=movement_rules,
    steps=1000)

simulation.run()
print(f"Final patterns: {simulation.emergent_patterns}")```

### 2. Discrete Event Simulation

```python
from geo_infer_sim import DiscreteEventSim

# Simulate discrete events
des = DiscreteEventSim()

sim = des.create(
    model=logistics_model,
    events=["arrival", "processing", "departure"],
    duration_hours=24)

results = sim.run()
print(f"Throughput: {results.throughput}")
print(f"Queue lengths: {results.queue_stats}")```

### 3. Scenario Analysis

```python
from geo_infer_sim import ScenarioAnalyzer

# Analyze multiple scenarios
analyzer = ScenarioAnalyzer()

scenarios = analyzer.compare(
    base_scenario=current_state,
    alternatives=[scenario_a, scenario_b, scenario_c],
    metrics=["cost", "coverage", "efficiency"])

print(f"Best scenario: {scenarios.best.name}")```

### 4. Monte Carlo Simulation

```python
from geo_infer_sim import MonteCarloSim

# Run Monte Carlo analysis
mc = MonteCarloSim()

analysis = mc.run(
    model=risk_model,
    iterations=10000,
    uncertain_params=["demand", "cost", "duration"])

print(f"Mean outcome: {analysis.mean}")
print(f"95% confidence: {analysis.ci_95}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **ABM** | ✅ Ready | Agent-based models |
| **DES** | ✅ Ready | Event simulation |
| **Scenarios** | ✅ Ready | Comparative analysis |
| **Monte Carlo** | ✅ Ready | Probabilistic analysis |

### Aspirational Features

- 🔮 **SimulationAgent**: Autonomous model running
- 🔮 **CalibrationAgent**: Auto-calibration

---

This AGENTS.md documents how GEO-INFER-SIM provides simulation capabilities for agents.

**Last Updated**: 2026-02-24
