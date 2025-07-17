"""
Advanced Geospatial Active Inference Methods

This module implements sophisticated geospatial active inference algorithms for
environmental modeling, resource optimization, predictive spatial dynamics, and
multi-scale hierarchical analysis. Integrates Active Inference principles with
cutting-edge geospatial analysis techniques.

Mathematical Foundation:
The geospatial active inference framework extends the free energy principle to
spatial domains by modeling:
1. Spatial generative models with environmental dynamics
2. Multi-scale hierarchical belief propagation
3. Spatial-temporal predictive coding
4. Resource allocation under environmental uncertainty

Key Components:
- Environmental Active Inference Engine
- Multi-scale Hierarchical Spatial Models
- Resource Optimization under Uncertainty
- Predictive Environmental Dynamics
- Spatial Attention Mechanisms
- H3-based Hexagonal Grid Analysis
"""

import numpy as np
import h3
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
import logging
from scipy import spatial, optimize, stats
from collections import defaultdict
import networkx as nx
from sklearn.cluster import DBSCAN
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentalState:
    """Represents environmental state at a spatial location."""
    location: str  # H3 cell ID
    temperature: float = 20.0
    humidity: float = 0.5
    vegetation_density: float = 0.5
    water_availability: float = 0.5
    soil_quality: float = 0.5
    biodiversity_index: float = 0.5
    human_activity: float = 0.0
    carbon_flux: float = 0.0
    timestamp: Optional[float] = None
    uncertainty: Dict[str, float] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Represents resource allocation decision."""
    location: str
    resource_type: str
    allocation_amount: float
    priority_score: float
    expected_benefit: float
    uncertainty: float
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpatialPrediction:
    """Spatial prediction with uncertainty quantification."""
    location: str
    predicted_value: float
    uncertainty: float
    confidence_interval: Tuple[float, float]
    prediction_horizon: float
    contributing_factors: Dict[str, float] = field(default_factory=dict)


class EnvironmentalActiveInferenceEngine:
    """
    Advanced environmental modeling using Active Inference principles.
    
    This engine models environmental dynamics as a hierarchical generative model
    where environmental states generate observations through complex spatial-temporal
    processes. The engine uses variational free energy minimization to:
    
    1. Learn environmental dynamics from observations
    2. Predict future environmental states
    3. Optimize resource allocation decisions
    4. Quantify environmental uncertainty
    
    Mathematical Framework:
    The environmental generative model is:
    p(o,s,a) = p(o|s)p(s|s',a)p(a|π)p(s')
    
    Where:
    - o: environmental observations (temperature, vegetation, etc.)
    - s: hidden environmental states
    - a: environmental actions/interventions
    - π: environmental policy (resource allocation strategy)
    """
    
    def __init__(self, 
                 h3_resolution: int = 8,
                 environmental_variables: List[str] = None,
                 prediction_horizon: int = 10,
                 uncertainty_threshold: float = 0.1):
        """
        Initialize Environmental Active Inference Engine.
        
        Args:
            h3_resolution: H3 hexagonal grid resolution for spatial modeling
            environmental_variables: List of environmental variables to model
            prediction_horizon: Number of timesteps for predictions
            uncertainty_threshold: Threshold for high uncertainty detection
        """
        self.h3_resolution = h3_resolution
        self.environmental_variables = environmental_variables or [
            'temperature', 'humidity', 'vegetation_density', 'water_availability',
            'soil_quality', 'biodiversity_index', 'carbon_flux'
        ]
        self.prediction_horizon = prediction_horizon
        self.uncertainty_threshold = uncertainty_threshold
        
        # Initialize internal models
        self.spatial_graph = None
        self.environmental_states = {}
        self.observation_history = []
        self.prediction_models = {}
        self.resource_optimizer = None
        
        # Gaussian Process models for each environmental variable
        self._initialize_gp_models()
        
        logger.info(f"Initialized EnvironmentalActiveInferenceEngine with {len(self.environmental_variables)} variables")
    
    def _initialize_gp_models(self):
        """Initialize Gaussian Process models for environmental prediction."""
        self.gp_models = {}
        
        for var in self.environmental_variables:
            # Use Matern kernel for environmental modeling (captures spatial correlations)
            kernel = Matern(length_scale=1.0, nu=2.5) + WhiteKernel(noise_level=0.01)
            self.gp_models[var] = GaussianProcessRegressor(
                kernel=kernel,
                alpha=1e-6,
                normalize_y=True,
                n_restarts_optimizer=5
            )
    
    def initialize_spatial_domain(self, boundary: Dict[str, Any]) -> None:
        """
        Initialize spatial domain using H3 hexagonal grid.
        
        Args:
            boundary: GeoJSON boundary specification
        """
        try:
            # Generate H3 cells within boundary
            h3_cells = self._generate_h3_cells_from_boundary(boundary)
            
            # Initialize environmental states
            for cell in h3_cells:
                self.environmental_states[cell] = EnvironmentalState(
                    location=cell,
                    timestamp=0.0
                )
            
            # Create spatial graph for neighbor relationships
            self.spatial_graph = self._create_h3_spatial_graph(h3_cells, max_neighbor_distance=3)
            
            logger.info(f"Initialized spatial domain with {len(h3_cells)} H3 cells")
            
        except Exception as e:
            logger.error(f"Failed to initialize spatial domain: {e}")
            raise
    
    def _generate_h3_cells_from_boundary(self, boundary: Dict[str, Any]) -> List[str]:
        """Generate H3 cells within the specified boundary."""
        cells = set()
        
        if 'coordinates' in boundary:
            coord_list = boundary['coordinates'][0][0]
            for coord in coord_list:
                try:
                    lng, lat = float(coord[0]), float(coord[1])
                    cell = h3.latlng_to_cell(lat, lng, self.h3_resolution)
                    cells.add(cell)
                    
                    # Add nearby cells to ensure coverage
                    for ring_distance in range(1, 3):
                        neighbors = h3.grid_ring(cell, ring_distance)
                        if isinstance(neighbors, list):
                            cells.update(neighbors)
                        else:
                            cells.update(list(neighbors))
                            
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid coordinate {coord}: {e}")
        
        return list(cells)
    
    def _create_h3_spatial_graph(self, h3_cells: List[str], max_neighbor_distance: int = 3) -> object:
        """Create a simple H3 spatial graph for neighbor relationships."""
        class H3SpatialGraph:
            def __init__(self, cells, max_distance=3):
                self.cells = cells
                self.neighbors = {}
                
                # Compute neighbor relationships
                for cell in cells:
                    self.neighbors[cell] = {}
                    for distance in range(1, max_distance + 1):
                        try:
                            ring_neighbors = h3.grid_ring(cell, distance)
                            if isinstance(ring_neighbors, list):
                                valid_neighbors = set(ring_neighbors) & set(cells)
                            else:
                                valid_neighbors = set(list(ring_neighbors)) & set(cells)
                            self.neighbors[cell][distance] = valid_neighbors
                        except Exception:
                            self.neighbors[cell][distance] = set()
        
        return H3SpatialGraph(h3_cells, max_neighbor_distance)
    
    def observe_environment(self, 
                           observations: Dict[str, Dict[str, float]], 
                           timestamp: float) -> None:
        """
        Update environmental state beliefs based on new observations.
        
        Args:
            observations: Dictionary mapping H3 cells to environmental observations
            timestamp: Observation timestamp
        """
        observation_data = {
            'timestamp': timestamp,
            'observations': observations,
            'updated_cells': []
        }
        
        for cell, obs_data in observations.items():
            if cell in self.environmental_states:
                # Update environmental state with new observations
                env_state = self.environmental_states[cell]
                
                for var, value in obs_data.items():
                    if var in self.environmental_variables:
                        setattr(env_state, var, value)
                
                env_state.timestamp = timestamp
                observation_data['updated_cells'].append(cell)
        
        self.observation_history.append(observation_data)
        
        # Update prediction models with new data
        self._update_prediction_models()
        
        logger.debug(f"Updated {len(observation_data['updated_cells'])} cells with new observations")
    
    def _update_prediction_models(self):
        """Update Gaussian Process models with latest observations."""
        if len(self.observation_history) < 2:
            return
        
        # Prepare training data for each environmental variable
        for var in self.environmental_variables:
            X_spatial = []  # [lat, lng, time]
            y_values = []   # environmental variable values
            
            for obs_record in self.observation_history:
                timestamp = obs_record['timestamp']
                
                for cell, obs_data in obs_record['observations'].items():
                    if var in obs_data and cell in self.environmental_states:
                        lat, lng = h3.cell_to_latlng(cell)
                        X_spatial.append([lat, lng, timestamp])
                        y_values.append(obs_data[var])
            
            if len(X_spatial) > 5:  # Minimum samples for GP training
                X_spatial = np.array(X_spatial)
                y_values = np.array(y_values)
                
                try:
                    self.gp_models[var].fit(X_spatial, y_values)
                    logger.debug(f"Updated GP model for {var} with {len(X_spatial)} samples")
                except Exception as e:
                    logger.warning(f"Failed to update GP model for {var}: {e}")
    
    def predict_environmental_dynamics(self, 
                                     forecast_timesteps: int = None) -> Dict[str, List[SpatialPrediction]]:
        """
        Predict future environmental states using learned dynamics.
        
        Args:
            forecast_timesteps: Number of timesteps to forecast
            
        Returns:
            Dictionary mapping variables to spatial predictions
        """
        if forecast_timesteps is None:
            forecast_timesteps = self.prediction_horizon
        
        predictions = defaultdict(list)
        current_time = max([obs['timestamp'] for obs in self.observation_history]) if self.observation_history else 0.0
        
        for timestep in range(1, forecast_timesteps + 1):
            future_time = current_time + timestep
            
            for cell in self.environmental_states:
                lat, lng = h3.cell_to_latlng(cell)
                
                for var in self.environmental_variables:
                    if var in self.gp_models:
                        try:
                            # Predict at future timestep
                            X_pred = np.array([[lat, lng, future_time]])
                            mean_pred, std_pred = self.gp_models[var].predict(X_pred, return_std=True)
                            
                            # Create prediction object
                            prediction = SpatialPrediction(
                                location=cell,
                                predicted_value=float(mean_pred[0]),
                                uncertainty=float(std_pred[0]),
                                confidence_interval=(
                                    float(mean_pred[0] - 1.96 * std_pred[0]),
                                    float(mean_pred[0] + 1.96 * std_pred[0])
                                ),
                                prediction_horizon=timestep,
                                contributing_factors=self._analyze_prediction_factors(cell, var)
                            )
                            
                            predictions[var].append(prediction)
                            
                        except Exception as e:
                            logger.warning(f"Prediction failed for {var} at {cell}: {e}")
        
        logger.info(f"Generated {sum(len(v) for v in predictions.values())} spatial predictions")
        return dict(predictions)
    
    def _analyze_prediction_factors(self, cell: str, variable: str) -> Dict[str, float]:
        """Analyze factors contributing to predictions."""
        factors = {}
        
        # Spatial factors (neighboring cells influence)
        if self.spatial_graph:
            neighbors = self.spatial_graph.neighbors.get(cell, {}).get(1, set())
            neighbor_values = []
            
            for neighbor in neighbors:
                if neighbor in self.environmental_states:
                    env_state = self.environmental_states[neighbor]
                    if hasattr(env_state, variable):
                        neighbor_values.append(getattr(env_state, variable))
            
            if neighbor_values:
                factors['spatial_correlation'] = np.corrcoef([
                    getattr(self.environmental_states[cell], variable, 0.5)
                ] + neighbor_values)[0, 1:].mean()
            else:
                factors['spatial_correlation'] = 0.0
        
        # Temporal autocorrelation
        historical_values = []
        for obs_record in self.observation_history[-10:]:  # Last 10 observations
            if cell in obs_record['observations'] and variable in obs_record['observations'][cell]:
                historical_values.append(obs_record['observations'][cell][variable])
        
        if len(historical_values) > 1:
            # Simple autocorrelation calculation
            autocorr = np.corrcoef(historical_values[:-1], historical_values[1:])[0, 1]
            factors['temporal_autocorrelation'] = autocorr if not np.isnan(autocorr) else 0.0
        else:
            factors['temporal_autocorrelation'] = 0.0
        
        # Environmental interactions
        current_state = self.environmental_states[cell]
        factors['temperature_vegetation_interaction'] = current_state.temperature * current_state.vegetation_density
        factors['water_soil_interaction'] = current_state.water_availability * current_state.soil_quality
        
        return factors
    
    def optimize_resource_allocation(self, 
                                   resource_budget: float,
                                   resource_types: List[str],
                                   optimization_objective: str = 'biodiversity') -> List[ResourceAllocation]:
        """
        Optimize resource allocation using active inference principles.
        
        This method formulates resource allocation as an active inference problem
        where the agent (resource manager) must select actions (resource allocations)
        that minimize expected free energy, balancing:
        1. Pragmatic value: achieving environmental objectives
        2. Epistemic value: reducing uncertainty about environmental dynamics
        
        Mathematical Framework:
        The expected free energy for resource allocation is:
        G(π) = E_q[log q(s|π)] - E_q[log p(o,s|π)]
             = Risk + Ambiguity
        
        Where Risk is the cost of not achieving objectives and Ambiguity
        is the uncertainty about environmental outcomes.
        
        Args:
            resource_budget: Total budget for resource allocation
            resource_types: Types of resources to allocate
            optimization_objective: Primary objective ('biodiversity', 'carbon', 'stability')
            
        Returns:
            List of optimal resource allocations
        """
        logger.info(f"Optimizing resource allocation with budget {resource_budget}")
        
        allocations = []
        available_budget = resource_budget
        
        # Get current environmental predictions
        predictions = self.predict_environmental_dynamics(forecast_timesteps=5)
        
        # Score each location for resource allocation priority
        location_scores = self._compute_allocation_priorities(predictions, optimization_objective)
        
        # Sort locations by priority
        sorted_locations = sorted(location_scores.items(), key=lambda x: x[1]['priority'], reverse=True)
        
        for cell, score_data in sorted_locations:
            if available_budget <= 0:
                break
            
            # Determine optimal allocation for this location
            optimal_allocation = self._optimize_location_allocation(
                cell, score_data, resource_types, available_budget, optimization_objective
            )
            
            if optimal_allocation and optimal_allocation.allocation_amount <= available_budget:
                allocations.append(optimal_allocation)
                available_budget -= optimal_allocation.allocation_amount
        
        logger.info(f"Generated {len(allocations)} resource allocations, used {resource_budget - available_budget:.2f}/{resource_budget:.2f} budget")
        return allocations
    
    def _compute_allocation_priorities(self, 
                                     predictions: Dict[str, List[SpatialPrediction]], 
                                     objective: str) -> Dict[str, Dict[str, float]]:
        """Compute priority scores for resource allocation."""
        priorities = {}
        
        for cell in self.environmental_states:
            # Initialize priority metrics
            priority_data = {
                'priority': 0.0,
                'urgency': 0.0,
                'impact_potential': 0.0,
                'uncertainty': 0.0,
                'feasibility': 1.0
            }
            
            # Analyze current state
            current_state = self.environmental_states[cell]
            
            # Compute urgency based on environmental degradation
            if objective == 'biodiversity':
                urgency = max(0, 0.5 - current_state.biodiversity_index)  # Higher urgency for low biodiversity
                impact_potential = (1.0 - current_state.biodiversity_index)  # Higher potential if currently low
            elif objective == 'carbon':
                urgency = max(0, -current_state.carbon_flux)  # Urgency for carbon loss
                impact_potential = abs(current_state.carbon_flux)  # Potential for carbon improvement
            elif objective == 'stability':
                # Stability based on prediction uncertainty
                uncertainties = []
                for var_predictions in predictions.values():
                    for pred in var_predictions:
                        if pred.location == cell:
                            uncertainties.append(pred.uncertainty)
                avg_uncertainty = np.mean(uncertainties) if uncertainties else 0.5
                urgency = avg_uncertainty  # High uncertainty = high urgency
                impact_potential = avg_uncertainty  # High uncertainty = high impact potential
            else:
                urgency = 0.5
                impact_potential = 0.5
            
            # Compute overall uncertainty
            prediction_uncertainties = []
            for var_predictions in predictions.values():
                for pred in var_predictions:
                    if pred.location == cell and pred.prediction_horizon <= 3:
                        prediction_uncertainties.append(pred.uncertainty)
            
            avg_uncertainty = np.mean(prediction_uncertainties) if prediction_uncertainties else 0.5
            
            # Compute feasibility based on environmental conditions
            feasibility = (current_state.water_availability + current_state.soil_quality) / 2.0
            
            # Combined priority score using active inference principles
            # Higher priority for high urgency, high impact potential, and high uncertainty (epistemic value)
            priority_score = (
                0.4 * urgency +           # Pragmatic value (current need)
                0.3 * impact_potential +  # Pragmatic value (potential benefit)
                0.2 * avg_uncertainty +   # Epistemic value (learning opportunity)
                0.1 * feasibility         # Feasibility constraint
            )
            
            priority_data.update({
                'priority': priority_score,
                'urgency': urgency,
                'impact_potential': impact_potential,
                'uncertainty': avg_uncertainty,
                'feasibility': feasibility
            })
            
            priorities[cell] = priority_data
        
        return priorities
    
    def _optimize_location_allocation(self,
                                    cell: str,
                                    score_data: Dict[str, float],
                                    resource_types: List[str],
                                    available_budget: float,
                                    objective: str) -> Optional[ResourceAllocation]:
        """Optimize resource allocation for a specific location."""
        
        # Simple allocation strategy based on priority score
        if score_data['priority'] < 0.3:  # Low priority threshold
            return None
        
        # Allocate based on urgency and available budget
        base_allocation = min(
            available_budget * 0.1,  # Maximum 10% of budget per location
            score_data['priority'] * available_budget * 0.05  # Scale by priority
        )
        
        # Select most appropriate resource type
        current_state = self.environmental_states[cell]
        
        if objective == 'biodiversity':
            if current_state.vegetation_density < 0.3:
                resource_type = 'vegetation_restoration'
            elif current_state.water_availability < 0.3:
                resource_type = 'water_conservation'
            else:
                resource_type = 'habitat_protection'
        elif objective == 'carbon':
            resource_type = 'carbon_sequestration'
        else:
            resource_type = 'environmental_monitoring'
        
        # Select from available resource types
        selected_resource = resource_types[0] if resource_types else resource_type
        
        # Compute expected benefit using simple heuristic
        expected_benefit = score_data['priority'] * score_data['feasibility']
        
        return ResourceAllocation(
            location=cell,
            resource_type=selected_resource,
            allocation_amount=base_allocation,
            priority_score=score_data['priority'],
            expected_benefit=expected_benefit,
            uncertainty=score_data['uncertainty'],
            constraints={
                'urgency': score_data['urgency'],
                'feasibility': score_data['feasibility']
            }
        )
    
    def analyze_environmental_uncertainty(self) -> Dict[str, Any]:
        """
        Analyze environmental uncertainty across the spatial domain.
        
        Returns:
            Comprehensive uncertainty analysis
        """
        uncertainty_analysis = {
            'global_uncertainty': {},
            'spatial_uncertainty_patterns': {},
            'temporal_uncertainty_trends': {},
            'high_uncertainty_regions': [],
            'uncertainty_sources': {}
        }
        
        # Global uncertainty metrics
        all_uncertainties = defaultdict(list)
        
        for cell, env_state in self.environmental_states.items():
            for var in self.environmental_variables:
                if var in env_state.uncertainty:
                    all_uncertainties[var].append(env_state.uncertainty[var])
        
        for var, uncertainties in all_uncertainties.items():
            if uncertainties:
                uncertainty_analysis['global_uncertainty'][var] = {
                    'mean': np.mean(uncertainties),
                    'std': np.std(uncertainties),
                    'max': np.max(uncertainties),
                    'min': np.min(uncertainties)
                }
        
        # High uncertainty regions
        for cell, env_state in self.environmental_states.items():
            avg_uncertainty = np.mean(list(env_state.uncertainty.values())) if env_state.uncertainty else 0.5
            
            if avg_uncertainty > self.uncertainty_threshold:
                lat, lng = h3.cell_to_latlng(cell)
                uncertainty_analysis['high_uncertainty_regions'].append({
                    'location': cell,
                    'coordinates': [lat, lng],
                    'uncertainty_level': avg_uncertainty,
                    'primary_sources': [k for k, v in env_state.uncertainty.items() if v > self.uncertainty_threshold]
                })
        
        logger.info(f"Identified {len(uncertainty_analysis['high_uncertainty_regions'])} high uncertainty regions")
        return uncertainty_analysis
    
    def compute_environmental_free_energy(self) -> Dict[str, float]:
        """
        Compute environmental free energy for the entire spatial domain.
        
        Environmental free energy quantifies the "surprise" or unexpectedness
        of current environmental observations given the learned environmental model.
        High free energy indicates:
        1. Unexpected environmental changes
        2. Model inadequacy
        3. Need for more observations/interventions
        
        Returns:
            Free energy components and total free energy
        """
        if not self.observation_history:
            return {'total_free_energy': np.inf, 'components': {}}
        
        free_energy_components = {}
        total_accuracy = 0.0
        total_complexity = 0.0
        
        latest_observations = self.observation_history[-1]['observations']
        
        for var in self.environmental_variables:
            if var in self.gp_models:
                var_accuracy = 0.0
                var_complexity = 0.0
                var_observations = 0
                
                for cell, obs_data in latest_observations.items():
                    if var in obs_data and cell in self.environmental_states:
                        # Get current prediction
                        lat, lng = h3.cell_to_latlng(cell)
                        current_time = self.observation_history[-1]['timestamp']
                        
                        try:
                            X_pred = np.array([[lat, lng, current_time]])
                            mean_pred, std_pred = self.gp_models[var].predict(X_pred, return_std=True)
                            
                            # Accuracy: negative log-likelihood of observation
                            observed_value = obs_data[var]
                            log_likelihood = stats.norm.logpdf(observed_value, mean_pred[0], std_pred[0])
                            accuracy = -log_likelihood
                            
                            # Complexity: KL divergence from prior (simplified)
                            prior_mean = 0.5  # Assume neutral prior
                            prior_std = 0.5
                            complexity = stats.norm.logpdf(mean_pred[0], prior_mean, prior_std)
                            
                            var_accuracy += accuracy
                            var_complexity += complexity
                            var_observations += 1
                            
                        except Exception as e:
                            logger.warning(f"Free energy computation failed for {var} at {cell}: {e}")
                
                if var_observations > 0:
                    var_accuracy /= var_observations
                    var_complexity /= var_observations
                    var_free_energy = var_accuracy + var_complexity
                    
                    free_energy_components[var] = {
                        'accuracy': var_accuracy,
                        'complexity': var_complexity,
                        'free_energy': var_free_energy,
                        'observations': var_observations
                    }
                    
                    total_accuracy += var_accuracy
                    total_complexity += var_complexity
        
        total_free_energy = total_accuracy + total_complexity
        
        return {
            'total_free_energy': total_free_energy,
            'total_accuracy': total_accuracy,
            'total_complexity': total_complexity,
            'components': free_energy_components,
            'n_variables': len(free_energy_components)
        }
    
    def get_environmental_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of environmental state and dynamics."""
        summary = {
            'spatial_domain': {
                'n_cells': len(self.environmental_states),
                'h3_resolution': self.h3_resolution,
                'coverage_area_km2': len(self.environmental_states) * (
                    h3.cell_area(list(self.environmental_states.keys())[0], 'km^2') 
                    if self.environmental_states else 0.0
                )
            },
            'temporal_domain': {
                'n_observations': len(self.observation_history),
                'time_span': (
                    self.observation_history[-1]['timestamp'] - self.observation_history[0]['timestamp']
                    if len(self.observation_history) > 1 else 0.0
                )
            },
            'environmental_variables': self.environmental_variables,
            'model_status': {
                'trained_models': len([m for m in self.gp_models.values() if hasattr(m, 'X_train_')]),
                'total_models': len(self.gp_models)
            }
        }
        
        # Current environmental statistics
        if self.environmental_states:
            for var in self.environmental_variables:
                values = []
                for env_state in self.environmental_states.values():
                    if hasattr(env_state, var):
                        values.append(getattr(env_state, var))
                
                if values:
                    summary[f'{var}_stats'] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
        
        return summary


