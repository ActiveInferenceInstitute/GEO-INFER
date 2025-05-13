#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Belief-Desire-Intention (BDI) Agent.

This module implements the BDI agent architecture, which models
agents in terms of their beliefs (what they know), desires (what they
want to achieve), and intentions (how they plan to achieve their desires).
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime
import json

from geo_infer_agent.core.agent_base import BaseAgent, AgentState

logger = logging.getLogger("geo_infer_agent.models.bdi")

class Belief:
    """
    Represents a belief in the agent's belief base.
    
    A belief represents something the agent believes to be true about the world.
    Beliefs can have different confidence levels and can be updated based on
    new perceptions.
    """
    
    def __init__(self, name: str, value: Any, confidence: float = 1.0, 
                 timestamp: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a belief.
        
        Args:
            name: Name/identifier for the belief
            value: Value of the belief
            confidence: Confidence level (0-1)
            timestamp: When the belief was formed
            metadata: Additional information about the belief
        """
        self.name = name
        self.value = value
        self.confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
        self.history = []  # Track changes
        
    def update(self, value: Any, confidence: Optional[float] = None, 
               metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the belief with new information.
        
        Args:
            value: New value
            confidence: New confidence level
            metadata: Updated metadata
        """
        # Store current state in history
        self.history.append({
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": self.metadata.copy()
        })
        
        # Update state
        self.value = value
        if confidence is not None:
            self.confidence = max(0.0, min(1.0, confidence))
        if metadata:
            self.metadata.update(metadata)
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "history_length": len(self.history)
        }
        
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Belief':
        """Create from dictionary."""
        belief = Belief(
            name=data["name"],
            value=data["value"],
            confidence=data["confidence"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data["metadata"]
        )
        return belief


class Desire:
    """
    Represents a desire in the agent's desire set.
    
    A desire represents a goal the agent wants to achieve.
    Desires have priority levels and conditions for satisfaction.
    """
    
    def __init__(self, name: str, description: str, priority: float = 0.5,
                 deadline: Optional[datetime] = None, 
                 conditions: Optional[Dict[str, Any]] = None):
        """
        Initialize a desire.
        
        Args:
            name: Identifier for the desire
            description: Human-readable description
            priority: Priority level (0-1)
            deadline: When the desire must be fulfilled by
            conditions: Conditions that must be true for the desire to be satisfied
        """
        self.name = name
        self.description = description
        self.priority = max(0.0, min(1.0, priority))  # Clamp to 0-1
        self.deadline = deadline
        self.conditions = conditions or {}
        self.created_at = datetime.now()
        self.achieved = False
        self.achieved_at = None
        
    def set_achieved(self, achieved: bool = True) -> None:
        """
        Mark the desire as achieved or not.
        
        Args:
            achieved: Whether the desire has been achieved
        """
        self.achieved = achieved
        self.achieved_at = datetime.now() if achieved else None
        
    def is_expired(self) -> bool:
        """Check if the desire has expired."""
        if not self.deadline:
            return False
        return datetime.now() > self.deadline
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "achieved": self.achieved,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None
        }
        
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Desire':
        """Create from dictionary."""
        desire = Desire(
            name=data["name"],
            description=data["description"],
            priority=data["priority"],
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            conditions=data["conditions"]
        )
        desire.created_at = datetime.fromisoformat(data["created_at"])
        desire.achieved = data["achieved"]
        if data.get("achieved_at"):
            desire.achieved_at = datetime.fromisoformat(data["achieved_at"])
        return desire


