# GEO-INFER-HEALTH: Health Intelligence Agents

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---


## Overview

The GEO-INFER-HEALTH module provides intelligent agents for public health surveillance, disease outbreak detection, healthcare resource optimization, and environmental health monitoring. These agents leverage spatial epidemiology and Active Inference for adaptive health system management.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational.

### Currently Implemented

- ✅ **DiseaseModelingPipeline**: Epidemiological modeling and prediction
- ✅ **HealthAccessAnalyzer**: Healthcare accessibility analysis
- ✅ **EnvironmentalHealthAssessor**: Environmental health factor analysis
- ✅ **HealthDataIntegrator**: Multi-source health data fusion

### Aspirational/Planned Features

- 🔮 **OutbreakDetectionAgent**: Early warning for disease outbreaks
- 🔮 **ResourceAllocationAgent**: Dynamic healthcare resource optimization
- 🔮 **ContactTracingAgent**: Spatial contact network analysis

## Agent Architecture

### Disease Surveillance System

**Location**: `src/geo_infer_health/core/disease_modeling.py`

```python
from geo_infer_health.core.disease_modeling import DiseaseModelingPipeline

# Initialize disease surveillance
pipeline = DiseaseModelingPipeline(
    epidemiological_models=['SIR', 'SEIR', 'spatial_transmission'],
    data_sources=['case_reports', 'hospital_admissions', 'syndromic_surveillance']
)

# Run spatial epidemiological analysis
outbreak_assessment = pipeline.assess_outbreak(
    case_data=reported_cases,
    population_data=demographic_data,
    spatial_resolution='county',
    temporal_window='7_days'
)
```

### Healthcare Access Analysis

**Location**: `src/geo_infer_health/core/health_access.py`

```python
from geo_infer_health.core.health_access import HealthAccessAnalyzer

# Analyze healthcare accessibility
analyzer = HealthAccessAnalyzer()

# Calculate accessibility metrics
accessibility = analyzer.analyze_access(
    population_distribution=population_data,
    facility_locations=healthcare_facilities,
    transportation_network=road_network,
    metrics=['travel_time', 'distance', 'capacity']
)
```

## Proposed Agents 🔮

### 1. Outbreak Detection Agent 🔮

**Purpose**: Early detection and warning for disease outbreaks.

```python
# 🔮 Planned - Conceptual Example
from geo_infer_health.agents import OutbreakDetectionAgent

agent = OutbreakDetectionAgent(
    name="outbreak_sentinel",
    surveillance_region=monitoring_area,
    detection_methods=['aberration_detection', 'cluster_analysis', 'syndromic']
)

# Configure detection thresholds
agent.set_thresholds({
    'case_rate_increase': 2.0,  # 2x baseline
    'spatial_clustering': 0.05,  # p-value
    'temporal_acceleration': 0.3  # growth rate
})

# Start surveillance
agent.start()
alerts = agent.get_alerts()
```

### 2. Resource Allocation Agent 🔮

**Purpose**: Optimal allocation of healthcare resources during crises.

```python
# 🔮 Planned - Conceptual Example
from geo_infer_health.agents import ResourceAllocationAgent

agent = ResourceAllocationAgent(
    name="resource_optimizer",
    resource_types=['hospital_beds', 'ventilators', 'personnel', 'vaccines'],
    optimization_criteria=['minimize_mortality', 'equitable_access']
)

# Generate allocation plan
allocation = agent.optimize_allocation(
    demand_forecast=predicted_demand,
    resource_inventory=available_resources,
    constraints=['transport_capacity', 'storage_requirements']
)
```

## Integration with Other Modules

- **GEO-INFER-SPACE**: Spatial analysis for disease mapping and clustering
- **GEO-INFER-TIME**: Temporal modeling for outbreak forecasting
- **GEO-INFER-RISK**: Health risk assessment and vulnerability mapping
- **GEO-INFER-ACT**: Active Inference for adaptive surveillance strategies

## Implementation Status

| Agent Type | Status | Description |
|------------|--------|-------------|
| **DiseaseModelingPipeline** | ✅ Implemented | Epidemiological modeling |
| **HealthAccessAnalyzer** | ✅ Implemented | Accessibility analysis |
| **EnvironmentalHealthAssessor** | ✅ Implemented | Environmental factors |
| **OutbreakDetectionAgent** | 🔮 Planned | Early warning systems |
| **ResourceAllocationAgent** | 🔮 Planned | Resource optimization |
| **ContactTracingAgent** | 🔮 Planned | Contact networks |

---

This AGENTS.md documents the health intelligence agent implementations for public health surveillance and healthcare resource management.
