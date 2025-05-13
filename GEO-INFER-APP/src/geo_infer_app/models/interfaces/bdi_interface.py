"""
BDI Agent Interface Implementation

Implements the AgentInterface for Belief-Desire-Intention (BDI) agents.
This interface connects the GEO-INFER-APP UI to the BDI agent implementation
in GEO-INFER-AGENT.
"""

from typing import Dict, List, Any, Optional, Callable
import logging
import datetime
import uuid
import json

try:
    # Import BDI agent implementation from GEO-INFER-AGENT
    from geo_infer_agent.models.bdi import BDIAgent, BeliefBase, DesireSet, IntentionStructure
except ImportError:
    # Mock implementation if GEO-INFER-AGENT is not available
    class BDIAgent:
        def __init__(self, **kwargs):
            self.id = str(uuid.uuid4())
            self.name = kwargs.get("name", f"BDI-Agent-{self.id[:8]}")
            self.beliefs = kwargs.get("beliefs", {})
            self.desires = kwargs.get("desires", [])
            self.intentions = []
            self.location = kwargs.get("initial_location", {"lat": 0.0, "lng": 0.0})
            self.status = "idle"
            
        def update_beliefs(self, beliefs):
            self.beliefs.update(beliefs)
            
        def add_desire(self, desire):
            self.desires.append(desire)
            
        def deliberate(self):
            # Simple mock implementation
            for desire in self.desires:
                if desire not in self.intentions:
                    self.intentions.append(desire)
                    
        def execute(self):
            # Simple mock implementation
            if self.intentions:
                self.status = "executing"
                # Simulate execution by removing the first intention
                if self.intentions:
                    self.intentions.pop(0)
            else:
                self.status = "idle"
    
    class BeliefBase:
        pass
        
    class DesireSet:
        pass
        
    class IntentionStructure:
        pass

from geo_infer_app.models.agent_interface import AgentInterface, AgentState, AgentType

# Configure logging
logger = logging.getLogger(__name__)

