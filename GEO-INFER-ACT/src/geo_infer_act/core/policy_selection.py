"""
Policy selection for active inference models.

This module implements policy selection mechanisms based on expected
free energy minimization and other active inference principles.
"""
import numpy as np
from typing import Dict, List, Any, Optional
import logging

from geo_infer_act.utils.math import softmax

logger = logging.getLogger(__name__)


class PolicySelector:
    """
    Policy selector for active inference models.
    
    Selects actions/policies based on expected free energy minimization,
    balancing exploration (epistemic value) and exploitation (pragmatic value).
    """
    
    def __init__(self, temperature: float = 1.0):
        """
        Initialize the policy selector.
        
        Args:
            temperature: Temperature parameter for policy selection
        """
        self.temperature = temperature
    
    def select_policy(self, 
                     beliefs: np.ndarray,
                     policies: List[Dict[str, Any]],
                     preferences: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Select a policy based on expected free energy.
        
        Args:
            beliefs: Current belief distribution
            policies: List of available policies
            preferences: Prior preferences
            
        Returns:
            Selected policy and associated information
        """
        if not policies:
            # Create default policies if none provided
            policies = self._create_default_policies(len(beliefs))
        
        # Compute expected free energy for each policy
        expected_free_energies = []
        
        for policy in policies:
            efe = self.compute_expected_free_energy(
                beliefs, policy, preferences
            )
            expected_free_energies.append(efe)
        
        expected_free_energies = np.array(expected_free_energies)
        
        # Convert to policy probabilities (lower EFE = higher probability)
        policy_probs = softmax(-expected_free_energies / self.temperature)
        
        # Select policy
        selected_idx = np.random.choice(len(policies), p=policy_probs)
        selected_policy = policies[selected_idx]
        
        return {
            'policy': selected_policy,
            'probability': policy_probs[selected_idx],
            'expected_free_energy': expected_free_energies[selected_idx],
            'all_probabilities': policy_probs,
            'all_free_energies': expected_free_energies
        }
    
    def _create_default_policies(self, n_states: int) -> List[Dict[str, Any]]:
        """
        Create default policies for exploration.
        
        Args:
            n_states: Number of states in the model
            
        Returns:
            List of default policies
        """
        policies = []
        
        # Create diverse policies with different characteristics
        for i in range(5):  # Create 5 default policies
            policy = {
                'id': i,
                'exploration_bonus': np.random.uniform(0.0, 0.5),
                'temporal_discount': np.random.uniform(0.8, 1.0),
                'risk_preference': np.random.uniform(-0.2, 0.2),
                'type': 'exploration' if i < 3 else 'exploitation'
            }
            policies.append(policy)
        
        return policies
    
    def compute_expected_free_energy(self,
                                     beliefs: np.ndarray,
                                     policy: Dict[str, Any],
                                     preferences: Optional[np.ndarray] = None) -> float:
        """
        Compute expected free energy for a policy.
        
        Args:
            beliefs: Current beliefs
            policy: Policy to evaluate
            preferences: Prior preferences
            
        Returns:
            Expected free energy value
        """
        if isinstance(policy, int):
            policy = {'action': policy, 'exploration_bonus': 0.1}
        # Epistemic value (information gain / exploration)
        entropy = -np.sum(beliefs * np.log(beliefs + 1e-8))
        epistemic_value = entropy
        
        # Pragmatic value (preference satisfaction / exploitation)
        pragmatic_value = np.dot(beliefs, preferences) if preferences is not None else 0.0
        
        # Policy-specific modulation
        exploration_bonus = policy.get('exploration_bonus', 0.1)
        risk_preference = policy.get('risk_preference', 0.0)
        temporal_discount = policy.get('temporal_discount', 0.9)
        
        # Risk term (uncertainty aversion/seeking)
        risk_term = risk_preference * np.var(beliefs)
        
        # Expected free energy combines pragmatic and epistemic terms
        expected_free_energy = (
            temporal_discount * pragmatic_value -
            exploration_bonus * epistemic_value +
            risk_term
        )
        
        return float(expected_free_energy)
    
    def compute_policy_precision(self, 
                               expected_free_energies: np.ndarray,
                               baseline_precision: float = 1.0) -> float:
        """
        Compute precision parameter for policy distribution.
        
        Args:
            expected_free_energies: Array of EFE values
            baseline_precision: Baseline precision value
            
        Returns:
            Computed precision parameter
        """
        # Adaptive precision based on policy differentiation
        efe_range = np.max(expected_free_energies) - np.min(expected_free_energies)
        
        if efe_range > 1e-6:
            # Higher precision when policies are well-differentiated
            precision = baseline_precision * (1.0 + efe_range)
        else:
            # Lower precision when policies are similar
            precision = baseline_precision * 0.5
        
        return precision
    
    def evaluate_policy_set(self,
                           beliefs: np.ndarray,
                           policies: List[Dict[str, Any]],
                           preferences: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Evaluate a set of policies without selection.
        
        Args:
            beliefs: Current beliefs
            policies: List of policies to evaluate
            preferences: Prior preferences
            
        Returns:
            Policy evaluation results
        """
        if not policies:
            policies = self._create_default_policies(len(beliefs))
        
        # Compute metrics for all policies
        expected_free_energies = []
        epistemic_values = []
        pragmatic_values = []
        
        for policy in policies:
            efe = self.compute_expected_free_energy(beliefs, policy, preferences)
            expected_free_energies.append(efe)
            
            # Decompose into epistemic and pragmatic components
            entropy = -np.sum(beliefs * np.log(beliefs + 1e-8))
            epistemic_values.append(entropy)
            
            if preferences is not None:
                pragmatic = -np.sum(beliefs * np.log(preferences + 1e-8))
            else:
                uniform_prefs = np.ones_like(beliefs) / len(beliefs)
                pragmatic = -np.sum(beliefs * np.log(uniform_prefs + 1e-8))
            pragmatic_values.append(pragmatic)
        
        expected_free_energies = np.array(expected_free_energies)
        epistemic_values = np.array(epistemic_values)
        pragmatic_values = np.array(pragmatic_values)
        
        # Compute policy probabilities
        policy_probs = softmax(-expected_free_energies / self.temperature)
        
        return {
            'policies': policies,
            'expected_free_energies': expected_free_energies,
            'epistemic_values': epistemic_values,
            'pragmatic_values': pragmatic_values,
            'probabilities': policy_probs,
            'best_policy_idx': np.argmin(expected_free_energies),
            'diversity': np.std(expected_free_energies)
        }
    
    def select_action(self, beliefs: np.ndarray, available_actions: List[Any], 
                     generative_model: Any = None) -> Any:
        """
        Select a single action based on current beliefs.
        
        Args:
            beliefs: Current belief state
            available_actions: List of available actions
            generative_model: Optional generative model for context
            
        Returns:
            Selected action
        """
        if not available_actions:
            return None
        
        # For simple case, just select randomly from available actions
        # In a more sophisticated implementation, this would use the
        # policy selection mechanism
        if len(available_actions) == 1:
            return available_actions[0]
        
        # Use belief entropy to guide exploration vs exploitation
        entropy = -np.sum(beliefs * np.log(beliefs + 1e-8))
        
        if entropy > 1.0:  # High uncertainty - explore
            # More random selection
            probs = np.ones(len(available_actions)) / len(available_actions)
        else:  # Low uncertainty - exploit
            # Bias towards "better" actions (simple heuristic)
            probs = softmax(np.arange(len(available_actions)) / self.temperature)
        
        selected_idx = np.random.choice(len(available_actions), p=probs)
        return available_actions[selected_idx] 