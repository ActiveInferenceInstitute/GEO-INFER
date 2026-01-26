# models

## Overview

This directory contains domain-specific Active Inference models implementing specialized generative models for ecological, climate, urban planning, resource management, and multi-agent coordination applications. It includes 6 Python modules providing ready-to-use Active Inference models for various problem domains.

## Components

### base.py

Base models for active inference framework.

**Classes**: `ActiveInferenceModel`, `CategoricalModel`, `GaussianModel`

### climate.py

Climate Model for Active Inference.

**Classes**: `ClimateModel`

### ecological.py

Ecological niche modeling using Active Inference. Simulates organism adaptation to ecological niches by inferring hidden environmental states (resources, predation risk) from observations and selecting adaptive policies.

**Classes**: `EcologicalModel`

**Key Features**:
- Resource level and predation risk state inference
- Food and threat signal observation processing
- Adaptive policy selection (Wait, Forage, Hide)

### multi_agent.py

Multi-agent model for active inference.

**Classes**: `MultiAgentModel`

### resource.py

Resource management model for active inference.

**Classes**: `ResourceModel`

### urban.py

Urban planning model using active inference.

**Classes**: `UrbanModel`



## Usage

```python
from geo_infer_act.models import EcologicalModel, ClimateModel, UrbanModel

# Ecological niche modeling
eco_model = EcologicalModel()
observation = [1, 0]  # Food signal, threat signal
action = eco_model.step(observation)

# Climate adaptation
climate_model = ClimateModel()
climate_action = climate_model.step(climate_observations)

# Urban planning
urban_model = UrbanModel()
urban_result = urban_model.run_simulation(n_steps=100)
```

## Integration

This directory provides domain-specific Active Inference models used by:
- API interfaces in `geo_infer_act.api`
- Example demonstrations in `geo_infer_act.examples`
- Domain modules (GEO-INFER-AG, GEO-INFER-FOREST, GEO-INFER-CLIMATE) for specialized applications
- Multi-agent systems in `geo_infer_agent` for coordinated inference
