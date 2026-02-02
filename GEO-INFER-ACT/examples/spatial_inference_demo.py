#!/usr/bin/env python
"""
Spatial Active Inference Demo for GEO-INFER-ACT.

This self-contained demo demonstrates:
1. Creating a spatial active inference agent on H3 cells
2. Running a multi-step inference loop
3. Generating visualizations and logs
4. Exporting results for analysis

VFE/EFE Implementation:
    - VFE: Computed in `SpatialActiveInferenceAgent._compute_spatial_free_energy()` (line 248)
    - EFE: Computed in `SpatialActiveInferenceAgent.spatial_action()` via policy selection

Documentation:
    - Free Energy Principle: ../docs/free_energy_principle.md
    - Mathematical Framework: ../docs/mathematical_framework.md
    - Active Inference Overview: ../docs/active_inference_overview.md

Usage:
    python examples/spatial_inference_demo.py
"""

import sys
import os
import numpy as np
import logging
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geo_infer_act.core.spatial_agent import SpatialActiveInferenceAgent
from geo_infer_act.utils.spatial_diagnostics import SpatialDiagnostics

# Visualization imports (optional)
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def setup_logging(output_dir: Path) -> logging.Logger:
    """Configure logging for the demo."""
    log_file = output_dir / "simulation.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("SpatialDemo")


