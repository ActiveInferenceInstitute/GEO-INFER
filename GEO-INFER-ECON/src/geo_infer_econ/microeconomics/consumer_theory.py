"""
Consumer Theory Module

Implements comprehensive consumer theory models including:
- Utility maximization and demand functions
- Consumer choice with spatial considerations
- Welfare analysis and consumer surplus
- Revealed preference analysis
- Spatial consumer behavior modeling
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import geopandas as gpd
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import multivariate_normal
from sklearn.preprocessing import StandardScaler


@dataclass
class ConsumerProfile:
    """Profile of an individual consumer with spatial attributes"""
    consumer_id: str
    income: float
    location: Tuple[float, float]  # (lat, lon)
    preferences: Dict[str, float]
    demographic_attributes: Dict[str, Any]
    spatial_attributes: Dict[str, float]  # accessibility, distance to markets, etc.


class UtilityFunctions:
    """
    Collection of utility function implementations for consumer theory
    """
    
    @staticmethod
    def cobb_douglas(quantities: np.ndarray, alpha: np.ndarray) -> float:
        """
        Cobb-Douglas utility function: U = ∏(x_i^α_i)
        
        Args:
            quantities: Array of quantities consumed
            alpha: Array of preference parameters (should sum to 1)
            
        Returns:
            Utility value
        """
        if np.any(quantities <= 0):
            return 0
        return np.prod(np.power(quantities, alpha))
    
    @staticmethod
    def ces_utility(quantities: np.ndarray, alpha: np.ndarray, rho: float) -> float:
        """
        Constant Elasticity of Substitution (CES) utility function
        U = (∑(α_i * x_i^ρ))^(1/ρ)
        
        Args:
            quantities: Array of quantities consumed
            alpha: Array of preference parameters
            rho: Substitution parameter
            
        Returns:
            Utility value
        """
        if rho == 0:
            return UtilityFunctions.cobb_douglas(quantities, alpha)
        
        ces_sum = np.sum(alpha * np.power(quantities, rho))
        return np.power(ces_sum, 1/rho) if ces_sum > 0 else 0
    
    @staticmethod
    def linear_utility(quantities: np.ndarray, alpha: np.ndarray) -> float:
        """
        Linear utility function: U = ∑(α_i * x_i)
        Perfect substitutes case
        """
        return np.sum(alpha * quantities)
    
    @staticmethod
    def leontief_utility(quantities: np.ndarray, alpha: np.ndarray) -> float:
        """
        Leontief utility function: U = min(x_i/α_i)
        Perfect complements case
        """
        return np.min(quantities / alpha)
    
    @staticmethod
    def spatial_utility(quantities: np.ndarray, alpha: np.ndarray, 
                       location: Tuple[float, float], 
                       accessibility_weight: float = 0.1) -> float:
        """
        Spatial utility function incorporating location-based preferences
        
        Args:
            quantities: Array of quantities consumed
            alpha: Array of preference parameters
            location: Consumer location (lat, lon)
            accessibility_weight: Weight for spatial accessibility component
            
        Returns:
            Spatial utility value
        """
        base_utility = UtilityFunctions.cobb_douglas(quantities, alpha)
        
        # Simple accessibility modifier (can be made more sophisticated)
        accessibility_factor = 1 + accessibility_weight * np.sum(location)
        
        return base_utility * accessibility_factor


class DemandFunctions:
    """
    Implementation of various demand function derivations and estimations
    """
    
    def __init__(self, utility_function: str = "cobb_douglas"):
        self.utility_function = utility_function
        self.estimated_parameters = {}
    
    def marshallian_demand_cobb_douglas(self, income: float, prices: np.ndarray, 
                                      alpha: np.ndarray) -> np.ndarray:
        """
        Marshallian (uncompensated) demand for Cobb-Douglas utility
        x_i = (α_i * m) / p_i
        
        Args:
            income: Consumer income
            prices: Array of prices
            alpha: Array of preference parameters
            
        Returns:
            Array of optimal quantities
        """
        return (alpha * income) / prices
    
    def hicksian_demand_cobb_douglas(self, prices: np.ndarray, alpha: np.ndarray,
                                   utility_target: float) -> np.ndarray:
        """
        Hicksian (compensated) demand for Cobb-Douglas utility
        
        Args:
            prices: Array of prices
            alpha: Array of preference parameters  
            utility_target: Target utility level
            
        Returns:
            Array of optimal quantities
        """
        # For Cobb-Douglas: x_i = (α_i/p_i) * (U / ∏(α_j^α_j / p_j^α_j))
        price_index = np.prod(np.power(prices / alpha, alpha))
        expenditure = utility_target * price_index
        
        return (alpha * expenditure) / prices
    
    def estimate_demand_system(self, data: pd.DataFrame, 
                             method: str = "ols") -> Dict[str, Any]:
        """
        Estimate demand system from consumer data
        
        Args:
            data: DataFrame with columns for quantities, prices, income, demographics
            method: Estimation method ('ols', 'sls', 'aids')
            
        Returns:
            Dictionary with estimated parameters and diagnostics
        """
        if method == "aids":
            return self._estimate_aids_system(data)
        elif method == "sls":
            return self._estimate_sls_system(data)
        else:
            return self._estimate_ols_system(data)
    
    def _estimate_aids_system(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Estimate Almost Ideal Demand System (AIDS)"""
        # Implementation of AIDS estimation
        # w_i = α_i + ∑γ_ij*ln(p_j) + β_i*ln(m/P)
        
        results = {
            "method": "AIDS",
            "parameters": {},
            "elasticities": {},
            "diagnostics": {}
        }
        
        # Placeholder for full AIDS implementation
        # This would involve system estimation with cross-equation restrictions
        
        return results
    
    def _estimate_ols_system(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Simple OLS estimation of demand functions"""
        from sklearn.linear_model import LinearRegression
        
        results = {}
        
        # Estimate each demand equation separately
        for good in ['good_1', 'good_2']:  # Example goods
            if f'quantity_{good}' in data.columns:
                X = data[['income', f'price_{good}']].values
                y = data[f'quantity_{good}'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                results[good] = {
                    'coefficients': model.coef_,
                    'intercept': model.intercept_,
                    'r_squared': model.score(X, y)
                }
        
        return results
    
    def _estimate_sls_system(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Seemingly Unrelated Regression (SUR) estimation"""
        # Placeholder for SUR implementation
        return {"method": "SLS", "status": "not_implemented"}


class ConsumerChoiceModels:
    """
    Consumer choice modeling with spatial considerations
    """
    
    def __init__(self, utility_function: Callable = None):
        self.utility_function = utility_function or UtilityFunctions.cobb_douglas
        self.spatial_weights = {}
    
    def solve_utility_maximization(self, consumer: ConsumerProfile, 
                                 prices: np.ndarray, 
                                 goods: List[str]) -> Dict[str, Any]:
        """
        Solve consumer utility maximization problem
        
        Args:
            consumer: Consumer profile with income and preferences
            prices: Array of market prices
            goods: List of good names
            
        Returns:
            Dictionary with optimal quantities, utility, and expenditure
        """
        def objective(quantities):
            """Negative utility to minimize"""
            alpha = np.array([consumer.preferences.get(good, 1.0) for good in goods])
            return -self.utility_function(quantities, alpha)
        
        def budget_constraint(quantities):
            """Budget constraint: sum(p_i * x_i) <= income"""
            return consumer.income - np.sum(prices * quantities)
        
        # Non-negativity constraints
        bounds = [(0, None) for _ in goods]
        
        # Budget constraint
        constraints = {'type': 'ineq', 'fun': budget_constraint}
        
        # Initial guess
        x0 = np.ones(len(goods))
        
        # Solve optimization
        result = minimize(objective, x0, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_quantities = result.x
            optimal_utility = -result.fun
            total_expenditure = np.sum(prices * optimal_quantities)
            
            return {
                'quantities': dict(zip(goods, optimal_quantities)),
                'utility': optimal_utility,
                'expenditure': total_expenditure,
                'savings': consumer.income - total_expenditure,
                'success': True
            }
        else:
            return {'success': False, 'message': result.message}
    
    def spatial_consumer_choice(self, consumer: ConsumerProfile,
                              spatial_markets: gpd.GeoDataFrame,
                              transport_costs: Dict[str, float]) -> Dict[str, Any]:
        """
        Model consumer choice with spatial market selection
        
        Args:
            consumer: Consumer profile with location
            spatial_markets: GeoDataFrame of market locations and prices
            transport_costs: Dictionary of transport cost parameters
            
        Returns:
            Dictionary with optimal market choice and consumption bundle
        """
        consumer_point = gpd.points_from_xy([consumer.location[1]], 
                                          [consumer.location[0]])[0]
        
        best_choice = None
        max_net_utility = -np.inf
        
        for idx, market in spatial_markets.iterrows():
            # Calculate transport cost
            distance = consumer_point.distance(market.geometry)
            transport_cost = transport_costs.get('per_km', 0.1) * distance
            
            # Adjust effective income
            effective_income = consumer.income - transport_cost
            
            if effective_income > 0:
                # Get market prices
                market_prices = np.array([market.get(f'price_{good}', 1.0) 
                                        for good in ['good_1', 'good_2']])
                
                # Solve consumer choice for this market
                temp_consumer = ConsumerProfile(
                    consumer_id=consumer.consumer_id,
                    income=effective_income,
                    location=consumer.location,
                    preferences=consumer.preferences,
                    demographic_attributes=consumer.demographic_attributes,
                    spatial_attributes=consumer.spatial_attributes
                )
                
                choice_result = self.solve_utility_maximization(
                    temp_consumer, market_prices, ['good_1', 'good_2']
                )
                
                if choice_result['success']:
                    net_utility = choice_result['utility']
                    
                    if net_utility > max_net_utility:
                        max_net_utility = net_utility
                        best_choice = {
                            'market_id': idx,
                            'market_location': market.geometry,
                            'transport_cost': transport_cost,
                            'consumption': choice_result,
                            'net_utility': net_utility
                        }
        
        return best_choice or {'success': False, 'message': 'No feasible choice'}


class WelfareAnalysis:
    """
    Consumer welfare analysis tools
    """
    
    @staticmethod
    def consumer_surplus_linear(demand_function: Callable, 
                              price: float, 
                              quantity: float) -> float:
        """
        Calculate consumer surplus for linear demand
        CS = 0.5 * (choke_price - market_price) * quantity
        """
        # This is a simplified implementation
        # In practice, would need to integrate under demand curve
        choke_price = demand_function(0)  # Price where quantity = 0
        return 0.5 * (choke_price - price) * quantity
    
    @staticmethod
    def equivalent_variation(utility_function: Callable,
                           income: float,
                           prices_old: np.ndarray,
                           prices_new: np.ndarray,
                           alpha: np.ndarray) -> float:
        """
        Calculate equivalent variation for price change
        
        Args:
            utility_function: Consumer's utility function
            income: Consumer income
            prices_old: Original prices
            prices_new: New prices
            alpha: Preference parameters
            
        Returns:
            Equivalent variation amount
        """
        # Calculate utility at original prices
        quantities_old = (alpha * income) / prices_old  # Assuming Cobb-Douglas
        utility_old = utility_function(quantities_old, alpha)
        
        # Find income needed at new prices to achieve old utility
        def objective(test_income):
            quantities_new = (alpha * test_income) / prices_new
            utility_new = utility_function(quantities_new, alpha)
            return (utility_new - utility_old) ** 2
        
        result = minimize_scalar(objective)
        income_equivalent = result.x if result.success else income
        
        return income - income_equivalent
    
    @staticmethod
    def compensating_variation(utility_function: Callable,
                             income: float,
                             prices_old: np.ndarray,
                             prices_new: np.ndarray,
                             alpha: np.ndarray) -> float:
        """
        Calculate compensating variation for price change
        """
        # Calculate utility at new prices
        quantities_new = (alpha * income) / prices_new
        utility_new = utility_function(quantities_new, alpha)
        
        # Find income needed at old prices to achieve new utility
        def objective(test_income):
            quantities_old = (alpha * test_income) / prices_old
            utility_old = utility_function(quantities_old, alpha)
            return (utility_old - utility_new) ** 2
        
        result = minimize_scalar(objective)
        income_compensating = result.x if result.success else income
        
        return income_compensating - income


class ConsumerSurplus:
    """
    Consumer surplus calculation and analysis
    """
    
    def __init__(self):
        self.demand_models = {}
    
    def calculate_surplus_integral(self, demand_function: Callable,
                                 price_range: Tuple[float, float],
                                 market_price: float) -> float:
        """
        Calculate consumer surplus by integrating under demand curve
        
        Args:
            demand_function: Function mapping price to quantity demanded
            price_range: (min_price, max_price) for integration
            market_price: Current market price
            
        Returns:
            Consumer surplus value
        """
        from scipy.integrate import quad
        
        def integrand(p):
            return max(0, demand_function(p))
        
        # Integrate from market price to maximum price
        surplus, _ = quad(integrand, market_price, price_range[1])
        
        return surplus
    
    def spatial_surplus_analysis(self, consumers: List[ConsumerProfile],
                               spatial_markets: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Analyze consumer surplus across spatial markets
        
        Args:
            consumers: List of consumer profiles with locations
            spatial_markets: GeoDataFrame of market locations and characteristics
            
        Returns:
            Dictionary with spatial surplus analysis results
        """
        results = {
            'total_surplus': 0,
            'market_surpluses': {},
            'consumer_surpluses': {},
            'spatial_distribution': {}
        }
        
        for consumer in consumers:
            # Find nearest markets
            consumer_point = gpd.points_from_xy([consumer.location[1]], 
                                              [consumer.location[0]])[0]
            
            # Calculate distances to all markets
            distances = spatial_markets.geometry.distance(consumer_point)
            nearest_market_idx = distances.idxmin()
            
            # Calculate consumer surplus for nearest market
            # This would involve solving the consumer choice problem
            # and calculating the surplus
            
            # Placeholder calculation
            market_surplus = 100  # Would be calculated based on actual choice
            
            results['consumer_surpluses'][consumer.consumer_id] = market_surplus
            results['total_surplus'] += market_surplus
            
            # Aggregate by market
            if nearest_market_idx not in results['market_surpluses']:
                results['market_surpluses'][nearest_market_idx] = 0
            results['market_surpluses'][nearest_market_idx] += market_surplus
        
        return results


# Example usage and testing functions
def example_consumer_analysis():
    """
    Example usage of consumer theory models
    """
    # Create sample consumer
    consumer = ConsumerProfile(
        consumer_id="consumer_001",
        income=1000.0,
        location=(40.7128, -74.0060),  # NYC coordinates
        preferences={"good_1": 0.6, "good_2": 0.4},
        demographic_attributes={"age": 35, "education": "college"},
        spatial_attributes={"accessibility_index": 0.8}
    )
    
    # Initialize choice model
    choice_model = ConsumerChoiceModels()
    
    # Solve utility maximization
    prices = np.array([2.0, 3.0])
    goods = ["good_1", "good_2"]
    
    result = choice_model.solve_utility_maximization(consumer, prices, goods)
    
    print("Consumer Choice Results:")
    print(f"Optimal quantities: {result.get('quantities', {})}")
    print(f"Maximum utility: {result.get('utility', 0):.2f}")
    print(f"Total expenditure: {result.get('expenditure', 0):.2f}")
    
    return result


if __name__ == "__main__":
    # Run example
    example_result = example_consumer_analysis() 