class Plan:
    """
    Represents a plan in the agent's intention structure.
    
    A plan is a sequence of actions designed to satisfy one or more desires.
    """
    
    def __init__(self, name: str, desire_name: str, actions: List[Dict[str, Any]], 
                 context_conditions: Optional[Dict[str, Any]] = None):
        """
        Initialize a plan.
        
        Args:
            name: Identifier for the plan
            desire_name: Name of the desire this plan addresses
            actions: List of actions to execute
            context_conditions: Conditions that must be true for the plan to be applicable
        """
        self.name = name
        self.desire_name = desire_name
        self.actions = actions
        self.context_conditions = context_conditions or {}
        self.created_at = datetime.now()
        self.current_action_index = 0
        self.complete = False
        self.successful = False
        self.execution_record = []
        
    def next_action(self) -> Optional[Dict[str, Any]]:
        """Get the next action to execute."""
        if self.complete or self.current_action_index >= len(self.actions):
            return None
        return self.actions[self.current_action_index]
        
    def record_action_result(self, action_index: int, result: Dict[str, Any], 
                           success: bool) -> None:
        """
        Record the result of an action.
        
        Args:
            action_index: Index of the action
            result: Result of the action
            success: Whether the action was successful
        """
        self.execution_record.append({
            "action_index": action_index,
            "action": self.actions[action_index] if action_index < len(self.actions) else None,
            "result": result,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
    def advance(self) -> bool:
        """
        Advance to the next action in the plan.
        
        Returns:
            True if there are more actions, False if plan is complete
        """
        self.current_action_index += 1
        if self.current_action_index >= len(self.actions):
            self.complete = True
            return False
        return True
        
    def mark_complete(self, successful: bool) -> None:
        """
        Mark the plan as complete.
        
        Args:
            successful: Whether the plan was successful
        """
        self.complete = True
        self.successful = successful
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "desire_name": self.desire_name,
            "actions": self.actions,
            "context_conditions": self.context_conditions,
            "created_at": self.created_at.isoformat(),
            "current_action_index": self.current_action_index,
            "complete": self.complete,
            "successful": self.successful,
            "execution_record": self.execution_record
        }
        
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Plan':
        """Create from dictionary."""
        plan = Plan(
            name=data["name"],
            desire_name=data["desire_name"],
            actions=data["actions"],
            context_conditions=data["context_conditions"]
        )
        plan.created_at = datetime.fromisoformat(data["created_at"])
        plan.current_action_index = data["current_action_index"]
        plan.complete = data["complete"]
        plan.successful = data["successful"]
        plan.execution_record = data["execution_record"]
        return plan


class BDIState(AgentState):
    """
    Extended agent state for BDI agents.
    
    This state tracks:
    - Beliefs: facts the agent believes about the world
    - Desires: goals the agent wants to achieve
    - Intentions: plans the agent intends to execute
    """
    
    def __init__(self, capacity: int = 1000):
        """Initialize BDI state."""
        super().__init__(capacity)
        self.beliefs_dict = {}  # name -> Belief
        self.desires_dict = {}  # name -> Desire
        self.intentions = []    # List of Plan objects
        self.current_intention = None
        
    def add_belief(self, belief: Belief) -> None:
        """
        Add a new belief or update an existing one.
        
        Args:
            belief: Belief to add
        """
        if belief.name in self.beliefs_dict:
            # Update existing belief
            old_belief = self.beliefs_dict[belief.name]
            old_value = old_belief.value
            old_confidence = old_belief.confidence
            
            old_belief.update(
                value=belief.value,
                confidence=belief.confidence,
                metadata=belief.metadata
            )
            
            # Add to memory
            self.add_to_memory({
                "type": "belief_updated",
                "name": belief.name,
                "old_value": old_value,
                "new_value": belief.value,
                "old_confidence": old_confidence,
                "new_confidence": belief.confidence,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Add new belief
            self.beliefs_dict[belief.name] = belief
            
            # Add to memory
            self.add_to_memory({
                "type": "belief_added",
                "name": belief.name,
                "value": belief.value,
                "confidence": belief.confidence,
                "timestamp": datetime.now().isoformat()
            })
            
        # Update general belief map for compatibility
        self.beliefs[belief.name] = belief.value
        self.last_update = datetime.now()
        
    def update_belief(self, name: str, value: Any, confidence: Optional[float] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update a belief with new information.
        
        Args:
            name: Name of the belief
            value: New value
            confidence: New confidence level
            metadata: Updated metadata
        """
        if name in self.beliefs_dict:
            old_belief = self.beliefs_dict[name]
            old_value = old_belief.value
            old_confidence = old_belief.confidence
            
            old_belief.update(
                value=value,
                confidence=confidence,
                metadata=metadata
            )
            
            # Add to memory
            self.add_to_memory({
                "type": "belief_updated",
                "name": name,
                "old_value": old_value,
                "new_value": value,
                "old_confidence": old_confidence,
                "new_confidence": confidence if confidence is not None else old_confidence,
                "timestamp": datetime.now().isoformat()
            })
        else:
            # Create new belief
            belief = Belief(name, value, confidence or 1.0, metadata=metadata)
            self.beliefs_dict[name] = belief
            
            # Add to memory
            self.add_to_memory({
                "type": "belief_added",
                "name": name,
                "value": value,
                "confidence": confidence or 1.0,
                "timestamp": datetime.now().isoformat()
            })
            
        # Update general belief map for compatibility
        self.beliefs[name] = value
        self.last_update = datetime.now()
        
    def get_belief(self, name: str) -> Optional[Belief]:
        """
        Get a belief by name.
        
        Args:
            name: Name of the belief
            
        Returns:
            Belief object or None if not found
        """
        return self.beliefs_dict.get(name)
        
    def add_desire(self, desire: Desire) -> None:
        """
        Add a new desire.
        
        Args:
            desire: Desire to add
        """
        self.desires_dict[desire.name] = desire
        
        # Add to general desires list for compatibility
        super().add_desire({
            "description": desire.description,
            "priority": desire.priority,
            "name": desire.name
        })
        
        # Add to memory
        self.add_to_memory({
            "type": "desire_added",
            "name": desire.name,
            "description": desire.description,
            "priority": desire.priority,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_desire(self, name: str) -> Optional[Desire]:
        """
        Get a desire by name.
        
        Args:
            name: Name of the desire
            
        Returns:
            Desire object or None if not found
        """
        return self.desires_dict.get(name)
        
    def get_desires_by_priority(self) -> List[Desire]:
        """
        Get all desires ordered by priority.
        
        Returns:
            List of desires, highest priority first
        """
        return sorted(
            self.desires_dict.values(), 
            key=lambda d: d.priority, 
            reverse=True
        )
        
    def add_intention(self, plan: Plan) -> None:
        """
        Add a new intention (plan).
        
        Args:
            plan: Plan to add
        """
        self.intentions.append(plan)
        
        # Add to general intentions list for compatibility
        super().set_intention({
            "plan_name": plan.name,
            "desire_name": plan.desire_name,
            "actions": plan.actions
        })
        
        # Add to memory
        self.add_to_memory({
            "type": "intention_added",
            "plan_name": plan.name,
            "desire_name": plan.desire_name,
            "actions_count": len(plan.actions),
            "timestamp": datetime.now().isoformat()
        })
        
    def set_current_intention(self, plan: Optional[Plan]) -> None:
        """
        Set the currently active intention.
        
        Args:
            plan: Plan to set as current intention
        """
        self.current_intention = plan
        
        # Add to memory if plan is not None
        if plan:
            self.add_to_memory({
                "type": "intention_selected",
                "plan_name": plan.name,
                "desire_name": plan.desire_name,
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.add_to_memory({
                "type": "intention_cleared",
                "timestamp": datetime.now().isoformat()
            })
            
    def get_current_intention(self) -> Optional[Plan]:
        """Get the currently active intention."""
        return self.current_intention
        
    def get_intentions_for_desire(self, desire_name: str) -> List[Plan]:
        """
        Get all intentions for a specific desire.
        
        Args:
            desire_name: Name of the desire
            
        Returns:
            List of plans for the desire
        """
        return [p for p in self.intentions if p.desire_name == desire_name and not p.complete]
        
    def remove_completed_intentions(self) -> int:
        """
        Remove completed intentions.
        
        Returns:
            Number of intentions removed
        """
        before_count = len(self.intentions)
        self.intentions = [i for i in self.intentions if not i.complete]
        after_count = len(self.intentions)
        return before_count - after_count
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        base_dict = super().to_dict()
        
        # Add BDI-specific state
        bdi_dict = {
            "beliefs": {name: belief.to_dict() for name, belief in self.beliefs_dict.items()},
            "desires": {name: desire.to_dict() for name, desire in self.desires_dict.items()},
            "intentions": [intention.to_dict() for intention in self.intentions],
            "current_intention": self.current_intention.to_dict() if self.current_intention else None
        }
        
        # Merge dictionaries
        base_dict.update(bdi_dict)
        
        return base_dict
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BDIState':
        """Create state from dictionary."""
        state = super(BDIState, cls).from_dict(data)
        
        # Restore BDI-specific state
        if "beliefs" in data:
            for name, belief_data in data["beliefs"].items():
                state.beliefs_dict[name] = Belief.from_dict(belief_data)
                
        if "desires" in data:
            for name, desire_data in data["desires"].items():
                state.desires_dict[name] = Desire.from_dict(desire_data)
                
        if "intentions" in data:
            state.intentions = [Plan.from_dict(plan_data) for plan_data in data["intentions"]]
                
        if "current_intention" in data and data["current_intention"]:
            state.current_intention = Plan.from_dict(data["current_intention"])
            
        return state


class BDIAgent(BaseAgent):
    """
    Belief-Desire-Intention (BDI) agent implementation.
    
    This agent implements the BDI architecture, which models agent behavior
    in terms of beliefs, desires, and intentions.
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        """Initialize the BDI agent."""
        super().__init__(agent_id, config)
        
        # Initialize BDI state
        self.state = BDIState(capacity=self.config.get("memory_capacity", 1000))
        
        # Library of plans
        self.plan_library = {}  # plan_name -> Plan template
        
        # Action execution handlers
        self.action_handlers = {}  # action_type -> handler function
        
        # Perception handlers
        self.perception_handlers = []  # List of perception handler functions
        
        # Deliberation parameters
        self.deliberation_interval = self.config.get("deliberation_interval", 5)  # seconds
        self.commitment_strategy = self.config.get("commitment_strategy", "single_minded")
        
        logger.info(f"BDI agent {self.agent_id} initialized")
        
    async def initialize(self) -> None:
        """Initialize the agent."""
        logger.info(f"Initializing BDI agent {self.agent_id}")
        
        # Register default action handlers
        self._register_default_action_handlers()
        
        # Register default perception handlers
        self._register_default_perception_handlers()
        
        # Load plans from config
        self._load_plans_from_config()
        
        # Initialize beliefs from config
        self._initialize_beliefs()
        
        # Initialize desires from config
        self._initialize_desires()
        
        logger.info(f"BDI agent {self.agent_id} initialization complete")
        
    async def perceive(self) -> Dict[str, Any]:
        """
        Perceive the environment.
        
        Returns:
            Dictionary of perceptions
        """
        # Basic implementation - could be extended for specific agent types
        perceptions = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
        }
        
        # Extend with geospatial perceptions if available
        if "region" in self.config:
            perceptions["region"] = self.config["region"]
            
        # Add random sensor data for demonstration
        # (in a real implementation, this would come from actual sensors or data sources)
        perceptions["sensors"] = {
            "temperature": 20 + (hash(datetime.now().isoformat()) % 10),
            "humidity": 50 + (hash(datetime.now().isoformat() + "humidity") % 30),
            "wind_speed": 5 + (hash(datetime.now().isoformat() + "wind") % 10)
        }
        
        logger.debug(f"BDI agent {self.agent_id} perceptions: {perceptions}")
        return perceptions
        
    def update_beliefs(self, perception: Dict[str, Any]) -> None:
        """
        Update beliefs based on new perceptions.
        
        Args:
            perception: New perception data
        """
        # Run all perception handlers
        for handler in self.perception_handlers:
            handler(self, perception)
            
        # Store last perception time
        self.state.update_belief("last_perception_time", datetime.now())
        
        logger.debug(f"BDI agent {self.agent_id} beliefs updated from perception")
        
    async def decide(self) -> Optional[Dict[str, Any]]:
        """
        Make decisions based on current beliefs and desires.
        
        Returns:
            Action to take or None
        """
        # Check if we're already committed to an intention
        current_intention = self.state.get_current_intention()
        
        if current_intention and not current_intention.complete:
            # Check if intention is still valid
            if self._is_intention_valid(current_intention):
                # Continue with current intention
                action = current_intention.next_action()
                if action:
                    logger.debug(f"BDI agent {self.agent_id} continuing intention {current_intention.name}")
                    return action
                    
        # Intention complete or invalid, need to select a new one
        logger.debug(f"BDI agent {self.agent_id} selecting new intention")
        
        # Clear current intention
        self.state.set_current_intention(None)
        
        # Get desires by priority
        desires = self.state.get_desires_by_priority()
        
        for desire in desires:
            # Skip achieved desires
            if desire.achieved:
                continue
                
            # Skip expired desires
            if desire.is_expired():
                continue
                
            # Try to find a plan for this desire
            plan = self._find_plan_for_desire(desire.name)
            
            if plan:
                # Found a plan, adopt it as intention
                self.state.set_current_intention(plan)
                action = plan.next_action()
                if action:
                    logger.debug(f"BDI agent {self.agent_id} selected new intention {plan.name}")
                    return action
                    
        logger.debug(f"BDI agent {self.agent_id} found no valid intentions")
        return None
        
    async def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.
        
        Args:
            action: Action to execute
            
        Returns:
            Result of the action
        """
        if not action or "type" not in action:
            logger.warning(f"BDI agent {self.agent_id} received invalid action: {action}")
            return {"success": False, "error": "Invalid action"}
            
        action_type = action["type"]
        
        # Execute action using handler
        if action_type in self.action_handlers:
            try:
                handler = self.action_handlers[action_type]
                result = await handler(self, action)
                
                # Get current intention
                current_intention = self.state.get_current_intention()
                if current_intention:
                    # Record action result
                    current_intention.record_action_result(
                        current_intention.current_action_index,
                        result,
                        result.get("success", False)
                    )
                    
                    # Advance to next action if successful
                    if result.get("success", False):
                        current_intention.advance()
                        
                        # Check if plan is complete
                        if current_intention.complete:
                            # Check if desire is satisfied
                            if self._is_desire_satisfied(current_intention.desire_name):
                                desire = self.state.get_desire(current_intention.desire_name)
                                if desire:
                                    desire.set_achieved(True)
                                    logger.info(f"BDI agent {self.agent_id} achieved desire {desire.name}")
                
                return result
            except Exception as e:
                logger.error(f"BDI agent {self.agent_id} error executing action {action_type}: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            logger.warning(f"BDI agent {self.agent_id} has no handler for action {action_type}")
            return {"success": False, "error": f"No handler for action type {action_type}"}
            
    async def shutdown(self) -> None:
        """Shutdown the agent."""
        logger.info(f"BDI agent {self.agent_id} shutting down")
        
    def _register_default_action_handlers(self) -> None:
        """Register default action handlers."""
        # Register some basic action handlers
        self.action_handlers["wait"] = self._handle_wait_action
        self.action_handlers["update_belief"] = self._handle_update_belief_action
        self.action_handlers["query_belief"] = self._handle_query_belief_action
        self.action_handlers["log"] = self._handle_log_action
        
    def _register_default_perception_handlers(self) -> None:
        """Register default perception handlers."""
        # Handler for basic sensor data
        self.perception_handlers.append(self._handle_sensor_perceptions)
        
    def _handle_sensor_perceptions(self, agent: 'BDIAgent', perception: Dict[str, Any]) -> None:
        """
        Handle sensor data from perceptions.
        
        Args:
            agent: The agent instance
            perception: Perception data
        """
        if "sensors" in perception:
            sensors = perception["sensors"]
            
            # Update beliefs with sensor readings
            for sensor_name, value in sensors.items():
                belief_name = f"sensor.{sensor_name}"
                agent.state.update_belief(belief_name, value)
                
    async def _handle_wait_action(self, agent: 'BDIAgent', action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a wait action.
        
        Args:
            agent: The agent instance
            action: The action data
            
        Returns:
            Action result
        """
        # Get wait duration in seconds
        duration = action.get("duration", 1)
        
        # Wait for specified duration
        await asyncio.sleep(duration)
        
        return {
            "success": True,
            "duration": duration
        }
        
    async def _handle_update_belief_action(self, agent: 'BDIAgent', action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an update belief action.
        
        Args:
            agent: The agent instance
            action: The action data
            
        Returns:
            Action result
        """
        # Get belief details
        belief_name = action.get("belief_name")
        belief_value = action.get("belief_value")
        confidence = action.get("confidence")
        metadata = action.get("metadata")
        
        if not belief_name:
            return {"success": False, "error": "Missing belief name"}
            
        # Update the belief
        agent.state.update_belief(belief_name, belief_value, confidence, metadata)
        
        return {
            "success": True,
            "belief_name": belief_name,
            "belief_value": belief_value
        }
        
    async def _handle_query_belief_action(self, agent: 'BDIAgent', action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a query belief action.
        
        Args:
            agent: The agent instance
            action: The action data
            
        Returns:
            Action result
        """
        # Get belief name
        belief_name = action.get("belief_name")
        
        if not belief_name:
            return {"success": False, "error": "Missing belief name"}
            
        # Get the belief
        belief = agent.state.get_belief(belief_name)
        
        if not belief:
            return {
                "success": False,
                "error": f"Belief {belief_name} not found"
            }
            
        return {
            "success": True,
            "belief_name": belief_name,
            "belief_value": belief.value,
            "confidence": belief.confidence,
            "timestamp": belief.timestamp.isoformat()
        }
        
    async def _handle_log_action(self, agent: 'BDIAgent', action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a log action.
        
        Args:
            agent: The agent instance
            action: The action data
            
        Returns:
            Action result
        """
        # Get log message
        message = action.get("message", "")
        level = action.get("level", "info")
        
        # Log the message
        if level == "debug":
            logger.debug(f"BDI agent {agent.agent_id}: {message}")
        elif level == "info":
            logger.info(f"BDI agent {agent.agent_id}: {message}")
        elif level == "warning":
            logger.warning(f"BDI agent {agent.agent_id}: {message}")
        elif level == "error":
            logger.error(f"BDI agent {agent.agent_id}: {message}")
        else:
            logger.info(f"BDI agent {agent.agent_id}: {message}")
            
        return {
            "success": True,
            "message": message,
            "level": level
        }
        
    def _load_plans_from_config(self) -> None:
        """Load plan templates from configuration."""
        plans = self.config.get("plans", [])
        
        for plan_template in plans:
            if "name" not in plan_template or "desire_name" not in plan_template or "actions" not in plan_template:
                logger.warning(f"BDI agent {self.agent_id} skipping invalid plan template: {plan_template}")
                continue
                
            self.plan_library[plan_template["name"]] = plan_template
            
        logger.debug(f"BDI agent {self.agent_id} loaded {len(self.plan_library)} plan templates")
        
    def _initialize_beliefs(self) -> None:
        """Initialize beliefs from configuration."""
        initial_beliefs = self.config.get("initial_beliefs", {})
        
        for belief_name, belief_data in initial_beliefs.items():
            if isinstance(belief_data, dict):
                value = belief_data.get("value")
                confidence = belief_data.get("confidence", 1.0)
                metadata = belief_data.get("metadata", {})
                
                # Create belief
                belief = Belief(belief_name, value, confidence, metadata=metadata)
                self.state.add_belief(belief)
            else:
                # Simple value
                self.state.update_belief(belief_name, belief_data)
                
        logger.debug(f"BDI agent {self.agent_id} initialized {len(initial_beliefs)} beliefs")
        
    def _initialize_desires(self) -> None:
        """Initialize desires from configuration."""
        initial_desires = self.config.get("initial_desires", [])
        
        for desire_data in initial_desires:
            if "name" not in desire_data or "description" not in desire_data:
                logger.warning(f"BDI agent {self.agent_id} skipping invalid desire: {desire_data}")
                continue
                
            priority = desire_data.get("priority", 0.5)
            deadline = None
            if "deadline" in desire_data:
                try:
                    deadline = datetime.fromisoformat(desire_data["deadline"])
                except:
                    logger.warning(f"BDI agent {self.agent_id} invalid deadline format: {desire_data['deadline']}")
                    
            conditions = desire_data.get("conditions", {})
            
            # Create desire
            desire = Desire(
                name=desire_data["name"],
                description=desire_data["description"],
                priority=priority,
                deadline=deadline,
                conditions=conditions
            )
            
            self.state.add_desire(desire)
            
        logger.debug(f"BDI agent {self.agent_id} initialized {len(initial_desires)} desires")
        
    def _find_plan_for_desire(self, desire_name: str) -> Optional[Plan]:
        """
        Find a suitable plan for a desire.
        
        Args:
            desire_name: Name of the desire
            
        Returns:
            A new Plan instance or None if no suitable plan found
        """
        # First check if we already have intentions for this desire
        existing_plans = self.state.get_intentions_for_desire(desire_name)
        if existing_plans:
            # Find the first non-complete plan
            for plan in existing_plans:
                if not plan.complete:
                    return plan
                    
        # No existing plans, create a new one
        for plan_name, template in self.plan_library.items():
            if template["desire_name"] != desire_name:
                continue
                
            # Check context conditions
            if self._check_context_conditions(template.get("context_conditions", {})):
                # Create new plan instance
                plan = Plan(
                    name=plan_name,
                    desire_name=desire_name,
                    actions=template["actions"],
                    context_conditions=template.get("context_conditions", {})
                )
                
                # Add to intentions
                self.state.add_intention(plan)
                
                return plan
                
        return None
        
    def _check_context_conditions(self, conditions: Dict[str, Any]) -> bool:
        """
        Check if context conditions are satisfied.
        
        Args:
            conditions: Dictionary of conditions to check
            
        Returns:
            True if all conditions are satisfied
        """
        for belief_name, expected_value in conditions.items():
            belief = self.state.get_belief(belief_name)
            
            if not belief:
                return False
                
            if belief.value != expected_value:
                return False
                
        return True
        
    def _is_intention_valid(self, intention: Plan) -> bool:
        """
        Check if an intention is still valid.
        
        Args:
            intention: The intention to check
            
        Returns:
            True if the intention is valid
        """
        # Check if the desire still exists and is not achieved
        desire = self.state.get_desire(intention.desire_name)
        if not desire or desire.achieved or desire.is_expired():
            return False
            
        # Check if context conditions are still satisfied
        return self._check_context_conditions(intention.context_conditions)
        
    def _is_desire_satisfied(self, desire_name: str) -> bool:
        """
        Check if a desire is satisfied.
        
        Args:
            desire_name: Name of the desire
            
        Returns:
            True if the desire is satisfied
        """
        desire = self.state.get_desire(desire_name)
        if not desire:
            return False
            
        # Check conditions
        for belief_name, expected_value in desire.conditions.items():
            belief = self.state.get_belief(belief_name)
            
            if not belief:
                return False
                
            if belief.value != expected_value:
                return False
                
        return True 