---
title: "GEO-INFER-NORMS: Normative Reasoning and Compliance"
description: "Rule-based behavior, ethical constraints, and regulatory compliance for geospatial agents"
purpose: "Provide normative reasoning, rule engines, and compliance checking for agent behavior"
module_type: "Core Infrastructure"
status: "Beta"
last_updated: "2026-02-25"
dependencies: ["ACT", "AGENT"]
compatibility: ["GEO-INFER-ACT", "GEO-INFER-AGENT", "GEO-INFER-SEC"]
tags: ["norms", "rules", "compliance", "ethics", "regulations"]
difficulty: "Advanced"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-NORMS: Normative Reasoning and Compliance

## Overview

**GEO-INFER-NORMS** provides normative reasoning capabilities for agents, enabling:

- **Rule Engines**: Define and enforce spatial rules and constraints
- **Regulatory Compliance**: Validate against regulations and policies
- **Ethical Constraints**: Apply ethical boundaries to agent behavior
- **Norm Reasoning**: Resolve conflicts between competing norms

## Features

### Rule Engine

```python
from geo_infer_norms import RuleEngine

# Create spatial rule engine
engine = RuleEngine()

# Add protection rules
engine.add_rule(
    name="protected_area_restriction",
    condition="location WITHIN protected_areas",
    action="DENY",
    message="Access restricted in protected areas"
)

engine.add_rule(
    name="noise_ordinance",
    condition="activity == 'construction' AND time.hour < 7",
    action="DENY",
    message="Construction not allowed before 7 AM"
)

# Check compliance
result = engine.check(
    action=proposed_action,
    location=point,
    context={"time": datetime.now()}
)

print(f"Allowed: {result.allowed}")
print(f"Reason: {result.reason}")
```

### Regulatory Compliance

```python
from geo_infer_norms import ComplianceChecker

# Check regulatory compliance
compliance = ComplianceChecker()

# Load regulations
compliance.load_regulations([
    "zoning_code",
    "environmental_regulations",
    "building_code"
])

# Validate project
validation = compliance.validate(
    activity="commercial_development",
    location=project_site,
    project_details=proposal
)

print(f"Compliant: {validation.is_compliant}")
print(f"Violations: {validation.violations}")
print(f"Required permits: {validation.required_permits}")
```

### Ethical Framework

```python
from geo_infer_norms import EthicsFramework

# Apply ethical constraints
ethics = EthicsFramework()

# Define ethical boundaries
ethics.add_constraint(
    name="privacy_protection",
    description="Minimize surveillance in residential areas",
    affected_areas=residential_zones,
    strength="hard"  # Cannot be overridden
)

ethics.add_constraint(
    name="environmental_care",
    description="Minimize environmental disturbance",
    affected_areas=sensitive_habitats,
    strength="soft"  # Can be balanced against other concerns
)

# Assess action ethics
assessment = ethics.assess(
    proposed_action="drone_monitoring",
    location=proposed_location,
    purpose="security"
)

print(f"Ethical score: {assessment.score}")
print(f"Concerns: {assessment.concerns}")
```

### Norm Conflict Resolution

```python
from geo_infer_norms import NormReasoner

# Resolve norm conflicts
reasoner = NormReasoner()

# Define conflicting norms
resolution = reasoner.resolve(
    norms=[
        {"type": "obligation", "action": "respond_to_emergency"},
        {"type": "prohibition", "action": "enter_restricted_area"}
    ],
    context={"is_emergency": True, "lives_at_risk": True}
)

print(f"Resolution: {resolution.recommended_action}")
print(f"Justification: {resolution.justification}")
```

## Norm Types

| Type | Description | Example |
|------|-------------|---------|
| **Obligation** | Must do | Respond to emergencies |
| **Prohibition** | Must not do | Enter protected areas |
| **Permission** | May do | Collect non-sensitive data |
| **Power** | Can create/modify | Grant temporary access |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-ACT** | Action validation |
| **GEO-INFER-AGENT** | Agent behavior constraints |
| **GEO-INFER-SEC** | Security policy enforcement |
| **GEO-INFER-METAGOV** | Governance frameworks |

## Installation

```bash
uv pip install -e "./GEO-INFER-NORMS"
```

## Use Cases

### Drone Flight Compliance

```python
from geo_infer_norms import DroneCompliance

compliance = DroneCompliance(jurisdiction="faa")

# Validate flight plan
check = compliance.validate_flight(
    flight_path=route,
    altitude_agl=300,
    aircraft_type="small_uas"
)

print(f"Approved: {check.approved}")
print(f"Restrictions: {check.restrictions}")
```

## Related Documentation

- [GEO-INFER-SEC](../GEO-INFER-SEC/README.md): Security
- [GEO-INFER-METAGOV](../GEO-INFER-METAGOV/README.md): Governance
- [AGENTS.md](./AGENTS.md): Norms agent capabilities

---

**Status**: Beta - Core functionality stable

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
