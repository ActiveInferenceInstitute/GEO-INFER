# utils

## Overview

This directory contains utility functions and helper classes supporting Active
Inference operations including analysis, visualization, mathematical
computations, configuration management, H3 adaptation, spatial diagnostics, and
integration with other GEO-INFER modules and modern inference frameworks. It
includes 8 Python modules providing 13 public classes and 58 public functions.

## Components

### analysis.py

Analysis utilities for Active Inference models.

**Classes**: `ActiveInferenceAnalyzer`

**Functions**: `create_shared_visualizations`, `create_belief_heatmap`, `create_free_energy_plots`, `create_policy_plots`, `create_correlation_analysis`

### config.py

Configuration utilities for GEO-INFER-ACT.

**Functions**: `load_config`, `save_config`, `merge_configs`, `get_config_value`, `_merge_dicts`

### geospatial_ai.py

Geospatial Active Inference Methods

**Classes**: `EnvironmentalState`, `ResourceAllocation`, `SpatialPrediction`, `EnvironmentalActiveInferenceEngine`, `MultiScaleHierarchicalAnalyzer`, `H3SpatialGraph`, `LevelSpatialGraph`

**Functions**: `analyze_multi_scale_patterns`

### h3_adapter.py

H3 v4 adapter and belief-vector normalization helpers.

**Classes**: `H3Adapter`

**Functions**: `get_h3_adapter`, `normalize_belief_vector`, `edge_count_from_graph`

### integration.py

Integration utilities for connecting with other GEO-INFER modules and modern tools.

**Classes**: `ModernToolsIntegration`, `IntegrationUtils`

**Functions**: `initialize_logger`, `integrate_rxinfer`, `integrate_bayeux`, `integrate_pymdp`, `integrate_space`, `integrate_time`, `integrate_sim`, `create_h3_spatial_model`, `coordinate_multi_agent_system`, `_consensus_belief_updating`, `_hierarchical_coordination`, `_pairwise_coordination`

### math.py

Mathematical utilities for active inference models.

**Functions**: `softmax`, `normalize_distribution`, `kl_divergence`, `entropy`, `mutual_information`, `precision_weighted_error`, `gaussian_log_likelihood`, `categorical_log_likelihood`, `dirichlet_kl_divergence`, `sample_categorical`, `compute_free_energy_categorical`, `compute_expected_free_energy`, `numerical_gradient`, `stable_log_sum_exp`, `matrix_log_det`, `detect_stationarity`, `detect_periodicity`, `assess_complexity`, `compute_prediction_accuracy`, `compute_information_gain`, `compute_surprise`, `assess_convergence`, `sample_dirichlet`

### spatial_diagnostics.py

Spatial consistency and information-flow diagnostics for cell-indexed ACT runs.

**Classes**: `SpatialDiagnostics`

**Functions**: `compute_spatial_kl_divergence`, `compute_information_flow`

### visualization.py

Visualization utilities for active inference models.

**Classes**: `BeliefVisualizer`

**Functions**: `plot_belief_update`, `plot_free_energy`, `plot_policies`, `plot_perception_analysis`, `plot_action_analysis`, `create_interpretability_dashboard`, `plot_hierarchical_beliefs`, `plot_markov_blanket`, `plot_h3_grid_static`, `create_h3_gif`, `create_interactive_h3_slider`

`plot_hierarchical_beliefs()` accepts both raw arrays and model-style belief
payloads such as `{"states": ...}`. `plot_markov_blanket()` accepts both
dictionary payloads and the canonical `core.generative_model.MarkovBlanket`
dataclass.



## Usage

```python
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer
from geo_infer_act.utils.math import softmax, kl_divergence
from geo_infer_act.utils.integration import IntegrationUtils

# Analyze Active Inference model behavior
analyzer = ActiveInferenceAnalyzer()
analyzer.record_step(beliefs, observations, actions, policies, free_energy)
report = analyzer.generate_comprehensive_report()

# Mathematical utilities
probabilities = softmax(logits, temperature=1.0)
divergence = kl_divergence(p, q)

# Integration with other modules
utils = IntegrationUtils()
spatial_result = utils.integrate_with_space(spatial_data)
```

## Integration

This directory provides utilities used throughout the module:
- Mathematical functions used by `geo_infer_act.core` for free energy and belief calculations
- Analysis tools used by `geo_infer_act.models` for model evaluation
- Visualization functions for creating plots and dashboards
- Integration utilities for connecting with GEO-INFER-SPACE, GEO-INFER-TIME, and external inference frameworks

## Verification

```bash
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_utils.py -q
uv run --package geo-infer-act --extra dev python GEO-INFER-ACT/verify_comprehensive.py \
  --output-dir GEO-INFER-ACT/examples/output/comprehensive_act_audit
```

The comprehensive audit records utility, math, and visualization evidence under
`examples/output/comprehensive_act_audit/method_audit/inference_math/` and
`examples/output/comprehensive_act_audit/method_audit/visualization_methods/`.
