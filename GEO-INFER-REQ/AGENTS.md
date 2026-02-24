# GEO-INFER-REQ: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-REQ** module provides requirements management and dependency resolution capabilities for agents, enabling intelligent project planning and resource management.

## Agent Capabilities

### 1. Requirements Analysis

```python
from geo_infer_req import RequirementsAnalyzer

# Analyze project requirements
analyzer = RequirementsAnalyzer()

# Parse and validate requirements
requirements = analyzer.parse(
    source="requirements.txt",
    format="pip")

# Check compatibility
compatibility = analyzer.check_compatibility(
    requirements=requirements,
    environment={
        "python_version": "3.11",
        "platform": "linux"
    })

print(f"Compatible: {compatibility.is_compatible}")
print(f"Issues: {compatibility.issues}")```

### 2. Dependency Resolution

```python
from geo_infer_req import DependencyResolver

# Resolve complex dependency trees
resolver = DependencyResolver()

# Resolve dependencies with constraints
solution = resolver.resolve(
    requirements=["geo-infer-act>=1.0", "geo-infer-space>=2.0"],
    constraints={
        "numpy": ">=1.20,<2.0",
        "h3": ">=4.0"
    })

print(f"Resolved packages: {solution.packages}")
print(f"Install order: {solution.install_order}")```

### 3. Project Planning

```python
from geo_infer_req import ProjectPlanner

# Plan project with requirements
planner = ProjectPlanner()

# Create project plan
plan = planner.create_plan(
    project_type="geospatial_analysis",
    modules_needed=["SPACE", "TIME", "ACT"],
    constraints={
        "memory_limit": "8GB",
        "time_budget": "2_hours"
    })

print(f"Required modules: {plan.modules}")
print(f"Estimated resources: {plan.resource_estimate}")
print(f"Setup steps: {plan.setup_steps}")```

### 4. Environment Management

```python
from geo_infer_req import EnvironmentManager

# Manage execution environments
env_manager = EnvironmentManager()

# Create isolated environment
env = env_manager.create(
    name="analysis_env",
    requirements=["geo-infer-act", "geo-infer-space"],
    isolation="virtual")

# Validate environment
validation = env_manager.validate(env)
print(f"Environment valid: {validation.is_valid}")```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Requirements Parsing** | ✅ Ready | Parse various formats |
| **Dependency Resolution** | ✅ Ready | Resolve complex trees |
| **Compatibility Check** | ✅ Ready | Version compatibility |
| **Environment Setup** | ✅ Ready | Environment creation |
| **Constraint Solving** | ✅ Ready | SAT-based solving |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **RequirementsPlannerAgent** | 🔮 High | Auto-suggest requirements |
| **DependencyOptimizerAgent** | 🔮 Medium | Optimize dependencies |
| **UpdateAdvisorAgent** | 🔮 Medium | Recommend updates |

## Integration with Agent Framework

```mermaid
graph TD
    subgraph Requirements_Management
        PARSE[Requirements Parser]
        RESOLVE[Dependency Resolver]
        PLAN[Project Planner]
        ENV[Environment Manager]
    end
    
    subgraph Agent_Operations
        SETUP[Agent Setup]
        DEPLOY[Agent Deployment]
        UPDATE[Agent Update]
    end
    
    PARSE --> SETUP
    RESOLVE --> SETUP
    PLAN --> DEPLOY
    ENV --> DEPLOY
    RESOLVE --> UPDATE```

## Use Cases

### 1. Agent Self-Configuration

```python
from geo_infer_req import RequirementsManager
from geo_infer_agent import BaseAgent

class SelfConfiguringAgent(BaseAgent):
    def __init__(self, capabilities_needed):
        self.req_manager = RequirementsManager()
        
       

# Resolve required dependencies
        deps = self.req_manager.resolve_for_capabilities(
            capabilities_needed
        )
        
       

# Verify environment
        if not self.req_manager.verify_installed(deps):
            self.req_manager.install_missing(deps)
        
        super().__init__()```

### 2. Multi-Agent Deployment

```python
from geo_infer_req import DeploymentPlanner

# Plan multi-agent deployment
planner = DeploymentPlanner()

deployment = planner.plan_deployment(
    agents=["DataCollectorAgent", "AnalysisAgent", "ReportAgent"],
    target_environment="kubernetes",
    resources={"cpu": "4", "memory": "16GB"})

print(f"Container images: {deployment.images}")
print(f"Resource allocation: {deployment.resources}")
print(f"Deployment order: {deployment.order}")```

---

This AGENTS.md documents how GEO-INFER-REQ provides requirements management for agents.

**Last Updated**: 2026-02-24