def create_output_directory() -> Path:
    """Create timestamped output directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    repo_root = Path(__file__).parent.parent.parent
    output_dir = repo_root / "output" / f"spatial_inference_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_synthetic_observations(
    cells: list,
    state_dim: int,
    step: int,
    pattern: str = "wave"
) -> dict:
    """
    Generate synthetic observations with spatial structure.
    
    Args:
        cells: List of cell IDs
        state_dim: Dimension of observations
        step: Current time step
        pattern: Type of pattern ("wave", "random", "clustered")
        
    Returns:
        Dict mapping cell IDs to observation vectors
    """
    observations = {}
    n_cells = len(cells)
    
    for i, cell_id in enumerate(cells):
        if pattern == "wave":
            # Wave pattern: observations depend on position and time
            phase = 2 * np.pi * i / n_cells + 0.3 * step
            base = 0.5 + 0.4 * np.sin(phase)
            obs = np.zeros(state_dim)
            obs[int(base * (state_dim - 1))] = 1.0
            # Add noise
            obs += np.random.normal(0, 0.1, state_dim)
            obs = np.clip(obs, 0, 1)
            obs = obs / obs.sum()  # Normalize
        elif pattern == "clustered":
            # Clustered: cells near each other have similar observations
            cluster = i // max(1, n_cells // 3)
            obs = np.zeros(state_dim)
            obs[cluster % state_dim] = 0.8
            obs += np.random.dirichlet(np.ones(state_dim) * 0.1)
            obs = obs / obs.sum()
        else:  # random
            obs = np.random.dirichlet(np.ones(state_dim))
        
        observations[cell_id] = obs
    
    return observations


def plot_free_energy_evolution(fe_history: list, output_dir: Path) -> None:
    """Plot free energy over time."""
    if not HAS_MATPLOTLIB or not fe_history:
        return
    
    plt.figure(figsize=(10, 6))
    plt.plot(fe_history, 'b-', linewidth=2, label='Free Energy')
    
    # Add trend line
    x = np.arange(len(fe_history))
    slope, intercept = np.polyfit(x, fe_history, 1)
    trend = slope * x + intercept
    plt.plot(x, trend, 'r--', alpha=0.7, label=f'Trend (slope={slope:.4f})')
    
    plt.xlabel('Step', fontsize=12)
    plt.ylabel('Free Energy', fontsize=12)
    plt.title('Free Energy Evolution', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'free_energy_evolution.png', dpi=150)
    plt.close()


def plot_belief_heatmap(beliefs: np.ndarray, cells: list, output_dir: Path) -> None:
    """Plot belief distribution as heatmap."""
    if not HAS_MATPLOTLIB:
        return
    
    plt.figure(figsize=(12, 6))
    plt.imshow(beliefs.T, aspect='auto', cmap='viridis')
    plt.colorbar(label='Belief Probability')
    plt.xlabel('Cell Index', fontsize=12)
    plt.ylabel('State', fontsize=12)
    plt.title('Spatial Belief Distribution', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_dir / 'spatial_beliefs.png', dpi=150)
    plt.close()


def plot_action_distribution(action_history: list, output_dir: Path) -> None:
    """Plot action selection distribution."""
    if not HAS_MATPLOTLIB or not action_history:
        return
    
    action_names = ['stay', 'north', 'south', 'east', 'west']
    action_counts = {name: 0 for name in action_names}
    
    for entry in action_history:
        name = entry.get('action_name', 'unknown')
        if name in action_counts:
            action_counts[name] += 1
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(action_counts.keys(), action_counts.values(), color='steelblue')
    plt.xlabel('Action', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Action Selection Distribution', fontsize=14)
    
    # Add value labels
    for bar, count in zip(bars, action_counts.values()):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 str(count), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'action_distribution.png', dpi=150)
    plt.close()


def run_simulation():
    """Run the spatial active inference simulation."""
    # Setup
    output_dir = create_output_directory()
    logger = setup_logging(output_dir)
    
    logger.info("=" * 60)
    logger.info("Spatial Active Inference Demo")
    logger.info("=" * 60)
    logger.info(f"Output directory: {output_dir}")
    
    # Configuration
    config = {
        "h3_resolution": 9,
        "n_cells": 7,  # Hexagon with ring
        "state_dim": 4,
        "obs_dim": 4,
        "diffusion_rate": 0.15,
        "precision_scale": 1.2,
        "n_steps": 20,
        "observation_pattern": "wave"
    }
    
    logger.info(f"Configuration: {config}")
    
    # Generate initial cells (synthetic for demo without h3)
    cells = [f"cell_{i}" for i in range(config["n_cells"])]
    
    # Create spatial agent
    logger.info("Creating Spatial Active Inference Agent...")
    agent = SpatialActiveInferenceAgent(
        h3_resolution=config["h3_resolution"],
        initial_cells=cells,
        state_dim=config["state_dim"],
        obs_dim=config["obs_dim"],
        diffusion_rate=config["diffusion_rate"],
        precision_scale=config["precision_scale"],
        enable_logging=True
    )
    
    logger.info(f"Agent initialized with {len(agent.cells)} cells")
    
    # Create diagnostics tracker
    diagnostics = SpatialDiagnostics(output_dir=str(output_dir))
    
    # Set preferences (prefer state 0)
    preferences = {cell: np.array([0.6, 0.2, 0.1, 0.1]) for cell in cells}
    agent.set_preferences(preferences)
    
    # Run simulation
    logger.info(f"Running simulation for {config['n_steps']} steps...")
    logger.info("-" * 40)
    
    for step in range(config["n_steps"]):
        # Generate observations
        observations = generate_synthetic_observations(
            cells=cells,
            state_dim=config["state_dim"],
            step=step,
            pattern=config["observation_pattern"]
        )
        
        # Run perception-action cycle
        result = agent.step(observations, propagate_beliefs=True)
        
        # Record diagnostics
        diagnostics.record_step(
            step=step,
            beliefs=agent.beliefs,
            free_energy=result['free_energy'],
            action=result['action']
        )
        
        # Log progress
        if step % 5 == 0 or step == config["n_steps"] - 1:
            logger.info(
                f"Step {step+1}/{config['n_steps']}: "
                f"FE={result['free_energy']:.4f}, "
                f"Action={result['action']['action_name']}, "
                f"Conf={result['action']['confidence']:.3f}"
            )
    
    logger.info("-" * 40)
    logger.info("Simulation complete!")
    
    # Get final diagnostics
    final_diag = agent.get_diagnostics()
    logger.info(f"Final diagnostics:")
    logger.info(f"  Mean entropy: {final_diag['belief_stats']['mean_entropy']:.4f}")
    logger.info(f"  FE trend: {final_diag['free_energy']['trend']}")
    logger.info(f"  Spatial coherence: {final_diag['spatial_coherence']['mean']:.4f}")
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    plot_free_energy_evolution(agent.free_energy_history, output_dir)
    plot_belief_heatmap(agent.beliefs, cells, output_dir)
    plot_action_distribution(agent.action_history, output_dir)
    
    # Export results
    logger.info("Exporting results...")
    agent.export_results(str(output_dir / "simulation_results.json"))
    diagnostics.export_to_json("diagnostics.json")
    diagnostics.export_to_csv("step_metrics.csv")
    
    # Summary
    logger.info("=" * 60)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total steps: {agent.step_count}")
    logger.info(f"Initial FE: {agent.free_energy_history[0]:.4f}")
    logger.info(f"Final FE: {agent.free_energy_history[-1]:.4f}")
    logger.info(f"FE change: {agent.free_energy_history[-1] - agent.free_energy_history[0]:.4f}")
    logger.info(f"Action distribution: {final_diag['action_distribution']}")
    logger.info(f"\nOutput files saved to: {output_dir}")
    
    return {
        "status": "success",
        "output_dir": str(output_dir),
        "final_free_energy": agent.free_energy_history[-1],
        "diagnostics": final_diag
    }


if __name__ == "__main__":
    result = run_simulation()
    print(f"\nDemo completed: {result['status']}")
    print(f"Results in: {result['output_dir']}")
