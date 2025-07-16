#!/usr/bin/env python
"""
Ecological niche modeling using active inference.

This example demonstrates how to use GEO-INFER-ACT for ecological niche
modeling, where species adapt to environmental conditions through active
inference processes.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import os
import sys
import time
import logging
from typing import Dict, List, Tuple
from pathlib import Path

# Add parent directory to path to import GEO-INFER-ACT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geo_infer_act.api.interface import ActiveInferenceInterface
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer, create_shared_visualizations
from geo_infer_act.utils.visualization import (
    plot_belief_update, plot_policies, plot_free_energy,
    plot_perception_analysis, plot_action_analysis, create_interpretability_dashboard
)
from geo_infer_act.utils.math import entropy, assess_complexity, detect_stationarity, compute_surprise

# Setup logging for this script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
        # Create script-specific output directory
        self.script_name = "ecological_model"
        self.output_dir = Path(__file__).parent / 'output' / self.script_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Active Inference Analyzer
        self.analyzer = ActiveInferenceAnalyzer(output_dir=str(self.output_dir))
        
        # Initialize AI interface
        self.ai_interface = ActiveInferenceInterface(config_path)
        self.model_id = "eco_niche_model"
        
        # Enhanced environment and species parameters
        self.n_env_states = 5
        self.n_actions = 6
        self.environmental_drift = 0.02
        self.seasonal_variation = 0.1
        self.current_time = 0
        
        # Initialize model
        self._initialize_model()
        
        logger.info(f"EcologicalNicheModel initialized with output: {self.output_dir}")
        
    def _initialize_model(self):
        """Initialize the active inference model for ecological niche with enhanced parameters."""
        parameters = {
            "state_dim": self.n_env_states,
            "obs_dim": 4,  # Multi-dimensional environmental observations
            "prior_precision": 1.5,  # Higher precision for ecological sensitivity
            "learning_rate": 0.15,   # Faster adaptation for ecological dynamics
            "temporal_precision": 2.0,
            "enable_adaptation": True
        }
        
        self.ai_interface.create_model(
            model_id=self.model_id,
            model_type="categorical",
            parameters=parameters
        )
        
        # Set more complex preferences (species' preferred environmental conditions)
        preferences = {
            "observations": np.array([0.15, 0.4, 0.3, 0.15])
        }
        
        self.ai_interface.set_preferences(self.model_id, preferences)
        
        logger.info("Ecological niche model initialized with enhanced parameters")
        
    def observe_environment(self, timestep: int) -> np.ndarray:
        """
        Generate realistic environmental observations with temporal dynamics.
        
        Args:
            timestep: Current time step
            
        Returns:
            Environmental observation vector
        """
        # Base environmental conditions
        base_conditions = np.array([0.3, 0.4, 0.2, 0.1])
        
        # Add environmental drift (climate change effect)
        drift_effect = self.environmental_drift * timestep * np.array([0.5, -0.3, -0.2, 0.1])
        
        # Add seasonal variation
        seasonal_effect = self.seasonal_variation * np.sin(2 * np.pi * timestep / 20) * np.array([0.3, 0.4, 0.2, 0.1])
        
        # Add stochastic events
        if np.random.random() < 0.1:  # 10% chance of extreme event
            stochastic_effect = np.random.normal(0, 0.2, 4)
        else:
            stochastic_effect = np.random.normal(0, 0.05, 4)
        
        # Combine effects
        observation = base_conditions + drift_effect + seasonal_effect + stochastic_effect
        
        # Ensure valid probability distribution
        observation = np.clip(observation, 0.01, 0.99)
        observation = observation / observation.sum()
        
        return observation
        
    def update_beliefs(self, observation: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Update beliefs based on environmental observations.
        
        Args:
            observation: Observed environmental conditions
            
        Returns:
            Updated beliefs about the environment
        """
        # Format observation for the model
        formatted_obs = {"observations": observation}
        
        # Update beliefs with enhanced dynamics
        updated_beliefs = self.ai_interface.update_beliefs(
            self.model_id, formatted_obs
        )
        
        return updated_beliefs
        
    def select_adaptation(self) -> Dict[str, any]:
        """
        Select adaptation strategy based on current beliefs.
        
        Returns:
            Selected adaptation strategy
        """
        return self.ai_interface.select_policy(self.model_id)
    
    def run_simulation(self, n_timesteps: int = 30) -> Tuple[List[Dict], List[Dict], List[np.ndarray]]:
        """
        Run a simulation of niche adaptation over time with enhanced analysis.
        
        Args:
            n_timesteps: Number of time steps to simulate
            
        Returns:
            Tuple of (belief_history, adaptation_history, observation_history)
        """
        belief_history = []
        adaptation_history = []
        observation_history = []
        
        logger.info(f"Running ecological simulation with {n_timesteps} timesteps...")
        logger.info("Simulating species adaptation to changing environment...")
        
        start_time = time.time()
        
        for t in range(n_timesteps):
            self.current_time = t
            
            # Generate realistic environmental observation
            observation = self.observe_environment(t)
            observation_history.append(observation.copy())
            
            # Update beliefs with observation
            beliefs = self.update_beliefs(observation)
            belief_history.append(beliefs.copy())
            
            # Select adaptation
            adaptation = self.select_adaptation()
            adaptation_history.append(adaptation.copy())
            
            # Calculate free energy
            free_energy = self.ai_interface.get_free_energy(self.model_id)
            
            # Record step in analyzer
            self.analyzer.record_step(
                beliefs=beliefs['states'],
                observations=observation,
                actions=adaptation['policy']['id'],
                policies=adaptation,
                free_energy=free_energy,
                timestamp=time.time()
            )
            
            # Log detailed progress
            if t % 5 == 0 or t < 5:
                belief_entropy = entropy(beliefs['states'])
                surprise = compute_surprise(observation, beliefs['states'])
                
                logger.info(f"Timestep {t+1}/{n_timesteps}:")
                logger.info(f"  Environment: Temp={observation[0]:.3f}, Precip={observation[1]:.3f}, "
                          f"Resources={observation[2]:.3f}, Quality={observation[3]:.3f}")
                logger.info(f"  Belief entropy: {belief_entropy:.3f}")
                logger.info(f"  Surprise: {surprise:.3f}")
                logger.info(f"  Selected adaptation: Policy {adaptation['policy']['id']} "
                          f"(prob={adaptation['probability']:.3f})")
                logger.info(f"  Free energy: {free_energy:.4f}")
        
        simulation_time = time.time() - start_time
        logger.info(f"Simulation completed in {simulation_time:.2f} seconds")
        
        return belief_history, adaptation_history, observation_history
    
    def analyze_results(self, belief_history, adaptation_history, observation_history):
        """
        Comprehensive analysis of simulation results.
        
        Args:
            belief_history: History of beliefs
            adaptation_history: History of adaptations
            observation_history: History of environmental observations
        """
        logger.info("Starting comprehensive result analysis...")
        
        # Run all analyses
        perception_analysis = self.analyzer.analyze_perception_patterns()
        action_analysis = self.analyzer.analyze_action_selection_patterns()
        fe_analysis = self.analyzer.analyze_free_energy_patterns()
        
        # Ecological-specific analyses
        eco_analysis = self._analyze_ecological_patterns(belief_history, observation_history)
        
        # Save comprehensive data
        self.analyzer.save_traces_to_csv()
        
        # Generate shared visualizations
        create_shared_visualizations(self.analyzer)
        
        # Create ecological-specific visualizations
        self._create_ecological_visualizations(belief_history, adaptation_history, observation_history)
        
        # Create comprehensive perception and action analysis
        plot_perception_analysis(
            [b['states'] for b in belief_history],
            observation_history,
            self.output_dir,
            "Ecological Perception Analysis"
        )
        
        plot_action_analysis(
            adaptation_history,
            [a['policy']['id'] for a in adaptation_history],
            self.output_dir,
            "Ecological Action Selection Analysis"
        )
        
        # Create interpretability dashboard
        create_interpretability_dashboard(self.analyzer, self.output_dir)
        
        # Generate comprehensive report
        report = self.analyzer.generate_comprehensive_report()
        
        logger.info("Comprehensive analysis completed")
        return {
            'perception_analysis': perception_analysis,
            'action_analysis': action_analysis,
            'free_energy_analysis': fe_analysis,
            'ecological_analysis': eco_analysis,
            'report': report
        }
    
    def _analyze_ecological_patterns(self, belief_history, observation_history):
        """Analyze ecological-specific patterns."""
        beliefs_array = np.array([b['states'] for b in belief_history])
        obs_array = np.array(observation_history)
        
        # Adaptive capacity analysis
        belief_changes = np.diff(beliefs_array, axis=0)
        adaptive_capacity = np.mean(np.linalg.norm(belief_changes, axis=1))
        
        # Environmental tracking
        obs_changes = np.diff(obs_array, axis=0)
        env_variability = np.mean(np.linalg.norm(obs_changes, axis=1))
        
        # Species-environment coupling
        tracking_efficiency = adaptive_capacity / (env_variability + 1e-6)
        
        # Niche stability
        dominant_states = np.argmax(beliefs_array, axis=1)
        niche_switches = np.sum(np.diff(dominant_states) != 0)
        niche_stability = 1.0 - (niche_switches / len(beliefs_array))
        
        # Environmental stress detection
        stress_events = []
        for t, obs in enumerate(observation_history):
            # Detect deviations from preferred conditions
            preferred = np.array([0.15, 0.4, 0.3, 0.15])
            stress_level = np.linalg.norm(obs - preferred)
            if stress_level > 0.3:  # Threshold for stress
                stress_events.append({'timestep': t, 'stress_level': stress_level})
        
        # Complexity analysis
        belief_complexity = assess_complexity(beliefs_array)
        env_complexity = assess_complexity(obs_array)
        
        # Stationarity analysis
        belief_stationarity = detect_stationarity(np.mean(beliefs_array, axis=1))
        env_stationarity = detect_stationarity(np.mean(obs_array, axis=1))
        
        eco_analysis = {
            'adaptive_capacity': float(adaptive_capacity),
            'environmental_variability': float(env_variability),
            'tracking_efficiency': float(tracking_efficiency),
            'niche_stability': float(niche_stability),
            'niche_switches': int(niche_switches),
            'stress_events': stress_events,
            'belief_complexity': belief_complexity,
            'environmental_complexity': env_complexity,
            'belief_stationarity': belief_stationarity,
            'environmental_stationarity': env_stationarity
        }
        
        # Save ecological analysis
        self.analyzer._save_analysis(eco_analysis, 'ecological_analysis.json')
        
        return eco_analysis
    
    def _create_ecological_visualizations(self, belief_history, adaptation_history, observation_history):
        """Create ecological-specific visualizations."""
        beliefs_array = np.array([b['states'] for b in belief_history])
        obs_array = np.array(observation_history)
        
        # Enhanced ecological dynamics plot
        fig, axes = plt.subplots(3, 3, figsize=(18, 15))
        
        state_labels = ["Temp Sensitivity", "Water Dependency", "Resource Efficiency", 
                       "Habitat Selectivity", "Predator Avoidance"]
        obs_labels = ["Temperature", "Precipitation", "Resources", "Habitat Quality"]
        
        # 1. Belief evolution with environmental overlay
        ax1 = axes[0, 0]
        for i in range(self.n_env_states):
            ax1.plot(beliefs_array[:, i], label=state_labels[i], linewidth=2, marker='o', markersize=3)
        ax1.set_title('Species Belief Evolution', fontweight='bold')
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Belief Probability')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Environmental dynamics
        ax2 = axes[0, 1]
        for i in range(4):
            ax2.plot(obs_array[:, i], label=obs_labels[i], linewidth=2, marker='s', markersize=3)
        ax2.set_title('Environmental Dynamics', fontweight='bold')
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Environmental Value')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Species-environment coupling
        ax3 = axes[0, 2]
        belief_changes = np.diff(beliefs_array, axis=0)
        obs_changes = np.diff(obs_array, axis=0)
        belief_magnitude = np.linalg.norm(belief_changes, axis=1)
        env_magnitude = np.linalg.norm(obs_changes, axis=1)
        
        ax3.scatter(env_magnitude, belief_magnitude, alpha=0.6, s=50)
        ax3.plot([0, max(env_magnitude)], [0, max(env_magnitude)], 'r--', alpha=0.5, label='Perfect Tracking')
        ax3.set_title('Species-Environment Coupling', fontweight='bold')
        ax3.set_xlabel('Environmental Change Magnitude')
        ax3.set_ylabel('Belief Change Magnitude')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Niche breadth over time
        ax4 = axes[1, 0]
        niche_breadth = [entropy(beliefs) for beliefs in beliefs_array]
        ax4.plot(niche_breadth, linewidth=2, color='purple', marker='d', markersize=3)
        ax4.set_title('Ecological Niche Breadth', fontweight='bold')
        ax4.set_xlabel('Time Step')
        ax4.set_ylabel('Niche Breadth (Entropy)')
        ax4.grid(True, alpha=0.3)
        
        # 5. Environmental stress response
        ax5 = axes[1, 1]
        preferred = np.array([0.15, 0.4, 0.3, 0.15])
        stress_levels = [np.linalg.norm(obs - preferred) for obs in obs_array]
        adaptation_rates = [a['probability'] for a in adaptation_history]
        
        ax5_twin = ax5.twinx()
        line1 = ax5.plot(stress_levels, linewidth=2, color='red', label='Environmental Stress')
        line2 = ax5_twin.plot(adaptation_rates, linewidth=2, color='blue', label='Adaptation Rate')
        
        ax5.set_title('Stress Response', fontweight='bold')
        ax5.set_xlabel('Time Step')
        ax5.set_ylabel('Environmental Stress', color='red')
        ax5_twin.set_ylabel('Adaptation Rate', color='blue')
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax5.legend(lines, labels)
        ax5.grid(True, alpha=0.3)
        
        # 6. Policy adaptation patterns
        ax6 = axes[1, 2]
        policy_probs = np.array([a['all_probabilities'] for a in adaptation_history])
        policy_entropy = [-np.sum(probs * np.log(probs + 1e-8)) for probs in policy_probs]
        
        im6 = ax6.imshow(policy_probs.T, aspect='auto', cmap='viridis', interpolation='nearest')
        ax6.set_title('Adaptation Strategy Patterns', fontweight='bold')
        ax6.set_xlabel('Time Step')
        ax6.set_ylabel('Adaptation Strategy')
        plt.colorbar(im6, ax=ax6, label='Selection Probability')
        
        # 7. Fitness landscape
        ax7 = axes[2, 0]
        # Compute fitness proxy (inverse of stress + high probability adaptations)
        fitness_proxy = []
        for t, (stress, adaptation) in enumerate(zip(stress_levels, adaptation_history)):
            fitness = (1.0 / (1.0 + stress)) * adaptation['probability']
            fitness_proxy.append(fitness)
        
        ax7.plot(fitness_proxy, linewidth=2, color='green', marker='^', markersize=3)
        ax7.fill_between(range(len(fitness_proxy)), fitness_proxy, alpha=0.3, color='green')
        ax7.set_title('Ecological Fitness Proxy', fontweight='bold')
        ax7.set_xlabel('Time Step')
        ax7.set_ylabel('Fitness Proxy')
        ax7.grid(True, alpha=0.3)
        
        # 8. Environmental predictability
        ax8 = axes[2, 1]
        # Calculate environmental predictability using moving window correlation
        window_size = 5
        predictability = []
        for i in range(window_size, len(obs_array)):
            window = obs_array[i-window_size:i]
            if len(window) > 1:
                # Simple predictability measure: inverse of variance
                pred = 1.0 / (1.0 + np.mean(np.var(window, axis=0)))
                predictability.append(pred)
        
        if predictability:
            ax8.plot(range(window_size, len(obs_array)), predictability, 
                    linewidth=2, color='orange', marker='o', markersize=3)
            ax8.set_title('Environmental Predictability', fontweight='bold')
            ax8.set_xlabel('Time Step')
            ax8.set_ylabel('Predictability')
            ax8.grid(True, alpha=0.3)
        
        # 9. Adaptation efficiency
        ax9 = axes[2, 2]
        free_energies = self.analyzer.traces['free_energy']
        if len(free_energies) > 1:
            # Efficiency as rate of free energy reduction
            fe_changes = np.diff(free_energies)
            efficiency = []
            for i, (fe_change, stress) in enumerate(zip(fe_changes, stress_levels[1:])):
                # Higher efficiency = more FE reduction per unit stress
                eff = -fe_change / (stress + 1e-6)  # Negative because we want reduction
                efficiency.append(eff)
            
            ax9.plot(efficiency, linewidth=2, color='teal', marker='s', markersize=3)
            ax9.set_title('Adaptation Efficiency', fontweight='bold')
            ax9.set_xlabel('Time Step')
            ax9.set_ylabel('Efficiency (FE reduction/stress)')
            ax9.grid(True, alpha=0.3)
        
        plt.suptitle('Ecological Niche Dynamics Analysis', fontsize=20, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'ecological_dynamics_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Ecological visualizations saved to: {self.output_dir}")
    
    def print_final_analysis(self, analysis_results):
        """Print comprehensive final analysis results."""
        logger.info("\n" + "=" * 80)
        logger.info("COMPREHENSIVE ECOLOGICAL NICHE ANALYSIS")
        logger.info("=" * 80)
        
        # Basic metrics
        final_beliefs = self.analyzer.traces['beliefs'][-1]
        final_entropy = entropy(final_beliefs)
        final_free_energy = self.analyzer.traces['free_energy'][-1]
        
        logger.info(f"Final belief distribution:")
        state_labels = ["Temp Sensitivity", "Water Dependency", "Resource Efficiency", 
                       "Habitat Selectivity", "Predator Avoidance"]
        for i, (label, belief) in enumerate(zip(state_labels, final_beliefs)):
            logger.info(f"  {label}: {belief:.4f}")
        
        logger.info(f"\nKey Metrics:")
        logger.info(f"  Final belief entropy: {final_entropy:.4f}")
        logger.info(f"  Final free energy: {final_free_energy:.4f}")
        
        if len(self.analyzer.traces['free_energy']) > 1:
            fe_reduction = self.analyzer.traces['free_energy'][0] - final_free_energy
            logger.info(f"  Free energy reduction: {fe_reduction:.4f}")
        
        # Perception analysis
        if 'perception_analysis' in analysis_results:
            perc = analysis_results['perception_analysis']
            if 'perception_quality' in perc:
                quality = perc['perception_quality']
                logger.info(f"\nPerception Quality: {quality.get('quality_rating', 'Unknown')}")
                logger.info(f"  Responsiveness: {'Good' if not quality.get('is_flat', True) else 'Poor'}")
                logger.info(f"  Structure score: {quality.get('structure_score', 0):.3f}")
        
        # Action analysis
        if 'action_analysis' in analysis_results:
            action = analysis_results['action_analysis']
            if 'decision_quality' in action:
                decision = action['decision_quality']
                logger.info(f"\nDecision Quality: {decision.get('quality_rating', 'Unknown')}")
                logger.info(f"  Overall score: {decision.get('overall_quality_score', 0):.3f}")
        
        # Free energy analysis
        if 'free_energy_analysis' in analysis_results:
            fe = analysis_results['free_energy_analysis']
            if 'minimization_dynamics' in fe:
                fe_min = fe['minimization_dynamics']
                logger.info(f"\nFree Energy Dynamics: {fe_min.get('minimization_quality', 'Unknown')}")
                logger.info(f"  Total reduction: {fe_min.get('total_reduction', 0):.4f}")
                logger.info(f"  Efficiency: {fe_min.get('efficiency', 0):.4f}")
        
        # Ecological-specific analysis
        if 'ecological_analysis' in analysis_results:
            eco = analysis_results['ecological_analysis']
            logger.info(f"\nEcological Analysis:")
            logger.info(f"  Adaptive capacity: {eco.get('adaptive_capacity', 0):.4f}")
            logger.info(f"  Tracking efficiency: {eco.get('tracking_efficiency', 0):.4f}")
            logger.info(f"  Niche stability: {eco.get('niche_stability', 0):.4f}")
            logger.info(f"  Stress events: {len(eco.get('stress_events', []))}")
            
            if 'belief_complexity' in eco:
                complexity = eco['belief_complexity']
                logger.info(f"  Belief complexity: {complexity.get('overall_complexity', 0):.3f}")
        
        logger.info(f"\nComprehensive outputs saved to: {self.output_dir}")
        logger.info("Ecological adaptation simulation complete!")


def main():
    """Run an ecological niche modeling example with comprehensive analysis."""
    print("🌱 GEO-INFER-ACT: Comprehensive Ecological Niche Modeling")
    print("=" * 80)
    print("Simulating species adaptation to dynamic environmental conditions")
    print("Including climate change, seasonal variation, and stochastic events")
    print("With comprehensive analysis and pattern detection")
    print()
    
    # Initialize model
    config_path = os.path.join(os.path.dirname(__file__), '../config/example.yaml')
    eco_model = EcologicalNicheModel(config_path)
    
    # Run simulation with comprehensive logging
    logger.info("Starting ecological niche simulation...")
    belief_history, adaptation_history, observation_history = eco_model.run_simulation(n_timesteps=40)
    
    # Comprehensive analysis
    logger.info("Starting comprehensive analysis...")
    analysis_results = eco_model.analyze_results(belief_history, adaptation_history, observation_history)
    
    # Print final analysis
    eco_model.print_final_analysis(analysis_results)


if __name__ == "__main__":
    main() 