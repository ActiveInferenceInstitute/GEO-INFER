"""
Plan module for BDI agents.

Plans represent procedural knowledge about how to achieve goals. This module provides:
- Plan representation with conditions and actions
- Plan selection based on context and applicability
- Plan execution with success/failure handling
- Plan library management for reusable plans
"""

from typing import Dict, Any, List, Optional, Set, Callable, Union, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class PlanStatus(Enum):
    """Enumeration of possible statuses for a plan."""
    PENDING = "pending"       # The plan has not been started
    RUNNING = "running"       # The plan is currently running
    SUCCEEDED = "succeeded"   # The plan has succeeded
    FAILED = "failed"         # The plan has failed


@dataclass
class Plan:
    """
    A plan representing a way to achieve a goal.
    
    Attributes:
        name: Unique identifier for the plan
        description: Human-readable description of the plan
        goal: The name of the desire/goal this plan aims to achieve
        context_condition: Condition that must be true for the plan to be applicable
        precondition: Condition that must be true for the plan to start
        postcondition: Condition that indicates the plan has succeeded
        failure_condition: Condition that indicates the plan has failed
        actions: List of actions or sub-plans to execute
        status: Current status of the plan
        priority: Priority level of the plan (higher values = higher priority)
        metadata: Additional information about this plan
    """
    name: str
    description: str
    goal: str
    context_condition: Dict[str, Any] = field(default_factory=dict)
    precondition: Dict[str, Any] = field(default_factory=dict)
    postcondition: Dict[str, Any] = field(default_factory=dict)
    failure_condition: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    status: PlanStatus = PlanStatus.PENDING
    priority: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_applicable(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if this plan is applicable in the current context.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if the plan is applicable, False otherwise
        """
        for key, value in self.context_condition.items():
            if key not in belief_values or belief_values[key] != value:
                return False
                
        return True
    
    def can_start(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if this plan can start based on its precondition.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if the plan can start, False otherwise
        """
        if self.status != PlanStatus.PENDING:
            return False
            
        for key, value in self.precondition.items():
            if key not in belief_values or belief_values[key] != value:
                return False
                
        return True
    
    def has_succeeded(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if this plan has succeeded based on its postcondition.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if the plan has succeeded, False otherwise
        """
        for key, value in self.postcondition.items():
            if key not in belief_values or belief_values[key] != value:
                return False
                
        return True
    
    def has_failed(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if this plan has failed based on its failure condition.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if the plan has failed, False otherwise
        """
        for key, value in self.failure_condition.items():
            if key in belief_values and belief_values[key] == value:
                return True
                
        return False
    
    def start(self) -> None:
        """
        Start executing this plan.
        
        Raises:
            ValueError: If the plan is not in the PENDING status
        """
        if self.status != PlanStatus.PENDING:
            raise ValueError(f"Cannot start plan '{self.name}' with status '{self.status.value}'")
            
        self.status = PlanStatus.RUNNING
        logger.debug(f"Started plan: {self.name}")
    
    def succeed(self) -> None:
        """
        Mark this plan as succeeded.
        
        Raises:
            ValueError: If the plan is not in the RUNNING status
        """
        if self.status != PlanStatus.RUNNING:
            raise ValueError(f"Cannot succeed plan '{self.name}' with status '{self.status.value}'")
            
        self.status = PlanStatus.SUCCEEDED
        logger.debug(f"Plan succeeded: {self.name}")
    
    def fail(self) -> None:
        """
        Mark this plan as failed.
        
        Raises:
            ValueError: If the plan is not in the RUNNING status
        """
        if self.status != PlanStatus.RUNNING:
            raise ValueError(f"Cannot fail plan '{self.name}' with status '{self.status.value}'")
            
        self.status = PlanStatus.FAILED
        logger.debug(f"Plan failed: {self.name}")
    
    def reset(self) -> None:
        """Reset this plan to the PENDING status."""
        self.status = PlanStatus.PENDING
        logger.debug(f"Reset plan: {self.name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this plan to a dictionary representation.
        
        Returns:
            Dictionary representation of this plan
        """
        return {
            "name": self.name,
            "description": self.description,
            "goal": self.goal,
            "context_condition": self.context_condition,
            "precondition": self.precondition,
            "postcondition": self.postcondition,
            "failure_condition": self.failure_condition,
            "actions": self.actions,
            "status": self.status.value,
            "priority": self.priority,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """
        Create a Plan instance from a dictionary.
        
        Args:
            data: Dictionary representation of a plan
            
        Returns:
            Plan instance
        """
        # Handle status conversion from string
        if "status" in data and isinstance(data["status"], str):
            data["status"] = PlanStatus(data["status"])
            
        return cls(**data)


class PlanLibrary:
    """
    A collection of plans maintained by an agent.
    
    This class handles:
    - Adding, updating, and removing plans
    - Querying plans by various criteria
    - Plan selection based on goals and context
    """
    
    def __init__(self):
        """Initialize an empty plan library."""
        self._plans: Dict[str, Plan] = {}
    
    def add(self, plan: Plan) -> None:
        """
        Add a new plan to the plan library.
        
        Args:
            plan: Plan to add
            
        Raises:
            ValueError: If a plan with the same name already exists
        """
        if plan.name in self._plans:
            raise ValueError(f"Plan with name '{plan.name}' already exists")
            
        self._plans[plan.name] = plan
        logger.debug(f"Added plan: {plan.name}")
    
    def get(self, name: str) -> Plan:
        """
        Get a plan by name.
        
        Args:
            name: Name of the plan to get
            
        Returns:
            The plan with the given name
            
        Raises:
            KeyError: If no plan with the given name exists
        """
        if name not in self._plans:
            raise KeyError(f"No plan with name '{name}' exists")
            
        return self._plans[name]
    
    def remove(self, name: str) -> None:
        """
        Remove a plan from the plan library.
        
        Args:
            name: Name of the plan to remove
            
        Raises:
            KeyError: If no plan with the given name exists
        """
        if name not in self._plans:
            raise KeyError(f"No plan with name '{name}' exists")
            
        del self._plans[name]
        logger.debug(f"Removed plan: {name}")
    
    def has_plan(self, name: str) -> bool:
        """
        Check if a plan with the given name exists.
        
        Args:
            name: Name of the plan to check for
            
        Returns:
            True if a plan with the given name exists, False otherwise
        """
        return name in self._plans
    
    def get_all(self) -> Dict[str, Plan]:
        """
        Get all plans in the plan library.
        
        Returns:
            Dictionary mapping plan names to Plan objects
        """
        return dict(self._plans)
    
    def get_by_goal(self, goal: str) -> List[Plan]:
        """
        Get all plans for a specific goal.
        
        Args:
            goal: Name of the goal to get plans for
            
        Returns:
            List of plans for the given goal
        """
        return [plan for plan in self._plans.values() if plan.goal == goal]
    
    def select_plan(self, goal: str, belief_values: Dict[str, Any]) -> Optional[Plan]:
        """
        Select the most appropriate plan for a given goal in the current context.
        
        Args:
            goal: Name of the goal to select a plan for
            belief_values: Dictionary of belief values to check against
            
        Returns:
            The most appropriate applicable plan, or None if no applicable plan exists
        """
        # Get all plans for this goal
        candidate_plans = self.get_by_goal(goal)
        
        # Filter out non-applicable plans
        applicable_plans = [plan for plan in candidate_plans if plan.is_applicable(belief_values)]
        
        # If no applicable plans, return None
        if not applicable_plans:
            return None
            
        # Sort by priority (highest first)
        applicable_plans.sort(key=lambda p: p.priority, reverse=True)
        
        # Return the highest priority applicable plan
        return applicable_plans[0]
    
    def create_plan_instance(self, template_name: str, instance_name: str = None) -> Plan:
        """
        Create a new instance of a plan from a template.
        
        Args:
            template_name: Name of the template plan
            instance_name: Name for the new plan instance (generated if None)
            
        Returns:
            A new instance of the template plan
            
        Raises:
            KeyError: If no template plan with the given name exists
        """
        # Get the template plan
        template = self.get(template_name)
        
        # Create a copy of the template
        template_dict = template.to_dict()
        
        # Reset the status to PENDING
        template_dict["status"] = PlanStatus.PENDING.value
        
        # Generate a unique name if none provided
        if instance_name is None:
            instance_name = f"{template_name}_instance_{id(template_dict)}"
            
        template_dict["name"] = instance_name
        
        # Create a new plan from the template
        return Plan.from_dict(template_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the plan library to a dictionary representation.
        
        Returns:
            Dictionary representation of the plan library
        """
        return {
            "plans": {name: plan.to_dict() for name, plan in self._plans.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanLibrary':
        """
        Create a PlanLibrary instance from a dictionary.
        
        Args:
            data: Dictionary representation of a plan library
            
        Returns:
            PlanLibrary instance
        """
        plan_library = cls()
        
        # Add plans
        for name, plan_data in data.get("plans", {}).items():
            plan = Plan.from_dict(plan_data)
            plan_library._plans[name] = plan
            
        return plan_library 