# Agent
: core ## Scope
 This directory contains core components for the module. It provides 4 classes and 0 functions. ## Classes
 and Functions ### ExecutionStrateg
y
 Available execution strategies for workflow orchestration. ### ModuleStatu
s
 Module availability and health status. ### WorkflowExecutio
n
 Represents a single workflow execution instance. ### ModuleOrchestrato
r
 orchestrator for managing cross-module integrations and workflows. **Methods**: - `register_workflow(workflow: WorkflowDefinition) -> bool`: Register a workflow definition. - `get_workflow_status(execution_id: str) -> Optional[WorkflowExecution]`: Get the status of a workflow execution. - `get_module_health() -> Dict[str, ModuleStatus]`: Get current health status of all modules. - `list_workflows() -> List[str]`: List all registered workflow IDs. - `get_workflow_definition(workflow_id: str) -> Optional[WorkflowDefinition]`: Get workflow definition by ID. - `shutdown()`: Gracefully shutdown the orchestrator. ## Capabilities
 - **4 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-EXAMPLES/src/geo_infer_examples/core` - **Type**: Directory Node 