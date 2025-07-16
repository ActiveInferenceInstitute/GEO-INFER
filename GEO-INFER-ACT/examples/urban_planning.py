#!/usr/bin/env python
"""
Urban planning example using active inference.

This example demonstrates the use of GEO-INFER-ACT for urban planning,
where multiple stakeholders (agents) interact to allocate resources
and improve urban development outcomes.
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import Dict, List, Any
import matplotlib.cm as cm

# Add parent directory to path to import GEO-INFER-ACT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geo_infer_act.models.urban import UrbanModel


def plot_resource_distribution(urban_model: UrbanModel, 
                              step: int, 
                              save_dir: str) -> None:
    """
    Plot resource distribution across locations.
    
    Args:
        urban_model: Urban model instance
        step: Current time step
        save_dir: Directory to save plots
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get resource distribution
    resource_dist = urban_model.resource_distribution
    n_resources, n_locations = resource_dist.shape
    
    # Create x positions for grouped bar chart
    x = np.arange(n_locations)
    width = 0.8 / n_resources
    
    # Plot bars for each resource
    for i in range(n_resources):
        ax.bar(x + i*width - 0.4 + width/2, resource_dist[i], 
               width, label=f"Resource {i+1}")
    
    # Add agent locations as markers
    for i, location in enumerate(urban_model._get_current_state()["agent_locations"]):
        ax.plot(location, -0.05, marker="^", markersize=10, 
                label=f"Agent {i+1}" if i == 0 else "", color="red")
    
    ax.set_xlabel("Location")
    ax.set_ylabel("Resource Amount")
    ax.set_title(f"Resource Distribution at Step {step}")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Loc {i+1}" for i in range(n_locations)])
    ax.legend()
    
    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"resource_dist_step_{step}.png"))
    plt.close(fig)


def plot_connectivity(urban_model: UrbanModel, save_dir: str) -> None:
    """
    Plot location connectivity as a network.
    
    Args:
        urban_model: Urban model instance
        save_dir: Directory to save plots
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get connectivity matrix
    connectivity = urban_model.location_connectivity
    n_locations = connectivity.shape[0]
    
    # Create network layout (circular)
    theta = np.linspace(0, 2*np.pi, n_locations, endpoint=False)
    x = np.cos(theta)
    y = np.sin(theta)
    
    # Plot nodes
    ax.scatter(x, y, s=300, c="lightblue", edgecolors="black", zorder=2)
    
    # Add node labels
    for i in range(n_locations):
        ax.text(x[i]*1.1, y[i]*1.1, f"Loc {i+1}", 
                ha="center", va="center", fontsize=12)
    
    # Plot edges
    for i in range(n_locations):
        for j in range(i+1, n_locations):
            if connectivity[i, j] > 0.1:  # Only plot significant connections
                ax.plot([x[i], x[j]], [y[i], y[j]], 
                        linewidth=connectivity[i, j]*3, 
                        alpha=connectivity[i, j], 
                        color="gray", zorder=1)
    
    ax.set_title("Location Connectivity Network")
    ax.axis("equal")
    ax.axis("off")
    
    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "connectivity_network.png"))
    plt.close(fig)


def plot_agent_preferences(urban_model: UrbanModel, save_dir: str) -> None:
    """
    Plot agent preferences for resources.
    
    Args:
        urban_model: Urban model instance
        save_dir: Directory to save plots
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get agent preferences
    preferences = urban_model.agent_preferences
    n_agents, n_resources = preferences.shape
    
    # Create x positions for grouped bar chart
    x = np.arange(n_resources)
    width = 0.8 / n_agents
    
    # Plot bars for each agent
    for i in range(n_agents):
        ax.bar(x + i*width - 0.4 + width/2, preferences[i], 
               width, label=f"Agent {i+1}")
    
    ax.set_xlabel("Resource Type")
    ax.set_ylabel("Preference Strength")
    ax.set_title("Agent Resource Preferences")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Resource {i+1}" for i in range(n_resources)])
    ax.legend()
    
    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "agent_preferences.png"))
    plt.close(fig)


