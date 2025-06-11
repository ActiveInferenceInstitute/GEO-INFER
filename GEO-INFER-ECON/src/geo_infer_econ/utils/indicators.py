"""
Economic indicators calculation utilities.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
import pandas as pd
from scipy import stats
import logging

class EconomicIndicators:
    """
    Utility class for calculating various economic indicators and metrics.
    
    Provides methods for computing standard economic measures and indices.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the EconomicIndicators calculator.
        
        Args:
            config: Optional configuration for calculations
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
    def calculate_growth_rate(self, 
                            values: Union[pd.Series, np.ndarray],
                            periods: int = 1,
                            method: str = 'simple') -> Union[pd.Series, np.ndarray]:
        """
        Calculate growth rates for time series data.
        
        Args:
            values: Time series values
            periods: Number of periods for growth calculation
            method: 'simple' or 'compound' growth rate
            
        Returns:
            Growth rates
        """
        if isinstance(values, pd.Series):
            if method == 'simple':
                return values.pct_change(periods=periods)
            else:  # compound
                return (values / values.shift(periods)) ** (1/periods) - 1
        else:
            if method == 'simple':
                return np.diff(values, n=periods) / values[:-periods]
            else:  # compound
                return (values[periods:] / values[:-periods]) ** (1/periods) - 1
                
    def calculate_gini_coefficient(self, values: np.ndarray) -> float:
        """
        Calculate Gini coefficient for inequality measurement.
        
        Args:
            values: Array of values (e.g., income, wealth)
            
        Returns:
            Gini coefficient (0 = perfect equality, 1 = perfect inequality)
        """
        # Sort values in ascending order
        sorted_values = np.sort(values)
        n = len(values)
        
        # Calculate Gini coefficient
        cumulative_values = np.cumsum(sorted_values)
        gini = (2 * np.sum((np.arange(1, n+1) * sorted_values))) / (n * cumulative_values[-1]) - (n + 1) / n
        
        return gini
        
    def calculate_theil_index(self, values: np.ndarray) -> float:
        """
        Calculate Theil index for inequality measurement.
        
        Args:
            values: Array of values
            
        Returns:
            Theil index
        """
        mean_value = np.mean(values)
        # Avoid log(0) by adding small epsilon
        ratio = values / mean_value
        ratio = np.where(ratio <= 0, 1e-10, ratio)
        
        theil = np.mean(ratio * np.log(ratio))
        return theil
        
    def calculate_unemployment_rate(self, 
                                  unemployed: Union[float, np.ndarray],
                                  labor_force: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate unemployment rate.
        
        Args:
            unemployed: Number of unemployed persons
            labor_force: Total labor force
            
        Returns:
            Unemployment rate (as percentage)
        """
        return (unemployed / labor_force) * 100
        
    def calculate_inflation_rate(self, 
                               prices: Union[pd.Series, np.ndarray],
                               base_period: int = 0) -> Union[pd.Series, np.ndarray]:
        """
        Calculate inflation rate from price index.
        
        Args:
            prices: Price index values
            base_period: Base period index
            
        Returns:
            Inflation rates
        """
        if isinstance(prices, pd.Series):
            base_price = prices.iloc[base_period]
            return ((prices / base_price) - 1) * 100
        else:
            base_price = prices[base_period]
            return ((prices / base_price) - 1) * 100
            
    def calculate_gdp_per_capita(self, 
                               gdp: Union[float, np.ndarray],
                               population: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """
        Calculate GDP per capita.
        
        Args:
            gdp: Gross Domestic Product
            population: Population size
            
        Returns:
            GDP per capita
        """
        return gdp / population
        
    def calculate_productivity_growth(self,
                                    output: np.ndarray,
                                    inputs: np.ndarray,
                                    method: str = 'total_factor') -> np.ndarray:
        """
        Calculate productivity growth.
        
        Args:
            output: Output values over time
            inputs: Input values over time (can be multidimensional)
            method: 'labor' or 'total_factor' productivity
            
        Returns:
            Productivity growth rates
        """
        if method == 'labor':
            # Simple labor productivity
            labor_productivity = output / inputs
            return self.calculate_growth_rate(labor_productivity)
        else:
            # Total factor productivity (simplified Solow residual)
            if inputs.ndim == 1:
                # Single input case
                tfp = output / inputs
            else:
                # Multiple inputs - geometric mean
                tfp = output / np.prod(inputs, axis=1)
                
            return self.calculate_growth_rate(tfp)
            
    def calculate_economic_complexity_index(self, 
                                          exports_matrix: np.ndarray,
                                          countries: List[str],
                                          products: List[str]) -> Dict[str, float]:
        """
        Calculate Economic Complexity Index (ECI) for countries.
        
        Args:
            exports_matrix: Matrix of exports (countries x products)
            countries: List of country names
            products: List of product names
            
        Returns:
            Dictionary with ECI values for each country
        """
        # This is a simplified version of the ECI calculation
        # Full implementation would follow Hidalgo & Hausmann methodology
        
        # Calculate Revealed Comparative Advantage (RCA)
        total_exports_country = np.sum(exports_matrix, axis=1, keepdims=True)
        total_exports_product = np.sum(exports_matrix, axis=0, keepdims=True)
        total_exports_world = np.sum(exports_matrix)
        
        # Avoid division by zero
        total_exports_country = np.where(total_exports_country == 0, 1e-10, total_exports_country)
        total_exports_product = np.where(total_exports_product == 0, 1e-10, total_exports_product)
        
        rca = (exports_matrix / total_exports_country) / (total_exports_product / total_exports_world)
        
        # Binary matrix (RCA >= 1)
        M = (rca >= 1).astype(int)
        
        # Calculate diversity and ubiquity
        diversity = np.sum(M, axis=1)  # Number of products with RCA >= 1
        ubiquity = np.sum(M, axis=0)   # Number of countries with RCA >= 1 for each product
        
        # Simple complexity measure (more sophisticated methods exist)
        complexity_scores = diversity / np.mean(diversity)
        
        return dict(zip(countries, complexity_scores))
        
    def calculate_regional_convergence(self, 
                                     regional_data: pd.DataFrame,
                                     value_column: str,
                                     time_column: str) -> Dict[str, float]:
        """
        Calculate regional convergence indicators.
        
        Args:
            regional_data: DataFrame with regional economic data
            value_column: Column with economic values (e.g., GDP per capita)
            time_column: Column with time periods
            
        Returns:
            Dictionary with convergence indicators
        """
        # Beta convergence
        initial_values = regional_data.groupby(regional_data.index)[value_column].first()
        final_values = regional_data.groupby(regional_data.index)[value_column].last()
        
        growth_rates = np.log(final_values / initial_values)
        log_initial = np.log(initial_values)
        
        # Simple regression for beta convergence
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_initial, growth_rates)
        beta_convergence = -slope
        
        # Sigma convergence
        time_periods = sorted(regional_data[time_column].unique())
        sigma_values = []
        
        for period in time_periods:
            period_data = regional_data[regional_data[time_column] == period][value_column]
            if len(period_data) > 1:
                sigma = np.std(np.log(period_data))
                sigma_values.append(sigma)
                
        sigma_convergence = len(sigma_values) > 1 and sigma_values[-1] < sigma_values[0]
        
        return {
            'beta_convergence': beta_convergence,
            'beta_significance': p_value,
            'sigma_convergence': sigma_convergence,
            'initial_sigma': sigma_values[0] if sigma_values else None,
            'final_sigma': sigma_values[-1] if sigma_values else None
        }
        
    def calculate_economic_distance(self, 
                                  region1_data: Dict[str, float],
                                  region2_data: Dict[str, float],
                                  method: str = 'euclidean') -> float:
        """
        Calculate economic distance between regions.
        
        Args:
            region1_data: Economic indicators for region 1
            region2_data: Economic indicators for region 2
            method: Distance metric ('euclidean', 'manhattan', 'cosine')
            
        Returns:
            Economic distance measure
        """
        # Get common indicators
        common_indicators = set(region1_data.keys()) & set(region2_data.keys())
        
        if not common_indicators:
            raise ValueError("No common economic indicators found")
            
        # Extract values for common indicators
        values1 = np.array([region1_data[ind] for ind in common_indicators])
        values2 = np.array([region2_data[ind] for ind in common_indicators])
        
        # Normalize values
        combined = np.vstack([values1, values2])
        normalized = (combined - np.mean(combined, axis=0)) / np.std(combined, axis=0)
        
        norm_values1, norm_values2 = normalized[0], normalized[1]
        
        if method == 'euclidean':
            distance = np.sqrt(np.sum((norm_values1 - norm_values2) ** 2))
        elif method == 'manhattan':
            distance = np.sum(np.abs(norm_values1 - norm_values2))
        elif method == 'cosine':
            dot_product = np.dot(norm_values1, norm_values2)
            norms = np.linalg.norm(norm_values1) * np.linalg.norm(norm_values2)
            distance = 1 - (dot_product / norms) if norms > 0 else 0
        else:
            raise ValueError(f"Unknown distance method: {method}")
            
        return distance 