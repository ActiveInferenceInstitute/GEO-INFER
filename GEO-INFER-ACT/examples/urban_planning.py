#!/usr/bin/env python
"""
Urban planning example using active inference with comprehensive analysis.

This example demonstrates the use of GEO-INFER-ACT for urban planning,
where multiple stakeholders (agents) interact to allocate resources
and improve urban development outcomes. Enhanced with comprehensive
analysis, logging, and interpretability features.

Features:
- Multi-agent resource allocation and coordination
- Active inference for urban decision-making
- Comprehensive analysis and pattern detection
- Real-time logging and quality assessment
- Professional visualization suite
- Spatial-temporal dynamics modeling
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path
import matplotlib.cm as cm
from scipy.spatial.distance import cdist

# Add parent directory to path to import GEO-INFER-ACT
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geo_infer_act.api.interface import ActiveInferenceInterface
from geo_infer_act.utils.visualization import (
    plot_perception_analysis, plot_action_analysis, create_interpretability_dashboard
)
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer
from geo_infer_act.utils.math import (
    compute_surprise, compute_information_gain, assess_convergence,
    detect_stationarity, detect_periodicity, assess_complexity
)


def create_output_directory() -> Path:
    """Create timestamped output directory in the root /output folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create output in the repository root /output directory
    repo_root = Path(__file__).parent.parent.parent  # Go up from examples/urban_planning.py to repo root
    output_dir = repo_root / "output" / f"urban_planning_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def setup_logging() -> logging.Logger:
    """Set up comprehensive logging for the urban planning example."""
    # Create output directory
    output_dir = create_output_directory()
    
    # Configure logging
    log_file = output_dir / f'urban_planning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('UrbanActiveInference')
    logger.info("Urban Planning Active Inference - Comprehensive Analysis")
    logger.info("=" * 70)
    logger.info(f"Output directory: {output_dir}")
    
    return logger


