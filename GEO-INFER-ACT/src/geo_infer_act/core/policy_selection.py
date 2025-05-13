"""
Policy Selection module for Active Inference.
"""
from typing import Dict, List, Optional, Any
import numpy as np
from scipy.special import softmax

from geo_infer_act.core.free_energy import ExpectedFreeEnergy


class PolicySelection:
    """
    Policy selection based on active inference principles.
    
    This class implements policy evaluation and selection using
    expected free energy minimization.
    """
    
    def __init__(self, generative_model: Any, temp: float = 1.0):
        """
        Initialize the policy selector.
        
        Args:
            generative_model: The generative model to use
            temp: Precision of policy selection (inverse temperature)
        """
        self.model = generative_model
        self.temp = temp
        
        # For policy enumeration and evaluation
        self.policies = None
        self.efe_calculator = ExpectedFreeEnergy()
        
        # Initialize policies (actions in the context of model)
        self._initialize_policies()
    
    def _initialize_policies(self) -> None:
        """
        Initialize the set of available policies.
        
        This will depend on the type of model and domain.
        """
        # Example for a simple discrete action space
        # In a real implementation, this would define meaningful policies
        # specific to the domain of application
        
        # Placeholder implementation - define 5 generic policies
        self.policies = [{"id": f"policy_{i}", "actions": [i]} for i in range(5)]
    
    def select_policy(self) -> Dict[str, Any]:
        """
        Select the optimal policy using expected free energy.
        
        Returns:
            Selected policy and associated metrics
        """
        # Get current beliefs and preferences from model
        beliefs = self.model.beliefs
        preferences = self.model.preferences
        
        # Compute expected free energy for each policy
        G = self.efe_calculator.compute(
            beliefs=beliefs,
            preferences=preferences,
            policies=self.policies,
            model=self.model
        )
        
        # Apply softmax to convert to policy probabilities
        # Lower G (expected free energy) means higher probability
        P = softmax(-self.temp * G)
        
        # Select the policy with highest probability (lowest G)
        best_idx = np.argmax(P)
        selected_policy = self.policies[best_idx]
        
        return {
            "policy": selected_policy,
            "probability": P[best_idx],
            "expected_free_energy": G[best_idx],
            "all_probabilities": P,
            "all_free_energies": G
        }
    
    def set_temperature(self, temp: float) -> None:
        """
        Set the precision of policy selection.
        
        Args:
            temp: Precision parameter (inverse temperature)
        """
        self.temp = temp
    
    def add_policy(self, policy: Dict[str, Any]) -> None:
        """
        Add a new policy to the available set.
        
        Args:
            policy: Policy definition
        """
        if self.policies is None:
            self.policies = []
        
        self.policies.append(policy)
    
    def remove_policy(self, policy_id: str) -> None:
        """
        Remove a policy from the available set.
        
        Args:
            policy_id: Identifier of the policy to remove
        """
        if self.policies is None:
            return
        
        self.policies = [p for p in self.policies if p.get("id") != policy_id] 