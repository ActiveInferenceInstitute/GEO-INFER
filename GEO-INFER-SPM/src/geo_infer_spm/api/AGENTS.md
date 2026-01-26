

# Agent
: api 

## Scope
 This directory contains api components for the module. It provides 1 classes and 0 functions. 

## Classes
 and Functions 

### SPMAP
I
 REST API interface for SPM analysis. **Methods**: - `upload_data(data: Dict[str, Any], format: str) -> Dict[str, Any]`: Upload geospatial data for analysis. - `fit_model(dataset_id: str, design_spec: Dict[str, Any], method: str) -> Dict[str, Any]`: Fit GLM to uploaded dataset. - `run_contrast(result_id: str, contrast_spec: Dict[str, Any], correction: str) -> Dict[str, Any]`: Run statistical contrast on fitted model. - `get_results(result_id: str, format: str) -> Dict[str, Any]`: Retrieve analysis results. - `list_datasets() -> Dict[str, Any]`: List all uploaded datasets. - `list_results() -> Dict[str, Any]`: List all analysis results. 

## Capabilities
 
- **1 classes** for core functionality 

## Integration
 
- **Location**: `GEO-INFER-SPM/src/geo_infer_spm/api` 
- **Type**: Directory Node 