class UrbanPlanningModel:
    """
    Urban planning model using Active Inference for multi-stakeholder coordination.
    
    This model simulates urban development with multiple agents (stakeholders)
    making decisions about resource allocation, infrastructure development,
    and policy implementation using Active Inference principles.
    """
    
    def __init__(self, n_locations: int = 6, n_resources: int = 4, n_agents: int = 3):
        """Initialize the urban planning model."""
        self.n_locations = n_locations
        self.n_resources = n_resources
        self.n_agents = n_agents
        
        # Create spatial grid for urban area
        self.location_coords = self._create_urban_grid()
        
        # Development constraints (initialize before agents need them)
        self.constraints = {
            'budget_limits': np.ones(n_agents) * 100.0,
            'zoning_restrictions': np.random.choice([0, 1], size=(n_locations, n_resources)),
            'environmental_limits': np.random.uniform(0.5, 1.0, n_locations)
        }
        
        # Initialize resource distribution
        self.resource_distribution = self._initialize_resources()
        
        # Initialize agent states
        self.agent_states = self._initialize_agents()
        
        # Urban quality metrics
        self.urban_quality = {
            'infrastructure': np.random.uniform(0.3, 0.7, n_locations),
            'accessibility': np.random.uniform(0.2, 0.8, n_locations),
            'sustainability': np.random.uniform(0.4, 0.6, n_locations),
            'social_equity': np.random.uniform(0.3, 0.8, n_locations)
        }
        
    def _create_urban_grid(self) -> np.ndarray:
        """Create a spatial grid representing urban locations."""
        # Create a 2D grid of urban locations
        grid_size = int(np.ceil(np.sqrt(self.n_locations)))
        x, y = np.meshgrid(np.linspace(0, 10, grid_size), np.linspace(0, 10, grid_size))
        coords = np.column_stack([x.ravel(), y.ravel()])[:self.n_locations]
        return coords
    
    def _initialize_resources(self) -> np.ndarray:
        """Initialize resource distribution across locations."""
        # Resources: Housing, Commercial, Transportation, Green Space
        base_resources = np.random.uniform(0.1, 1.0, (self.n_resources, self.n_locations))
        
        # Add spatial correlation (resources tend to cluster)
        for i in range(self.n_resources):
            # Add some clustering based on distance
            center = np.random.randint(0, self.n_locations)
            distances = cdist([self.location_coords[center]], self.location_coords)[0]
            decay = np.exp(-distances / 3.0)
            base_resources[i] *= (0.5 + 0.5 * decay)
        
        return base_resources
    
    def _initialize_agents(self) -> List[Dict]:
        """Initialize agent states and preferences."""
        agent_types = ['Government', 'Developer', 'Community']
        agents = []
        
        for i in range(self.n_agents):
            agent = {
                'id': i,
                'type': agent_types[i % len(agent_types)],
                'location': np.random.randint(0, self.n_locations),
                'budget': self.constraints['budget_limits'][i],
                'priorities': np.random.dirichlet(np.ones(self.n_resources)),
                'satisfaction': 0.5,
                'cooperation_level': np.random.uniform(0.3, 0.9)
            }
            agents.append(agent)
        
        return agents
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current state of the urban system."""
        # Calculate overall urban metrics
        overall_quality = np.mean([
            np.mean(self.urban_quality['infrastructure']),
            np.mean(self.urban_quality['accessibility']),
            np.mean(self.urban_quality['sustainability']),
            np.mean(self.urban_quality['social_equity'])
        ])
        
        # Resource utilization
        resource_utilization = np.sum(self.resource_distribution, axis=1) / self.n_locations
        
        # Agent cooperation index
        cooperation_index = np.mean([agent['cooperation_level'] for agent in self.agent_states])
        
        return {
            'resource_distribution': self.resource_distribution.flatten(),
            'overall_quality': overall_quality,
            'resource_utilization': resource_utilization,
            'cooperation_index': cooperation_index,
            'agent_locations': [agent['location'] for agent in self.agent_states],
            'agent_satisfaction': [agent['satisfaction'] for agent in self.agent_states]
        }
    
    def apply_development_action(self, agent_id: int, action: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a development action and return the resulting state."""
        agent = self.agent_states[agent_id]
        location = action.get('location', agent['location'])
        resource_type = action.get('resource_type', 0)
        investment = action.get('investment', 10.0)
        
        # Check constraints
        if (investment > agent['budget'] or 
            not self.constraints['zoning_restrictions'][location, resource_type]):
            return {'success': False, 'reason': 'constraint_violation'}
        
        # Update resource distribution
        efficiency = self.constraints['environmental_limits'][location]
        actual_impact = investment * efficiency * agent['cooperation_level']
        
        self.resource_distribution[resource_type, location] += actual_impact * 0.1
        
        # Update agent budget and satisfaction
        agent['budget'] -= investment
        
        # Calculate satisfaction based on alignment with priorities
        priority_alignment = agent['priorities'][resource_type]
        satisfaction_change = (actual_impact * priority_alignment - investment * 0.01) * 0.1
        agent['satisfaction'] = np.clip(agent['satisfaction'] + satisfaction_change, 0, 1)
        
        # Update urban quality based on development
        quality_improvements = {
            0: {'infrastructure': 0.05, 'accessibility': 0.02},  # Housing
            1: {'infrastructure': 0.03, 'accessibility': 0.05, 'social_equity': 0.02},  # Commercial
            2: {'accessibility': 0.08, 'infrastructure': 0.04},  # Transportation
            3: {'sustainability': 0.06, 'social_equity': 0.03}   # Green Space
        }
        
        if resource_type in quality_improvements:
            for quality_type, improvement in quality_improvements[resource_type].items():
                self.urban_quality[quality_type][location] += improvement * actual_impact * 0.01
                self.urban_quality[quality_type][location] = np.clip(
                    self.urban_quality[quality_type][location], 0, 1
                )
        
        return {
            'success': True,
            'impact': actual_impact,
            'satisfaction_change': satisfaction_change,
            'new_state': self.get_current_state()
        }