class BDIAgentInterface(AgentInterface):
    """
    Implementation of AgentInterface for BDI agents.
    
    This class provides the bridge between the UI components in GEO-INFER-APP
    and the BDI agent implementation in GEO-INFER-AGENT.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the BDI agent interface.
        
        Args:
            **kwargs: Configuration parameters for the agent interface
        """
        self._agents: Dict[str, BDIAgent] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._config = kwargs
        
        logger.info("Initialized BDI agent interface")
    
    def get_agent_state(self, agent_id: str) -> AgentState:
        """
        Retrieve the current state of the specified agent.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            AgentState object containing the current state
            
        Raises:
            ValueError: If the agent with the specified ID does not exist
        """
        if agent_id not in self._agents:
            raise ValueError(f"Agent with ID {agent_id} not found")
        
        agent = self._agents[agent_id]
        
        # Convert BDI agent state to AgentState
        return AgentState(
            agent_id=agent_id,
            agent_type=AgentType.BDI,
            status=agent.status,
            location=agent.location,
            tasks=[],  # BDI agents don't have tasks in the same way
            beliefs=agent.beliefs,
            goals=agent.desires,  # In BDI, desires are similar to goals
            last_updated=datetime.datetime.now().isoformat(),
            metadata={
                "intentions": agent.intentions
            }
        )
    
    def list_agents(self, filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all available BDI agents, with optional filtering.
        
        Args:
            filter_params: Optional dictionary of filter parameters
            
        Returns:
            List of agent summary dictionaries
        """
        agents = []
        
        for agent_id, agent in self._agents.items():
            # Skip agents that don't match the filter
            if filter_params:
                if "status" in filter_params and agent.status != filter_params["status"]:
                    continue
                    
                if "location" in filter_params:
                    # Filter by location within a radius
                    agent_loc = agent.location
                    filter_loc = filter_params["location"]
                    
                    if not self._is_location_in_radius(
                        agent_loc, 
                        filter_loc.get("center"), 
                        filter_loc.get("radius", 0)
                    ):
                        continue
            
            # Add agent summary
            agents.append({
                "id": agent_id,
                "name": agent.name,
                "type": "bdi",
                "status": agent.status,
                "location": agent.location,
                "num_beliefs": len(agent.beliefs),
                "num_desires": len(agent.desires),
                "num_intentions": len(agent.intentions)
            })
        
        return agents
    
    def send_command(self, agent_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a command to a BDI agent.
        
        Args:
            agent_id: Unique identifier for the agent
            command: Command to send
            params: Parameters for the command
            
        Returns:
            Response from the agent
            
        Raises:
            ValueError: If the agent with the specified ID does not exist
            ValueError: If the command is not supported
        """
        if agent_id not in self._agents:
            raise ValueError(f"Agent with ID {agent_id} not found")
        
        agent = self._agents[agent_id]
        response = {"success": False, "message": "Unknown command"}
        
        if command == "add_belief":
            if "belief" in params:
                agent.update_beliefs(params["belief"])
                response = {"success": True, "message": "Belief added"}
        elif command == "add_desire":
            if "desire" in params:
                agent.add_desire(params["desire"])
                response = {"success": True, "message": "Desire added"}
        elif command == "deliberate":
            agent.deliberate()
            response = {"success": True, "message": "Agent deliberated"}
        elif command == "execute":
            agent.execute()
            response = {"success": True, "message": "Agent executed intentions"}
        elif command == "move":
            if "location" in params:
                agent.location = params["location"]
                response = {"success": True, "message": "Agent moved"}
        else:
            raise ValueError(f"Unsupported command: {command}")
        
        # Trigger event handlers for agent update
        self._trigger_event("agent_updated", {
            "agent_id": agent_id,
            "state": self.get_agent_state(agent_id)
        })
        
        return response
    
    def register_event_handler(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback function to handle agent events.
        
        Args:
            event_type: Type of event to handle
            callback: Function to call when the event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
            
        self._event_handlers[event_type].append(callback)
        logger.info(f"Registered event handler for {event_type}")
    
    def create_agent(self, agent_type: AgentType, config: Dict[str, Any]) -> str:
        """
        Create a new BDI agent instance.
        
        Args:
            agent_type: Type of agent to create (must be AgentType.BDI)
            config: Configuration parameters for the agent
            
        Returns:
            ID of the created agent
            
        Raises:
            ValueError: If agent_type is not AgentType.BDI
        """
        if agent_type != AgentType.BDI:
            raise ValueError(f"This interface only supports BDI agents, got {agent_type.value}")
        
        # Create a new BDI agent
        agent = BDIAgent(**config)
        agent_id = agent.id
        
        # Store the agent
        self._agents[agent_id] = agent
        
        # Trigger event handlers for agent creation
        self._trigger_event("agent_created", {
            "agent_id": agent_id,
            "state": self.get_agent_state(agent_id)
        })
        
        logger.info(f"Created BDI agent with ID {agent_id}")
        return agent_id
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Trigger all registered handlers for an event.
        
        Args:
            event_type: Type of event
            event_data: Data for the event
        """
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
    
    @staticmethod
    def _is_location_in_radius(location, center, radius):
        """
        Check if a location is within a radius of a center point.
        
        Args:
            location: Location to check
            center: Center location
            radius: Radius in kilometers
            
        Returns:
            True if the location is within the radius, False otherwise
        """
        if not location or not center or radius <= 0:
            return False
            
        # Simple Euclidean distance for demonstration
        # In a real implementation, use haversine formula for geographic coordinates
        lat_diff = location["lat"] - center["lat"]
        lng_diff = location["lng"] - center["lng"]
        distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
        
        return distance <= radius


# Register this interface with the agent factory
from geo_infer_app.models.agent_factory import AgentFactory
AgentFactory.register_interface(AgentType.BDI, BDIAgentInterface) 