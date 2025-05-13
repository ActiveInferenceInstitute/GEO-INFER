#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base Agent for GEO-INFER-AGENT

This module provides the base agent class that all specialized agents
will inherit from, implementing core functionality and interfaces.
"""

import os
import sys
import time
import yaml
import logging
import uuid
import json
import asyncio
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from pathlib import Path

# Configure logger
logger = logging.getLogger("geo_infer_agent.agent_base")

class AgentState:
    """
    Represents the internal state of an agent.
    
    This class tracks the agent's:
    - Beliefs (what it thinks about the world)
    - Desires (goals it wants to achieve)
    - Intentions (current plan of actions)
    - Memory (past observations and actions)
    """
    
    def __init__(self, capacity: int = 1000):
        """
        Initialize agent state.
        
        Args:
            capacity: Maximum number of memory items to store
        """
        self.beliefs = {}  # Current world model
        self.desires = []  # Goals
        self.intentions = []  # Planned actions
        self.memory = []  # Past observations and actions
        self.memory_capacity = capacity
        self.creation_time = datetime.now()
        self.last_update = self.creation_time
        
    def update_belief(self, key: str, value: Any) -> None:
        """
        Update a belief with new information.
        
        Args:
            key: Belief identifier
            value: New belief value
        """
        old_value = self.beliefs.get(key)
        self.beliefs[key] = value
        self.last_update = datetime.now()
        
        # Add to memory
        if old_value != value:
            self.add_to_memory({
                "type": "belief_update",
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "timestamp": self.last_update.isoformat()
            })
    
    def add_desire(self, desire: Dict[str, Any]) -> None:
        """
        Add a new goal/desire for the agent.
        
        Args:
            desire: Dictionary containing goal information
                   Must include 'priority' and 'description' keys
        """
        if "priority" not in desire or "description" not in desire:
            raise ValueError("Desire must include 'priority' and 'description'")
            
        desire["timestamp"] = datetime.now().isoformat()
        self.desires.append(desire)
        self.desires.sort(key=lambda x: x["priority"], reverse=True)
        self.last_update = datetime.now()
        
        # Add to memory
        self.add_to_memory({
            "type": "desire_added",
            "desire": desire,
            "timestamp": self.last_update.isoformat()
        })
    
    def set_intention(self, intention: Dict[str, Any]) -> None:
        """
        Set current intention/plan.
        
        Args:
            intention: Dictionary containing plan information
                      Must include 'actions' key with list of action steps
        """
        if "actions" not in intention:
            raise ValueError("Intention must include 'actions' list")
            
        intention["timestamp"] = datetime.now().isoformat()
        self.intentions.append(intention)
        self.last_update = datetime.now()
        
        # Add to memory
        self.add_to_memory({
            "type": "intention_set",
            "intention": intention,
            "timestamp": self.last_update.isoformat()
        })
    
    def add_to_memory(self, item: Dict[str, Any]) -> None:
        """
        Add an item to agent's memory.
        
        Args:
            item: Memory item (observation, action, or belief change)
        """
        if "timestamp" not in item:
            item["timestamp"] = datetime.now().isoformat()
            
        self.memory.append(item)
        
        # Enforce memory capacity
        if len(self.memory) > self.memory_capacity:
            self.memory.pop(0)
    
    def get_top_desire(self) -> Optional[Dict[str, Any]]:
        """
        Get the highest priority desire.
        
        Returns:
            Highest priority desire or None if no desires
        """
        return self.desires[0] if self.desires else None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary for serialization.
        
        Returns:
            Dictionary representation of state
        """
        return {
            "beliefs": self.beliefs,
            "desires": self.desires,
            "intentions": self.intentions,
            "memory": self.memory,
            "creation_time": self.creation_time.isoformat(),
            "last_update": self.last_update.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """
        Create state from dictionary.
        
        Args:
            data: Dictionary representation of state
            
        Returns:
            AgentState instance
        """
        state = cls()
        state.beliefs = data.get("beliefs", {})
        state.desires = data.get("desires", [])
        state.intentions = data.get("intentions", [])
        state.memory = data.get("memory", [])
        state.creation_time = datetime.fromisoformat(data.get("creation_time", datetime.now().isoformat()))
        state.last_update = datetime.fromisoformat(data.get("last_update", datetime.now().isoformat()))
        return state


class BaseAgent(ABC):
    """
    Base agent class that all specialized agents inherit from.
    
    This class implements:
    - Core agent lifecycle (initialize, run, stop)
    - State management
    - Perception and action interfaces
    - Communication with other agents
    - Persistence mechanisms
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize the agent.
        
        Args:
            agent_id: Unique identifier for this agent (auto-generated if None)
            config: Configuration dictionary
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.config = config or {}
        self.state = AgentState(capacity=self.config.get("memory_capacity", 1000))
        self.running = False
        self.loop = None  # Will store asyncio event loop
        self.start_time = None
        self.stop_time = None
        
        # Initialize communication channels
        self.message_queue = asyncio.Queue()
        
        # Setup logging
        self._setup_logging()
        
        logger.info(f"Agent {self.agent_id} initialized")
    
    def _setup_logging(self) -> None:
        """Configure agent-specific logging."""
        log_level = self.config.get("logging_level", "INFO")
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")
        
        # Add handler if none exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - Agent:{self.agent_id} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        logger.setLevel(numeric_level)
    
    async def run(self) -> None:
        """
        Main agent execution loop.
        
        This method:
        1. Initializes the agent
        2. Runs the perception-decision-action loop
        3. Handles shutdown when stopped
        """
        if self.running:
            logger.warning(f"Agent {self.agent_id} is already running")
            return
            
        self.running = True
        self.start_time = datetime.now()
        logger.info(f"Agent {self.agent_id} starting at {self.start_time}")
        
        # Store current event loop
        self.loop = asyncio.get_running_loop()
        
        try:
            # Initialize specific agent implementation
            await self.initialize()
            
            # Run agent until stopped
            while self.running:
                # Process any incoming messages
                await self.process_messages()
                
                # Perceive environment
                perception = await self.perceive()
                
                # Update beliefs based on perception
                self.update_beliefs(perception)
                
                # Decide what to do
                action = await self.decide()
                
                # Execute selected action
                if action:
                    result = await self.act(action)
                    # Record action and result
                    self.state.add_to_memory({
                        "type": "action",
                        "action": action,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Check if we should stop based on runtime limits
                self._check_runtime_limits()
                
                # Sleep for specified decision frequency
                await asyncio.sleep(self.config.get("decision_frequency", 1))
                
        except Exception as e:
            logger.error(f"Agent {self.agent_id} encountered an error: {str(e)}", exc_info=True)
        finally:
            # Cleanup
            self.running = False
            self.stop_time = datetime.now()
            logger.info(f"Agent {self.agent_id} stopped at {self.stop_time}")
            
            # Calculate runtime
            runtime = (self.stop_time - self.start_time).total_seconds()
            logger.info(f"Agent {self.agent_id} ran for {runtime:.2f} seconds")
            
            # Run shutdown procedure
            await self.shutdown()
    
    def _check_runtime_limits(self) -> None:
        """Check if the agent should stop based on runtime limits."""
        if not self.start_time:
            return
            
        max_runtime = self.config.get("max_runtime")
        if max_runtime:
            runtime = (datetime.now() - self.start_time).total_seconds()
            if runtime > max_runtime:
                logger.info(f"Agent {self.agent_id} reached max runtime of {max_runtime} seconds")
                self.stop()
    
    def stop(self) -> None:
        """Stop the agent execution."""
        logger.info(f"Agent {self.agent_id} stopping...")
        self.running = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize agent before running.
        
        Subclasses must implement this to set up agent-specific resources.
        """
        pass
    
    @abstractmethod
    async def perceive(self) -> Dict[str, Any]:
        """
        Collect information from the environment.
        
        Returns:
            Dictionary with perception data
        """
        pass
    
    @abstractmethod
    def update_beliefs(self, perception: Dict[str, Any]) -> None:
        """
        Update agent's beliefs based on perception.
        
        Args:
            perception: Data from the perceive method
        """
        pass
    
    @abstractmethod
    async def decide(self) -> Optional[Dict[str, Any]]:
        """
        Decide on next action based on beliefs and goals.
        
        Returns:
            Action to execute or None
        """
        pass
    
    @abstractmethod
    async def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a selected action.
        
        Args:
            action: Action to execute
            
        Returns:
            Result of the action
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Clean up resources when agent stops.
        
        Subclasses must implement this to release agent-specific resources.
        """
        pass
    
    async def send_message(self, to_agent_id: str, content: Dict[str, Any]) -> bool:
        """
        Send a message to another agent.
        
        Args:
            to_agent_id: Recipient agent ID
            content: Message content
            
        Returns:
            True if message was sent, False otherwise
        """
        message = {
            "from": self.agent_id,
            "to": to_agent_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "message_id": str(uuid.uuid4())
        }
        
        logger.debug(f"Agent {self.agent_id} sending message to {to_agent_id}")
        
        # This is a placeholder - actual implementation would depend on
        # the communication mechanism (direct, via broker, etc.)
        try:
            # Implementation-specific message sending logic would go here
            # For now, we just log that a message would be sent
            logger.info(f"Would send: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {to_agent_id}: {str(e)}")
            return False
    
    async def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Receive a message from another agent.
        
        Args:
            message: Message content
        """
        logger.debug(f"Agent {self.agent_id} received message from {message.get('from')}")
        await self.message_queue.put(message)
    
    async def process_messages(self) -> None:
        """Process all messages in the queue."""
        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                await self._handle_message(message)
                self.message_queue.task_done()
            except asyncio.QueueEmpty:
                break
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a single message.
        
        Args:
            message: Message to handle
        """
        # Record in memory
        self.state.add_to_memory({
            "type": "message_received",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Default implementation just logs the message
        # Subclasses should override for specific behavior
        logger.info(f"Agent {self.agent_id} handling message: {message}")
    
    def save_state(self, filepath: Optional[str] = None) -> str:
        """
        Save agent state to file.
        
        Args:
            filepath: Path to save state (default: agent_<id>_state.json)
            
        Returns:
            Filepath where state was saved
        """
        if filepath is None:
            filepath = f"agent_{self.agent_id}_state.json"
            
        try:
            with open(filepath, 'w') as f:
                state_dict = self.state.to_dict()
                state_dict["agent_id"] = self.agent_id
                state_dict["agent_type"] = self.__class__.__name__
                state_dict["save_time"] = datetime.now().isoformat()
                
                json.dump(state_dict, f, indent=2)
            
            logger.info(f"Agent {self.agent_id} state saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save agent state: {str(e)}")
            raise
    
    @classmethod
    def load_state(cls, filepath: str, config: Optional[Dict] = None) -> 'BaseAgent':
        """
        Create agent from saved state.
        
        Args:
            filepath: Path to state file
            config: Configuration to use (overrides saved config)
            
        Returns:
            Instantiated agent with loaded state
        """
        try:
            with open(filepath, 'r') as f:
                state_dict = json.load(f)
                
            agent_id = state_dict.get("agent_id")
            agent = cls(agent_id=agent_id, config=config)
            agent.state = AgentState.from_dict(state_dict)
            
            logger.info(f"Loaded agent {agent_id} state from {filepath}")
            return agent
        except Exception as e:
            logger.error(f"Failed to load agent state: {str(e)}")
            raise


# Example subclass (minimal implementation)
class ExampleAgent(BaseAgent):
    """Example agent implementation for demonstration."""
    
    async def initialize(self) -> None:
        """Initialize the example agent."""
        logger.info(f"Example agent {self.agent_id} initializing")
        
        # Set initial beliefs
        self.state.update_belief("environment_known", False)
        
        # Set initial desires
        self.state.add_desire({
            "description": "Explore environment",
            "priority": 10,
            "completed": False
        })
    
    async def perceive(self) -> Dict[str, Any]:
        """Simple perception that just returns current time."""
        return {
            "current_time": datetime.now().isoformat(),
            "random_observation": uuid.uuid4().hex[:8]
        }
    
    def update_beliefs(self, perception: Dict[str, Any]) -> None:
        """Update beliefs based on perception."""
        # Just store the entire perception as beliefs
        for key, value in perception.items():
            self.state.update_belief(key, value)
            
        # After 5 observations, consider environment known
        if len(self.state.memory) > 5:
            self.state.update_belief("environment_known", True)
    
    async def decide(self) -> Optional[Dict[str, Any]]:
        """Simple decision making."""
        # Get top desire
        desire = self.state.get_top_desire()
        if not desire:
            return None
            
        # If environment not known, explore
        if not self.state.beliefs.get("environment_known", False):
            return {
                "type": "explore",
                "target": "environment",
                "params": {}
            }
        else:
            # Mark exploration desire as completed
            for d in self.state.desires:
                if d["description"] == "Explore environment":
                    d["completed"] = True
            
            # No action needed
            return None
    
    async def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action."""
        if action["type"] == "explore":
            logger.info(f"Agent {self.agent_id} exploring {action['target']}")
            # Simulate exploration
            await asyncio.sleep(0.5)
            return {"status": "success", "info": "Exploration completed"}
        
        return {"status": "error", "info": "Unknown action type"}
    
    async def shutdown(self) -> None:
        """Clean up resources."""
        logger.info(f"Example agent {self.agent_id} shutting down")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    async def run_agent_example():
        # Create agent
        agent = ExampleAgent(config={"decision_frequency": 1, "memory_capacity": 100})
        
        # Run in background task
        task = asyncio.create_task(agent.run())
        
        # Let it run for a bit
        await asyncio.sleep(5)
        
        # Stop agent
        agent.stop()
        
        # Wait for agent to finish
        await task
        
        # Save state
        filepath = agent.save_state()
        print(f"Agent state saved to {filepath}")
    
    # Run example
    asyncio.run(run_agent_example()) 