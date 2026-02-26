# GEO-INFER-EMERGENCY: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-EMERGENCY** module provides emergency response capabilities for agents, enabling disaster management, resource coordination, and evacuation planning.

## Agent Capabilities

### 1. Incident Management

```python
from geo_infer_emergency import IncidentManager

# Manage emergency incidents
manager = IncidentManager()

incident = manager.create_incident(
    type="wildfire",
    location=fire_origin,
    severity="high",
    resources_needed=["fire", "ems", "law"])

print(f"Incident ID: {incident.id}")
print(f"ICS structure: {incident.command_structure}")```

### 2. Resource Deployment

```python
from geo_infer_emergency import ResourceDeployer

# Deploy emergency resources
deployer = ResourceDeployer()

deployment = deployer.optimize(
    incident=active_incident,
    resources=available_units,
    priorities=["life_safety", "containment"])

print(f"Assignments: {deployment.assignments}")
print(f"Coverage: {deployment.coverage}%")```

### 3. Evacuation Planning

```python
from geo_infer_emergency import EvacuationPlanner

# Plan evacuations
planner = EvacuationPlanner()

plan = planner.create(
    threat_zone=danger_area,
    population=affected_population,
    shelters=available_shelters,
    road_network=roads)

print(f"Routes: {len(plan.routes)}")
print(f"Clearance time: {plan.clearance_hours} hours")```

### 4. Situational Awareness

```python
from geo_infer_emergency import SituationMonitor

# Monitor emergency situation
monitor = SituationMonitor()

sitrep = monitor.get_situation(
    incident=incident_id,
    include=["perimeter", "resources", "weather"])

print(f"Threat evolution: {sitrep.threat_status}")
print(f"Population at risk: {sitrep.at_risk_population}")```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Incidents** | ✅ Ready | ICS management |
| **Resources** | ✅ Ready | Deployment optimization |
| **Evacuation** | ✅ Ready | Route planning |
| **Situational** | ✅ Ready | Real-time monitoring |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **IncidentCommanderAgent** | 🔮 High | Autonomous IC support |
| **EvacuationAgent** | 🔮 High | Dynamic routing |

## Use Cases

### Multi-Agency Response

```python
from geo_infer_emergency import MultiAgencyCoordinator

coordinator = MultiAgencyCoordinator(incident=incident)

coordinator.assign_sectors([
    {"agency": "fire", "sector": "alpha"},
    {"agency": "law", "sector": "bravo"}])

coordinator.establish_unified_command()```

---

This AGENTS.md documents how GEO-INFER-EMERGENCY provides emergency capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
