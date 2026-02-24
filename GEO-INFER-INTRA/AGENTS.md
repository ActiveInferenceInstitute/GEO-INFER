# GEO-INFER-INTRA: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-INTRA** module provides internal infrastructure that supports agent operations across the entire GEO-INFER framework, including configuration management, testing utilities, and repository assessment.

## Agent Capabilities

### Configuration Access

Agents can access centralized configuration:

```python
from geo_infer_intra.config import Config, load_config

class ConfigAwareAgent:
    def __init__(self):
        self.config = load_config("config/agent_settings.yaml")
        self.log_level = self.config.get("logging.level", "INFO")
        self.model_params = self.config.get("agent.model_params")
    
    def reload_config(self):
        """Hot-reload configuration without restart."""
        self.config = load_config("config/agent_settings.yaml")```

### Testing Infrastructure

Agents can use shared testing utilities:

```python
from geo_infer_intra.testing import GeospatialTestCase
from geo_infer_agent import BaseAgent

class TestMyAgent(GeospatialTestCase):
    def setUp(self):
        self.agent = BaseAgent(agent_id="test_agent")
        self.test_region = self.create_test_polygon(
            bounds=[-122.5, 37.7, -122.3, 37.9]
        )
    
    def test_agent_spatial_perception(self):
        """Test agent perceives spatial environment correctly."""
        observation = self.agent.perceive(self.test_region)
        self.assertIsNotNone(observation)```

### Repository Assessment

Agents can assess repository health:

```python
from geo_infer_intra import RepositoryAssessor

class RepositoryMonitorAgent:
    def __init__(self):
        self.assessor = RepositoryAssessor()
    
    def check_code_quality(self):
        """Monitor code quality metrics."""
        report = self.assessor.assess()
        return {
            "quality_score": report.code_quality_score,
            "doc_coverage": report.doc_coverage,
            "test_coverage": report.test_coverage,
            "issues": report.issues
        }```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Configuration Management** | ✅ Ready | YAML config loading and merging |
| **Testing Utilities** | ✅ Ready | Geospatial and temporal test helpers |
| **Repository Assessment** | ✅ Ready | Code quality and coverage analysis |
| **Template Management** | ✅ Ready | Project and module templates |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **ConfigurationAgent** | 🔮 Medium | Dynamic config optimization |
| **TestGeneratorAgent** | 🔮 Medium | Automatic test generation |
| **DocumentationAgent** | 🔮 High | Auto-documentation from code |

## Integration with Agent Framework

```mermaid
graph TD
    subgraph GEO_INFER_INTRA
        CONFIG[Configuration Manager]
        TEST[Testing Infrastructure]
        ASSESS[Repository Assessor]
    end
    
    subgraph Agent_Modules
        AGENT[GEO-INFER-AGENT]
        ACT[GEO-INFER-ACT]
        ANT[GEO-INFER-ANT]
    end
    
    CONFIG --> AGENT
    CONFIG --> ACT
    CONFIG --> ANT
    TEST --> AGENT
    TEST --> ACT
    TEST --> ANT
    ASSESS --> AGENT```

## Use Cases

### 1. Agent Development Workflow

```python
from geo_infer_intra.config import load_config
from geo_infer_intra.testing import AgentTestCase

# Load development configuration
dev_config = load_config("config/development.yaml")

# Create agent with config
agent = MyAgent(config=dev_config)

# Run tests
class TestMyAgent(AgentTestCase):
    def test_agent_behavior(self):
        result = agent.act()
        self.assertValidAction(result)```

### 2. Continuous Integration

```python
from geo_infer_intra import RepositoryAssessor

def ci_quality_check():
    """Run quality checks in CI pipeline."""
    assessor = RepositoryAssessor()
    report = assessor.assess()
    
    if report.code_quality_score < 80:
        raise QualityError("Code quality below threshold")
    if report.test_coverage < 70:
        raise CoverageError("Test coverage below threshold")
    
    return report```

---

This AGENTS.md documents how GEO-INFER-INTRA provides infrastructure support for all agent operations in the framework.

**Last Updated**: 2026-02-24