def create_urban_observation(urban_state: Dict[str, Any], agent_id: int) -> np.ndarray:
    """Create an observation vector for an agent based on urban state."""
    # Observation includes: local quality, resource availability, cooperation level
    local_quality = urban_state['overall_quality']
    resource_availability = np.mean(urban_state['resource_utilization'])
    cooperation = urban_state['cooperation_index']
    
    # Add agent-specific perspective
    agent_satisfaction = urban_state['agent_satisfaction'][agent_id]
    
    # Discretize observations for categorical model
    obs_vector = np.zeros(4)
    
    # Quality level observation
    if local_quality > 0.7:
        obs_vector[0] = 1.0  # High quality
    elif local_quality > 0.4:
        obs_vector[1] = 1.0  # Medium quality
    else:
        obs_vector[2] = 1.0  # Low quality
    
    # Cooperation observation
    if cooperation > 0.6:
        obs_vector[3] = 0.3  # High cooperation bonus
    
    return obs_vector


def plot_urban_analysis(urban_model: UrbanPlanningModel, 
                       step: int, 
                       save_dir: str,
                       analysis_history: List[Dict]) -> None:
    """Create comprehensive urban planning analysis visualization."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Resource distribution heatmap
    im1 = axes[0, 0].imshow(urban_model.resource_distribution, cmap='viridis', aspect='auto')
    axes[0, 0].set_title('Resource Distribution Across Locations', fontweight='bold')
    axes[0, 0].set_xlabel('Locations')
    axes[0, 0].set_ylabel('Resource Types\n(0:Housing, 1:Commercial,\n2:Transport, 3:Green)')
    plt.colorbar(im1, ax=axes[0, 0])
    
    # Urban quality radar chart
    qualities = ['Infrastructure', 'Accessibility', 'Sustainability', 'Social Equity']
    quality_keys = ['infrastructure', 'accessibility', 'sustainability', 'social_equity']
    quality_values = [np.mean(urban_model.urban_quality[key]) for key in quality_keys]
    
    angles = np.linspace(0, 2*np.pi, len(qualities), endpoint=False).tolist()
    quality_values += quality_values[:1]  # Complete the circle
    angles += angles[:1]
    
    axes[0, 1].plot(angles, quality_values, 'o-', linewidth=2, color='blue')
    axes[0, 1].fill(angles, quality_values, alpha=0.25, color='blue')
    axes[0, 1].set_xticks(angles[:-1])
    axes[0, 1].set_xticklabels(qualities)
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].set_title('Urban Quality Assessment', fontweight='bold')
    axes[0, 1].grid(True)
    
    # Agent satisfaction over time
    if len(analysis_history) > 1:
        satisfaction_data = []
        for hist in analysis_history:
            if 'agent_satisfaction' in hist:
                satisfaction_data.append(hist['agent_satisfaction'])
        
        if satisfaction_data:
            satisfaction_array = np.array(satisfaction_data)
            for i in range(satisfaction_array.shape[1]):
                axes[0, 2].plot(satisfaction_array[:, i], 
                              label=f'Agent {i} ({urban_model.agent_states[i]["type"]})',
                              linewidth=2, marker='o')
        
        axes[0, 2].set_title('Agent Satisfaction Evolution', fontweight='bold')
        axes[0, 2].set_xlabel('Time Steps')
        axes[0, 2].set_ylabel('Satisfaction Level')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
    
    # Spatial visualization of locations
    coords = urban_model.location_coords
    overall_quality = [np.mean([urban_model.urban_quality[q][i] for q in urban_model.urban_quality.keys()]) 
                      for i in range(urban_model.n_locations)]
    
    scatter = axes[1, 0].scatter(coords[:, 0], coords[:, 1], 
                                c=overall_quality, s=200, cmap='RdYlGn', alpha=0.7)
    
    # Add agent locations
    for agent in urban_model.agent_states:
        agent_coord = coords[agent['location']]
        axes[1, 0].plot(agent_coord[0], agent_coord[1], 
                       marker='*', markersize=15, color='black', 
                       label=f"Agent {agent['id']} ({agent['type']})")
    
    axes[1, 0].set_title('Spatial Urban Quality & Agent Locations', fontweight='bold')
    axes[1, 0].set_xlabel('X Coordinate')
    axes[1, 0].set_ylabel('Y Coordinate')
    axes[1, 0].legend()
    plt.colorbar(scatter, ax=axes[1, 0], label='Overall Quality')
    
    # Resource utilization efficiency
    resource_names = ['Housing', 'Commercial', 'Transport', 'Green Space']
    utilization = np.sum(urban_model.resource_distribution, axis=1)
    efficiency = utilization / np.max(utilization)
    
    bars = axes[1, 1].bar(resource_names, efficiency, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
    axes[1, 1].set_title('Resource Utilization Efficiency', fontweight='bold')
    axes[1, 1].set_ylabel('Relative Efficiency')
    axes[1, 1].set_ylim(0, 1)
    
    # Add value labels on bars
    for bar, eff in zip(bars, efficiency):
        axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{eff:.2f}', ha='center', va='bottom')
    
    # Development impact timeline
    if len(analysis_history) > 1:
        quality_timeline = []
        cooperation_timeline = []
        
        for hist in analysis_history:
            quality_timeline.append(hist.get('overall_quality', 0.5))
            cooperation_timeline.append(hist.get('cooperation_index', 0.5))
        
        ax2 = axes[1, 2]
        ax2.plot(quality_timeline, label='Overall Quality', linewidth=2, color='blue', marker='o')
        ax2.set_ylabel('Overall Quality', color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
        ax3 = ax2.twinx()
        ax3.plot(cooperation_timeline, label='Cooperation Index', linewidth=2, color='red', marker='s')
        ax3.set_ylabel('Cooperation Index', color='red')
        ax3.tick_params(axis='y', labelcolor='red')
        
        axes[1, 2].set_title('Urban Development Timeline', fontweight='bold')
        axes[1, 2].set_xlabel('Time Steps')
        axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f'urban_analysis_step_{step}.png'), dpi=300, bbox_inches='tight')
    plt.close()


def main():
    """Run comprehensive urban planning example with Active Inference."""
    # Set up logging
    logger = setup_logging()
    output_dir = create_output_directory()
    
    logger.info("Starting Urban Planning Active Inference Model")
    logger.info("Multi-agent resource allocation and coordination simulation")
    
    # 1. Initialize urban planning model
    n_locations = 6
    n_resources = 4  # Housing, Commercial, Transportation, Green Space
    n_agents = 3     # Government, Developer, Community Representative
    
    urban_model = UrbanPlanningModel(n_locations, n_resources, n_agents)
    logger.info(f"Initialized urban model: {n_locations} locations, {n_resources} resources, {n_agents} agents")
    
    # 2. Create Active Inference models for each agent
    config_path = os.path.join(os.path.dirname(__file__), '../config/example.yaml')
    ai_interface = ActiveInferenceInterface(config_path)
    
    # Create models for each agent type
    agent_models = {}
    analyzers = {}
    
    for i, agent in enumerate(urban_model.agent_states):
        model_id = f"agent_{i}_{agent['type'].lower()}"
        
        # Different agent types have different model parameters
        if agent['type'] == 'Government':
            parameters = {
                "state_dim": 5,  # Planning, Implementation, Evaluation, Coordination, Budget
                "obs_dim": 4,    # Quality, Resources, Cooperation, Satisfaction
                "prior_precision": 1.5,
                "learning_rate": 0.08,
                "enable_adaptation": True
            }
        elif agent['type'] == 'Developer':
            parameters = {
                "state_dim": 4,  # Investment, Development, Marketing, Profit
                "obs_dim": 4,
                "prior_precision": 1.2,
                "learning_rate": 0.12,
                "enable_adaptation": True
            }
        else:  # Community
            parameters = {
                "state_dim": 4,  # Advocacy, Participation, Satisfaction, Resistance
                "obs_dim": 4,
                "prior_precision": 1.0,
                "learning_rate": 0.15,
                "enable_adaptation": True
            }
        
        ai_interface.create_model(model_id, "categorical", parameters)
        agent_models[i] = model_id
        
        # Set agent-specific preferences
        if agent['type'] == 'Government':
            preferences = {"observations": np.array([0.3, 0.3, 0.3, 0.1])}  # Balanced development
        elif agent['type'] == 'Developer':
            preferences = {"observations": np.array([0.1, 0.4, 0.4, 0.1])}  # Profit-focused
        else:  # Community
            preferences = {"observations": np.array([0.4, 0.2, 0.2, 0.2])}  # Quality-focused
        
        ai_interface.set_preferences(model_id, preferences)
        
        # Initialize analyzer for each agent
        analyzers[i] = ActiveInferenceAnalyzer(
            output_dir=str(output_dir / f'agent_{i}')
        )
        
        logger.info(f"Created model for {agent['type']} agent (ID: {i})")
    
    # 3. Run urban development simulation
    n_steps = 20
    logger.info(f"Running urban development simulation for {n_steps} steps...")
    
    analysis_history = []
    
    for step in range(n_steps):
        step_start_time = datetime.now()
        logger.info(f"\n--- Step {step + 1}/{n_steps} ---")
        
        # Get current urban state
        current_state = urban_model.get_current_state()
        analysis_history.append(current_state.copy())
        
        logger.info(f"Overall urban quality: {current_state['overall_quality']:.3f}")
        logger.info(f"Cooperation index: {current_state['cooperation_index']:.3f}")
        
        # Each agent makes decisions based on Active Inference
        for agent_id, agent in enumerate(urban_model.agent_states):
            model_id = agent_models[agent_id]
            
            # Create observation for this agent
            observation = create_urban_observation(current_state, agent_id)
            
            # Get pre-update state for analysis
            pre_beliefs = ai_interface.models[model_id].beliefs['states'].copy()
            pre_free_energy = ai_interface.get_free_energy(model_id)
            
            # Update beliefs
            observation_dict = {"observations": observation}
            updated_beliefs = ai_interface.update_beliefs(model_id, observation_dict)
            post_free_energy = ai_interface.get_free_energy(model_id)
            
            # Select policy/action
            policy_result = ai_interface.select_policy(model_id)
            
            # Convert policy to urban development action
            policy_id = policy_result['policy']['id']
            action = {
                'location': np.random.randint(0, n_locations),
                'resource_type': policy_id % n_resources,
                'investment': min(agent['budget'] * 0.2, 25.0)
            }
            
            # Apply action to urban model
            result = urban_model.apply_development_action(agent_id, action)
            
            # Calculate analytical metrics
            surprise = compute_surprise(pre_beliefs, observation, sigma=0.1)
            
            # Calculate entropies for information gain
            prior_entropy = -np.sum(pre_beliefs * np.log(pre_beliefs + 1e-8))
            posterior_entropy = -np.sum(updated_beliefs['states'] * np.log(updated_beliefs['states'] + 1e-8))
            info_gain = compute_information_gain(prior_entropy, posterior_entropy)
            belief_entropy = posterior_entropy
            
            # Log agent decision
            logger.info(f"  Agent {agent_id} ({agent['type']}):")
            logger.info(f"    Observation: {observation}")
            logger.info(f"    Belief entropy: {belief_entropy:.4f}")
            logger.info(f"    Surprise: {surprise:.4f}")
            logger.info(f"    Information gain: {info_gain:.4f}")
            logger.info(f"    Free energy change: {pre_free_energy:.4f} → {post_free_energy:.4f}")
            logger.info(f"    Action: Invest {action['investment']:.1f} in {['Housing','Commercial','Transport','Green'][action['resource_type']]} at location {action['location']}")
            logger.info(f"    Action success: {result['success']}")
            logger.info(f"    Satisfaction: {agent['satisfaction']:.3f}")
            
            # Record step in analyzer
            step_data = {
                'agent_type': agent['type'],
                'action_location': action['location'],
                'action_resource_type': action['resource_type'],
                'action_investment': action['investment'],
                'action_success': result['success'],
                'surprise': surprise,
                'information_gain': info_gain,
                'belief_entropy': belief_entropy,
                'free_energy_change': post_free_energy - pre_free_energy,
                'agent_satisfaction': agent['satisfaction'],
                'cooperation_level': agent['cooperation_level'],
                'urban_quality': current_state['overall_quality'],
                'step_duration': (datetime.now() - step_start_time).total_seconds()
            }
            
            # Include step_data in the policies dictionary
            policies_with_data = policy_result.copy()
            policies_with_data.update(step_data)
            
            analyzers[agent_id].record_step(
                beliefs=updated_beliefs['states'],
                observations=observation,
                actions=np.array([policy_id]),
                policies=policies_with_data,
                free_energy=post_free_energy
            )
        
        # Create urban analysis visualization every 5 steps
        if (step + 1) % 5 == 0 or step == n_steps - 1:
            plot_urban_analysis(urban_model, step + 1, output_dir, analysis_history)
            logger.info(f"    Generated urban analysis visualization")
    
    # 4. Comprehensive post-simulation analysis
    logger.info("\n" + "=" * 70)
    logger.info("COMPREHENSIVE URBAN PLANNING ANALYSIS")
    logger.info("=" * 70)
    
    # Analyze each agent
    agent_analyses = {}
    for agent_id in range(n_agents):
        agent = urban_model.agent_states[agent_id]
        analyzer = analyzers[agent_id]
        
        logger.info(f"\nAGENT {agent_id} ({agent['type']}) ANALYSIS:")
        
        # Generate analysis reports
        perception_analysis = analyzer.analyze_perception_patterns()
        action_analysis = analyzer.analyze_action_selection_patterns()
        free_energy_analysis = analyzer.analyze_free_energy_patterns()
        
        agent_analyses[agent_id] = {
            'perception': perception_analysis,
            'action': action_analysis,
            'free_energy': free_energy_analysis
        }
        
        # Handle missing keys gracefully
        perception_quality = perception_analysis.get('perception_quality', {}).get('quality_rating', 'Unknown')
        action_consistency = action_analysis.get('action_consistency', {}).get('consistency_score', 0.0)
        fe_efficiency = free_energy_analysis.get('minimization_dynamics', {}).get('efficiency', 0.0)
        
        logger.info(f"  Perception quality: {perception_quality}")
        logger.info(f"  Action consistency: {action_consistency:.3f}")
        logger.info(f"  Free energy efficiency: {fe_efficiency:.3f}")
        logger.info(f"  Final satisfaction: {agent['satisfaction']:.3f}")
        logger.info(f"  Remaining budget: {agent['budget']:.1f}")
        
        # Create individual agent analysis visualizations
        agent_output_dir = output_dir / f'agent_{agent_id}'
        agent_output_dir.mkdir(parents=True, exist_ok=True)
        
        plot_perception_analysis(
            analyzer.traces['beliefs'],
            analyzer.traces['observations'],
            Path(agent_output_dir),
            title=f"Agent {agent_id} ({agent['type']}): Perception Analysis"
        )
        
        plot_action_analysis(
            analyzer.traces['policies'],
            analyzer.traces['actions'],
            Path(agent_output_dir),
            title=f"Agent {agent_id} ({agent['type']}): Action Analysis"
        )
        
        # Export individual agent data
        analyzer.save_traces_to_csv()
    
    # 5. System-wide analysis
    logger.info("\nSYSTEM-WIDE URBAN DEVELOPMENT ANALYSIS:")
    
    final_state = urban_model.get_current_state()
    initial_state = analysis_history[0]
    
    # Urban quality improvement
    quality_improvement = final_state['overall_quality'] - initial_state['overall_quality']
    cooperation_change = final_state['cooperation_index'] - initial_state['cooperation_index']
    
    logger.info(f"  Urban quality change: {initial_state['overall_quality']:.3f} → {final_state['overall_quality']:.3f} (Δ={quality_improvement:+.3f})")
    logger.info(f"  Cooperation change: {initial_state['cooperation_index']:.3f} → {final_state['cooperation_index']:.3f} (Δ={cooperation_change:+.3f})")
    
    # Resource development efficiency
    resource_names = ['Housing', 'Commercial', 'Transport', 'Green Space']
    for i, resource in enumerate(resource_names):
        initial_total = np.sum(initial_state['resource_distribution'][i::n_resources])
        final_total = np.sum(final_state['resource_distribution'][i::n_resources])
        development = final_total - initial_total
        logger.info(f"  {resource} development: {development:+.2f}")
    
    # Agent satisfaction analysis
    avg_satisfaction = np.mean([agent['satisfaction'] for agent in urban_model.agent_states])
    satisfaction_std = np.std([agent['satisfaction'] for agent in urban_model.agent_states])
    logger.info(f"  Average agent satisfaction: {avg_satisfaction:.3f} (±{satisfaction_std:.3f})")
    
    # Development equity analysis
    location_qualities = []
    for i in range(n_locations):
        location_quality = np.mean([urban_model.urban_quality[q][i] for q in urban_model.urban_quality.keys()])
        location_qualities.append(location_quality)
    
    equity_score = 1.0 - np.std(location_qualities)  # Higher when more equal
    logger.info(f"  Development equity score: {equity_score:.3f}")
    
    # Create comprehensive summary visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Agent performance comparison
    agent_metrics = []
    agent_labels = []
    for agent_id in range(n_agents):
        agent = urban_model.agent_states[agent_id]
        analysis = agent_analyses[agent_id]
        
        # Extract metrics with safe access
        perception_score = analysis.get('perception', {}).get('perception_quality', {}).get('structure_score', 0.5)
        action_score = analysis.get('action', {}).get('action_consistency', {}).get('consistency_score', 0.5)
        fe_score = analysis.get('free_energy', {}).get('minimization_dynamics', {}).get('efficiency', 0.5)
        
        metrics = [
            perception_score,
            action_score,
            fe_score,
            agent['satisfaction']
        ]
        agent_metrics.append(metrics)
        agent_labels.append(f"Agent {agent_id}\n({agent['type']})")
    
    metric_names = ['Perception\nQuality', 'Action\nConsistency', 'Free Energy\nEfficiency', 'Final\nSatisfaction']
    x = np.arange(len(metric_names))
    width = 0.25
    
    for i, (metrics, label) in enumerate(zip(agent_metrics, agent_labels)):
        axes[0, 0].bar(x + i*width - width, metrics, width, label=label, alpha=0.8)
    
    axes[0, 0].set_xlabel('Metrics')
    axes[0, 0].set_ylabel('Score')
    axes[0, 0].set_title('Agent Performance Comparison', fontweight='bold')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(metric_names)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Urban quality evolution
    quality_timeline = [state['overall_quality'] for state in analysis_history]
    axes[0, 1].plot(quality_timeline, linewidth=3, color='green', marker='o')
    axes[0, 1].set_xlabel('Time Steps')
    axes[0, 1].set_ylabel('Overall Urban Quality')
    axes[0, 1].set_title('Urban Quality Evolution', fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Final urban quality by location
    final_location_qualities = location_qualities
    axes[1, 0].bar(range(n_locations), final_location_qualities, color='skyblue', alpha=0.8)
    axes[1, 0].axhline(np.mean(final_location_qualities), color='red', linestyle='--', 
                      label=f'Mean: {np.mean(final_location_qualities):.3f}')
    axes[1, 0].set_xlabel('Location')
    axes[1, 0].set_ylabel('Quality Score')
    axes[1, 0].set_title('Final Quality by Location', fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Resource distribution summary
    final_resources = np.sum(urban_model.resource_distribution, axis=1)
    axes[1, 1].pie(final_resources, labels=resource_names, autopct='%1.1f%%', startangle=90)
    axes[1, 1].set_title('Final Resource Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'urban_planning_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Export comprehensive data and reports
    logger.info("\nExporting comprehensive analysis data...")
    
    # Export system-wide analysis
    system_data = {
        'timeline': analysis_history,
        'agent_analyses': agent_analyses,
        'final_metrics': {
            'quality_improvement': quality_improvement,
            'cooperation_change': cooperation_change,
            'avg_satisfaction': avg_satisfaction,
            'equity_score': equity_score,
            'location_qualities': location_qualities
        }
    }
    
    import json
    with open(output_dir / 'system_analysis.json', 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.float64):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        json.dump(convert_numpy(system_data), f, indent=2)
    
    # Generate comprehensive report
    report_lines = [
        "URBAN PLANNING ACTIVE INFERENCE - COMPREHENSIVE ANALYSIS REPORT",
        "=" * 70,
        f"\nSimulation Parameters:",
        f"  Locations: {n_locations}",
        f"  Resources: {n_resources}",
        f"  Agents: {n_agents}",
        f"  Time Steps: {n_steps}",
        f"\nFinal System State:",
        f"  Overall Urban Quality: {final_state['overall_quality']:.3f}",
        f"  Quality Improvement: {quality_improvement:+.3f}",
        f"  Cooperation Index: {final_state['cooperation_index']:.3f}",
        f"  Average Agent Satisfaction: {avg_satisfaction:.3f}",
        f"  Development Equity Score: {equity_score:.3f}",
        f"\nAgent Performance Summary:"
    ]
    
    for agent_id in range(n_agents):
        agent = urban_model.agent_states[agent_id]
        analysis = agent_analyses[agent_id]
        # Extract metrics safely for report
        perception_rating = analysis.get('perception', {}).get('perception_quality', {}).get('quality_rating', 'Unknown')
        action_consistency = analysis.get('action', {}).get('action_consistency', {}).get('consistency_score', 0.0)
        fe_efficiency = analysis.get('free_energy', {}).get('minimization_dynamics', {}).get('efficiency', 0.0)
        
        report_lines.extend([
            f"\n  Agent {agent_id} ({agent['type']}):",
            f"    Perception Quality: {perception_rating}",
            f"    Action Consistency: {action_consistency:.3f}",
            f"    Free Energy Efficiency: {fe_efficiency:.3f}",
            f"    Final Satisfaction: {agent['satisfaction']:.3f}",
            f"    Budget Utilization: {((100 - agent['budget']) / 100 * 100):.1f}%"
        ])
    
    report_lines.extend([
        f"\nResource Development Summary:",
        *[f"  {resource}: {np.sum(urban_model.resource_distribution[i]):.2f}" 
          for i, resource in enumerate(resource_names)],
        f"\nKey Insights:",
        f"  • Quality improvement of {quality_improvement:+.3f} achieved through coordinated development",
        f"  • Agent cooperation {'improved' if cooperation_change > 0 else 'declined'} by {abs(cooperation_change):.3f}",
        f"  • Development equity score of {equity_score:.3f} indicates {'balanced' if equity_score > 0.7 else 'uneven'} growth",
        f"  • Most effective agent: {max(range(n_agents), key=lambda i: agent_analyses[i]['free_energy'].get('minimization_dynamics', {}).get('efficiency', 0))} ({urban_model.agent_states[max(range(n_agents), key=lambda i: agent_analyses[i]['free_energy'].get('minimization_dynamics', {}).get('efficiency', 0))]['type']})",
        f"\nAnalysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ])
    
    report_content = '\n'.join(report_lines)
    
    with open(output_dir / 'comprehensive_report.txt', 'w') as f:
        f.write(report_content)
    
    logger.info("\nFEATURES DEMONSTRATED:")
    logger.info("• Multi-agent Active Inference coordination for urban planning")
    logger.info("• Comprehensive stakeholder behavior analysis and pattern detection")
    logger.info("• Real-time resource allocation optimization with constraint handling")
    logger.info("• Spatial-temporal urban development modeling and quality assessment")
    logger.info("• Agent-specific preference learning and satisfaction tracking")
    logger.info("• System-wide cooperation dynamics and equity analysis")
    logger.info("• Professional visualization suite for urban planning insights")
    logger.info("• Comprehensive data export and reporting for policy analysis")
    
    logger.info(f"\nUrban Planning Active Inference simulation complete!")
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"Total simulation time: {n_steps} steps")
    logger.info(f"Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main() 