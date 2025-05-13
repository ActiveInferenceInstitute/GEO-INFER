"""
Desire module for BDI agents.

Desires represent goals that the agent wants to achieve. This module provides:
- Basic desire representation with attributes
- Priority-based desire management
- Conditioned desires with activation/deactivation conditions
- Geospatial desires with location-specific goals
"""

from typing import Dict, Any, List, Optional, Set, Callable, Union, Tuple
import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class DesireState(Enum):
    """Enumeration of possible states for a desire."""
    ACTIVE = "active"         # The desire is currently active
    INACTIVE = "inactive"     # The desire is currently inactive
    ACHIEVED = "achieved"     # The desire has been achieved
    FAILED = "failed"         # The desire has permanently failed
    SUSPENDED = "suspended"   # The desire is temporarily suspended


@dataclass
class Desire:
    """
    A desire representing a goal the agent wants to achieve.
    
    Attributes:
        name: Unique identifier for the desire
        description: Human-readable description of the desire
        priority: Priority level of the desire (higher values = higher priority)
        state: Current state of the desire
        preconditions: Dictionary of conditions that must be met for the desire to be adopted
        success_conditions: Dictionary of conditions that indicate the desire has been achieved
        failure_conditions: Dictionary of conditions that indicate the desire has failed
        spatial_reference: Optional geospatial reference for location-specific desires
        metadata: Additional information about this desire
    """
    name: str
    description: str
    priority: float = 1.0
    state: DesireState = DesireState.ACTIVE
    preconditions: Dict[str, Any] = field(default_factory=dict)
    success_conditions: Dict[str, Any] = field(default_factory=dict)
    failure_conditions: Dict[str, Any] = field(default_factory=dict)
    spatial_reference: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_active(self) -> bool:
        """
        Check if this desire is active.
        
        Returns:
            True if the desire is active, False otherwise
        """
        return self.state == DesireState.ACTIVE
    
    def is_achieved(self) -> bool:
        """
        Check if this desire has been achieved.
        
        Returns:
            True if the desire has been achieved, False otherwise
        """
        return self.state == DesireState.ACHIEVED
    
    def is_failed(self) -> bool:
        """
        Check if this desire has failed.
        
        Returns:
            True if the desire has failed, False otherwise
        """
        return self.state == DesireState.FAILED
    
    def activate(self) -> None:
        """Activate this desire."""
        if self.state != DesireState.ACHIEVED and self.state != DesireState.FAILED:
            self.state = DesireState.ACTIVE
            logger.debug(f"Activated desire: {self.name}")
    
    def deactivate(self) -> None:
        """Deactivate this desire."""
        if self.state == DesireState.ACTIVE:
            self.state = DesireState.INACTIVE
            logger.debug(f"Deactivated desire: {self.name}")
    
    def suspend(self) -> None:
        """Suspend this desire."""
        if self.state == DesireState.ACTIVE:
            self.state = DesireState.SUSPENDED
            logger.debug(f"Suspended desire: {self.name}")
    
    def mark_achieved(self) -> None:
        """Mark this desire as achieved."""
        self.state = DesireState.ACHIEVED
        logger.debug(f"Marked desire as achieved: {self.name}")
    
    def mark_failed(self) -> None:
        """Mark this desire as failed."""
        self.state = DesireState.FAILED
        logger.debug(f"Marked desire as failed: {self.name}")
    
    def check_preconditions(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if the preconditions for this desire are met.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if all preconditions are met, False otherwise
        """
        for key, value in self.preconditions.items():
            if key not in belief_values or belief_values[key] != value:
                return False
                
        return True
    
    def check_success(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if the success conditions for this desire are met.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if all success conditions are met, False otherwise
        """
        for key, value in self.success_conditions.items():
            if key not in belief_values or belief_values[key] != value:
                return False
                
        return True
    
    def check_failure(self, belief_values: Dict[str, Any]) -> bool:
        """
        Check if the failure conditions for this desire are met.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            True if any failure condition is met, False otherwise
        """
        for key, value in self.failure_conditions.items():
            if key in belief_values and belief_values[key] == value:
                return True
                
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this desire to a dictionary representation.
        
        Returns:
            Dictionary representation of this desire
        """
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "state": self.state.value,
            "preconditions": self.preconditions,
            "success_conditions": self.success_conditions,
            "failure_conditions": self.failure_conditions,
            "spatial_reference": self.spatial_reference,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Desire':
        """
        Create a Desire instance from a dictionary.
        
        Args:
            data: Dictionary representation of a desire
            
        Returns:
            Desire instance
        """
        # Handle state conversion from string
        if "state" in data and isinstance(data["state"], str):
            data["state"] = DesireState(data["state"])
            
        return cls(**data)


class DesireSet:
    """
    A collection of desires maintained by an agent.
    
    This class handles:
    - Adding, updating, and removing desires
    - Querying desires by various criteria
    - Selecting desires based on priority and state
    - Checking desire conditions against beliefs
    """
    
    def __init__(self):
        """Initialize an empty desire set."""
        self._desires: Dict[str, Desire] = {}
    
    def add(self, desire: Desire) -> None:
        """
        Add a new desire to the desire set.
        
        Args:
            desire: Desire to add
            
        Raises:
            ValueError: If a desire with the same name already exists
        """
        if desire.name in self._desires:
            raise ValueError(f"Desire with name '{desire.name}' already exists")
            
        self._desires[desire.name] = desire
        logger.debug(f"Added desire: {desire.name}")
    
    def get(self, name: str) -> Desire:
        """
        Get a desire by name.
        
        Args:
            name: Name of the desire to get
            
        Returns:
            The desire with the given name
            
        Raises:
            KeyError: If no desire with the given name exists
        """
        if name not in self._desires:
            raise KeyError(f"No desire with name '{name}' exists")
            
        return self._desires[name]
    
    def remove(self, name: str) -> None:
        """
        Remove a desire from the desire set.
        
        Args:
            name: Name of the desire to remove
            
        Raises:
            KeyError: If no desire with the given name exists
        """
        if name not in self._desires:
            raise KeyError(f"No desire with name '{name}' exists")
            
        del self._desires[name]
        logger.debug(f"Removed desire: {name}")
    
    def has_desire(self, name: str) -> bool:
        """
        Check if a desire with the given name exists.
        
        Args:
            name: Name of the desire to check for
            
        Returns:
            True if a desire with the given name exists, False otherwise
        """
        return name in self._desires
    
    def get_all(self) -> Dict[str, Desire]:
        """
        Get all desires in the desire set.
        
        Returns:
            Dictionary mapping desire names to Desire objects
        """
        return dict(self._desires)
    
    def get_active(self) -> Dict[str, Desire]:
        """
        Get all active desires in the desire set.
        
        Returns:
            Dictionary mapping desire names to active Desire objects
        """
        return {name: desire for name, desire in self._desires.items() if desire.is_active()}
    
    def get_achieved(self) -> Dict[str, Desire]:
        """
        Get all achieved desires in the desire set.
        
        Returns:
            Dictionary mapping desire names to achieved Desire objects
        """
        return {name: desire for name, desire in self._desires.items() if desire.is_achieved()}
    
    def get_failed(self) -> Dict[str, Desire]:
        """
        Get all failed desires in the desire set.
        
        Returns:
            Dictionary mapping desire names to failed Desire objects
        """
        return {name: desire for name, desire in self._desires.items() if desire.is_failed()}
    
    def select_desires(self, max_count: Optional[int] = None) -> List[Desire]:
        """
        Select desires based on priority.
        
        Args:
            max_count: Maximum number of desires to select
            
        Returns:
            List of selected desires, sorted by priority (highest first)
        """
        # Get all active desires
        active_desires = list(self.get_active().values())
        
        # Sort by priority (highest first)
        active_desires.sort(key=lambda d: d.priority, reverse=True)
        
        # Limit to max_count if specified
        if max_count is not None and max_count >= 0:
            return active_desires[:max_count]
            
        return active_desires
    
    def update_states(self, belief_values: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Update the states of all desires based on the current beliefs.
        
        Args:
            belief_values: Dictionary of belief values to check against
            
        Returns:
            Tuple containing two lists:
            - List of names of newly achieved desires
            - List of names of newly failed desires
        """
        achieved = []
        failed = []
        
        for name, desire in self._desires.items():
            if desire.is_active():
                # Check for success
                if desire.check_success(belief_values):
                    desire.mark_achieved()
                    achieved.append(name)
                    
                # Check for failure
                elif desire.check_failure(belief_values):
                    desire.mark_failed()
                    failed.append(name)
            elif desire.state == DesireState.INACTIVE:
                # Check if preconditions are met
                if desire.check_preconditions(belief_values):
                    desire.activate()
                    
        return achieved, failed
    
    def query_spatial(self, center: Dict[str, float], radius: float) -> List[Desire]:
        """
        Query desires by spatial reference within a radius of a center point.
        
        Args:
            center: Center point coordinates
            radius: Radius to search within
            
        Returns:
            List of desires with spatial references within the radius
        """
        results = []
        
        for desire in self._desires.values():
            if desire.spatial_reference and self._is_in_radius(desire.spatial_reference, center, radius):
                results.append(desire)
                
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the desire set to a dictionary representation.
        
        Returns:
            Dictionary representation of the desire set
        """
        return {
            "desires": {name: desire.to_dict() for name, desire in self._desires.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DesireSet':
        """
        Create a DesireSet instance from a dictionary.
        
        Args:
            data: Dictionary representation of a desire set
            
        Returns:
            DesireSet instance
        """
        desire_set = cls()
        
        # Add desires
        for name, desire_data in data.get("desires", {}).items():
            desire = Desire.from_dict(desire_data)
            desire_set._desires[name] = desire
            
        return desire_set
    
    @staticmethod
    def _is_in_radius(location: Dict[str, float], center: Dict[str, float], radius: float) -> bool:
        """
        Check if a location is within a radius of a center point.
        
        Args:
            location: Location to check
            center: Center location
            radius: Radius to check within
            
        Returns:
            True if the location is within the radius, False otherwise
        """
        if not location or not center:
            return False
            
        # Simple Euclidean distance
        lat_diff = location.get("lat", 0) - center.get("lat", 0)
        lng_diff = location.get("lng", 0) - center.get("lng", 0)
        distance = (lat_diff ** 2 + lng_diff ** 2) ** 0.5
        
        return distance <= radius 