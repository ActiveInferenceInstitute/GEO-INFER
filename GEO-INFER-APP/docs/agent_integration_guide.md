# Agent Integration Guide

## Introduction

This guide explains how to integrate GEO-INFER agents with applications built using GEO-INFER-APP.

## Quick Start

### 1. Create an Agent

```python
from geo_infer_agent import MonitoringAgent

agent = MonitoringAgent(
    name="air_quality_monitor",
    region=city_boundary
)
```

### 2. Connect to Dashboard

```python
from geo_infer_app import Dashboard

dashboard = Dashboard("City Monitoring")

# Connect agent data to map widget
dashboard.add_map_layer(
    name="Agent Location",
    source=agent.location_stream
)

# Show agent observations
dashboard.add_chart(
    name="Observations",
    source=agent.observation_stream
)
```

### 3. Control Agent from UI

```python
# Add agent controls
@dashboard.on("start_button_click")
def start_agent():
    agent.start()

@dashboard.on("stop_button_click")
def stop_agent():
    agent.stop()
```

## Real-Time Data Streams

### Agent Observation Stream

```python
# Subscribe to agent observations
async for obs in agent.observe():
    dashboard.update_chart(obs)
```

### Agent Belief Stream

```python
# Visualize agent beliefs
async for beliefs in agent.belief_stream():
    dashboard.update_heatmap(beliefs.uncertainty)
```

## Multi-Agent Dashboard

```python
from geo_infer_agent import AgentSwarm

swarm = AgentSwarm(agents=[a1, a2, a3])

# Show all agents on map
for agent in swarm.agents:
    dashboard.add_marker(
        id=agent.id,
        source=agent.location_stream
    )

# Aggregate statistics
dashboard.add_metrics([
    {"label": "Active Agents", "value": swarm.active_count},
    {"label": "Coverage", "value": swarm.coverage_percent}
])
```

## Best Practices

1. **Use WebSockets** for real-time agent data
2. **Throttle updates** to avoid UI overload
3. **Buffer observations** for smooth visualization
4. **Handle disconnections** gracefully

---

**Last Updated**: 2026-02-24
