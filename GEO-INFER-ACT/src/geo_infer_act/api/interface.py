"""
Active Inference API Interface for GEO-INFER-ACT.

This module provides a high-level interface for creating and managing
active inference models, including belief updating and policy selection.
"""
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path

from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.policy_selection import PolicySelector
from geo_infer_act.core.variational_inference import VariationalInference
from geo_infer_act.utils.config import load_config
from geo_infer_act.utils.math import softmax, normalize_distribution

logger = logging.getLogger(__name__)


class ActiveInferenceInterface:
    """
    High-level interface for active inference models.
    
    This class provides a simplified API for creating, configuring,
    and running active inference models without requiring detailed
    knowledge of the underlying mathematical machinery.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the active inference interface.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path) if config_path else {}
        self.models: Dict[str, Any] = {}
        
        logger.info("ActiveInferenceInterface initialized")
    
    def create_model(self, 
                    model_id: str, 
                    model_type: str, 
                    parameters: Dict[str, Any]) -> None:
        """
        Create a new active inference model.
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model ('categorical', 'gaussian', 'hierarchical_gaussian')
            parameters: Model configuration parameters
        """
        from geo_infer_act.core.active_inference import ActiveInferenceModel
        from geo_infer_act.core.generative_model import GenerativeModel
        
        # Enhanced parameters with more dynamic defaults
        enhanced_params = {
            'learning_rate': 0.1,
            'temporal_precision': 1.0,
            'enable_learning': True,
            'enable_adaptation': True,
            **parameters
        }
        
        # Create Core Active Inference Model
        agent = ActiveInferenceModel(model_type=model_type, **enhanced_params)
        
        # Create Generative Model
        gen_model = GenerativeModel(
            model_type=model_type,
            parameters=enhanced_params,
            model_id=model_id
        )
        
        # Link them
        agent.set_generative_model(gen_model)
        
        self.models[model_id] = agent
        logger.info(f"Created {model_type} model: {model_id}")
    
    def update_beliefs(self, 
                      model_id: str, 
                      observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Update model beliefs based on observations.
        
        Args:
            model_id: Model identifier
            observations: Observed data
            
        Returns:
            Updated beliefs
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        agent = self.models[model_id]
        obs_data = observations.get('observations')
        
        # Handle dictionary observations if provided directly or nested
        if obs_data is None:
             # Try to process the dict as the observation itself if keys match expectations
             if agent.model_type == 'gaussian':
                  pass # Assuming complex handling handled by agent
             else:
                  # For categorical, we usually expect 'observations' key in input
                  # If not present, warn or fail
                  logger.warning(f"No 'observations' key in input for model {model_id}. Using default.")
                  obs_data = np.zeros(agent.generative_model.obs_dim)

        # Call the core agent perception
        updated_beliefs = agent.perceive(obs_data)
        
        # Return in expected format
        if agent.model_type == 'categorical':
             if isinstance(updated_beliefs, dict) and any(k.startswith('level_') for k in updated_beliefs.keys()):
                 return updated_beliefs
             if isinstance(updated_beliefs, dict) and 'states' in updated_beliefs:
                 return updated_beliefs
             return {'states': updated_beliefs}
        
        return updated_beliefs
    
    def select_policy(self, model_id: str) -> Dict[str, Any]:
        """
        Select optimal policy based on current beliefs.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Selected policy information
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        agent = self.models[model_id]
        
        # Use core agent action selection
        action = agent.act()
        
        # Wrap result to match expected interface format (legacy support for examples)
        # The examples expect a dict with 'policy': {'id': int...}
        
        # Create a dummy policy object that wraps the selected action
        # This preserves compatibility with urban_planning.py
        try:
            action_idx = int(action) if isinstance(action, (int, np.integer, float, np.floating)) else 0
        except (TypeError, ValueError):
            action_idx = 0
            
        # Get probability of selected action/policy if available
        probability = 1.0
        all_probs = [1.0]
        if hasattr(agent, 'q_pi') and agent.q_pi is not None:
             if len(agent.q_pi) > action_idx:
                 probability = float(agent.q_pi[action_idx])
             all_probs = agent.q_pi.tolist() if hasattr(agent.q_pi, 'tolist') else list(agent.q_pi)

        return {
            'policy': {
                'id': action_idx,
                'action': action,
                'expected_free_energy': agent.compute_free_energy()
            },
            'selected_action': action,
            'probability': probability,
            'all_probabilities': all_probs
        }
    
    def set_preferences(self, model_id: str, preferences: Dict[str, Any]) -> None:
        """
        Set prior preferences for the model.
        
        Args:
            model_id: Model identifier
            preferences: Preference specifications
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        agent = self.models[model_id]
        agent.update_preferences(preferences)
        logger.info(f"Set preferences for model {model_id}")
    
    def get_free_energy(self, model_id: str) -> float:
        """Calculate free energy for the current model state."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
            
        return self.models[model_id].compute_free_energy() 