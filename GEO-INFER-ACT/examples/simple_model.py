#!/usr/bin/env python
"""
Simple active inference model example for GEO-INFER-ACT.

This example demonstrates how to create a simple active inference model
for a categorical state and observation space, update beliefs based on
observations, and select policies.
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add parent directory to path to import GEO-INFER-ACT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.geo_infer_act.api.interface import ActiveInferenceInterface
from src.geo_infer_act.utils.visualization import plot_belief_update, plot_policies


def main():
    """Run a simple active inference model example."""
    print("GEO-INFER-ACT: Simple Active Inference Model Example")
    print("=" * 60)
    
    # 1. Initialize the active inference interface
    config_path = os.path.join(os.path.dirname(__file__), '../config/example.yaml')
    ai_interface = ActiveInferenceInterface(config_path)
    
    # 2. Create a categorical model
    model_id = "simple_model"
    model_type = "categorical"
    
    # Model parameters (simple 3-state, 2-observation model)
    parameters = {
        "state_dim": 3,  # Three possible states
        "obs_dim": 2,    # Two possible observations
        "prior_precision": 1.0
    }
    
    ai_interface.create_model(model_id, model_type, parameters)
    print(f"Created model: {model_id} (type: {model_type})")
    
    # 3. Set prior preferences
    # For this example, we prefer the first observation
    preferences = {
        "observations": np.array([0.8, 0.2])
    }
    ai_interface.set_preferences(model_id, preferences)
    print("Set prior preferences")
    
    # 4. Get initial beliefs
    initial_beliefs = ai_interface.models[model_id].beliefs
    print("\nInitial beliefs:")
    print(f"States: {initial_beliefs['states']}")
    
    # 5. Update beliefs with an observation
    # Observe the first observation type
    observation = {
        "observations": np.array([1, 0])
    }
    
    updated_beliefs = ai_interface.update_beliefs(model_id, observation)
    print("\nUpdated beliefs after observation [1, 0]:")
    print(f"States: {updated_beliefs['states']}")
    
    # 6. Visualize belief update
    state_labels = ["State A", "State B", "State C"]
    fig = plot_belief_update(
        initial_beliefs,
        updated_beliefs,
        state_labels=state_labels
    )
    
    # Save plot to file
    plot_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(plot_dir, exist_ok=True)
    fig.savefig(os.path.join(plot_dir, 'belief_update.png'))
    plt.close(fig)
    
    # 7. Select policy based on updated beliefs
    policy_result = ai_interface.select_policy(model_id)
    
    print("\nSelected policy:")
    print(f"Policy: {policy_result['policy']}")
    print(f"Probability: {policy_result['probability']:.4f}")
    print(f"Expected Free Energy: {policy_result['expected_free_energy']:.4f}")
    
    # 8. Visualize policy selection
    policy_probs = policy_result['all_probabilities']
    policy_efes = policy_result['all_free_energies']
    
    policy_labels = [f"Policy {i}" for i in range(len(policy_probs))]
    
    fig2 = plot_policies(
        policy_probs,
        policy_labels=policy_labels,
        expected_free_energies=policy_efes
    )
    
    # Save plot to file
    fig2.savefig(os.path.join(plot_dir, 'policy_selection.png'))
    plt.close(fig2)
    
    print("\nPlots saved to:", plot_dir)
    print("\nExample complete!")


if __name__ == "__main__":
    main() 