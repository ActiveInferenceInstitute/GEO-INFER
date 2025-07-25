"""
Active Inference model implementation.

This module contains the main ActiveInferenceModel class that orchestrates
all components of active inference including belief updating, policy selection,
and free energy minimization.
"""
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.policy_selection import PolicySelector
from geo_infer_act.core.belief_updating import BayesianBeliefUpdate
from geo_infer_act.utils.math import softmax, normalize_distribution

logger = logging.getLogger(__name__)


class ActiveInferenceModel:
    """
    Main class for active inference agents with support for nested models.
    """
    
    def __init__(self, model_type: str = "categorical", **kwargs):
        """
        Initialize an Active Inference model.
        
        Args:
            model_type: Type of underlying generative model
            **kwargs: Additional parameters
        """
        self.model_type = model_type
        self.parameters = kwargs
        
        # Initialize core components
        self.generative_model = None
        self.free_energy_calculator = FreeEnergyCalculator()
        self.policy_selector = PolicySelector()
        self.belief_updater = BayesianBeliefUpdate()
        
        # State variables
        self.current_beliefs = None
        self.current_observations = None
        self.current_actions = None
        self.history = []
        
        logger.info(f"Initialized ActiveInferenceModel with type: {model_type}")
    
    def set_generative_model(self, model: GenerativeModel):
        """Set the generative model for this active inference agent."""
        self.generative_model = model
        if model.state_dim > 0:
            self.current_beliefs = normalize_distribution(
                np.ones(model.state_dim) / model.state_dim
            )
    
    def perceive(self, observation: np.ndarray) -> np.ndarray:
        """
        Update beliefs based on new observation.
        
        Args:
            observation: New sensory observation
            
        Returns:
            Updated beliefs (posterior distribution)
        """
        if self.generative_model is None:
            raise ValueError("Generative model must be set before perception")
        
        # Store observation
        self.current_observations = observation
        
        # Update beliefs using Bayesian inference
        if self.current_beliefs is not None:
            if self.model_type == 'categorical':
                if self.generative_model.observation_model.shape[1] != len(self.current_beliefs):
                    self.generative_model.observation_model = np.ones((self.generative_model.obs_dim, len(self.current_beliefs))) / self.generative_model.obs_dim
                updated_beliefs = self.belief_updater.update_categorical(
                    self.current_beliefs,
                    observation,
                    self.generative_model.observation_model
                )
            else:
                # Add gaussian case
                updated_beliefs = self.current_beliefs
            self.current_beliefs = updated_beliefs
        
        return self.current_beliefs
    
    def act(self, available_actions: Optional[List[Any]] = None) -> Any:
        """
        Select action based on expected free energy minimization.
        
        Args:
            available_actions: List of available actions
            
        Returns:
            Selected action
        """
        if self.generative_model is None:
            raise ValueError("Generative model must be set before action selection")
        
        # Generate default actions if none provided
        if available_actions is None:
            available_actions = list(range(getattr(self.generative_model, 'action_dim', 3)))
        
        # Select action using policy selector
        selected_action = self.policy_selector.select_action(
            self.current_beliefs,
            available_actions,
            self.generative_model
        )
        
        self.current_actions = selected_action
        return selected_action
    
    def step(self, observation: np.ndarray, available_actions: Optional[List[Any]] = None) -> Tuple[np.ndarray, Any]:
        """
        Perform one complete active inference step.
        
        Args:
            observation: Current observation
            available_actions: Available actions
            
        Returns:
            Tuple of (updated_beliefs, selected_action)
        """
        # Perception: update beliefs
        beliefs = self.perceive(observation)
        
        # Action: select policy
        action = self.act(available_actions)
        
        # Store step in history
        step_data = {
            'observation': observation.copy() if hasattr(observation, 'copy') else observation,
            'beliefs': beliefs.copy() if hasattr(beliefs, 'copy') else beliefs,
            'action': action,
            'free_energy': self.compute_free_energy() if beliefs is not None else np.inf
        }
        self.history.append(step_data)
        
        return beliefs, action
    
    def compute_free_energy(self) -> float:
        """Compute current variational free energy."""
        if self.current_beliefs is None or self.current_observations is None:
            return np.inf
        preferences = np.ones_like(self.current_beliefs) / len(self.current_beliefs)
        return self.free_energy_calculator.compute_categorical_free_energy(
            self.current_beliefs,
            self.current_observations,
            preferences
        )
    
    def reset(self):
        """Reset the model to initial state."""
        if self.generative_model and hasattr(self.generative_model, 'state_dim'):
            self.current_beliefs = normalize_distribution(
                np.ones(self.generative_model.state_dim) / self.generative_model.state_dim
            )
        else:
            self.current_beliefs = None
        
        self.current_observations = None
        self.current_actions = None
        self.history = []
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the complete history of interactions."""
        return self.history.copy()
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current model state."""
        return {
            'beliefs': self.current_beliefs,
            'observations': self.current_observations, 
            'actions': self.current_actions,
            'free_energy': self.compute_free_energy(),
            'model_type': self.model_type
        } 

    def apply_to_h3(self, h3_obs: Dict[str, np.ndarray]):
        if self.generative_model is None:
            raise ValueError('Set generative model first')
        return self.generative_model.update_h3_beliefs(h3_obs) 

    def infer_over_h3_grid(self, h3_grid: Dict[str, Any]):
        results = {}
        for cell in h3_grid:
            obs = h3_grid[cell]
            beliefs, action = self.step(obs)
            results[cell] = {'beliefs': beliefs, 'action': action, 'free_energy': self.compute_free_energy(), 'precision': self.current_beliefs.get('precision', 1.0) if isinstance(self.current_beliefs, dict) else 1.0}
        return results 