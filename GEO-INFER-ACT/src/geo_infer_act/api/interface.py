"""
Active Inference Interface for external interaction.
"""
from typing import Dict, List, Optional, Union, Any
import numpy as np

from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.policy_selection import PolicySelection
from geo_infer_act.utils.config import load_config


class ActiveInferenceInterface:
    """
    Interface for interacting with active inference models.
    
    This class provides a standardized interface for creating, configuring,
    and using active inference models within the GEO-INFER framework.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the interface with optional configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path) if config_path else None
        self.models = {}
        self.policy_selectors = {}
        
    def create_model(self, model_id: str, model_type: str, 
                     parameters: Dict[str, Any]) -> str:
        """
        Create a new active inference model.
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model to create
            parameters: Model parameters
            
        Returns:
            model_id: Identifier of the created model
        """
        self.models[model_id] = GenerativeModel(
            model_type=model_type,
            parameters=parameters
        )
        
        self.policy_selectors[model_id] = PolicySelection(
            generative_model=self.models[model_id]
        )
        
        return model_id
    
    def update_beliefs(self, model_id: str, 
                      observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Update beliefs based on observations.
        
        Args:
            model_id: Identifier of the model
            observations: Dictionary of observations
            
        Returns:
            updated_beliefs: Updated belief distributions
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
            
        model = self.models[model_id]
        return model.update_beliefs(observations)
    
    def select_policy(self, model_id: str) -> Dict[str, Any]:
        """
        Select optimal policy based on expected free energy.
        
        Args:
            model_id: Identifier of the model
            
        Returns:
            policy: Selected policy and associated metrics
        """
        if model_id not in self.policy_selectors:
            raise ValueError(f"Policy selector for model {model_id} not found")
            
        policy_selector = self.policy_selectors[model_id]
        return policy_selector.select_policy()
    
    def get_free_energy(self, model_id: str) -> float:
        """
        Get current free energy of the model.
        
        Args:
            model_id: Identifier of the model
            
        Returns:
            free_energy: Current free energy value
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
            
        model = self.models[model_id]
        return model.compute_free_energy()
    
    def set_preferences(self, model_id: str, 
                       preferences: Dict[str, np.ndarray]) -> None:
        """
        Set preferences (prior preferences) for a model.
        
        Args:
            model_id: Identifier of the model
            preferences: Dictionary of preference distributions
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
            
        model = self.models[model_id]
        model.set_preferences(preferences) 