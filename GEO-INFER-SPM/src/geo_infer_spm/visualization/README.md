# visualization
 ## Overview
 This directory contains visualization components. It includes 3 Python modules. ## Components
 ### diagnostic
s
.py Diagnostic visualization tools for SPM analysis **Functions**: `plot_model_diagnostics`, `plot_contrast_results`, `_plot_qq_residuals`, `_plot_residuals_vs_fitted`, `_plot_scale_location`, `_plot_residual_histogram`, `_plot_cooks_distance`, `_plot_leverage`, `_compute_diagnostic_stats` ### interactiv
e
.py Interactive visualization tools for GEO-INFER-SPM **Functions**: `create_interactive_map`, `create_dashboard`, `create_time_series_explorer` ### map
s
.py Statistical map visualization for GEO-INFER-SPM **Functions**: `create_statistical_map`, `plot_spm_results`, `_plot_beta_coefficients`, `_plot_residuals`, `_plot_model_diagnostics`, `create_interactive_map` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 