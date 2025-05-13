#!/usr/bin/env python
"""
Ecological niche modeling using active inference.

This example demonstrates how to use GEO-INFER-ACT for ecological niche
modeling, where species adapt to environmental conditions through active
inference processes.
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import Dict, List, Tuple

# Add parent directory to path to import GEO-INFER-ACT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.geo_infer_act.api.interface import ActiveInferenceInterface
from src.geo_infer_act.utils.visualization import plot_belief_update, plot_policies, plot_free_energy


class EcologicalNicheModel:
    """
    A model of ecological niche dynamics using active inference.
    
    This model represents how a species adapts to and modifies its
    environment based on active inference principles.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the ecological niche model.
        
        Args:
            config_path: Path to configuration file
        """
        self.ai_interface = ActiveInferenceInterface(config_path)
        self.model_id = "eco_niche_model"
        self.free_energy_history = []
        
        # Environment states (simplified for demonstration)
        # States represent: temperature, precipitation, resource availability, etc.
        self.n_env_states = 4
        
        # Species actions/adaptations
        # Actions represent: migration, phenotypic changes, resource usage patterns
        self.n_actions = 5
        
        # Initialize model
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the active inference model for ecological niche."""
        parameters = {
            "state_dim": self.n_env_states,
            "obs_dim": 3,  # Simplified observations of environment
            "prior_precision": 2.0  # Higher precision for ecological models
        }
        
        self.ai_interface.create_model(
            model_id=self.model_id,
            model_type="categorical",
            parameters=parameters
        )
        
        # Set preferences (species' preferred environmental conditions)
        # In this example, the species prefers moderate temperature and
        # high resource availability
        preferences = {
            "observations": np.array([0.2, 0.6, 0.2])  # Prefer middle observation
        }
        
        self.ai_interface.set_preferences(self.model_id, preferences)
        
    def observe_environment(self, observation: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Update beliefs based on environmental observations.
        
        Args:
            observation: Observed environmental conditions
            
        Returns:
            Updated beliefs about the environment
        """
        # Format observation for the model
        formatted_obs = {"observations": observation}
        
        # Update beliefs
        updated_beliefs = self.ai_interface.update_beliefs(
            self.model_id, formatted_obs
        )
        
        # Track free energy
        free_energy = self.ai_interface.get_free_energy(self.model_id)
        self.free_energy_history.append(free_energy)
        
        return updated_beliefs
        
    def select_adaptation(self) -> Dict[str, any]:
        """
        Select adaptation strategy based on current beliefs.
        
        Returns:
            Selected adaptation strategy
        """
        return self.ai_interface.select_policy(self.model_id)
    
    def run_simulation(self, n_timesteps: int = 10) -> Tuple[List[Dict], List[Dict]]:
        """
        Run a simulation of niche adaptation over time.
        
        Args:
            n_timesteps: Number of time steps to simulate
            
        Returns:
            Tuple of (belief_history, adaptation_history)
        """
        belief_history = []
        adaptation_history = []
        
        # Simplified environmental dynamics:
        # We'll generate observations that gradually shift to represent
        # environmental change (e.g., climate change)
        
        for t in range(n_timesteps):
            # Generate observation that changes over time
            # Initial preference for observation pattern [0.2, 0.6, 0.2]
            # Gradually shifts to [0.6, 0.2, 0.2] (representing environmental change)
            alpha = t / (n_timesteps - 1) if n_timesteps > 1 else 0
            probs = (1 - alpha) * np.array([0.2, 0.6, 0.2]) + alpha * np.array([0.6, 0.2, 0.2])
            
            # Generate concrete observation from probability distribution
            observation = np.random.multinomial(1, probs)
            
            # Update beliefs with observation
            beliefs = self.observe_environment(observation)
            belief_history.append(beliefs.copy())
            
            # Select adaptation
            adaptation = self.select_adaptation()
            adaptation_history.append(adaptation.copy())
            
            # Print progress
            print(f"Time step {t+1}/{n_timesteps}:")
            print(f"  Observation: {observation}")
            print(f"  Beliefs: {beliefs['states']}")
            print(f"  Selected adaptation: {adaptation['policy']['id']}")
            print()
            
        return belief_history, adaptation_history
    
    def visualize_results(self, belief_history, adaptation_history):
        """
        Visualize simulation results.
        
        Args:
            belief_history: History of beliefs
            adaptation_history: History of adaptations
        """
        # Create output directory
        plot_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(plot_dir, exist_ok=True)
        
        # Plot belief evolution
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for i in range(self.n_env_states):
            beliefs = [b['states'][i] for b in belief_history]
            ax.plot(beliefs, label=f"State {i+1}")
            
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Belief Probability')
        ax.set_title('Evolution of Beliefs About Environmental States')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        fig.savefig(os.path.join(plot_dir, 'eco_belief_evolution.png'))
        plt.close(fig)
        
        # Plot adaptation probabilities
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract policy probabilities over time for each policy
        policy_probs = []
        for t in range(len(adaptation_history)):
            probs = adaptation_history[t]['all_probabilities']
            if t == 0:
                # Initialize with zeros
                policy_probs = [[] for _ in range(len(probs))]
            
            for i, p in enumerate(probs):
                policy_probs[i].append(p)
        
        for i, probs in enumerate(policy_probs):
            ax.plot(probs, label=f"Policy {i}")
            
        ax.set_xlabel('Time Step')
        ax.set_ylabel('Policy Probability')
        ax.set_title('Adaptation Strategy Selection Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        fig.savefig(os.path.join(plot_dir, 'eco_adaptation_evolution.png'))
        plt.close(fig)
        
        # Plot free energy history
        fig = plot_free_energy(
            self.free_energy_history,
            title="Free Energy Minimization During Ecological Adaptation"
        )
        fig.savefig(os.path.join(plot_dir, 'eco_free_energy.png'))
        plt.close(fig)
        
        print(f"Results visualized and saved to: {plot_dir}")


def main():
    """Run an ecological niche modeling example."""
    print("GEO-INFER-ACT: Ecological Niche Modeling Example")
    print("=" * 60)
    
    # Initialize model
    config_path = os.path.join(os.path.dirname(__file__), '../config/example.yaml')
    eco_model = EcologicalNicheModel(config_path)
    
    # Run simulation
    print("Running ecological niche simulation...")
    belief_history, adaptation_history = eco_model.run_simulation(n_timesteps=20)
    
    # Visualize results
    print("Visualizing results...")
    eco_model.visualize_results(belief_history, adaptation_history)
    
    print("\nExample complete!")


if __name__ == "__main__":
    main() 