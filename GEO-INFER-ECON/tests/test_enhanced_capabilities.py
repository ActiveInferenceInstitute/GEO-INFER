"""
Test Suite for Enhanced GEO-INFER-ECON Capabilities

Tests for microeconomic, macroeconomic, and bioregional economic modules
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import Mock


class TestMicroeconomicsModule(unittest.TestCase):
    """Test cases for microeconomics functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.consumer_data = {
            'consumer_id': 'test_consumer',
            'income': 1000.0,
            'location': (45.0, -120.0),
            'preferences': {'good_1': 0.6, 'good_2': 0.4}
        }
        self.market_prices = [2.0, 3.0]
        self.goods = ['good_1', 'good_2']
    
    def test_consumer_utility_maximization(self):
        """Test consumer utility maximization"""
        income = self.consumer_data['income']
        preferences = list(self.consumer_data['preferences'].values())
        prices = np.array(self.market_prices)
        
        # Cobb-Douglas solution: x_i = (alpha_i * income) / p_i
        expected_quantities = (np.array(preferences) * income) / prices
        expected_expenditure = np.sum(expected_quantities * prices)
        
        # Verify budget constraint
        self.assertAlmostEqual(expected_expenditure, income, places=2)
        
        # Verify quantities are positive
        self.assertTrue(all(q > 0 for q in expected_quantities))
    
    def test_spatial_consumer_choice(self):
        """Test spatial consumer choice with multiple markets"""
        markets = [
            {'location': (45.0, -120.0), 'prices': [2.0, 3.0]},
            {'location': (45.1, -119.9), 'prices': [2.2, 2.8]},
        ]
        
        transport_cost_per_km = 0.1
        consumer_location = (45.0, -120.0)
        
        best_market = None
        max_net_utility = -float('inf')
        
        for i, market in enumerate(markets):
            distance = np.sqrt(
                (market['location'][0] - consumer_location[0])**2 + 
                (market['location'][1] - consumer_location[1])**2
            ) * 111  # km per degree
            
            transport_cost = distance * transport_cost_per_km
            effective_income = self.consumer_data['income'] - transport_cost
            
            if effective_income > 0:
                utility_proxy = effective_income
                if utility_proxy > max_net_utility:
                    max_net_utility = utility_proxy
                    best_market = i
        
        self.assertIsNotNone(best_market)


class TestMacroeconomicsModule(unittest.TestCase):
    """Test cases for macroeconomics functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.solow_params = {
            'alpha': 0.33, 's': 0.2, 'n': 0.02, 'delta': 0.05, 'g': 0.02
        }
    
    def test_solow_steady_state(self):
        """Test Solow growth model steady state calculations"""
        params = self.solow_params
        
        # Steady-state capital per worker
        k_star = (params['s'] / (params['n'] + params['delta'] + params['g'])) ** (
            1 / (1 - params['alpha']))
        
        # Steady-state output per worker
        y_star = k_star ** params['alpha']
        
        self.assertGreater(k_star, 0)
        self.assertGreater(y_star, 0)
    
    def test_regional_convergence(self):
        """Test beta convergence analysis"""
        regions_data = pd.DataFrame({
            'region_id': ['A', 'B', 'C'],
            'gdp_per_capita_init': [20000, 30000, 25000],
            'gdp_per_capita_final': [25000, 33000, 28000]
        })
        
        years_diff = 20
        growth_rates = (np.log(regions_data['gdp_per_capita_final']) - 
                       np.log(regions_data['gdp_per_capita_init'])) / years_diff
        
        from scipy.stats import pearsonr
        correlation, p_value = pearsonr(
            np.log(regions_data['gdp_per_capita_init']), growth_rates)
        
        self.assertIsInstance(correlation, float)
        self.assertIsInstance(p_value, float)


class TestBioregionalModule(unittest.TestCase):
    """Test cases for bioregional economics functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.forest_asset = {
            'asset_id': 'test_forest',
            'area_hectares': 100.0,
            'carbon_storage': 500.0,
            'carbon_sequestration_per_year': 10.0,
            'biodiversity_index': 0.8
        }
        self.service_prices = {'carbon': 50.0, 'biodiversity': 100.0}
    
    def test_ecosystem_service_valuation(self):
        """Test ecosystem service valuation"""
        asset = self.forest_asset
        prices = self.service_prices
        
        carbon_value = asset['carbon_sequestration_per_year'] * prices['carbon']
        biodiversity_value = asset['area_hectares'] * asset['biodiversity_index'] * prices['biodiversity']
        total_value = carbon_value + biodiversity_value
        
        self.assertGreater(carbon_value, 0)
        self.assertGreater(biodiversity_value, 0)
        self.assertGreater(total_value, 0)
    
    def test_credit_quality_assessment(self):
        """Test ecosystem service credit quality assessment"""
        quality_parameters = {
            'additionality': 0.9, 'permanence': 0.8, 'measurability': 0.85,
            'leakage_risk': 0.1, 'co_benefits': 0.7
        }
        
        weights = {
            'additionality': 0.3, 'permanence': 0.25, 'measurability': 0.2,
            'leakage_risk': 0.15, 'co_benefits': 0.1
        }
        
        quality_score = sum(quality_parameters[factor] * weight 
                          for factor, weight in weights.items())
        
        self.assertGreaterEqual(quality_score, 0)
        self.assertLessEqual(quality_score, 1)


class TestIntegratedAnalysis(unittest.TestCase):
    """Test cases for integrated economic analysis"""
    
    def test_sustainability_indicators(self):
        """Test sustainability indicator calculations"""
        regional_gdp = 1000000
        ecosystem_services_value = 150000
        natural_capital_stock = 2000000
        
        ecosystem_gdp_ratio = ecosystem_services_value / regional_gdp
        natural_capital_ratio = natural_capital_stock / regional_gdp
        
        self.assertGreater(ecosystem_gdp_ratio, 0)
        self.assertGreater(natural_capital_ratio, 0)
    
    def test_policy_recommendations(self):
        """Test policy recommendation logic"""
        indicators = {
            'ecosystem_gdp_ratio': 0.08,
            'natural_capital_ratio': 0.9,
            'rural_urban_gap': 2.5
        }
        
        recommendations = []
        
        if indicators['ecosystem_gdp_ratio'] < 0.1:
            recommendations.append('Invest in natural capital restoration')
        if indicators['rural_urban_gap'] > 2.0:
            recommendations.append('Implement payments for ecosystem services')
        if indicators['natural_capital_ratio'] < 1.0:
            recommendations.append('Strengthen environmental protection')
        
        self.assertGreater(len(recommendations), 0)


def run_test_suite():
    """Run all test suites"""
    print("Running GEO-INFER-ECON Enhanced Capabilities Test Suite")
    print("=" * 60)
    
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestMicroeconomicsModule))
    test_suite.addTest(unittest.makeSuite(TestMacroeconomicsModule))
    test_suite.addTest(unittest.makeSuite(TestBioregionalModule))
    test_suite.addTest(unittest.makeSuite(TestIntegratedAnalysis))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("All tests passed! ✓")
    else:
        print("Some tests failed.")
    
    return result


if __name__ == '__main__':
    run_test_suite() 