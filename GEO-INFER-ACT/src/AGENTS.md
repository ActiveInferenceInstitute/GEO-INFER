# Agent: src

## Scope

This agent handles source code implementation for GEO-INFER-ACT module providing Active Inference modeling capabilities for complex ecological and civic systems.

## Implementation Status

### Currently Implemented

- ✅ **geo_infer_act Package**: Main Python package with Active Inference models and algorithms
- ✅ **Core Components**: Active Inference models, free energy calculation, generative models
- ✅ **Domain Models**: Ecological, climate, urban, resource, and multi-agent models
- ✅ **Package Metadata**: Generated package metadata (geo_infer_act.egg-info)

## Package Structure

### geo_infer_act/

Main Python package containing:

- **core/**: Core Active Inference components
 
- `active_inference.py`: Main ActiveInferenceModel class
 
- `free_energy.py`: FreeEnergyCalculator for variational free energy
 
- `generative_model.py`: GenerativeModel with Markov blankets
 
- `belief_updating.py`: BayesianBeliefUpdate
 
- `policy_selection.py`: PolicySelector
 
- `variational_inference.py`: VariationalInference
 
- `dynamic_causal_model.py`: DynamicCausalModel
 
- `markov_decision_process.py`: MarkovDecisionProcess

- **models/**: Domain-specific Active Inference models
 
- `ecological.py`: EcologicalModel for niche modeling
 
- `climate.py`: ClimateModel for climate adaptation
 
- `urban.py`: UrbanModel for urban planning
 
- `resource.py`: ResourceModel for resource management
 
- `multi_agent.py`: MultiAgentModel for coordination

- **api/**: API interfaces for Active Inference models
- **utils/**: Utility functions for integration and analysis

## Quick Start

```python
from geo_infer_act import ActiveInferenceModel, GenerativeModel, FreeEnergyCalculator
from geo_infer_act.models import EcologicalModel, ClimateModel

# Core Active Inference model
model = ActiveInferenceModel(
    state_dim=10,
    obs_dim=5,
    action_dim=3)

# Domain-specific models
eco_model = EcologicalModel()
climate_model = ClimateModel()

# Run inference
observation = [1, 0] 

# Food signal, threat signal
action = eco_model.step(observation)```

## Integration

- **Location**: `GEO-INFER-ACT/src`
- **Purpose**: Source code implementation directory
- **Package**: `geo_infer_act` - Main Python package for Active Inference
- **Dependencies**: `numpy`, `scipy`, `geo_infer_math`, `geo_infer_bayes`

---

This AGENTS.md documents the source code directory for GEO-INFER-ACT.
