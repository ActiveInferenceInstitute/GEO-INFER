"""
Agent Visualization Module

Provides components and utilities for visualizing agents and their states
in geospatial contexts within the GEO-INFER-APP.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import json
import logging
from enum import Enum
from dataclasses import dataclass
from .agent_interface import AgentState, AgentType

# Configure logging
logger = logging.getLogger(__name__)

class VisualizationType(Enum):
    """Enumeration of supported visualization types for agents."""
    MAP_MARKER = "map_marker"
    AGENT_DASHBOARD = "agent_dashboard"
    NETWORK_NODE = "network_node"
    TIMELINE_EVENT = "timeline_event"
    STATE_DIAGRAM = "state_diagram"


@dataclass
class VisualizationConfig:
    """Configuration for agent visualization."""
    vis_type: VisualizationType
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None  # Icon identifier or URL
    color: Optional[str] = None  # CSS color value
    scale: float = 1.0
    show_label: bool = True
    custom_props: Optional[Dict[str, Any]] = None


class AgentVisualization:
    """
    Class for converting agent states into visualization-friendly formats.
    
    This class handles:
    1. Converting agent states to visualization data
    2. Generating visualization configurations for different agent types
    3. Customizing visualizations based on agent properties
    """
    
    @staticmethod
    def get_default_config(agent_type: AgentType) -> Dict[str, VisualizationConfig]:
        """
        Get default visualization configurations for the specified agent type.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dictionary mapping visualization context to configuration
        """
        configs = {
            "map": VisualizationConfig(
                vis_type=VisualizationType.MAP_MARKER,
                title=f"{agent_type.name} Agent",
                icon="agent",
                color="#3498db",
                show_label=True
            ),
            "dashboard": VisualizationConfig(
                vis_type=VisualizationType.AGENT_DASHBOARD,
                title=f"{agent_type.name} Dashboard",
                description=f"Dashboard for {agent_type.name} agent type",
                icon="dashboard",
                custom_props={
                    "widgets": ["status", "tasks", "beliefs", "goals"]
                }
            ),
            "network": VisualizationConfig(
                vis_type=VisualizationType.NETWORK_NODE,
                title=f"{agent_type.name}",
                icon="node",
                color="#2ecc71"
            )
        }
        
        # Customize based on agent type
        if agent_type == AgentType.BDI:
            configs["map"].color = "#e74c3c"
            configs["dashboard"].custom_props["widgets"].append("intentions")
        elif agent_type == AgentType.ACTIVE_INFERENCE:
            configs["map"].color = "#f39c12"
            configs["dashboard"].custom_props["widgets"].append("predictions")
        elif agent_type == AgentType.RL:
            configs["map"].color = "#9b59b6"
            configs["dashboard"].custom_props["widgets"].append("rewards")
        
        return configs
    
    @staticmethod
    def state_to_map_feature(agent_state: AgentState) -> Dict[str, Any]:
        """
        Convert an agent state to a map feature representation.
        
        Args:
            agent_state: Current state of the agent
            
        Returns:
            Map feature representation for the agent
            
        Raises:
            ValueError: If the agent state doesn't include location
        """
        if not agent_state.location:
            raise ValueError(f"Agent {agent_state.agent_id} has no location data")
        
        configs = AgentVisualization.get_default_config(agent_state.agent_type)
        map_config = configs["map"]
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [agent_state.location["lng"], agent_state.location["lat"]]
            },
            "properties": {
                "id": agent_state.agent_id,
                "type": agent_state.agent_type.value,
                "status": agent_state.status,
                "title": map_config.title,
                "icon": map_config.icon,
                "color": map_config.color,
                "scale": map_config.scale,
                "showLabel": map_config.show_label,
                "lastUpdated": agent_state.last_updated,
                "metadata": agent_state.metadata
            }
        }
        
        return feature
    
    @staticmethod
    def state_to_dashboard_data(agent_state: AgentState) -> Dict[str, Any]:
        """
        Convert an agent state to dashboard data.
        
        Args:
            agent_state: Current state of the agent
            
        Returns:
            Dashboard data representation for the agent
        """
        configs = AgentVisualization.get_default_config(agent_state.agent_type)
        dash_config = configs["dashboard"]
        
        dashboard_data = {
            "id": agent_state.agent_id,
            "type": agent_state.agent_type.value,
            "title": dash_config.title,
            "status": agent_state.status,
            "lastUpdated": agent_state.last_updated,
            "widgets": {}
        }
        
        # Add data for each configured widget
        if "status" in dash_config.custom_props["widgets"]:
            dashboard_data["widgets"]["status"] = {
                "title": "Status",
                "value": agent_state.status
            }
        
        if "tasks" in dash_config.custom_props["widgets"] and agent_state.tasks:
            dashboard_data["widgets"]["tasks"] = {
                "title": "Tasks",
                "value": agent_state.tasks
            }
        
        if "beliefs" in dash_config.custom_props["widgets"] and agent_state.beliefs:
            dashboard_data["widgets"]["beliefs"] = {
                "title": "Beliefs",
                "value": agent_state.beliefs
            }
        
        if "goals" in dash_config.custom_props["widgets"] and agent_state.goals:
            dashboard_data["widgets"]["goals"] = {
                "title": "Goals",
                "value": agent_state.goals
            }
        
        # Agent type specific widgets
        if agent_state.agent_type == AgentType.BDI and "intentions" in dash_config.custom_props["widgets"]:
            if agent_state.metadata and "intentions" in agent_state.metadata:
                dashboard_data["widgets"]["intentions"] = {
                    "title": "Intentions",
                    "value": agent_state.metadata["intentions"]
                }
        
        return dashboard_data 