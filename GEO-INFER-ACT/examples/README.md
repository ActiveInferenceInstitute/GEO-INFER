# GEO-INFER-ACT Examples

This directory contains working examples demonstrating Active Inference capabilities in geospatial contexts.

## Available Examples

| Example | Description | VFE/EFE Usage |
|---------|-------------|---------------|
| [`simple_model.py`](simple_model.py) | Basic Active Inference with categorical states | VFE in belief updates |
| [`modern_active_inference.py`](modern_active_inference.py) | Hierarchical models, multi-agent coordination | VFE: L234-239, EFE: L46 |
| [`h3_active_inference.py`](h3_active_inference.py) | H3 spatial indexing integration | VFE: L265-313 |
| [`spatial_inference_demo.py`](spatial_inference_demo.py) | Spatial VFE/EFE demonstration | VFE: L248, EFE: via `spatial_action()` |
| [`urban_planning.py`](urban_planning.py) | Urban planning with spatial constraints | VFE/EFE for planning decisions |
| [`ecological_model.py`](ecological_model.py) | Ecological system modeling | VFE for environmental belief updates |

## Free Energy Calculations

### Variational Free Energy (VFE)

VFE measures the divergence between beliefs and observations. Lower VFE = better model fit.

**Core implementations:**

- [`core/free_energy.py`](../src/geo_infer_act/core/free_energy.py) - `FreeEnergyCalculator` class
- [`core/spatial_agent.py`](../src/geo_infer_act/core/spatial_agent.py) - `_compute_spatial_free_energy()` for H3 cells
- [`utils/math.py`](../src/geo_infer_act/utils/math.py) - `compute_free_energy_categorical()` utility

### Expected Free Energy (EFE)

EFE guides action selection by balancing epistemic (information-seeking) and pragmatic (goal-directed) value.

**Core implementations:**

- [`core/policy_selection.py`](../src/geo_infer_act/core/policy_selection.py) - `compute_expected_free_energy()`
- [`core/spatial_agent.py`](../src/geo_infer_act/core/spatial_agent.py) - `spatial_action()` for spatial policies
- [`utils/math.py`](../src/geo_infer_act/utils/math.py) - `compute_expected_free_energy()` utility

## Running Examples

```bash
cd GEO-INFER-ACT

# Run ALL examples with summary report
python examples/run_all_examples.py

# Run quick subset (simple_model + spatial_inference_demo)
python examples/run_all_examples.py --quick

# Run with verbose output
python examples/run_all_examples.py --verbose

# Individual examples
python examples/simple_model.py
python examples/modern_active_inference.py

# H3 spatial examples
python examples/h3_active_inference.py
python examples/spatial_inference_demo.py

# Domain-specific examples
python examples/urban_planning.py
python examples/ecological_model.py
```

## Documentation Links

For theoretical background on VFE and EFE calculations, see:

- [Free Energy Principle](../docs/free_energy_principle.md) - VFE/EFE theory and equations
- [Mathematical Framework](../docs/mathematical_framework.md) - Detailed mathematical formulations
- [Active Inference Overview](../docs/active_inference_overview.md) - Conceptual introduction
- [Geospatial Applications](../docs/geospatial_applications.md) - Spatial AI applications

## Integration

GEO-INFER-ACT integrates with:

- **SPACE**: Spatial Active Inference models
- **AGENT**: Active Inference agents
- **ANT**: Swarm intelligence with Active Inference
- **BAYES**: Bayesian belief updating

See `GEO-INFER-EXAMPLES` for cross-module integration examples.
