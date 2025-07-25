"""
Comprehensive H3 Geospatial Active Inference Demonstration

This advanced example demonstrates the full capabilities of the GEO-INFER-ACT
framework for geospatial active inference using H3 hexagonal grids.

Key Features Demonstrated:
1. H3-based spatial modeling with Active Inference
2. Multi-agent coordination on hexagonal grids
3. Environmental dynamics and resource optimization
4. Hierarchical multi-scale spatial analysis
5. Advanced visualization and data export
6. Real-time belief propagation and free energy dynamics
7. Spatial attention and adaptive sensing
8. Environmental uncertainty quantification

Mathematical Foundation:
The demonstration implements geospatial active inference where agents
minimize free energy across spatial domains:

F = E_q[log q(s|π)] - E_q[log p(o,s|π)]

Where:
- s: spatial environmental states on H3 grid
- o: environmental observations (temperature, vegetation, etc.)
- π: spatial policies (movement, sensing, resource allocation)
- q: posterior beliefs about environmental states
- p: generative model of spatial-environmental dynamics

The system demonstrates emergent spatial patterns, adaptive resource
allocation, and hierarchical environmental modeling.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile

# Set matplotlib backend before imports
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for headless environments

import numpy as np
import pandas as pd
import h3
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import seaborn as sns

# GEO-INFER imports
from geo_infer_act.models.multi_agent import MultiAgentModel
from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.active_inference import ActiveInferenceModel
from geo_infer_act.utils.visualization import (
    create_h3_gif, create_interactive_h3_slider, plot_h3_grid_static
)
from geo_infer_act.utils.geospatial_ai import (
    EnvironmentalActiveInferenceEngine, MultiScaleHierarchicalAnalyzer,
    analyze_multi_scale_patterns
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_output_directory() -> Path:
    """Create timestamped output directory in the root /output folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create output in the repository root /output directory
    repo_root = Path(__file__).parent.parent.parent  # Go up from examples/h3_active_inference.py to repo root
    output_dir = repo_root / "output" / f"h3_active_inference_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir


def setup_san_francisco_boundary() -> Dict[str, Any]:
    """Define San Francisco bay area boundary for demonstration."""
    return {
        'type': 'Polygon',
        'coordinates': [[[
            [-122.52, 37.70],  # Southwest corner
            [-122.52, 37.82],  # Northwest corner  
            [-122.35, 37.82],  # Northeast corner
            [-122.35, 37.70],  # Southeast corner
            [-122.52, 37.70]   # Close polygon
        ]]]
    }


# Modify the generate_realistic_environmental_observations function
def generate_realistic_environmental_observations(cells: List[str], 
                                                timestep: float, 
                                                base_patterns: Dict[str, Any] = None,
                                                spatial_seed: Optional[int] = None) -> Dict[str, Dict[str, float]]:
    """
    Generate sophisticated environmental observations with advanced spatial and temporal patterns.
    
    Args:
        cells: List of H3 cell IDs
        timestep: Current simulation timestep
        base_patterns: Base environmental patterns for consistency
        spatial_seed: Optional seed for reproducible spatial variation
        
    Returns:
        Dictionary mapping cells to environmental observations
    """
    # Set random seed for reproducibility if provided
    if spatial_seed is not None:
        np.random.seed(spatial_seed)
    
    # Default base patterns with more nuanced parameters
    if base_patterns is None:
        base_patterns = {
            'temperature': {
                'base': 20.0, 
                'amplitude': 5.0, 
                'spatial_scale': 50,  # Controls spatial variation
                'temporal_period': 10  # Controls temporal variation
            },
            'humidity': {
                'base': 0.6, 
                'amplitude': 0.2, 
                'spatial_scale': 30,
                'temporal_period': 8
            },
            'vegetation_density': {
                'base': 0.5, 
                'amplitude': 0.3, 
                'spatial_scale': 40,
                'temporal_period': 12,
                'coastal_gradient': True  # Adds coastal influence
            },
            'water_availability': {
                'base': 0.5, 
                'amplitude': 0.2, 
                'spatial_scale': 35,
                'temporal_period': 6,
                'seasonal_variation': True  # Adds seasonal dry/wet cycles
            },
            'soil_quality': {
                'base': 0.6, 
                'amplitude': 0.2, 
                'spatial_scale': 25,
                'temporal_period': 15
            },
            'biodiversity_index': {
                'base': 0.5, 
                'amplitude': 0.3, 
                'spatial_scale': 45,
                'temporal_period': 20,
                'ecosystem_complexity': True  # More complex variation
            },
            'carbon_flux': {
                'base': 0.0, 
                'amplitude': 0.1, 
                'spatial_scale': 60,
                'temporal_period': 4
            }
        }
    
    observations = {}
    
    for cell in cells:
        lat, lng = h3.cell_to_latlng(cell)
        
        observations[cell] = {}
        for var, pattern in base_patterns.items():
            # Advanced spatial variation
            spatial_factor = (
                np.sin(lat * pattern['spatial_scale']) * 
                np.cos(lng * pattern['spatial_scale']) + 1
            ) / 2
            
            # Temporal variation with more complex cycles
            temporal_factor = np.sin(timestep / pattern['temporal_period'] * 2 * np.pi)
            
            # Additional spatial variations
            if pattern.get('coastal_gradient', False):
                # Simulate coastal gradient effect
                distance_from_coast = abs(lng + 122.4)  # Approximate San Francisco coast
                spatial_factor *= (1 - 0.3 * distance_from_coast)
            
            if pattern.get('seasonal_variation', False):
                # Add seasonal dry/wet cycle
                seasonal_factor = np.sin((timestep + 2) / 12 * 2 * np.pi)
                temporal_factor += 0.2 * seasonal_factor
            
            if pattern.get('ecosystem_complexity', False):
                # Add more complex ecosystem interactions
                complexity_factor = np.sin(lat * 20) * np.cos(lng * 20)
                spatial_factor *= (1 + 0.2 * complexity_factor)
            
            # Compute value with noise and advanced variations
            value = (
                pattern['base'] + 
                pattern['amplitude'] * spatial_factor * temporal_factor + 
                np.random.normal(0, 0.05)
            )
            
            # Clip to appropriate range
            if var not in ['temperature', 'carbon_flux']:
                value = np.clip(value, 0, 1)
            
            observations[cell][var] = value
    
    return observations