class MultiScaleHierarchicalAnalyzer:
    """
    Multi-scale hierarchical analysis for geospatial active inference.
    
    This class implements hierarchical spatial models that operate across
    multiple scales simultaneously, enabling analysis of:
    1. Local environmental dynamics
    2. Regional patterns and trends  
    3. Global emergent phenomena
    4. Cross-scale interactions
    
    The hierarchical structure follows Active Inference principles where
    higher levels provide priors for lower levels, and lower levels
    provide evidence for higher level inference.
    """
    
    def __init__(self, 
                 base_resolution: int = 8,
                 hierarchy_levels: int = 3,
                 scale_factor: int = 3):
        """
        Initialize multi-scale hierarchical analyzer.
        
        Args:
            base_resolution: Finest H3 resolution level
            hierarchy_levels: Number of hierarchical levels
            scale_factor: Factor by which each level scales up
        """
        self.base_resolution = base_resolution
        self.hierarchy_levels = hierarchy_levels
        self.scale_factor = scale_factor
        
        # Initialize hierarchical models
        self.level_models = {}
        self.cross_scale_influences = {}
        self.hierarchical_beliefs = {}
        
        logger.info(f"Initialized MultiScaleHierarchicalAnalyzer with {hierarchy_levels} levels")
    
    def _create_hierarchical_h3_model(self, base_resolution: int, boundary: Dict[str, Any], levels: int) -> Dict[str, object]:
        """Create hierarchical H3 models at different resolutions."""
        hierarchical_graphs = {}
        
        for level in range(levels):
            resolution = max(0, base_resolution - level)
            level_name = f"level_{level}_res_{resolution}"
            
            # Generate H3 cells for this resolution
            level_cells = self._generate_h3_cells_from_boundary(boundary, resolution)
            
            # Create spatial graph for this level
            level_graph = self._create_level_spatial_graph(level_cells)
            hierarchical_graphs[level_name] = level_graph
        
        return hierarchical_graphs
    
    def _generate_h3_cells_from_boundary(self, boundary: Dict[str, Any], resolution: int) -> List[str]:
        """Generate H3 cells from boundary at specified resolution."""
        cells = set()
        
        if 'coordinates' in boundary:
            coord_list = boundary['coordinates'][0][0]
            for coord in coord_list:
                try:
                    lng, lat = float(coord[0]), float(coord[1])
                    cell = h3.latlng_to_cell(lat, lng, resolution)
                    cells.add(cell)
                    
                    # Add nearby cells for coverage
                    for ring_distance in range(1, 2):
                        neighbors = h3.grid_ring(cell, ring_distance)
                        if isinstance(neighbors, list):
                            cells.update(neighbors)
                        else:
                            cells.update(list(neighbors))
                            
                except (ValueError, TypeError):
                    continue
        
        return list(cells)
    
    def _create_level_spatial_graph(self, cells: List[str]) -> object:
        """Create spatial graph for a hierarchical level."""
        class LevelSpatialGraph:
            def __init__(self, cells):
                self.cells = cells
                self.neighbors = {}
                
                for cell in cells:
                    self.neighbors[cell] = {}
                    try:
                        ring_neighbors = h3.grid_ring(cell, 1)
                        if isinstance(ring_neighbors, list):
                            valid_neighbors = set(ring_neighbors) & set(cells)
                        else:
                            valid_neighbors = set(list(ring_neighbors)) & set(cells)
                        self.neighbors[cell][1] = valid_neighbors
                    except Exception:
                        self.neighbors[cell][1] = set()
        
        return LevelSpatialGraph(cells)
    
    def initialize_hierarchy(self, boundary: Dict[str, Any]) -> None:
        """Initialize hierarchical spatial models."""
        # Create hierarchical H3 models
        self.hierarchical_graphs = self._create_hierarchical_h3_model(
            self.base_resolution, boundary, self.hierarchy_levels
        )
        
        # Initialize beliefs at each level
        for level_name, spatial_graph in self.hierarchical_graphs.items():
            n_cells = len(spatial_graph.cells)
            # Initialize with uniform beliefs
            self.hierarchical_beliefs[level_name] = {
                cell: np.ones(4) / 4  # 4-state categorical model
                for cell in spatial_graph.cells
            }
        
        logger.info(f"Initialized hierarchy with {len(self.hierarchical_graphs)} levels")
    
    def propagate_beliefs_hierarchically(self, 
                                       bottom_up_evidence: Dict[str, Dict[str, np.ndarray]],
                                       top_down_priors: Dict[str, Dict[str, np.ndarray]] = None) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Propagate beliefs through the hierarchical structure.
        
        Implements hierarchical message passing where:
        - Bottom-up: evidence flows from fine to coarse scales
        - Top-down: priors flow from coarse to fine scales
        
        Args:
            bottom_up_evidence: Evidence from finest scale observations
            top_down_priors: Priors from coarsest scale (optional)
            
        Returns:
            Updated hierarchical beliefs
        """
        # Sort levels by resolution (finest to coarsest)
        sorted_levels = sorted(
            self.hierarchical_graphs.keys(),
            key=lambda x: int(x.split('_res_')[1]),
            reverse=True
        )
        
        # Bottom-up pass: propagate evidence upward
        for i, level_name in enumerate(sorted_levels):
            if i == 0:
                # Finest level: use bottom-up evidence
                if level_name in bottom_up_evidence:
                    self.hierarchical_beliefs[level_name].update(bottom_up_evidence[level_name])
            else:
                # Higher levels: aggregate from lower level
                lower_level = sorted_levels[i-1]
                self._aggregate_beliefs_upward(lower_level, level_name)
        
        # Top-down pass: propagate priors downward
        if top_down_priors:
            for i in reversed(range(len(sorted_levels))):
                level_name = sorted_levels[i]
                if i == len(sorted_levels) - 1:
                    # Coarsest level: use top-down priors
                    if level_name in top_down_priors:
                        self.hierarchical_beliefs[level_name].update(top_down_priors[level_name])
                else:
                    # Lower levels: receive priors from higher level
                    higher_level = sorted_levels[i+1]
                    self._propagate_priors_downward(higher_level, level_name)
        
        return self.hierarchical_beliefs.copy()
    
    def _aggregate_beliefs_upward(self, lower_level: str, higher_level: str) -> None:
        """Aggregate beliefs from lower level to higher level."""
        lower_beliefs = self.hierarchical_beliefs[lower_level]
        higher_beliefs = self.hierarchical_beliefs[higher_level]
        
        # Simple aggregation: spatial averaging within parent cells
        for higher_cell in higher_beliefs:
            # Find corresponding cells in lower level
            lower_cells = self._find_child_cells(higher_cell, lower_level)
            
            if lower_cells:
                # Average beliefs from child cells
                child_beliefs = [lower_beliefs[cell] for cell in lower_cells if cell in lower_beliefs]
                if child_beliefs:
                    aggregated_belief = np.mean(child_beliefs, axis=0)
                    higher_beliefs[higher_cell] = aggregated_belief / np.sum(aggregated_belief)
    
    def _propagate_priors_downward(self, higher_level: str, lower_level: str) -> None:
        """Propagate priors from higher level to lower level."""
        higher_beliefs = self.hierarchical_beliefs[higher_level]
        lower_beliefs = self.hierarchical_beliefs[lower_level]
        
        # Propagate parent beliefs to child cells
        for lower_cell in lower_beliefs:
            parent_cell = self._find_parent_cell(lower_cell, higher_level)
            
            if parent_cell and parent_cell in higher_beliefs:
                # Weighted combination of local belief and parent prior
                local_belief = lower_beliefs[lower_cell]
                parent_prior = higher_beliefs[parent_cell]
                
                # Hierarchical belief update (weighted average)
                alpha = 0.7  # Weight for local evidence
                updated_belief = alpha * local_belief + (1 - alpha) * parent_prior
                lower_beliefs[lower_cell] = updated_belief / np.sum(updated_belief)
    
    def _find_child_cells(self, parent_cell: str, child_level: str) -> List[str]:
        """Find child cells corresponding to a parent cell."""
        # Simplified: use spatial proximity
        child_graph = self.hierarchical_graphs[child_level]
        parent_lat, parent_lng = h3.cell_to_latlng(parent_cell)
        
        child_cells = []
        for child_cell in child_graph.cells:
            child_lat, child_lng = h3.cell_to_latlng(child_cell)
            
            # Check if child is within parent's approximate area
            distance = np.sqrt((parent_lat - child_lat)**2 + (parent_lng - child_lng)**2)
            if distance < 0.01:  # Threshold in degrees
                child_cells.append(child_cell)
        
        return child_cells
    
    def _find_parent_cell(self, child_cell: str, parent_level: str) -> Optional[str]:
        """Find parent cell corresponding to a child cell."""
        parent_graph = self.hierarchical_graphs[parent_level]
        child_lat, child_lng = h3.cell_to_latlng(child_cell)
        
        # Find closest parent cell
        min_distance = float('inf')
        closest_parent = None
        
        for parent_cell in parent_graph.cells:
            parent_lat, parent_lng = h3.cell_to_latlng(parent_cell)
            distance = np.sqrt((child_lat - parent_lat)**2 + (child_lng - parent_lng)**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_parent = parent_cell
        
        return closest_parent
    
    def analyze_cross_scale_interactions(self) -> Dict[str, Any]:
        """Analyze interactions between different spatial scales."""
        interactions = {
            'scale_coherence': {},
            'information_flow': {},
            'emergent_patterns': {},
            'scale_dependencies': {}
        }
        
        level_names = list(self.hierarchical_graphs.keys())
        
        # Compute scale coherence (similarity between levels)
        for i in range(len(level_names) - 1):
            lower_level = level_names[i]
            higher_level = level_names[i + 1]
            
            coherence = self._compute_scale_coherence(lower_level, higher_level)
            interactions['scale_coherence'][f'{lower_level}_to_{higher_level}'] = coherence
        
        # Analyze information flow
        for level_name in level_names:
            beliefs = self.hierarchical_beliefs[level_name]
            
            # Compute information content at each level
            level_entropy = np.mean([
                -np.sum(belief * np.log(belief + 1e-8))
                for belief in beliefs.values()
            ])
            
            interactions['information_flow'][level_name] = {
                'entropy': level_entropy,
                'n_cells': len(beliefs),
                'information_density': level_entropy / len(beliefs) if len(beliefs) > 0 else 0
            }
        
        return interactions
    
    def _compute_scale_coherence(self, lower_level: str, higher_level: str) -> float:
        """Compute coherence between two hierarchical levels."""
        lower_beliefs = self.hierarchical_beliefs[lower_level]
        higher_beliefs = self.hierarchical_beliefs[higher_level]
        
        coherences = []
        
        for higher_cell, higher_belief in higher_beliefs.items():
            child_cells = self._find_child_cells(higher_cell, lower_level)
            
            if child_cells:
                child_beliefs = [lower_beliefs[cell] for cell in child_cells if cell in lower_beliefs]
                
                if child_beliefs:
                    # Compute similarity between parent and aggregated child beliefs
                    aggregated_child = np.mean(child_beliefs, axis=0)
                    aggregated_child = aggregated_child / np.sum(aggregated_child)
                    
                    # Use cosine similarity
                    similarity = np.dot(higher_belief, aggregated_child) / (
                        np.linalg.norm(higher_belief) * np.linalg.norm(aggregated_child) + 1e-8
                    )
                    coherences.append(similarity)
        
        return np.mean(coherences) if coherences else 0.0
    
    def detect_emergent_patterns(self) -> List[Dict[str, Any]]:
        """Detect emergent patterns across scales."""
        patterns = []
        
        # Analyze each hierarchical level
        for level_name, beliefs in self.hierarchical_beliefs.items():
            spatial_graph = self.hierarchical_graphs[level_name]
            
            # Detect spatial clusters of similar beliefs
            from sklearn.cluster import DBSCAN
            
            # Prepare data for clustering
            coordinates = []
            belief_features = []
            cell_ids = []
            
            for cell, belief in beliefs.items():
                lat, lng = h3.cell_to_latlng(cell)
                coordinates.append([lat, lng])
                belief_features.append(belief)
                cell_ids.append(cell)
            
            if len(coordinates) > 3:
                coordinates = np.array(coordinates)
                belief_features = np.array(belief_features)
                
                # Combine spatial and belief features
                combined_features = np.hstack([
                    coordinates * 100,  # Scale coordinates
                    belief_features
                ])
                
                # Apply DBSCAN clustering
                clustering = DBSCAN(eps=0.5, min_samples=2)
                cluster_labels = clustering.fit_predict(combined_features)
                
                # Analyze clusters
                unique_labels = set(cluster_labels)
                for label in unique_labels:
                    if label != -1:  # Ignore noise points
                        cluster_cells = [cell_ids[i] for i, l in enumerate(cluster_labels) if l == label]
                        cluster_beliefs = belief_features[cluster_labels == label]
                        
                        if len(cluster_cells) >= 2:
                            # Compute cluster characteristics
                            mean_belief = np.mean(cluster_beliefs, axis=0)
                            belief_coherence = 1.0 - np.std(cluster_beliefs, axis=0).mean()
                            
                            pattern = {
                                'type': 'spatial_cluster',
                                'level': level_name,
                                'cells': cluster_cells,
                                'size': len(cluster_cells),
                                'mean_belief': mean_belief.tolist(),
                                'coherence': float(belief_coherence),
                                'spatial_extent': self._compute_spatial_extent(cluster_cells)
                            }
                            patterns.append(pattern)
        
        logger.info(f"Detected {len(patterns)} emergent patterns across scales")
        return patterns
    
    def _compute_spatial_extent(self, cells: List[str]) -> Dict[str, float]:
        """Compute spatial extent of a cell cluster."""
        latitudes = []
        longitudes = []
        
        for cell in cells:
            lat, lng = h3.cell_to_latlng(cell)
            latitudes.append(lat)
            longitudes.append(lng)
        
        return {
            'lat_range': max(latitudes) - min(latitudes),
            'lng_range': max(longitudes) - min(longitudes),
            'centroid_lat': np.mean(latitudes),
            'centroid_lng': np.mean(longitudes),
            'area_km2': len(cells) * h3.cell_area(cells[0], unit='km^2') if cells else 0.0
        }


def analyze_multi_scale_patterns(hierarchical_graphs: Dict[str, Any], 
                               hierarchical_beliefs: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, Any]:
    """
    Analyze patterns across multiple spatial scales.
    
    Args:
        hierarchical_graphs: Dictionary of spatial graphs at different scales
        hierarchical_beliefs: Beliefs at each hierarchical level
        
    Returns:
        Multi-scale pattern analysis
    """
    analyzer = MultiScaleHierarchicalAnalyzer()
    analyzer.hierarchical_graphs = hierarchical_graphs
    analyzer.hierarchical_beliefs = hierarchical_beliefs
    
    analysis = {
        'cross_scale_interactions': analyzer.analyze_cross_scale_interactions(),
        'emergent_patterns': analyzer.detect_emergent_patterns(),
        'scale_statistics': {}
    }
    
    # Compute statistics for each scale
    for level_name, beliefs in hierarchical_beliefs.items():
        level_stats = {
            'n_cells': len(beliefs),
            'mean_entropy': np.mean([
                -np.sum(belief * np.log(belief + 1e-8))
                for belief in beliefs.values()
            ]),
            'belief_variance': np.var([
                belief.tolist() for belief in beliefs.values()
            ], axis=0).tolist() if beliefs else [0.0]
        }
        analysis['scale_statistics'][level_name] = level_stats
    
    return analysis