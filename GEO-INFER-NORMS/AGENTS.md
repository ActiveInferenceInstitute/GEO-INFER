# GEO-INFER-NORMS: Normative Framework

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-NORMS module provides regulatory compliance and normative reasoning capabilities enabling agents to operate within legal, ethical, and policy frameworks.

## Implementation Status

### Currently Implemented

- ✅ **ComplianceChecker**: Regulatory compliance validation
- ✅ **PolicyEngine**: Policy rule enforcement
- ✅ **NormativeReasoner**: Ethical and normative reasoning
- ✅ **AuditTrail**: Compliance documentation

### Aspirational/Planned Features

- 🔮 **ComplianceAgent**: Autonomous compliance monitoring
- 🔮 **EthicalReasoningAgent**: Value-aligned decision making

## Agent Capabilities Supported

### 1. Compliance Checking

```python
from geo_infer_norms import ComplianceChecker

# Agent checks compliance
checker = ComplianceChecker()
compliance = checker.validate(
    action=proposed_action,
    regulations=['environmental', 'zoning', 'safety']
)
```

### 2. Normative Reasoning

```python
from geo_infer_norms import NormativeReasoner

# Normative evaluation
reasoner = NormativeReasoner()
permitted = reasoner.evaluate(
    action=agent_intention,
    norms=applicable_norms,
    context=situational_context
)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Compliance Check** | ✅ Ready | Regulation validation |
| **Policy Engine** | ✅ Ready | Rule enforcement |
| **Normative Reasoning** | ✅ Ready | Ethical reasoning |
| **Audit Trail** | ✅ Ready | Documentation |
| **Compliance Agent** | 🔮 Planned | Autonomous monitoring |

---

This AGENTS.md documents how GEO-INFER-NORMS provides compliance capabilities for the agent ecosystem.
