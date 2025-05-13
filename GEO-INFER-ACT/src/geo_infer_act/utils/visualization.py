"""
Visualization utilities for active inference models.
"""
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.cm as cm


def plot_belief_update(
    beliefs_before: Dict[str, np.ndarray],
    beliefs_after: Dict[str, np.ndarray],
    state_labels: Optional[List[str]] = None,
    title: str = "Belief Update",
    figsize: Tuple[int, int] = (10, 6)
) -> Figure:
    """
    Plot belief distributions before and after update.
    
    Args:
        beliefs_before: Belief distribution before update
        beliefs_after: Belief distribution after update
        state_labels: Labels for state dimensions
        title: Plot title
        figsize: Figure size
        
    Returns:
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Handle categorical and Gaussian beliefs differently
    if 'states' in beliefs_before and 'states' in beliefs_after:
        # Categorical case
        states_before = beliefs_before['states']
        states_after = beliefs_after['states']
        
        n_states = len(states_before)
        x = np.arange(n_states)
        
        # Create labels if not provided
        if state_labels is None:
            state_labels = [f"State {i}" for i in range(n_states)]
        
        # Plot bars
        width = 0.35
        ax.bar(x - width/2, states_before, width, label='Prior')
        ax.bar(x + width/2, states_after, width, label='Posterior')
        
        ax.set_xticks(x)
        ax.set_xticklabels(state_labels)
        ax.set_ylabel('Probability')
        ax.set_ylim(0, 1)
        
    elif 'mean' in beliefs_before and 'mean' in beliefs_after:
        # Gaussian case - just plot means and confidence intervals
        mean_before = beliefs_before['mean']
        mean_after = beliefs_after['mean']
        
        precision_before = beliefs_before['precision']
        precision_after = beliefs_after['precision']
        
        # Convert precision to standard deviation for plotting
        if np.isscalar(precision_before) or precision_before.ndim == 0:
            std_before = 1.0 / np.sqrt(precision_before)
        else:
            std_before = 1.0 / np.sqrt(np.diag(precision_before))
            
        if np.isscalar(precision_after) or precision_after.ndim == 0:
            std_after = 1.0 / np.sqrt(precision_after)
        else:
            std_after = 1.0 / np.sqrt(np.diag(precision_after))
        
        n_dims = len(mean_before)
        x = np.arange(n_dims)
        
        # Create labels if not provided
        if state_labels is None:
            state_labels = [f"Dim {i}" for i in range(n_dims)]
        
        # Plot means with error bars
        ax.errorbar(x - 0.1, mean_before, yerr=std_before, fmt='o', label='Prior')
        ax.errorbar(x + 0.1, mean_after, yerr=std_after, fmt='o', label='Posterior')
        
        ax.set_xticks(x)
        ax.set_xticklabels(state_labels)
        ax.set_ylabel('Value')
    
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_free_energy(
    free_energy_history: List[float],
    iterations: Optional[List[int]] = None,
    title: str = "Free Energy Minimization",
    figsize: Tuple[int, int] = (10, 6)
) -> Figure:
    """
    Plot free energy over optimization iterations.
    
    Args:
        free_energy_history: List of free energy values
        iterations: List of iteration indices
        title: Plot title
        figsize: Figure size
        
    Returns:
        Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if iterations is None:
        iterations = np.arange(len(free_energy_history))
    
    ax.plot(iterations, free_energy_history, marker='o', linestyle='-')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Free Energy')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_policies(
    policy_probabilities: np.ndarray,
    policy_labels: Optional[List[str]] = None,
    expected_free_energies: Optional[np.ndarray] = None,
    title: str = "Policy Evaluation",
    figsize: Tuple[int, int] = (12, 8)
) -> Figure:
    """
    Plot policy probabilities and expected free energies.
    
    Args:
        policy_probabilities: Probabilities for each policy
        policy_labels: Labels for policies
        expected_free_energies: Expected free energy values
        title: Plot title
        figsize: Figure size
        
    Returns:
        Figure object
    """
    n_policies = len(policy_probabilities)
    
    if policy_labels is None:
        policy_labels = [f"Policy {i}" for i in range(n_policies)]
    
    if expected_free_energies is not None:
        # Create two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
        
        # Plot probabilities
        bars1 = ax1.bar(policy_labels, policy_probabilities)
        ax1.set_ylabel('Probability')
        ax1.set_ylim(0, 1)
        ax1.set_title(f"{title} - Probabilities")
        
        # Plot expected free energies
        bars2 = ax2.bar(policy_labels, expected_free_energies)
        ax2.set_ylabel('Expected Free Energy')
        ax2.set_title("Expected Free Energy (lower is better)")
        
        # Highlight the best policy
        best_idx = np.argmax(policy_probabilities)
        bars1[best_idx].set_color('green')
        bars2[best_idx].set_color('green')
        
    else:
        # Just plot probabilities
        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.bar(policy_labels, policy_probabilities)
        ax.set_ylabel('Probability')
        ax.set_ylim(0, 1)
        ax.set_title(title)
        
        # Highlight the best policy
        best_idx = np.argmax(policy_probabilities)
        bars[best_idx].set_color('green')
    
    plt.tight_layout()
    return fig 