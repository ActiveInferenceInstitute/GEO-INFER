# utils
 ## Overview
 This directory contains utils components. It includes 5 Python modules. ## Components
 ### data_processin
g
.py Data processing utilities for Bayesian inference with geospatial data. **Functions**: `prepare_spatial_data`, `load_geospatial_data`, `_detect_file_format`, `_load_json_data`, `_parse_geojson`, `_process_temporal_data`, `validate_spatial_data`, `create_spatial_grid`, `sample_spatial_data`, `save_processed_data` ### diagnostic
s
.py Diagnostics for Bayesian inference. **Functions**: `mcmc_diagnostics`, `convergence_metrics` ### likelihood
s
.py Likelihood functions for Bayesian geospatial models. **Classes**: `SpatialLikelihood`, `PoissonProcess`, `GaussianLikelihood` ### prior
s
.py Prior distributions for Bayesian geospatial models. **Classes**: `SpatialPrior`, `TemporalPrior`, `GaussianProcessPrior` ### visualizatio
n
.py Visualization utilities for Bayesian geospatial models. **Functions**: `plot_posterior`, `plot_spatial_prediction`, `plot_uncertainty`, `plot_model_comparison` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 