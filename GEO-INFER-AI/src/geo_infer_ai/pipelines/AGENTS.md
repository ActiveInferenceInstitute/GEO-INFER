

# Agent
: pipelines 

## Scope
 This directory contains pipelines components for the module. It provides 1 classes and 0 functions. 

## Classes
 and Functions 

### MLflowPipelin
e
 MLflow pipeline for experiment tracking and model management. **Methods**: - `start_run(run_name: Optional[str], tags: Optional[Dict[str, str]]) -> None`: Start a MLflow run. - `end_run() -> None`: End the current MLflow run. - `log_params(params: Dict[str, Any]) -> None`: Log parameters to MLflow. - `log_metrics(metrics: Dict[str, float], step: Optional[int]) -> None`: Log metrics to MLflow. - `log_model(model: Any, artifact_path: str, registered_model_name: Optional[str]) -> None`: Log a model to MLflow. - `log_artifacts(local_dir: Union[str, Path], artifact_path: Optional[str]) -> None`: Log artifacts (files) to MLflow. - `load_model(model_uri: str) -> Any`: Load a model from MLflow. 

## Capabilities
 
- **1 classes** for core functionality 

## Integration
 
- **Location**: `GEO-INFER-AI/src/geo_infer_ai/pipelines` 
- **Type**: Directory Node 