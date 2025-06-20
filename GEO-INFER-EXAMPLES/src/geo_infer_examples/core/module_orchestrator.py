#!/usr/bin/env python3
"""
GEO-INFER Module Orchestrator

Advanced orchestration system for managing cross-module integrations,
workflow execution, and pattern-based coordination across the GEO-INFER ecosystem.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models.integration_models import (
    WorkflowDefinition, ModuleSpec, IntegrationResult, 
    ExecutionContext, ModuleConnection
)
from ..utils.config_manager import ConfigManager
from ..utils.logging_helper import setup_logging
from ..utils.api_connector import APIConnector
from ..monitoring.performance_monitor import PerformanceMonitor


class ExecutionStrategy(Enum):
    """Available execution strategies for workflow orchestration."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    EVENT_DRIVEN = "event_driven"
    FEEDBACK_LOOP = "feedback_loop"


class ModuleStatus(Enum):
    """Module availability and health status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    ERROR = "error"
    INITIALIZING = "initializing"


@dataclass
class WorkflowExecution:
    """Represents a single workflow execution instance."""
    workflow_id: str
    execution_id: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    module_statuses: Dict[str, ModuleStatus] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class ModuleOrchestrator:
    """
    Advanced orchestrator for managing cross-module integrations and workflows.
    
    Key capabilities:
    - Pattern-based workflow execution
    - Module health monitoring and failover
    - Performance optimization and resource management
    - Event-driven coordination
    - Configuration management across modules
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 monitoring_enabled: bool = True,
                 resilience_enabled: bool = True):
        """
        Initialize the module orchestrator.
        
        Args:
            config_path: Path to orchestrator configuration file
            monitoring_enabled: Enable performance and health monitoring
            resilience_enabled: Enable automatic failover and recovery
        """
        self.logger = setup_logging(__name__)
        self.config_manager = ConfigManager(config_path)
        self.api_connector = APIConnector()
        
        # Core components
        self.modules: Dict[str, Any] = {}
        self.module_health: Dict[str, ModuleStatus] = {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        # Monitoring and optimization
        self.monitoring_enabled = monitoring_enabled
        self.resilience_enabled = resilience_enabled
        if monitoring_enabled:
            self.performance_monitor = PerformanceMonitor()
        
        # Execution resources
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.event_bus = {}  # Simple event system
        
        # Load configuration
        self._load_configuration()
        self._initialize_modules()
    
    def _load_configuration(self):
        """Load orchestrator configuration and workflow definitions."""
        try:
            # Load orchestrator settings
            orchestrator_config = self.config_manager.get_config('orchestrator', {})
            self.max_concurrent_workflows = orchestrator_config.get('max_concurrent_workflows', 5)
            self.default_timeout = orchestrator_config.get('default_timeout', 300)
            self.retry_attempts = orchestrator_config.get('retry_attempts', 3)
            
            # Load workflow definitions
            workflows_path = Path(__file__).parent.parent / 'workflows'
            if workflows_path.exists():
                for workflow_file in workflows_path.glob('*.yaml'):
                    with open(workflow_file, 'r') as f:
                        workflow_data = yaml.safe_load(f)
                        workflow = WorkflowDefinition.from_dict(workflow_data)
                        self.workflows[workflow.id] = workflow
                        
            self.logger.info(f"Loaded {len(self.workflows)} workflow definitions")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def _initialize_modules(self):
        """Initialize and health-check available modules."""
        module_configs = self.config_manager.get_config('modules', {})
        
        for module_name, module_config in module_configs.items():
            try:
                self._initialize_module(module_name, module_config)
            except Exception as e:
                self.logger.warning(f"Failed to initialize module {module_name}: {e}")
                self.module_health[module_name] = ModuleStatus.ERROR
    
    def _initialize_module(self, module_name: str, config: Dict[str, Any]):
        """Initialize a specific module and check its health."""
        self.logger.info(f"Initializing module: {module_name}")
        self.module_health[module_name] = ModuleStatus.INITIALIZING
        
        try:
            # Health check via API
            health_response = self.api_connector.get(
                module=module_name,
                endpoint='/health',
                timeout=10
            )
            
            if health_response.status_code == 200:
                self.module_health[module_name] = ModuleStatus.AVAILABLE
                self.modules[module_name] = {
                    'config': config,
                    'api_base': config.get('api_base'),
                    'capabilities': health_response.json().get('capabilities', [])
                }
                self.logger.info(f"Module {module_name} is available")
            else:
                self.module_health[module_name] = ModuleStatus.DEGRADED
                self.logger.warning(f"Module {module_name} health check failed")
                
        except Exception as e:
            self.module_health[module_name] = ModuleStatus.UNAVAILABLE
            self.logger.error(f"Module {module_name} initialization failed: {e}")
    
    def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """
        Register a new workflow definition.
        
        Args:
            workflow: Workflow definition to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate workflow
            if not self._validate_workflow(workflow):
                return False
            
            self.workflows[workflow.id] = workflow
            self.logger.info(f"Registered workflow: {workflow.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering workflow {workflow.id}: {e}")
            return False
    
    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition and module dependencies."""
        # Check if required modules are available
        for step in workflow.steps:
            module_name = step.module
            if module_name not in self.modules:
                self.logger.error(f"Required module {module_name} not available")
                return False
            
            if self.module_health[module_name] == ModuleStatus.ERROR:
                self.logger.error(f"Required module {module_name} in error state")
                return False
        
        # Validate step dependencies
        step_names = {step.name for step in workflow.steps}
        for step in workflow.steps:
            for dependency in step.dependencies:
                if dependency not in step_names:
                    self.logger.error(f"Invalid dependency {dependency} in step {step.name}")
                    return False
        
        return True
    
    async def execute_workflow(self, 
                             workflow_id: str,
                             input_data: Dict[str, Any],
                             execution_context: Optional[ExecutionContext] = None) -> IntegrationResult:
        """
        Execute a registered workflow with given input data.
        
        Args:
            workflow_id: ID of workflow to execute
            input_data: Input data for workflow execution
            execution_context: Optional execution context and parameters
            
        Returns:
            Integration result with outputs and metadata
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = f"{workflow_id}_{int(time.time())}"
        
        # Create execution tracking
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            execution_id=execution_id,
            status="initializing",
            start_time=time.time()
        )
        self.active_executions[execution_id] = execution
        
        try:
            self.logger.info(f"Starting workflow execution: {execution_id}")
            
            if self.monitoring_enabled:
                self.performance_monitor.start_workflow_tracking(execution_id)
            
            # Execute based on strategy
            if workflow.execution_strategy == ExecutionStrategy.SEQUENTIAL:
                result = await self._execute_sequential(workflow, input_data, execution)
            elif workflow.execution_strategy == ExecutionStrategy.PARALLEL:
                result = await self._execute_parallel(workflow, input_data, execution)
            elif workflow.execution_strategy == ExecutionStrategy.CONDITIONAL:
                result = await self._execute_conditional(workflow, input_data, execution)
            elif workflow.execution_strategy == ExecutionStrategy.EVENT_DRIVEN:
                result = await self._execute_event_driven(workflow, input_data, execution)
            elif workflow.execution_strategy == ExecutionStrategy.FEEDBACK_LOOP:
                result = await self._execute_feedback_loop(workflow, input_data, execution)
            else:
                raise ValueError(f"Unknown execution strategy: {workflow.execution_strategy}")
            
            execution.status = "completed"
            execution.end_time = time.time()
            execution.results = result.data
            
            if self.monitoring_enabled:
                execution.performance_metrics = self.performance_monitor.get_workflow_metrics(execution_id)
            
            self.logger.info(f"Workflow execution completed: {execution_id}")
            return result
            
        except Exception as e:
            execution.status = "failed"
            execution.end_time = time.time()
            execution.errors.append(str(e))
            
            self.logger.error(f"Workflow execution failed: {execution_id} - {e}")
            
            if self.resilience_enabled:
                # Attempt recovery
                recovery_result = await self._attempt_recovery(workflow, input_data, execution, e)
                if recovery_result:
                    return recovery_result
            
            raise
        finally:
            if self.monitoring_enabled:
                self.performance_monitor.stop_workflow_tracking(execution_id)
    
    async def _execute_sequential(self, 
                                workflow: WorkflowDefinition,
                                input_data: Dict[str, Any],
                                execution: WorkflowExecution) -> IntegrationResult:
        """Execute workflow steps sequentially."""
        current_data = input_data.copy()
        results = {}
        
        for step in workflow.steps:
            self.logger.debug(f"Executing step: {step.name}")
            
            try:
                # Check module health
                if self.module_health.get(step.module) == ModuleStatus.ERROR:
                    raise Exception(f"Module {step.module} is in error state")
                
                # Execute step
                step_result = await self._execute_step(step, current_data, execution)
                results[step.name] = step_result
                
                # Update data for next step
                if step.output_mapping:
                    for key, value in step.output_mapping.items():
                        current_data[key] = step_result.get(value, step_result)
                else:
                    current_data.update(step_result)
                
                execution.module_statuses[step.module] = ModuleStatus.AVAILABLE
                
            except Exception as e:
                execution.module_statuses[step.module] = ModuleStatus.ERROR
                if not step.optional:
                    raise
                else:
                    self.logger.warning(f"Optional step {step.name} failed: {e}")
                    results[step.name] = {"error": str(e), "status": "skipped"}
        
        return IntegrationResult(
            success=True,
            data=results,
            metadata={
                "execution_id": execution.execution_id,
                "workflow_id": workflow.id,
                "execution_time": time.time() - execution.start_time
            }
        )
    
    async def _execute_parallel(self, 
                              workflow: WorkflowDefinition,
                              input_data: Dict[str, Any],
                              execution: WorkflowExecution) -> IntegrationResult:
        """Execute independent workflow steps in parallel."""
        # Group steps by dependencies
        dependency_groups = self._group_by_dependencies(workflow.steps)
        results = {}
        current_data = input_data.copy()
        
        for group in dependency_groups:
            # Execute group in parallel
            tasks = []
            for step in group:
                task = asyncio.create_task(
                    self._execute_step(step, current_data, execution)
                )
                tasks.append((step.name, step, task))
            
            # Wait for group completion
            group_results = {}
            for step_name, step, task in tasks:
                try:
                    step_result = await task
                    group_results[step_name] = step_result
                    execution.module_statuses[step.module] = ModuleStatus.AVAILABLE
                    
                except Exception as e:
                    execution.module_statuses[step.module] = ModuleStatus.ERROR
                    if not step.optional:
                        raise
                    group_results[step_name] = {"error": str(e), "status": "skipped"}
            
            results.update(group_results)
            
            # Update data with group results
            for step_name, step_result in group_results.items():
                if isinstance(step_result, dict) and "error" not in step_result:
                    current_data.update(step_result)
        
        return IntegrationResult(
            success=True,
            data=results,
            metadata={
                "execution_id": execution.execution_id,
                "workflow_id": workflow.id,
                "execution_time": time.time() - execution.start_time
            }
        )
    
    async def _execute_conditional(self, 
                                 workflow: WorkflowDefinition,
                                 input_data: Dict[str, Any],
                                 execution: WorkflowExecution) -> IntegrationResult:
        """Execute workflow with conditional step execution."""
        current_data = input_data.copy()
        results = {}
        
        for step in workflow.steps:
            # Check execution condition
            if step.condition and not self._evaluate_condition(step.condition, current_data):
                self.logger.debug(f"Skipping step {step.name} - condition not met")
                results[step.name] = {"status": "skipped", "reason": "condition_not_met"}
                continue
            
            try:
                step_result = await self._execute_step(step, current_data, execution)
                results[step.name] = step_result
                
                # Update data
                if step.output_mapping:
                    for key, value in step.output_mapping.items():
                        current_data[key] = step_result.get(value, step_result)
                else:
                    current_data.update(step_result)
                
                execution.module_statuses[step.module] = ModuleStatus.AVAILABLE
                
            except Exception as e:
                execution.module_statuses[step.module] = ModuleStatus.ERROR
                if not step.optional:
                    raise
                results[step.name] = {"error": str(e), "status": "failed"}
        
        return IntegrationResult(
            success=True,
            data=results,
            metadata={
                "execution_id": execution.execution_id,
                "workflow_id": workflow.id,
                "execution_time": time.time() - execution.start_time
            }
        )
    
    async def _execute_event_driven(self, 
                                  workflow: WorkflowDefinition,
                                  input_data: Dict[str, Any],
                                  execution: WorkflowExecution) -> IntegrationResult:
        """Execute workflow using event-driven pattern."""
        # Initialize event bus for this execution
        execution_events = {}
        results = {}
        current_data = input_data.copy()
        
        # Set up event listeners
        for step in workflow.steps:
            if step.trigger_events:
                for event in step.trigger_events:
                    if event not in execution_events:
                        execution_events[event] = []
                    execution_events[event].append(step)
        
        # Start with steps that have no trigger events
        initial_steps = [step for step in workflow.steps if not step.trigger_events]
        
        # Execute initial steps
        for step in initial_steps:
            try:
                step_result = await self._execute_step(step, current_data, execution)
                results[step.name] = step_result
                current_data.update(step_result)
                
                # Trigger events
                if step.emits_events:
                    for event in step.emits_events:
                        await self._trigger_event(event, step_result, execution_events, 
                                                current_data, execution, results)
                
            except Exception as e:
                if not step.optional:
                    raise
                results[step.name] = {"error": str(e), "status": "failed"}
        
        return IntegrationResult(
            success=True,
            data=results,
            metadata={
                "execution_id": execution.execution_id,
                "workflow_id": workflow.id,
                "execution_time": time.time() - execution.start_time
            }
        )
    
    async def _execute_feedback_loop(self, 
                                   workflow: WorkflowDefinition,
                                   input_data: Dict[str, Any],
                                   execution: WorkflowExecution) -> IntegrationResult:
        """Execute workflow with feedback loops (Active Inference pattern)."""
        current_data = input_data.copy()
        results = {}
        max_iterations = workflow.max_iterations or 10
        convergence_threshold = workflow.convergence_threshold or 0.001
        
        for iteration in range(max_iterations):
            self.logger.debug(f"Feedback loop iteration {iteration + 1}")
            iteration_results = {}
            
            # Execute all steps in current iteration
            for step in workflow.steps:
                try:
                    step_result = await self._execute_step(step, current_data, execution)
                    iteration_results[step.name] = step_result
                    
                    # Update beliefs/data
                    if step.feedback_mapping:
                        for key, value in step.feedback_mapping.items():
                            current_data[key] = step_result.get(value, step_result)
                    
                except Exception as e:
                    if not step.optional:
                        raise
                    iteration_results[step.name] = {"error": str(e), "status": "failed"}
            
            results[f"iteration_{iteration}"] = iteration_results
            
            # Check convergence
            if iteration > 0 and self._check_convergence(results, convergence_threshold):
                self.logger.info(f"Workflow converged at iteration {iteration + 1}")
                break
        
        return IntegrationResult(
            success=True,
            data=results,
            metadata={
                "execution_id": execution.execution_id,
                "workflow_id": workflow.id,
                "iterations": len([k for k in results.keys() if k.startswith("iteration_")]),
                "execution_time": time.time() - execution.start_time
            }
        )
    
    async def _execute_step(self, 
                          step: Any,
                          input_data: Dict[str, Any],
                          execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a single workflow step."""
        module_name = step.module
        
        if self.monitoring_enabled:
            self.performance_monitor.start_step_tracking(execution.execution_id, step.name)
        
        try:
            # Prepare step input
            step_input = input_data.copy()
            if step.input_mapping:
                step_input = {key: input_data.get(value, value) 
                            for key, value in step.input_mapping.items()}
            
            # Execute via API
            response = await self.api_connector.post_async(
                module=module_name,
                endpoint=step.endpoint,
                data=step_input,
                timeout=step.timeout or self.default_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Step execution failed: {response.status_code} - {response.text}")
                
        finally:
            if self.monitoring_enabled:
                self.performance_monitor.stop_step_tracking(execution.execution_id, step.name)
    
    def _group_by_dependencies(self, steps: List[Any]) -> List[List[Any]]:
        """Group workflow steps by their dependency relationships."""
        groups = []
        remaining_steps = steps.copy()
        processed_steps = set()
        
        while remaining_steps:
            # Find steps with no unprocessed dependencies
            ready_steps = []
            for step in remaining_steps:
                if all(dep in processed_steps for dep in step.dependencies):
                    ready_steps.append(step)
            
            if not ready_steps:
                # Circular dependency or other issue
                raise Exception("Unable to resolve step dependencies")
            
            groups.append(ready_steps)
            for step in ready_steps:
                remaining_steps.remove(step)
                processed_steps.add(step.name)
        
        return groups
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Evaluate a conditional expression against current data."""
        try:
            # Simple expression evaluation (extend as needed)
            # Example: "data.temperature > 25"
            return eval(condition, {"data": data, "__builtins__": {}})
        except Exception:
            return False
    
    async def _trigger_event(self, 
                           event_name: str,
                           event_data: Dict[str, Any],
                           execution_events: Dict[str, List[Any]],
                           current_data: Dict[str, Any],
                           execution: WorkflowExecution,
                           results: Dict[str, Any]):
        """Trigger an event and execute associated steps."""
        if event_name in execution_events:
            for step in execution_events[event_name]:
                if step.name not in results:  # Avoid duplicate execution
                    try:
                        step_result = await self._execute_step(step, current_data, execution)
                        results[step.name] = step_result
                        current_data.update(step_result)
                        
                        # Chain events
                        if step.emits_events:
                            for next_event in step.emits_events:
                                await self._trigger_event(next_event, step_result, 
                                                        execution_events, current_data, 
                                                        execution, results)
                    except Exception as e:
                        if not step.optional:
                            raise
                        results[step.name] = {"error": str(e), "status": "failed"}
    
    def _check_convergence(self, results: Dict[str, Any], threshold: float) -> bool:
        """Check if feedback loop has converged."""
        iterations = [k for k in results.keys() if k.startswith("iteration_")]
        if len(iterations) < 2:
            return False
        
        # Simple convergence check - extend based on specific needs
        try:
            last_iteration = results[iterations[-1]]
            prev_iteration = results[iterations[-2]]
            
            # Compare some metric (implement domain-specific logic)
            # This is a placeholder implementation
            return True  # Implement actual convergence checking
            
        except Exception:
            return False
    
    async def _attempt_recovery(self, 
                              workflow: WorkflowDefinition,
                              input_data: Dict[str, Any],
                              execution: WorkflowExecution,
                              error: Exception) -> Optional[IntegrationResult]:
        """Attempt to recover from workflow execution failure."""
        self.logger.info(f"Attempting recovery for execution {execution.execution_id}")
        
        # Implement recovery strategies:
        # 1. Retry with degraded modules
        # 2. Skip optional failing steps
        # 3. Use cached results if available
        # 4. Switch to alternative workflow
        
        try:
            # Simple retry strategy for now
            await asyncio.sleep(1)  # Brief delay
            
            # Try again with optional modules marked as skippable
            modified_workflow = self._create_resilient_workflow(workflow)
            return await self.execute_workflow(
                modified_workflow.id, 
                input_data, 
                ExecutionContext(resilience_mode=True)
            )
            
        except Exception as recovery_error:
            self.logger.error(f"Recovery failed: {recovery_error}")
            return None
    
    def _create_resilient_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Create a modified workflow for resilient execution."""
        # Mark problematic modules as optional
        resilient_workflow = workflow.copy()
        for step in resilient_workflow.steps:
            if self.module_health.get(step.module) in [ModuleStatus.ERROR, ModuleStatus.UNAVAILABLE]:
                step.optional = True
        
        return resilient_workflow
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status of a workflow execution."""
        return self.active_executions.get(execution_id)
    
    def get_module_health(self) -> Dict[str, ModuleStatus]:
        """Get current health status of all modules."""
        return self.module_health.copy()
    
    def list_workflows(self) -> List[str]:
        """List all registered workflow IDs."""
        return list(self.workflows.keys())
    
    def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID."""
        return self.workflows.get(workflow_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of orchestrator and modules."""
        health_status = {
            "orchestrator": "healthy",
            "modules": {},
            "active_executions": len(self.active_executions),
            "registered_workflows": len(self.workflows),
            "timestamp": time.time()
        }
        
        # Check each module
        for module_name in self.modules:
            try:
                response = await self.api_connector.get_async(
                    module=module_name,
                    endpoint='/health',
                    timeout=5
                )
                
                if response.status_code == 200:
                    health_status["modules"][module_name] = "healthy"
                    self.module_health[module_name] = ModuleStatus.AVAILABLE
                else:
                    health_status["modules"][module_name] = "degraded"
                    self.module_health[module_name] = ModuleStatus.DEGRADED
                    
            except Exception as e:
                health_status["modules"][module_name] = f"unhealthy: {str(e)}"
                self.module_health[module_name] = ModuleStatus.UNAVAILABLE
        
        return health_status
    
    def shutdown(self):
        """Gracefully shutdown the orchestrator."""
        self.logger.info("Shutting down module orchestrator")
        
        # Cancel active executions
        for execution_id in list(self.active_executions.keys()):
            execution = self.active_executions[execution_id]
            if execution.status in ["initializing", "running"]:
                execution.status = "cancelled"
                execution.end_time = time.time()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        if self.monitoring_enabled:
            self.performance_monitor.shutdown()
        
        self.logger.info("Module orchestrator shutdown complete")


# Example workflow definitions
SAMPLE_WORKFLOWS = {
    "health_surveillance_basic": {
        "id": "health_surveillance_basic",
        "name": "Basic Health Surveillance",
        "description": "Simple health data analysis workflow",
        "execution_strategy": "sequential",
        "steps": [
            {
                "name": "data_ingestion",
                "module": "DATA",
                "endpoint": "/ingest",
                "dependencies": [],
                "optional": False
            },
            {
                "name": "spatial_analysis",
                "module": "SPACE",
                "endpoint": "/analyze/spatial",
                "dependencies": ["data_ingestion"],
                "optional": False
            },
            {
                "name": "health_assessment",
                "module": "HEALTH",
                "endpoint": "/assess/outbreak",
                "dependencies": ["spatial_analysis"],
                "optional": False
            }
        ]
    }
}


if __name__ == "__main__":
    # Example usage
    async def main():
        orchestrator = ModuleOrchestrator()
        
        # Health check
        health = await orchestrator.health_check()
        print(f"Health status: {health}")
        
        # Execute sample workflow
        if orchestrator.workflows:
            workflow_id = list(orchestrator.workflows.keys())[0]
            result = await orchestrator.execute_workflow(
                workflow_id,
                {"test_data": "sample_input"}
            )
            print(f"Workflow result: {result}")
        
        orchestrator.shutdown()
    
    asyncio.run(main()) 