def run_basic_h3_active_inference(output_dir: Path, 
                                  h3_resolution: int = 8, 
                                  timesteps: int = 10,
                                  n_agents: int = 3,
                                  spatial_seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Run comprehensive H3 active inference simulation with advanced environmental modeling.
    
    Args:
        output_dir: Directory to save simulation outputs
        h3_resolution: H3 grid resolution
        timesteps: Number of simulation timesteps
        n_agents: Number of agents
        spatial_seed: Optional seed for reproducible spatial variation
    
    Returns:
        Comprehensive simulation results and metrics
    """
    logger.info("=== Starting Advanced H3 Active Inference Simulation ===")
    
    # Setup boundary and spatial model
    boundary = setup_san_francisco_boundary()
    
    # Create multi-agent model
    model = MultiAgentModel(n_agents=n_agents)
    model.enable_h3_spatial(h3_resolution, boundary)
    
    if not hasattr(model, 'h3_cells') or len(model.h3_cells) == 0:
        logger.error("Failed to initialize H3 spatial model")
        return {'error': 'H3 initialization failed'}
    
    logger.info(f"Initialized H3 grid with {len(model.h3_cells)} cells at resolution {h3_resolution}")
    
    # Simulation tracking
    simulation_history = []
    free_energy_evolution = []
    agent_coordination_history = []
    environmental_observations_history = []
    
    # Agent mapping strategy
    agent_map = {cell: i % n_agents for i, cell in enumerate(model.h3_cells)}
    
    # Simulation loop with advanced tracking
    for t in range(timesteps):
        timestep_start = time.time()
        step_data = {}
        step_free_energy = 0.0
        
        # Generate environmental observations with spatial seed for reproducibility
        environmental_obs = generate_realistic_environmental_observations(
            model.h3_cells, t, spatial_seed=spatial_seed
        )
        environmental_observations_history.append(environmental_obs)
        
        # Process each cell
        for cell in model.h3_cells:
            agent_idx = agent_map[cell]
            agent = model.agent_models[agent_idx]
            
            # Convert environmental observations to agent observations
            env_obs = environmental_obs[cell]
            obs_vector = np.array([
                env_obs['temperature'] / 30.0,  # Normalize temperature
                env_obs['humidity'],
                env_obs['vegetation_density'],
                env_obs['biodiversity_index']
            ])
            obs_vector = obs_vector / np.sum(obs_vector)  # Normalize to probability
            
            # Advanced agent processing
            beliefs = agent.update_beliefs(obs_vector)
            free_energy = agent.compute_free_energy()
            precision = 1.0  # Default precision value
            
            step_data[cell] = {
                'beliefs': beliefs.tolist(),
                'free_energy': free_energy,
                'precision': precision,
                'environmental_state': env_obs,
                'agent_id': agent_idx
            }
            
            step_free_energy += free_energy
        
        # Agent coordination with more detailed tracking
        coordination_result = model.coordinate_agents()
        avg_free_energy = step_free_energy / len(model.h3_cells)
        
        # Store detailed timestep data
        timestep_data = {
            'timestep': t,
            'cells': step_data,
            'global_metrics': {
                'average_free_energy': avg_free_energy,
                'total_free_energy': step_free_energy,
                'coordination_coherence': np.mean(coordination_result['coordination_matrix']),
                'processing_time': time.time() - timestep_start
            },
            'coordination': coordination_result
        }
        
        simulation_history.append(timestep_data)
        free_energy_evolution.append(avg_free_energy)
        agent_coordination_history.append(coordination_result)
        
        logger.info(f"Timestep {t}: FE={avg_free_energy:.4f}, Processing={timestep_data['global_metrics']['processing_time']:.3f}s")
    
    # Compute comprehensive results
    results = {
        'simulation_params': {
            'h3_resolution': h3_resolution,
            'n_cells': len(model.h3_cells),
            'n_agents': n_agents,
            'timesteps': timesteps,
            'boundary': boundary,
            'spatial_seed': spatial_seed
        },
        'history': simulation_history,
        'metrics': {
            'free_energy_evolution': free_energy_evolution,
            'final_free_energy': free_energy_evolution[-1],
            'free_energy_change': free_energy_evolution[-1] - free_energy_evolution[0],
            'total_processing_time': sum(h['global_metrics']['processing_time'] for h in simulation_history)
        },
        'environmental_observations': environmental_observations_history,
        'agent_coordination_history': agent_coordination_history
    }
    
    logger.info(f"Advanced simulation completed: {timesteps} timesteps, {len(model.h3_cells)} cells")
    logger.info(f"Free energy evolution: {free_energy_evolution[0]:.4f} → {free_energy_evolution[-1]:.4f}")
    
    return results


def run_environmental_active_inference(output_dir: Path) -> Dict[str, Any]:
    """
    Run advanced environmental active inference with resource optimization.
    
    Returns:
        Environmental analysis results
    """
    logger.info("=== Starting Environmental Active Inference Analysis ===")
    
    # Setup environmental engine
    boundary = setup_san_francisco_boundary()
    engine = EnvironmentalActiveInferenceEngine(
        h3_resolution=8,
        prediction_horizon=5,
        uncertainty_threshold=0.15
    )
    engine.initialize_spatial_domain(boundary)
    
    if len(engine.environmental_states) == 0:
        logger.error("Failed to initialize environmental domain")
        return {'error': 'Environmental initialization failed'}
    
    logger.info(f"Initialized environmental domain with {len(engine.environmental_states)} cells")
    
    # Environmental observation sequence
    environmental_history = []
    prediction_history = []
    resource_allocation_history = []
    
    for t in range(12):  # 12 timesteps for environmental modeling
        # Generate environmental observations
        observations = generate_realistic_environmental_observations(
            list(engine.environmental_states.keys()), t
        )
        
        # Update environmental engine
        engine.observe_environment(observations, float(t))
        environmental_history.append({
            'timestep': t,
            'observations': observations,
            'n_observed_cells': len(observations)
        })
        
        # Generate environmental predictions (after sufficient observations)
        if t >= 5:
            predictions = engine.predict_environmental_dynamics(forecast_timesteps=3)
            prediction_history.append({
                'timestep': t,
                'predictions': predictions,
                'n_predicted_variables': len(predictions)
            })
            
            # Optimize resource allocation
            resource_allocations = engine.optimize_resource_allocation(
                resource_budget=200.0,
                resource_types=['vegetation_restoration', 'water_conservation', 'carbon_sequestration'],
                optimization_objective='biodiversity'
            )
            
            resource_allocation_history.append({
                'timestep': t,
                'allocations': resource_allocations,
                'total_allocated': sum(alloc.allocation_amount for alloc in resource_allocations),
                'n_allocations': len(resource_allocations)
            })
            
            logger.info(f"Environmental timestep {t}: {len(predictions)} predictions, {len(resource_allocations)} allocations")
        
        logger.info(f"Environmental observation {t}: {len(observations)} cells updated")
    
    # Analyze environmental uncertainty
    uncertainty_analysis = engine.analyze_environmental_uncertainty()
    
    # Compute environmental free energy
    environmental_free_energy = engine.compute_environmental_free_energy()
    
    # Get comprehensive environmental summary
    environmental_summary = engine.get_environmental_summary()
    
    results = {
        'environmental_params': {
            'h3_resolution': engine.h3_resolution,
            'n_cells': len(engine.environmental_states),
            'n_observations': len(environmental_history),
            'environmental_variables': engine.environmental_variables
        },
        'observation_history': environmental_history,
        'prediction_history': prediction_history,
        'resource_allocation_history': resource_allocation_history,
        'uncertainty_analysis': uncertainty_analysis,
        'environmental_free_energy': environmental_free_energy,
        'environmental_summary': environmental_summary
    }
    
    logger.info(f"Environmental analysis completed: {len(environmental_history)} observations")
    logger.info(f"Environmental free energy: {environmental_free_energy.get('total_free_energy', 'N/A')}")
    
    return results


def run_hierarchical_multi_scale_analysis(output_dir: Path) -> Dict[str, Any]:
    """
    Run hierarchical multi-scale spatial analysis.
    
    Returns:
        Multi-scale analysis results
    """
    logger.info("=== Starting Hierarchical Multi-Scale Analysis ===")
    
    # Setup hierarchical analyzer
    boundary = setup_san_francisco_boundary()
    analyzer = MultiScaleHierarchicalAnalyzer(
        base_resolution=8,
        hierarchy_levels=3,
        scale_factor=3
    )
    analyzer.initialize_hierarchy(boundary)
    
    if len(analyzer.hierarchical_graphs) == 0:
        logger.error("Failed to initialize hierarchical structure")
        return {'error': 'Hierarchical initialization failed'}
    
    logger.info(f"Initialized {len(analyzer.hierarchical_graphs)} hierarchical levels")
    
    # Generate bottom-up evidence from environmental observations
    finest_level = sorted(analyzer.hierarchical_graphs.keys(), 
                         key=lambda x: int(x.split('_res_')[1]), reverse=True)[0]
    
    bottom_up_evidence = {finest_level: {}}
    
    # Create realistic spatial evidence patterns
    for cell in analyzer.hierarchical_beliefs[finest_level]:
        lat, lng = h3.cell_to_latlng(cell)
        
        # Create environmental quality score
        distance_from_center = np.sqrt((lat - 37.76)**2 + (lng + 122.43)**2)
        environmental_quality = np.exp(-distance_from_center * 5)  # Gaussian decay from center
        
        # Convert to belief distribution (4-state environmental quality model)
        if environmental_quality > 0.7:
            belief = np.array([0.1, 0.15, 0.25, 0.5])  # High quality
        elif environmental_quality > 0.4:
            belief = np.array([0.2, 0.3, 0.35, 0.15])  # Medium quality
        elif environmental_quality > 0.2:
            belief = np.array([0.4, 0.35, 0.2, 0.05])  # Low quality
        else:
            belief = np.array([0.6, 0.25, 0.1, 0.05])  # Very low quality
        
        # Add noise
        belief += np.random.normal(0, 0.02, 4)
        belief = np.clip(belief, 0.01, 0.99)
        belief = belief / np.sum(belief)  # Renormalize
        
        bottom_up_evidence[finest_level][cell] = belief
    
    # Propagate beliefs hierarchically
    hierarchical_beliefs = analyzer.propagate_beliefs_hierarchically(bottom_up_evidence)
    
    # Analyze cross-scale interactions
    cross_scale_analysis = analyzer.analyze_cross_scale_interactions()
    
    # Detect emergent patterns
    emergent_patterns = analyzer.detect_emergent_patterns()
    
    # Comprehensive multi-scale pattern analysis
    multi_scale_analysis = analyze_multi_scale_patterns(
        analyzer.hierarchical_graphs, 
        hierarchical_beliefs
    )
    
    results = {
        'hierarchical_params': {
            'base_resolution': analyzer.base_resolution,
            'hierarchy_levels': analyzer.hierarchy_levels,
            'scale_factor': analyzer.scale_factor,
            'level_names': list(analyzer.hierarchical_graphs.keys())
        },
        'hierarchical_beliefs': {
            level: {cell: belief.tolist() for cell, belief in beliefs.items()}
            for level, beliefs in hierarchical_beliefs.items()
        },
        'cross_scale_interactions': cross_scale_analysis,
        'emergent_patterns': emergent_patterns,
        'multi_scale_analysis': multi_scale_analysis
    }
    
    logger.info(f"Hierarchical analysis completed: {len(hierarchical_beliefs)} levels")
    logger.info(f"Detected {len(emergent_patterns)} emergent patterns")
    
    return results


def create_comprehensive_visualizations(basic_results: Dict[str, Any], 
                                       environmental_results: Dict[str, Any],
                                       hierarchical_results: Dict[str, Any],
                                       output_dir: Path) -> Dict[str, str]:
    """
    Create comprehensive visualizations of all simulation results.
    
    Returns:
        Dictionary mapping visualization types to file paths
    """
    logger.info("=== Creating Comprehensive Visualizations ===")
    
    visualization_files = {}
    
    try:
        # 1. Basic H3 simulation visualizations
        if 'history' in basic_results:
            # H3 free energy evolution GIF
            h3_data_for_gif = []
            for timestep_data in basic_results['history']:
                gif_frame = {}
                for cell, cell_data in timestep_data['cells'].items():
                    gif_frame[cell] = {
                        'fe': cell_data['free_energy'],
                        'beliefs': cell_data['beliefs'],
                        'precision': cell_data['precision']
                    }
                h3_data_for_gif.append(gif_frame)
            
            # Create animated GIF
            gif_path = output_dir / 'h3_free_energy_evolution.gif'
            create_h3_gif(h3_data_for_gif, str(gif_path))
            visualization_files['h3_evolution_gif'] = str(gif_path)
            
            # Create interactive slider
            slider_path = output_dir / 'interactive_h3_exploration.html'
            slider_fig = create_interactive_h3_slider(h3_data_for_gif)
            slider_fig.write_html(str(slider_path))
            visualization_files['h3_interactive'] = str(slider_path)
            
            # Free energy evolution plot
            plt.figure(figsize=(12, 6))
            timesteps = list(range(len(basic_results['metrics']['free_energy_evolution'])))
            fe_values = basic_results['metrics']['free_energy_evolution']
            
            plt.subplot(1, 2, 1)
            plt.plot(timesteps, fe_values, 'b-', linewidth=2, label='Free Energy')
            plt.xlabel('Timestep')
            plt.ylabel('Average Free Energy')
            plt.title('Free Energy Evolution')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Processing time plot
            plt.subplot(1, 2, 2)
            processing_times = [h['global_metrics']['processing_time'] for h in basic_results['history']]
            plt.plot(timesteps, processing_times, 'r-', linewidth=2, label='Processing Time')
            plt.xlabel('Timestep')
            plt.ylabel('Processing Time (seconds)')
            plt.title('Computational Performance')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plt.tight_layout()
            performance_plot_path = output_dir / 'simulation_performance.png'
            plt.savefig(performance_plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            visualization_files['performance_plot'] = str(performance_plot_path)
        
        # 2. Environmental analysis visualizations
        if 'environmental_summary' in environmental_results:
            # Environmental variables distribution
            fig, axes = plt.subplots(2, 4, figsize=(16, 8))
            axes = axes.flatten()
            
            env_vars = environmental_results['environmental_params']['environmental_variables']
            for i, var in enumerate(env_vars):
                if i < len(axes):
                    # Get variable statistics from summary
                    var_stats_key = f'{var}_stats'
                    if var_stats_key in environmental_results['environmental_summary']:
                        stats = environmental_results['environmental_summary'][var_stats_key]
                        
                        # Create distribution visualization
                        x = np.linspace(stats['min'], stats['max'], 100)
                        y = np.exp(-0.5 * ((x - stats['mean']) / stats['std'])**2)
                        
                        axes[i].plot(x, y, linewidth=2)
                        axes[i].fill_between(x, 0, y, alpha=0.3)
                        axes[i].set_title(f'{var.replace("_", " ").title()}')
                        axes[i].set_xlabel('Value')
                        axes[i].set_ylabel('Density')
                        axes[i].grid(True, alpha=0.3)
            
            # Remove unused subplots
            for i in range(len(env_vars), len(axes)):
                fig.delaxes(axes[i])
            
            plt.tight_layout()
            env_dist_path = output_dir / 'environmental_distributions.png'
            plt.savefig(env_dist_path, dpi=150, bbox_inches='tight')
            plt.close()
            visualization_files['environmental_distributions'] = str(env_dist_path)
            
            # Resource allocation visualization
            if environmental_results['resource_allocation_history']:
                plt.figure(figsize=(14, 6))
                
                # Resource allocation over time
                plt.subplot(1, 2, 1)
                timesteps = [r['timestep'] for r in environmental_results['resource_allocation_history']]
                total_allocated = [r['total_allocated'] for r in environmental_results['resource_allocation_history']]
                n_allocations = [r['n_allocations'] for r in environmental_results['resource_allocation_history']]
                
                plt.plot(timesteps, total_allocated, 'g-', linewidth=2, label='Total Budget Allocated')
                plt.xlabel('Timestep')
                plt.ylabel('Resource Budget')
                plt.title('Resource Allocation Over Time')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # Number of allocation decisions
                plt.subplot(1, 2, 2)
                plt.plot(timesteps, n_allocations, 'orange', linewidth=2, label='Number of Allocations')
                plt.xlabel('Timestep')
                plt.ylabel('Count')
                plt.title('Resource Allocation Decisions')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                plt.tight_layout()
                resource_plot_path = output_dir / 'resource_allocation_analysis.png'
                plt.savefig(resource_plot_path, dpi=150, bbox_inches='tight')
                plt.close()
                visualization_files['resource_allocation'] = str(resource_plot_path)
        
        # 3. Hierarchical multi-scale visualizations
        if 'multi_scale_analysis' in hierarchical_results:
            # Cross-scale coherence visualization
            plt.figure(figsize=(12, 8))
            
            # Scale statistics
            scale_stats = hierarchical_results['multi_scale_analysis']['scale_statistics']
            
            plt.subplot(2, 2, 1)
            levels = list(scale_stats.keys())
            n_cells = [scale_stats[level]['n_cells'] for level in levels]
            mean_entropy = [scale_stats[level]['mean_entropy'] for level in levels]
            
            plt.bar(range(len(levels)), n_cells, alpha=0.7, label='Number of Cells')
            plt.xlabel('Hierarchical Level')
            plt.ylabel('Number of Cells')
            plt.title('Spatial Scale Hierarchy')
            plt.xticks(range(len(levels)), [f"L{i}" for i in range(len(levels))])
            plt.legend()
            
            plt.subplot(2, 2, 2)
            plt.bar(range(len(levels)), mean_entropy, alpha=0.7, color='orange', label='Mean Entropy')
            plt.xlabel('Hierarchical Level')
            plt.ylabel('Information Content (bits)')
            plt.title('Information Across Scales')
            plt.xticks(range(len(levels)), [f"L{i}" for i in range(len(levels))])
            plt.legend()
            
            # Cross-scale interactions
            plt.subplot(2, 2, 3)
            cross_scale = hierarchical_results['cross_scale_interactions']
            if 'scale_coherence' in cross_scale:
                coherence_values = list(cross_scale['scale_coherence'].values())
                interaction_names = list(cross_scale['scale_coherence'].keys())
                
                plt.bar(range(len(coherence_values)), coherence_values, alpha=0.7, color='green')
                plt.xlabel('Scale Interaction')
                plt.ylabel('Coherence')
                plt.title('Cross-Scale Coherence')
                plt.xticks(range(len(interaction_names)), [f"I{i}" for i in range(len(interaction_names))])
            
            # Emergent patterns
            plt.subplot(2, 2, 4)
            emergent_patterns = hierarchical_results['emergent_patterns']
            if emergent_patterns:
                pattern_sizes = [p['size'] for p in emergent_patterns]
                pattern_levels = [p['level'] for p in emergent_patterns]
                
                plt.scatter(range(len(pattern_sizes)), pattern_sizes, 
                          alpha=0.7, s=100, color='purple')
                plt.xlabel('Pattern Index')
                plt.ylabel('Pattern Size (cells)')
                plt.title('Emergent Spatial Patterns')
            
            plt.tight_layout()
            hierarchical_plot_path = output_dir / 'hierarchical_multi_scale_analysis.png'
            plt.savefig(hierarchical_plot_path, dpi=150, bbox_inches='tight')
            plt.close()
            visualization_files['hierarchical_analysis'] = str(hierarchical_plot_path)
        
        logger.info(f"Created {len(visualization_files)} visualization files")
        
    except Exception as e:
        logger.error(f"Error creating visualizations: {e}")
        visualization_files['error'] = str(e)
    
    return visualization_files


def export_comprehensive_data(basic_results: Dict[str, Any],
                            environmental_results: Dict[str, Any], 
                            hierarchical_results: Dict[str, Any],
                            output_dir: Path) -> Dict[str, str]:
    """
    Export comprehensive simulation data in multiple formats.
    
    Returns:
        Dictionary mapping export types to file paths
    """
    logger.info("=== Exporting Comprehensive Data ===")
    
    export_files = {}
    
    try:
        # 1. Complete JSON export
        complete_results = {
            'basic_simulation': basic_results,
            'environmental_analysis': environmental_results,
            'hierarchical_analysis': hierarchical_results,
            'export_metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'framework': 'GEO-INFER-ACT'
            }
        }
        
        json_path = output_dir / 'complete_simulation_results.json'
        with open(json_path, 'w') as f:
            json.dump(complete_results, f, indent=2, default=str)
        export_files['complete_json'] = str(json_path)
        
        # 2. CSV export for basic simulation
        if 'history' in basic_results:
            csv_data = []
            for timestep_data in basic_results['history']:
                t = timestep_data['timestep']
                for cell, cell_data in timestep_data['cells'].items():
                    env_state = cell_data.get('environmental_state', {})
                    csv_data.append({
                        'timestep': t,
                        'cell_id': cell,
                        'free_energy': cell_data['free_energy'],
                        'precision': cell_data['precision'],
                        'agent_id': cell_data['agent_id'],
                        'temperature': env_state.get('temperature', 0),
                        'humidity': env_state.get('humidity', 0),
                        'vegetation_density': env_state.get('vegetation_density', 0),
                        'biodiversity_index': env_state.get('biodiversity_index', 0),
                        'carbon_flux': env_state.get('carbon_flux', 0)
                    })
            
            df = pd.DataFrame(csv_data)
            csv_path = output_dir / 'simulation_timeseries.csv'
            df.to_csv(csv_path, index=False)
            export_files['simulation_csv'] = str(csv_path)
            
            logger.info(f"Exported {len(csv_data)} simulation records to CSV")
        
        # 3. Environmental data export
        if 'observation_history' in environmental_results:
            env_csv_data = []
            for obs_data in environmental_results['observation_history']:
                t = obs_data['timestep']
                for cell, observations in obs_data['observations'].items():
                    record = {'timestep': t, 'cell_id': cell}
                    record.update(observations)
                    env_csv_data.append(record)
            
            env_df = pd.DataFrame(env_csv_data)
            env_csv_path = output_dir / 'environmental_observations.csv'
            env_df.to_csv(env_csv_path, index=False)
            export_files['environmental_csv'] = str(env_csv_path)
            
            logger.info(f"Exported {len(env_csv_data)} environmental records to CSV")
        
        # 4. Resource allocation export
        if 'resource_allocation_history' in environmental_results:
            resource_data = []
            for alloc_data in environmental_results['resource_allocation_history']:
                t = alloc_data['timestep']
                for allocation in alloc_data['allocations']:
                    resource_data.append({
                        'timestep': t,
                        'cell_id': allocation.location,
                        'resource_type': allocation.resource_type,
                        'allocation_amount': allocation.allocation_amount,
                        'priority_score': allocation.priority_score,
                        'expected_benefit': allocation.expected_benefit,
                        'uncertainty': allocation.uncertainty
                    })
            
            if resource_data:
                resource_df = pd.DataFrame(resource_data)
                resource_csv_path = output_dir / 'resource_allocations.csv'
                resource_df.to_csv(resource_csv_path, index=False)
                export_files['resource_csv'] = str(resource_csv_path)
                
                logger.info(f"Exported {len(resource_data)} resource allocation records to CSV")
        
        # 5. Summary statistics export
        summary_stats = {
            'basic_simulation': {
                'total_cells': basic_results['simulation_params']['n_cells'],
                'total_agents': basic_results['simulation_params']['n_agents'],
                'total_timesteps': basic_results['simulation_params']['timesteps'],
                'final_free_energy': basic_results['metrics']['final_free_energy'],
                'free_energy_reduction': -basic_results['metrics']['free_energy_change'],
                'total_processing_time': basic_results['metrics']['total_processing_time']
            },
            'environmental_analysis': {
                'total_environmental_cells': environmental_results['environmental_params']['n_cells'],
                'environmental_variables': len(environmental_results['environmental_params']['environmental_variables']),
                'total_observations': environmental_results['environmental_params']['n_observations'],
                'environmental_free_energy': environmental_results['environmental_free_energy'].get('total_free_energy', 'N/A')
            },
            'hierarchical_analysis': {
                'hierarchy_levels': hierarchical_results['hierarchical_params']['hierarchy_levels'],
                'base_resolution': hierarchical_results['hierarchical_params']['base_resolution'],
                'emergent_patterns_detected': len(hierarchical_results['emergent_patterns'])
            }
        }
        
        summary_path = output_dir / 'simulation_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary_stats, f, indent=2, default=str)
        export_files['summary_json'] = str(summary_path)
        
        logger.info(f"Created {len(export_files)} export files")
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        export_files['error'] = str(e)
    
    return export_files


def main():
    """
    Main execution function for comprehensive H3 geospatial active inference demonstration.
    """
    logger.info("🌍 GEO-INFER-ACT: Comprehensive H3 Geospatial Active Inference Demonstration")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir = create_output_directory()
    
    try:
        # Phase 1: Basic H3 Active Inference Simulation
        logger.info("🧠 Phase 1: Basic H3 Active Inference")
        basic_results = run_basic_h3_active_inference(output_dir)
        
        if 'error' in basic_results:
            logger.error(f"Basic simulation failed: {basic_results['error']}")
            return
        
        # Phase 2: Environmental Active Inference
        logger.info("🌱 Phase 2: Environmental Active Inference")
        environmental_results = run_environmental_active_inference(output_dir)
        
        if 'error' in environmental_results:
            logger.error(f"Environmental analysis failed: {environmental_results['error']}")
            environmental_results = {}
        
        # Phase 3: Hierarchical Multi-Scale Analysis
        logger.info("🏗️ Phase 3: Hierarchical Multi-Scale Analysis")
        hierarchical_results = run_hierarchical_multi_scale_analysis(output_dir)
        
        if 'error' in hierarchical_results:
            logger.error(f"Hierarchical analysis failed: {hierarchical_results['error']}")
            hierarchical_results = {}
        
        # Phase 4: Comprehensive Visualizations
        logger.info("📊 Phase 4: Creating Comprehensive Visualizations")
        visualization_files = create_comprehensive_visualizations(
            basic_results, environmental_results, hierarchical_results, output_dir
        )
        
        # Phase 5: Data Export
        logger.info("💾 Phase 5: Exporting Comprehensive Data")
        export_files = export_comprehensive_data(
            basic_results, environmental_results, hierarchical_results, output_dir
        )
        
        # Final Summary
        logger.info("=" * 80)
        logger.info("🎉 COMPREHENSIVE DEMONSTRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        # Print results summary
        if 'metrics' in basic_results:
            logger.info(f"📈 Basic Simulation Results:")
            logger.info(f"   • Cells: {basic_results['simulation_params']['n_cells']}")
            logger.info(f"   • Agents: {basic_results['simulation_params']['n_agents']}")
            logger.info(f"   • Timesteps: {basic_results['simulation_params']['timesteps']}")
            logger.info(f"   • Free Energy: {basic_results['metrics']['free_energy_evolution'][0]:.4f} → {basic_results['metrics']['final_free_energy']:.4f}")
            logger.info(f"   • Processing Time: {basic_results['metrics']['total_processing_time']:.2f}s")
        
        if environmental_results:
            logger.info(f"🌱 Environmental Analysis Results:")
            logger.info(f"   • Environmental Cells: {environmental_results['environmental_params']['n_cells']}")
            logger.info(f"   • Environmental Variables: {len(environmental_results['environmental_params']['environmental_variables'])}")
            logger.info(f"   • Observations: {environmental_results['environmental_params']['n_observations']}")
            if 'total_free_energy' in environmental_results['environmental_free_energy']:
                logger.info(f"   • Environmental Free Energy: {environmental_results['environmental_free_energy']['total_free_energy']:.4f}")
        
        if hierarchical_results:
            logger.info(f"🏗️ Hierarchical Analysis Results:")
            logger.info(f"   • Hierarchy Levels: {hierarchical_results['hierarchical_params']['hierarchy_levels']}")
            logger.info(f"   • Base Resolution: {hierarchical_results['hierarchical_params']['base_resolution']}")
            logger.info(f"   • Emergent Patterns: {len(hierarchical_results['emergent_patterns'])}")
        
        logger.info(f"📊 Visualizations Created: {len(visualization_files)}")
        for viz_type, viz_path in visualization_files.items():
            if viz_type != 'error':
                logger.info(f"   • {viz_type}: {viz_path}")
        
        logger.info(f"💾 Data Exports Created: {len(export_files)}")
        for export_type, export_path in export_files.items():
            if export_type != 'error':
                logger.info(f"   • {export_type}: {export_path}")
        
        logger.info(f"📁 All outputs saved to: {output_dir}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Demonstration failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main()) 