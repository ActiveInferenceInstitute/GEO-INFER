"""
Agent Factory Module

Factory pattern implementation for creating various types of agent interfaces.
This module handles the instantiation of appropriate agent interfaces based on 
the requested agent type, configuration, and available agent model implementations.
"""

from typing import Dict, Any, Type, Optional
import importlib
import logging
from .agent_interface import AgentInterface, AgentType

# Configure logging
logger = logging.getLogger(__name__)

class AgentFactory:
    """
    Factory class for creating agent interfaces.
    
    This class is responsible for:
    1. Registering agent interface implementations
    2. Creating agent interface instances
    3. Managing agent interface lifecycle
    """
    
    # Registry of agent interface implementations
    _registry: Dict[AgentType, Type[AgentInterface]] = {}
    
    @classmethod
    def register_interface(cls, agent_type: AgentType, interface_class: Type[AgentInterface]) -> None:
        """
        Register an agent interface implementation for a specific agent type.
        
        Args:
            agent_type: Type of agent this interface is for
            interface_class: Class implementing the AgentInterface
        """
        if not issubclass(interface_class, AgentInterface):
            raise TypeError(f"Interface class must be a subclass of AgentInterface")
        
        cls._registry[agent_type] = interface_class
        logger.info(f"Registered interface {interface_class.__name__} for agent type {agent_type.value}")
    
    @classmethod
    def create_interface(cls, agent_type: AgentType, config: Optional[Dict[str, Any]] = None) -> AgentInterface:
        """
        Create an agent interface instance for the specified agent type.
        
        Args:
            agent_type: Type of agent interface to create
            config: Configuration for the agent interface
            
        Returns:
            An instance of AgentInterface appropriate for the agent type
            
        Raises:
            ValueError: If no interface is registered for the agent type
        """
        if agent_type not in cls._registry:
            # Try to dynamically import the interface
            try:
                module_name = f"geo_infer_app.models.interfaces.{agent_type.value}_interface"
                importlib.import_module(module_name)
                
                # If we reach here, the module was imported but the interface wasn't registered
                raise ValueError(f"Interface for agent type {agent_type.value} was not registered")
            except ModuleNotFoundError:
                raise ValueError(f"No interface found for agent type {agent_type.value}")
        
        interface_class = cls._registry[agent_type]
        config = config or {}
        
        logger.info(f"Creating interface for agent type {agent_type.value}")
        return interface_class(**config)
    
    @classmethod
    def get_available_agent_types(cls) -> Dict[str, str]:
        """
        Get a dictionary of available agent types.
        
        Returns:
            Dictionary mapping agent type values to descriptions
        """
        return {agent_type.value: agent_type.name for agent_type in cls._registry.keys()} 