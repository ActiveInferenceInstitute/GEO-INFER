#!/usr/bin/env python
"""
Simple active inference model example for GEO-INFER-ACT.

This example demonstrates how to create a simple active inference model
for a categorical state and observation space, update beliefs based on
observations, and select policies with comprehensive analysis and logging.

Enhanced with comprehensive tracing, pattern detection, and interpretability
features while maintaining conceptual simplicity.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import GEO-INFER-ACT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geo_infer_act.api.interface import ActiveInferenceInterface
from geo_infer_act.utils.visualization import (
    plot_belief_update, plot_policies, plot_perception_analysis, 
    plot_action_analysis, create_interpretability_dashboard
)
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer
from geo_infer_act.utils.math import (
    compute_surprise, assess_convergence, compute_information_gain,
    detect_stationarity, detect_periodicity, assess_complexity
)


def setup_logging() -> logging.Logger:
    """Set up comprehensive logging for the simple model example."""
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 'simple')
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure logging
    log_file = os.path.join(output_dir, f'simple_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('SimpleActiveInference')
    logger.info("Simple Active Inference Model - Comprehensive Analysis")
    logger.info("=" * 70)
    
    return logger


def main():
    """Run a simple active inference model example with comprehensive analysis."""
    # Set up logging
    logger = setup_logging()
    output_dir = os.path.join(os.path.dirname(__file__), 'output', 'simple')
    
    logger.info("Starting Simple Active Inference Model with Enhanced Analysis")
    logger.info("Demonstrating dynamic belief updating, policy selection, and pattern detection")
    
    # 1. Initialize the active inference interface
    config_path = os.path.join(os.path.dirname(__file__), '../config/example.yaml')
    ai_interface = ActiveInferenceInterface(config_path)
    
    # 2. Create a categorical model with enhanced parameters
    model_id = "simple_model"
    model_type = "categorical"
    
    # Model parameters (4-state, 3-observation model for rich dynamics)
    parameters = {
        "state_dim": 4,  # Four possible states for interesting dynamics
        "obs_dim": 3,    # Three possible observations
        "prior_precision": 1.2,
        "learning_rate": 0.12,
        "enable_adaptation": True
    }
    
    ai_interface.create_model(model_id, model_type, parameters)
    logger.info(f"Created enhanced model: {model_id} (type: {model_type})")
    logger.info(f"State dimensions: {parameters['state_dim']}, Observation dimensions: {parameters['obs_dim']}")
    
    # 3. Initialize comprehensive analyzer
    analyzer = ActiveInferenceAnalyzer(output_dir=output_dir)
    
    logger.info("Initialized ActiveInferenceAnalyzer for comprehensive tracing")
    
    # 4. Set prior preferences with clear structure
    preferences = {
        "observations": np.array([0.2, 0.6, 0.2])  # Prefer middle observation (success state)
    }
    ai_interface.set_preferences(model_id, preferences)
    logger.info(f"Set structured prior preferences: {preferences['observations']}")
    
    # 5. Get initial beliefs and record baseline
    initial_beliefs = ai_interface.models[model_id].beliefs
    state_labels = ["Exploration", "Exploitation", "Planning", "Rest"]
    observation_labels = ["Search", "Success", "Transition"]
    
    logger.info("Initial beliefs:")
    for i, (state, prob) in enumerate(zip(state_labels, initial_beliefs['states'])):
        logger.info(f"  {state}: {prob:.4f}")
    
    # Record initial state in analyzer
    analyzer.record_step(
        beliefs=initial_beliefs['states'],
        observations=np.array([0, 0, 0]),
        actions=np.array([0]),
        policies={'phase': 'initialization', 'description': 'Initial beliefs'},
        free_energy=ai_interface.get_free_energy(model_id)
    )
    
    # 6. Create structured observation sequence
    logger.info("Creating structured observation sequence for dynamic analysis...")
    
    # Design a sequence that demonstrates learning and adaptation
    observation_sequence = [
        (np.array([1, 0, 0]), "Initial Search", "exploration"),
        (np.array([1, 0, 0]), "Continued Search", "exploration"), 
        (np.array([0, 1, 0]), "First Discovery", "exploitation"),
        (np.array([0, 1, 0]), "Successful Exploitation", "exploitation"),
        (np.array([0, 0, 1]), "Transition/Rest", "planning"),
        (np.array([1, 0, 0]), "New Search Phase", "exploration"),
        (np.array([0, 1, 0]), "Quick Rediscovery", "exploitation"),
        (np.array([0, 1, 0]), "Sustained Success", "exploitation"),
        (np.array([0, 0, 1]), "Strategic Rest", "planning"),
        (np.array([1, 0, 0]), "Exploration Again", "exploration"),
        (np.array([0, 1, 0]), "Efficient Discovery", "exploitation"),
        (np.array([0, 1, 0]), "Optimization", "exploitation")
    ]
    
    # 7. Run comprehensive simulation with real-time analysis
    logger.info("Running simulation with comprehensive real-time analysis...")
    logger.info("-" * 50)
    
    for t, (observation, description, phase) in enumerate(observation_sequence):
        step_start_time = datetime.now()
        
        logger.info(f"Step {t+1}: {description} ({phase} phase)")
        logger.info(f"  Observation: {observation} ({observation_labels[np.argmax(observation)]})")
        
        # Get pre-update state
        pre_beliefs = ai_interface.models[model_id].beliefs['states'].copy()
        pre_free_energy = ai_interface.get_free_energy(model_id)
        
        # Update beliefs with this observation
        observation_dict = {"observations": observation}
        updated_beliefs = ai_interface.update_beliefs(model_id, observation_dict)
        post_free_energy = ai_interface.get_free_energy(model_id)
        
        # Select policy
        policy_result = ai_interface.select_policy(model_id)
        selected_action = np.array([policy_result['policy']['id']])
        
        # Calculate analytical metrics
        surprise = compute_surprise(pre_beliefs, observation, sigma=0.1)
        
        # Calculate entropies for information gain
        prior_entropy = -np.sum(pre_beliefs * np.log(pre_beliefs + 1e-8))
        posterior_entropy = -np.sum(updated_beliefs['states'] * np.log(updated_beliefs['states'] + 1e-8))
        info_gain = compute_information_gain(prior_entropy, posterior_entropy)
        belief_entropy = posterior_entropy
        
        # Log detailed step information
        logger.info(f"  Pre-update beliefs: {pre_beliefs}")
        logger.info(f"  Post-update beliefs: {updated_beliefs['states']}")
        logger.info(f"  Belief entropy: {belief_entropy:.4f}")
        logger.info(f"  Surprise: {surprise:.4f}")
        logger.info(f"  Information gain: {info_gain:.4f}")
        logger.info(f"  Free energy change: {pre_free_energy:.4f} → {post_free_energy:.4f} (Δ={post_free_energy-pre_free_energy:.4f})")
        logger.info(f"  Selected policy: {policy_result['policy']['id']} (prob: {policy_result['probability']:.3f})")
        
        # Record comprehensive step data in analyzer  
        policies_data = {
            'phase': phase,
            'description': description,
            'observation_type': observation_labels[np.argmax(observation)],
            'surprise': surprise,
            'information_gain': info_gain,
            'belief_entropy': belief_entropy,
            'free_energy_change': post_free_energy - pre_free_energy,
            'policy_confidence': policy_result['probability'],
            'step_duration': (datetime.now() - step_start_time).total_seconds(),
            'policy_result': policy_result
        }
        
        analyzer.record_step(
            beliefs=updated_beliefs['states'],
            observations=observation,
            actions=selected_action,
            policies=policies_data,
            free_energy=post_free_energy
        )
        
        logger.info("")
    
    # 8. Perform comprehensive analysis
    logger.info("Performing comprehensive post-simulation analysis...")
    
    # Generate analysis reports
    perception_analysis = analyzer.analyze_perception_patterns()
    action_analysis = analyzer.analyze_action_selection_patterns() 
    free_energy_analysis = analyzer.analyze_free_energy_patterns()
    
    # Log analysis results
    logger.info("PERCEPTION ANALYSIS:")
    logger.info(f"  Analysis completed: {len(perception_analysis)} components analyzed")
    
    logger.info("ACTION SELECTION ANALYSIS:")
    logger.info(f"  Analysis completed: {len(action_analysis)} components analyzed")
    
    logger.info("FREE ENERGY ANALYSIS:")
    logger.info(f"  Analysis completed: {len(free_energy_analysis)} components analyzed")
    
    # 9. Advanced pattern detection
    logger.info("Running advanced pattern detection...")
    
    # Extract time series for analysis
    beliefs_series = np.array(analyzer.traces['beliefs'])
    free_energy_series = np.array(analyzer.traces['free_energy'])
    
    # Detect patterns in beliefs
    belief_stationarity = detect_stationarity(beliefs_series.mean(axis=1))
    belief_periodicity = detect_periodicity(beliefs_series.mean(axis=1))
    belief_complexity = assess_complexity(beliefs_series.mean(axis=1))
    
    # Detect patterns in free energy
    fe_convergence = assess_convergence(free_energy_series)
    fe_stationarity = detect_stationarity(free_energy_series)
    
    logger.info("ADVANCED PATTERN ANALYSIS:")
    logger.info(f"  Belief stationarity: {belief_stationarity}")
    logger.info(f"  Belief periodicity: {belief_periodicity}")
    logger.info(f"  Belief complexity: {belief_complexity.get('overall_complexity', 0.0):.3f}")
    logger.info(f"  Free energy convergence: {fe_convergence}")
    logger.info(f"  Free energy stationarity: {fe_stationarity}")
    
    # 10. Create comprehensive visualizations
    logger.info("Creating comprehensive visualizations...")
    
    # Generate perception analysis visualization
    plot_perception_analysis(
        analyzer.traces['beliefs'],
        analyzer.traces['observations'],
        Path(output_dir),
        title="Simple Model: Perception Analysis"
    )
    
    # Generate action analysis visualization  
    plot_action_analysis(
        analyzer.traces['actions'],
        analyzer.traces['policies'],
        Path(output_dir),
        title="Simple Model: Action Selection Analysis"
    )
    
    # Create interpretability dashboard
    create_interpretability_dashboard(
        analyzer,
        Path(output_dir)
    )
    
    # Create traditional evolution plots with enhanced analysis
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Belief evolution with analysis annotations
    belief_array = np.array(analyzer.traces['beliefs'])
    for i in range(parameters['state_dim']):
        axes[0, 0].plot(belief_array[:, i], label=state_labels[i], 
                       linewidth=2, marker='o', markersize=4)
    
    # Add convergence detection
    for i in range(parameters['state_dim']):
        if assess_convergence(belief_array[:, i]):
            axes[0, 0].annotate(f'{state_labels[i]} converged', 
                              xy=(len(belief_array)-1, belief_array[-1, i]),
                              xytext=(10, 10), textcoords='offset points',
                              fontsize=8, alpha=0.7)
    
    axes[0, 0].set_xlabel('Time Step', fontsize=12)
    axes[0, 0].set_ylabel('Belief Probability', fontsize=12)
    axes[0, 0].set_title('Belief Evolution with Convergence Analysis', fontsize=14, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Free energy with trend analysis
    free_energy_history = analyzer.traces['free_energy']
    axes[0, 1].plot(free_energy_history, linewidth=2, color='red', marker='d', markersize=4)
    
    # Add trend line
    x_trend = np.arange(len(free_energy_history))
    z = np.polyfit(x_trend, free_energy_history, 1)
    p = np.poly1d(z)
    axes[0, 1].plot(x_trend, p(x_trend), "--", alpha=0.7, color='darkred', label=f'Trend: {z[0]:.4f}')
    
    axes[0, 1].set_xlabel('Time Step', fontsize=12)
    axes[0, 1].set_ylabel('Free Energy', fontsize=12)
    axes[0, 1].set_title('Free Energy Minimization with Trend', fontsize=14, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Surprise evolution
    surprise_history = [p.get('surprise', 0) for p in analyzer.traces['policies'][1:] if isinstance(p, dict)]
    if surprise_history:
        axes[0, 2].plot(surprise_history, linewidth=2, color='orange', marker='s', markersize=4)
    axes[0, 2].set_xlabel('Time Step', fontsize=12)
    axes[0, 2].set_ylabel('Surprise', fontsize=12)
    axes[0, 2].set_title('Surprise Over Time', fontsize=14, fontweight='bold')
    axes[0, 2].grid(True, alpha=0.3)
    
    # Information gain
    info_gain_history = [p.get('information_gain', 0) for p in analyzer.traces['policies'][1:] if isinstance(p, dict)]
    if info_gain_history:
        axes[1, 0].plot(info_gain_history, linewidth=2, color='green', marker='^', markersize=4)
    axes[1, 0].set_xlabel('Time Step', fontsize=12)
    axes[1, 0].set_ylabel('Information Gain', fontsize=12)
    axes[1, 0].set_title('Information Gain Per Step', fontsize=14, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Belief entropy evolution
    entropy_history = [p.get('belief_entropy', 0) for p in analyzer.traces['policies'][1:] if isinstance(p, dict)]
    if entropy_history:
        axes[1, 1].plot(entropy_history, linewidth=2, color='purple', marker='v', markersize=4)
    axes[1, 1].set_xlabel('Time Step', fontsize=12)
    axes[1, 1].set_ylabel('Belief Entropy', fontsize=12)
    axes[1, 1].set_title('Belief Uncertainty Evolution', fontsize=14, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Phase analysis
    phases = [p.get('phase', 'unknown') for p in analyzer.traces['policies'][1:] if isinstance(p, dict)]
    phase_colors = {'exploration': 'blue', 'exploitation': 'green', 'planning': 'red'}
    
    for i, phase in enumerate(phases):
        color = phase_colors.get(phase, 'gray')
        axes[1, 2].scatter(i, entropy_history[i], c=color, s=50, alpha=0.7, label=phase)
    
    # Remove duplicate labels
    handles, labels = axes[1, 2].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    axes[1, 2].legend(by_label.values(), by_label.keys())
    
    axes[1, 2].set_xlabel('Time Step', fontsize=12)
    axes[1, 2].set_ylabel('Belief Entropy', fontsize=12)
    axes[1, 2].set_title('Entropy by Phase', fontsize=14, fontweight='bold')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comprehensive_evolution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 11. Export data and generate reports
    logger.info("Exporting data and generating reports...")
    
    # Export to CSV
    analyzer.save_traces_to_csv()
    
    # Generate comprehensive report
    report = analyzer.generate_comprehensive_report()
    report_file = os.path.join(output_dir, 'analysis_report.txt')
    with open(report_file, 'w') as f:
        f.write(report)
    
    # 12. Final comprehensive summary
    logger.info("\n" + "=" * 70)
    logger.info("COMPREHENSIVE SIMPLE MODEL ANALYSIS COMPLETE")
    logger.info("=" * 70)
    
    # Calculate comprehensive metrics
    initial_beliefs = belief_array[0]
    final_beliefs = belief_array[-1]
    
    initial_entropy = -np.sum(initial_beliefs * np.log(initial_beliefs + 1e-8))
    final_entropy = -np.sum(final_beliefs * np.log(final_beliefs + 1e-8))
    
    logger.info("BELIEF EVOLUTION SUMMARY:")
    for i, state in enumerate(state_labels):
        change = final_beliefs[i] - initial_beliefs[i]
        logger.info(f"  {state}: {initial_beliefs[i]:.4f} → {final_beliefs[i]:.4f} (Δ={change:+.4f})")
    
    logger.info(f"\nBELIEF UNCERTAINTY ANALYSIS:")
    logger.info(f"  Initial entropy: {initial_entropy:.4f}")
    logger.info(f"  Final entropy: {final_entropy:.4f}")
    logger.info(f"  Entropy change: {final_entropy - initial_entropy:+.4f}")
    
    logger.info(f"\nFREE ENERGY ANALYSIS:")
    initial_fe = free_energy_history[0]
    final_fe = free_energy_history[-1]
    total_reduction = initial_fe - final_fe
    logger.info(f"  Initial: {initial_fe:.4f}")
    logger.info(f"  Final: {final_fe:.4f}")
    logger.info(f"  Total reduction: {total_reduction:.4f}")
    logger.info(f"  Minimization efficiency: {(total_reduction / initial_fe * 100):.1f}%")
    
    logger.info(f"\nPERFORMANCE METRICS:")
    avg_surprise = np.mean(surprise_history)
    avg_info_gain = np.mean(info_gain_history)
    total_info_gain = np.sum(info_gain_history)
    
    logger.info(f"  Average surprise: {avg_surprise:.4f}")
    logger.info(f"  Average information gain: {avg_info_gain:.4f}")
    logger.info(f"  Total information gain: {total_info_gain:.4f}")
    logger.info(f"  Learning efficiency: {total_info_gain / len(observation_sequence):.4f} per step")
    
    logger.info(f"\nQUALITY ASSESSMENTS:")
    # Use safe dict access with defaults for quality scores
    perception_quality = perception_analysis.get('belief_dynamics', {}).get('quality_score', 0.0)
    action_quality = action_analysis.get('policy_dynamics', {}).get('consistency_score', 0.0)
    free_energy_quality = free_energy_analysis.get('minimization', {}).get('efficiency_score', 0.0)
    
    logger.info(f"  Perception quality: {perception_quality:.3f}/1.0")
    logger.info(f"  Action quality: {action_quality:.3f}/1.0")
    logger.info(f"  Free energy quality: {free_energy_quality:.3f}/1.0")
    
    logger.info(f"\nOUTPUTS GENERATED:")
    logger.info(f"  Analysis data: {os.path.join(output_dir, 'simple_model_data.csv')}")
    logger.info(f"  Comprehensive report: {report_file}")
    logger.info(f"  Visualizations: {output_dir}/*.png")
    logger.info(f"  Log file: Multiple .log files in {output_dir}")
    
    logger.info("\nFEATURES DEMONSTRATED:")
    logger.info("• Comprehensive belief dynamics tracking and analysis")
    logger.info("• Real-time perception pattern detection and quality assessment")
    logger.info("• Advanced action selection analysis with convergence detection")
    logger.info("• Free energy minimization efficiency analysis")
    logger.info("• Information-theoretic learning metrics and pattern detection")
    logger.info("• Multi-phase behavioral analysis and interpretation")
    logger.info("• Professional visualization suite with interpretability dashboards")
    logger.info("• Automated pattern detection and convergence analysis")
    logger.info("• Comprehensive data export and reporting capabilities")
    
    logger.info("\nSimple Active Inference model with comprehensive analysis complete!")
    logger.info(f"Total steps analyzed: {len(analyzer.traces['beliefs'])}")
    logger.info(f"Analysis completed successfully at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main() 