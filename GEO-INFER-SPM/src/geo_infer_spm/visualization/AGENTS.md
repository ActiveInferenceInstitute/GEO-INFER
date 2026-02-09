# Agent
: visualization

## Scope
 This directory contains visualization components for the module. It provides 0 classes and 18 functions.

## Classes
 and Functions

### plot_model_diagnostics
 `plot_model_diagnostics(spm_result: SPMResult, figsize: Tuple[int, int]) -> Dict[str, Any]` Create model diagnostic plots.

### plot_contrast_results
 `plot_contrast_results(contrast_result: ContrastResult, figsize: Tuple[int, int]) -> Dict[str, Any]` Create plots for contrast analysis results.

### create_interactive_map
 `create_interactive_map(spm_result: SPMResult, contrast_idx: int, map_type: str, **kwargs) -> Optional[Any]` Create interactive geographical map of SPM results.

### create_dashboard
 `create_dashboard(spm_result: SPMResult, include_diagnostics: bool) -> Optional[Any]` Create interactive dashboard of SPM results.

### create_time_series_explorer
 `create_time_series_explorer(spm_result: SPMResult) -> Optional[Any]` Create interactive time series explorer for temporal SPM data.

### create_statistical_map
 `create_statistical_map(spm_result: SPMResult, contrast_idx: int, threshold: Optional[float], colormap: str, title: Optional[str]) -> Dict[str, Any]` Create statistical parametric map visualization.

### plot_spm_results
 `plot_spm_results(spm_result: SPMResult, plot_type: str, **kwargs) -> Dict[str, Any]` Create SPM results visualization.

### create_interactive_map
 `create_interactive_map(spm_result: SPMResult, contrast_idx: int, **kwargs) -> Optional[Any]` Create interactive statistical map using plotly.

## Capabilities

- **18 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-SPM/src/geo_infer_spm/visualization`
- **Type**: Directory Node
