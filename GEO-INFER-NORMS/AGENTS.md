# GEO-INFER-NORMS: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-NORMS** module provides normative reasoning capabilities for agents, enabling rule-based behavior, ethical constraints, and regulatory compliance in geospatial contexts.

## Agent Capabilities

### 1. Rule Engine

```python
from geo_infer_norms import RuleEngine

# Define and enforce rules
engine = RuleEngine()

# Add spatial rules
engine.add_rule(
    name="protected_area_restriction",
    condition="location WITHIN protected_areas",
    action="DENY",
    message="Access restricted in protected areas"
)

# Check compliance
result = engine.check(
    agent_id="drone_001",
    proposed_action="fly_through",
    location=point
)

print(f"Allowed: {result.allowed}")
print(f"Reason: {result.reason}")
```

### 2. Regulatory Compliance

```python
from geo_infer_norms import ComplianceChecker

# Check regulatory compliance
compliance = ComplianceChecker()

# Validate against regulations
validation = compliance.validate(
    activity="construction",
    location=project_site,
    regulations=["zoning", "environmental", "building_code"]
)

print(f"Compliant: {validation.is_compliant}")
print(f"Violations: {validation.violations}")
print(f"Required permits: {validation.required_permits}")
```

### 3. Ethical Constraints

```python
from geo_infer_norms import EthicsFramework

# Apply ethical constraints to agent behavior
ethics = EthicsFramework()

# Define ethical boundaries
ethics.add_constraint(
    name="privacy_protection",
    description="Avoid surveillance in residential areas",
    affected_areas=residential_zones,
    constraint_type="soft"
)

# Check action ethics
assessment = ethics.assess(
    action="continuous_monitoring",
    location=proposed_location
)

print(f"Ethical score: {assessment.score}")
print(f"Concerns: {assessment.concerns}")
```

### 4. Norm Reasoning

```python
from geo_infer_norms import NormReasoner

# Reason about norms and conflicts
reasoner = NormReasoner()

# Resolve norm conflicts
resolution = reasoner.resolve_conflict(
    norms=[
        {"type": "obligation", "action": "respond_to_emergency"},
        {"type": "prohibition", "action": "enter_restricted_area"}
    ],
    context=emergency_situation
)

print(f"Resolution: {resolution.recommended_action}")
print(f"Justification: {resolution.justification}")
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Rule Engine** | ✅ Ready | Spatial rule enforcement |
| **Compliance Checker** | ✅ Ready | Regulatory validation |
| **Ethics Framework** | ✅ Ready | Ethical constraints |
| **Norm Reasoner** | ✅ Ready | Conflict resolution |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **ComplianceAgent** | 🔮 High | Autonomous compliance monitoring |
| **EthicsAdvisorAgent** | 🔮 High | Real-time ethical guidance |
| **NormLearningAgent** | 🔮 Medium | Learn norms from examples |

## Use Cases

### Drone Operations Compliance

```python
from geo_infer_norms import DroneCompliance

compliance = DroneCompliance(jurisdiction="faa_part_107")

# Check flight plan compliance
check = compliance.validate_flight(
    flight_path=proposed_route,
    altitude_ft=300,
    time=planned_time,
    operator_cert="remote_pilot"
)

print(f"Flight approved: {check.approved}")
print(f"Restrictions: {check.restrictions}")
```

---

This AGENTS.md documents how GEO-INFER-NORMS provides normative reasoning for agents.

**Last Updated**: 2026-01-26
