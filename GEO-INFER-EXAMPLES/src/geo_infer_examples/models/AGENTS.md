# Agent
: models ## Scope
 This directory contains models components for the module. It provides 17 classes and 2 functions. ## Classes
 and Functions ### ModuleTyp
e
 Categories of GEO-INFER modules. ### DataForma
t
 Supported data formats for inter-module communication. ### IntegrationPatter
n
 Integration patterns between modules. ### ModuleSpe
c
 Specification for a GEO-INFER module. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert to dictionary representation. - `from_dict(cls, data: Dict[str, Any]) -> 'ModuleSpec'`: Create from dictionary representation. ### ModuleConnectio
n
 Defines connection between two modules. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert to dictionary representation. ### WorkflowSte
p
 Individual step in a workflow. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert to dictionary representation. - `from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep'`: Create from dictionary representation. ### WorkflowDefinitio
n
 workflow definition. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert to dictionary representation. - `from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDefinition'`: Create from dictionary representation. - `copy() -> 'WorkflowDefinition'`: Create a deep copy of the workflow definition. ### ExecutionContex
t
 Context for workflow execution. ### SpatialTemporalDat
a
 Standardized spatial-temporal data structure. **Methods**: - `to_geojson() -> Dict[str, Any]`: Convert to GeoJSON format. ### AnalysisResul
t
 Standardized analysis result structure. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert to dictionary representation. ### IntegrationResul
t
 Result of cross-module integration. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert to dictionary representation. - `add_module_result(module_name: str, result: AnalysisResult)`: Add result from a specific module. - `get_module_result(module_name: str) -> Optional[AnalysisResult]`: Get result from a specific module. ### HealthSurveillanceDat
a
 Specialized data structure for health surveillance. **Methods**: - `to_health_geojson() -> Dict[str, Any]`: Convert to health-specific GeoJSON format. ### AgriculturalDat
a
 Specialized data structure for agricultural applications. **Methods**: - `to_agricultural_geojson() -> Dict[str, Any]`: Convert to agriculture-specific GeoJSON format. ### UrbanPlanningDat
a
 Specialized data structure for urban planning. **Methods**: - `to_urban_geojson() -> Dict[str, Any]`: Convert to urban planning-specific GeoJSON format. ### ClimateDat
a
 Specialized data structure for climate applications. **Methods**: - `to_climate_geojson() -> Dict[str, Any]`: Convert to climate-specific GeoJSON format. ### IntegrationPattern
s
 Collection of common integration patterns and templates. **Methods**: - `create_health_surveillance_workflow() -> WorkflowDefinition`: Create a standard health surveillance workflow. - `create_precision_agriculture_workflow() -> WorkflowDefinition`: Create a precision agriculture monitoring workflow. - `create_active_inference_workflow() -> WorkflowDefinition`: Create an active inference feedback loop workflow. ### DataFormatConverte
r
 Utility class for converting between different data formats. **Methods**: - `convert_to_standard_format(data: Dict[str, Any], source_format: DataFormat, target_format: DataFormat) -> Dict[str, Any]`: Convert data between different standardized formats. ### load_workflow_from_fil
e
 `load_workflow_from_file(file_path: Union[str, Path]) -> WorkflowDefinition` Load workflow definition from YAML or JSON file. ### save_workflow_to_fil
e
 `save_workflow_to_file(workflow: WorkflowDefinition, file_path: Union[str, Path], format: str) -> None` Save workflow definition to YAML or JSON file. ## Capabilities
 - **17 classes** for core functionality - **2 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-EXAMPLES/src/geo_infer_examples/models` - **Type**: Directory Node 