def plot_metrics(metrics_history: List[Dict[str, float]], save_dir: str) -> None:
    """
    Plot urban planning metrics over time.
    
    Args:
        metrics_history: History of metric values
        save_dir: Directory to save plots
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    # Extract metrics
    steps = np.arange(len(metrics_history))
    evenness = [m["resource_evenness"] for m in metrics_history]
    accessibility = [m["resource_accessibility"] for m in metrics_history]
    satisfaction = [m["agent_satisfaction"] for m in metrics_history]
    overall = [m["overall_score"] for m in metrics_history]
    
    # Plot metrics
    axes[0].plot(steps, evenness, marker="o", color="blue")
    axes[0].set_title("Resource Evenness")
    axes[0].set_xlabel("Time Step")
    axes[0].set_ylabel("Metric Value")
    axes[0].grid(alpha=0.3)
    
    axes[1].plot(steps, accessibility, marker="o", color="green")
    axes[1].set_title("Resource Accessibility")
    axes[1].set_xlabel("Time Step")
    axes[1].set_ylabel("Metric Value")
    axes[1].grid(alpha=0.3)
    
    axes[2].plot(steps, satisfaction, marker="o", color="purple")
    axes[2].set_title("Agent Satisfaction")
    axes[2].set_xlabel("Time Step")
    axes[2].set_ylabel("Metric Value")
    axes[2].grid(alpha=0.3)
    
    axes[3].plot(steps, overall, marker="o", color="red")
    axes[3].set_title("Overall Score")
    axes[3].set_xlabel("Time Step")
    axes[3].set_ylabel("Metric Value")
    axes[3].grid(alpha=0.3)
    
    # Save plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "planning_metrics.png"))
    plt.close(fig)


def main():
    """Run urban planning simulation."""
    print("GEO-INFER-ACT: Urban Planning Example")
    print("=" * 60)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output", "urban")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize urban model
    n_agents = 4
    n_resources = 3
    n_locations = 6
    
    print(f"Initializing urban model with:")
    print(f"  {n_agents} agents/stakeholders")
    print(f"  {n_resources} resource types")
    print(f"  {n_locations} spatial locations")
    
    urban_model = UrbanModel(
        n_agents=n_agents, 
        n_resources=n_resources,
        n_locations=n_locations
    )
    
    # Plot initial state
    print("\nPlotting initial state...")
    plot_resource_distribution(urban_model, 0, output_dir)
    plot_connectivity(urban_model, output_dir)
    plot_agent_preferences(urban_model, output_dir)
    
    # Run simulation
    n_steps = 20
    print(f"\nRunning urban simulation for {n_steps} steps...")
    
    state_history = []
    metrics_history = []
    
    for step in range(n_steps):
        # Advance simulation
        state, _ = urban_model.step()
        state_history.append(state)
        
        # Evaluate current plan
        metrics = urban_model.evaluate_plan(state_history)
        metrics_history.append(metrics)
        
        # Plot at selected steps
        if step % 5 == 0 or step == n_steps - 1:
            plot_resource_distribution(urban_model, step+1, output_dir)
            
        # Print progress
        print(f"Step {step+1}/{n_steps} - Score: {metrics['overall_score']:.4f}")
        print(f"  Resource evenness: {metrics['resource_evenness']:.4f}")
        print(f"  Resource accessibility: {metrics['resource_accessibility']:.4f}")
        print(f"  Agent satisfaction: {metrics['agent_satisfaction']:.4f}")
    
    # Plot metrics
    print("\nPlotting results...")
    plot_metrics(metrics_history, output_dir)
    
    # Print final results
    print("\nFinal urban planning metrics:")
    print(f"  Resource evenness: {metrics_history[-1]['resource_evenness']:.4f}")
    print(f"  Resource accessibility: {metrics_history[-1]['resource_accessibility']:.4f}")
    print(f"  Agent satisfaction: {metrics_history[-1]['agent_satisfaction']:.4f}")
    print(f"  Overall score: {metrics_history[-1]['overall_score']:.4f}")
    
    print(f"\nPlots saved to: {output_dir}")
    print("\nExample complete!")


if __name__ == "__main__":
    main() 