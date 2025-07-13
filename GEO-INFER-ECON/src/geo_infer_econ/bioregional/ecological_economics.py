"""
Ecological Economics for Bioregional Analysis

This module provides ecological economics modeling and analysis capabilities
for the GEO-INFER framework, focusing on the relationship between economic
systems and ecological systems.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class EcologicalEconomicsConfig:
    """Configuration for ecological economics models."""
    
    # Economic parameters
    discount_rate: float = 0.05
    time_horizon: int = 50  # years
    currency: str = 'USD'
    
    # Ecological parameters
    ecosystem_services: List[str] = field(default_factory=lambda: [
        'provisioning', 'regulating', 'cultural', 'supporting'
    ])
    
    # Valuation parameters
    valuation_methods: List[str] = field(default_factory=lambda: [
        'market_price', 'replacement_cost', 'travel_cost', 'hedonic_pricing',
        'contingent_valuation', 'choice_experiment'
    ])
    
    # Spatial parameters
    spatial_resolution: float = 0.1  # degrees
    analysis_units: str = 'hectares'

class BiophysicalEquilibriumModels:
    """
    Models for biophysical equilibrium analysis in ecological economics.
    
    Provides methods for analyzing the equilibrium between biological
    and physical systems in economic contexts.
    """
    
    def __init__(self, config: Optional[EcologicalEconomicsConfig] = None):
        """
        Initialize biophysical equilibrium models.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or EcologicalEconomicsConfig()
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize equilibrium models."""
        self.models = {
            'lotka_volterra': self._lotka_volterra_model,
            'predator_prey': self._predator_prey_model,
            'resource_competition': self._resource_competition_model,
            'ecosystem_services': self._ecosystem_services_model
        }
        logger.info("Initialized biophysical equilibrium models")
    
    def analyze_equilibrium(self, 
                          model_type: str,
                          parameters: Dict[str, Any],
                          time_steps: int = 100) -> Dict[str, Any]:
        """
        Analyze equilibrium for a specific model type.
        
        Args:
            model_type: Type of equilibrium model
            parameters: Model parameters
            time_steps: Number of time steps for simulation
            
        Returns:
            Equilibrium analysis results
        """
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        model_func = self.models[model_type]
        return model_func(parameters, time_steps)
    
    def _lotka_volterra_model(self, 
                             parameters: Dict[str, Any],
                             time_steps: int) -> Dict[str, Any]:
        """Lotka-Volterra predator-prey model."""
        # Extract parameters
        r = parameters.get('growth_rate', 0.5)
        a = parameters.get('predation_rate', 0.1)
        b = parameters.get('conversion_efficiency', 0.2)
        m = parameters.get('mortality_rate', 0.3)
        
        # Initial populations
        prey = parameters.get('initial_prey', 100)
        predator = parameters.get('initial_predator', 20)
        
        # Time series
        prey_population = [prey]
        predator_population = [predator]
        
        dt = 0.1  # Time step
        
        for t in range(time_steps):
            # Lotka-Volterra equations
            d_prey = r * prey - a * prey * predator
            d_predator = b * a * prey * predator - m * predator
            
            prey += d_prey * dt
            predator += d_predator * dt
            
            # Ensure non-negative populations
            prey = max(0, prey)
            predator = max(0, predator)
            
            prey_population.append(prey)
            predator_population.append(predator)
        
        return {
            'model_type': 'lotka_volterra',
            'equilibrium_reached': self._check_equilibrium(prey_population, predator_population),
            'final_prey': prey_population[-1],
            'final_predator': predator_population[-1],
            'prey_population': prey_population,
            'predator_population': predator_population,
            'parameters': parameters
        }
    
    def _predator_prey_model(self, 
                           parameters: Dict[str, Any],
                           time_steps: int) -> Dict[str, Any]:
        """Enhanced predator-prey model with carrying capacity."""
        # Extract parameters
        r = parameters.get('growth_rate', 0.5)
        K = parameters.get('carrying_capacity', 200)
        a = parameters.get('predation_rate', 0.1)
        b = parameters.get('conversion_efficiency', 0.2)
        m = parameters.get('mortality_rate', 0.3)
        
        # Initial populations
        prey = parameters.get('initial_prey', 100)
        predator = parameters.get('initial_predator', 20)
        
        # Time series
        prey_population = [prey]
        predator_population = [predator]
        
        dt = 0.1  # Time step
        
        for t in range(time_steps):
            # Enhanced predator-prey equations with carrying capacity
            d_prey = r * prey * (1 - prey / K) - a * prey * predator
            d_predator = b * a * prey * predator - m * predator
            
            prey += d_prey * dt
            predator += d_predator * dt
            
            # Ensure non-negative populations
            prey = max(0, prey)
            predator = max(0, predator)
            
            prey_population.append(prey)
            predator_population.append(predator)
        
        return {
            'model_type': 'predator_prey',
            'equilibrium_reached': self._check_equilibrium(prey_population, predator_population),
            'final_prey': prey_population[-1],
            'final_predator': predator_population[-1],
            'prey_population': prey_population,
            'predator_population': predator_population,
            'parameters': parameters
        }
    
    def _resource_competition_model(self, 
                                  parameters: Dict[str, Any],
                                  time_steps: int) -> Dict[str, Any]:
        """Resource competition model for multiple species."""
        # Extract parameters
        n_species = parameters.get('n_species', 2)
        growth_rates = parameters.get('growth_rates', [0.5, 0.4])
        carrying_capacities = parameters.get('carrying_capacities', [100, 80])
        competition_coefficients = parameters.get('competition_coefficients', [[1.0, 0.5], [0.5, 1.0]])
        
        # Initial populations
        populations = parameters.get('initial_populations', [50, 40])
        
        # Time series
        population_history = [populations.copy()]
        
        dt = 0.1  # Time step
        
        for t in range(time_steps):
            new_populations = []
            
            for i in range(n_species):
                # Competition equation
                d_pop = growth_rates[i] * populations[i] * (1 - populations[i] / carrying_capacities[i])
                
                # Competition terms
                for j in range(n_species):
                    if i != j:
                        d_pop -= growth_rates[i] * populations[i] * competition_coefficients[i][j] * populations[j] / carrying_capacities[i]
                
                new_pop = populations[i] + d_pop * dt
                new_pop = max(0, new_pop)  # Ensure non-negative
                new_populations.append(new_pop)
            
            populations = new_populations
            population_history.append(populations.copy())
        
        return {
            'model_type': 'resource_competition',
            'equilibrium_reached': self._check_equilibrium_multi(population_history),
            'final_populations': populations,
            'population_history': population_history,
            'parameters': parameters
        }
    
    def _ecosystem_services_model(self, 
                                parameters: Dict[str, Any],
                                time_steps: int) -> Dict[str, Any]:
        """Ecosystem services valuation model."""
        # Extract parameters
        service_types = parameters.get('service_types', ['provisioning', 'regulating', 'cultural'])
        initial_values = parameters.get('initial_values', [100, 80, 60])
        growth_rates = parameters.get('growth_rates', [0.1, 0.05, 0.08])
        interaction_matrix = parameters.get('interaction_matrix', [[1.0, 0.2, 0.1], [0.1, 1.0, 0.3], [0.2, 0.1, 1.0]])
        
        # Initial service values
        service_values = initial_values.copy()
        
        # Time series
        value_history = [service_values.copy()]
        
        dt = 0.1  # Time step
        
        for t in range(time_steps):
            new_values = []
            
            for i in range(len(service_types)):
                # Base growth
                d_value = growth_rates[i] * service_values[i]
                
                # Interaction effects
                for j in range(len(service_types)):
                    if i != j:
                        d_value += interaction_matrix[i][j] * service_values[j] * 0.01
                
                new_value = service_values[i] + d_value * dt
                new_value = max(0, new_value)  # Ensure non-negative
                new_values.append(new_value)
            
            service_values = new_values
            value_history.append(service_values.copy())
        
        # Calculate total economic value
        total_value = sum(service_values)
        
        return {
            'model_type': 'ecosystem_services',
            'equilibrium_reached': self._check_equilibrium_multi(value_history),
            'final_values': service_values,
            'total_economic_value': total_value,
            'value_history': value_history,
            'parameters': parameters
        }
    
    def _check_equilibrium(self, 
                          population1: List[float],
                          population2: List[float],
                          tolerance: float = 0.01) -> bool:
        """Check if populations have reached equilibrium."""
        if len(population1) < 10 or len(population2) < 10:
            return False
        
        # Check last 10% of time series
        n_check = max(1, len(population1) // 10)
        
        recent1 = population1[-n_check:]
        recent2 = population2[-n_check:]
        
        # Calculate coefficient of variation
        cv1 = np.std(recent1) / np.mean(recent1) if np.mean(recent1) > 0 else float('inf')
        cv2 = np.std(recent2) / np.mean(recent2) if np.mean(recent2) > 0 else float('inf')
        
        return cv1 < tolerance and cv2 < tolerance
    
    def _check_equilibrium_multi(self, 
                               population_history: List[List[float]],
                               tolerance: float = 0.01) -> bool:
        """Check if multiple populations have reached equilibrium."""
        if len(population_history) < 10:
            return False
        
        n_check = max(1, len(population_history) // 10)
        recent_history = population_history[-n_check:]
        
        # Check each population
        for i in range(len(recent_history[0])):
            population = [pop[i] for pop in recent_history]
            cv = np.std(population) / np.mean(population) if np.mean(population) > 0 else float('inf')
            if cv >= tolerance:
                return False
        
        return True
    
    def calculate_ecosystem_value(self, 
                                service_values: List[float],
                                valuation_method: str = 'market_price') -> float:
        """
        Calculate total ecosystem value.
        
        Args:
            service_values: Values of ecosystem services
            valuation_method: Method for valuation
            
        Returns:
            Total economic value
        """
        if valuation_method == 'market_price':
            # Simple market price valuation
            return sum(service_values)
        elif valuation_method == 'replacement_cost':
            # Replacement cost valuation (typically higher)
            return sum(service_values) * 1.5
        elif valuation_method == 'contingent_valuation':
            # Contingent valuation (willingness to pay)
            return sum(service_values) * 2.0
        else:
            return sum(service_values)

# Export the main class
__all__ = ['BiophysicalEquilibriumModels', 'EcologicalEconomicsConfig'] 