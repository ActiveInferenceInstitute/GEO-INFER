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

class EcosystemService:
    """Represents an ecosystem service with economic value."""
    
    def __init__(self, 
                 service_type: str,
                 name: str,
                 description: str,
                 unit: str,
                 value_per_unit: float):
        """
        Initialize ecosystem service.
        
        Args:
            service_type: Type of ecosystem service
            name: Name of the service
            description: Description of the service
            unit: Unit of measurement
            value_per_unit: Economic value per unit
        """
        self.service_type = service_type
        self.name = name
        self.description = description
        self.unit = unit
        self.value_per_unit = value_per_unit
        self.quantity = 0.0
        self.total_value = 0.0
    
    def calculate_value(self, quantity: float) -> float:
        """
        Calculate total economic value.
        
        Args:
            quantity: Quantity of the service
            
        Returns:
            Total economic value
        """
        self.quantity = quantity
        self.total_value = quantity * self.value_per_unit
        return self.total_value

class NaturalCapitalAccount:
    """Natural capital accounting system."""
    
    def __init__(self, config: Optional[EcologicalEconomicsConfig] = None):
        """
        Initialize natural capital account.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or EcologicalEconomicsConfig()
        self.assets = {}
        self.services = {}
        self.flows = []
    
    def add_ecosystem_asset(self, 
                           asset_id: str,
                           asset_type: str,
                           location: Dict[str, float],
                           area: float,
                           condition: float = 1.0) -> str:
        """
        Add an ecosystem asset to the account.
        
        Args:
            asset_id: Unique asset identifier
            asset_type: Type of ecosystem asset
            location: Geographic location
            area: Area of the asset
            condition: Condition of the asset (0-1)
            
        Returns:
            Asset identifier
        """
        asset = {
            'id': asset_id,
            'type': asset_type,
            'location': location,
            'area': area,
            'condition': condition,
            'services': [],
            'value': 0.0
        }
        
        self.assets[asset_id] = asset
        logger.info(f"Added ecosystem asset: {asset_id}")
        
        return asset_id
    
    def add_ecosystem_service(self, 
                            asset_id: str,
                            service: EcosystemService,
                            quantity: float) -> bool:
        """
        Add an ecosystem service to an asset.
        
        Args:
            asset_id: Asset identifier
            service: Ecosystem service
            quantity: Quantity of the service
            
        Returns:
            True if successful
        """
        if asset_id not in self.assets:
            logger.error(f"Asset {asset_id} not found")
            return False
        
        # Calculate service value
        service_value = service.calculate_value(quantity)
        
        # Add service to asset
        self.assets[asset_id]['services'].append({
            'service': service,
            'quantity': quantity,
            'value': service_value
        })
        
        # Update asset total value
        self.assets[asset_id]['value'] += service_value
        
        logger.info(f"Added service {service.name} to asset {asset_id}")
        return True
    
    def calculate_total_natural_capital(self) -> Dict[str, float]:
        """
        Calculate total natural capital value.
        
        Returns:
            Dictionary with total values by category
        """
        totals = {
            'total_value': 0.0,
            'by_asset_type': {},
            'by_service_type': {}
        }
        
        for asset_id, asset in self.assets.items():
            asset_value = asset['value']
            totals['total_value'] += asset_value
            
            # By asset type
            asset_type = asset['type']
            if asset_type not in totals['by_asset_type']:
                totals['by_asset_type'][asset_type] = 0.0
            totals['by_asset_type'][asset_type] += asset_value
            
            # By service type
            for service_data in asset['services']:
                service_type = service_data['service'].service_type
                if service_type not in totals['by_service_type']:
                    totals['by_service_type'][service_type] = 0.0
                totals['by_service_type'][service_type] += service_data['value']
        
        return totals
    
    def generate_balance_sheet(self) -> pd.DataFrame:
        """
        Generate natural capital balance sheet.
        
        Returns:
            DataFrame with balance sheet information
        """
        balance_data = []
        
        for asset_id, asset in self.assets.items():
            for service_data in asset['services']:
                service = service_data['service']
                
                balance_data.append({
                    'asset_id': asset_id,
                    'asset_type': asset['type'],
                    'service_name': service.name,
                    'service_type': service.service_type,
                    'quantity': service_data['quantity'],
                    'unit': service.unit,
                    'value_per_unit': service.value_per_unit,
                    'total_value': service_data['value'],
                    'area': asset['area'],
                    'condition': asset['condition']
                })
        
        return pd.DataFrame(balance_data)

class EcologicalEconomicsEngine:
    """Main engine for ecological economics analysis."""
    
    def __init__(self, config: Optional[EcologicalEconomicsConfig] = None):
        """
        Initialize ecological economics engine.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or EcologicalEconomicsConfig()
        self.natural_capital = NaturalCapitalAccount(config)
        self.valuation_methods = {}
        self._initialize_valuation_methods()
    
    def _initialize_valuation_methods(self):
        """Initialize valuation methods."""
        self.valuation_methods = {
            'market_price': self._market_price_valuation,
            'replacement_cost': self._replacement_cost_valuation,
            'travel_cost': self._travel_cost_valuation,
            'hedonic_pricing': self._hedonic_pricing_valuation,
            'contingent_valuation': self._contingent_valuation_valuation,
            'choice_experiment': self._choice_experiment_valuation
        }
    
    def analyze_ecosystem_services(self, 
                                 location: Dict[str, float],
                                 area: float,
                                 ecosystem_type: str) -> Dict[str, Any]:
        """
        Analyze ecosystem services for a given location.
        
        Args:
            location: Geographic location
            area: Area of analysis
            ecosystem_type: Type of ecosystem
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing ecosystem services for {ecosystem_type}")
        
        # Create ecosystem asset
        asset_id = f"{ecosystem_type}_{location['lat']:.3f}_{location['lon']:.3f}"
        self.natural_capital.add_ecosystem_asset(
            asset_id, ecosystem_type, location, area
        )
        
        # Define ecosystem services based on type
        services = self._get_ecosystem_services(ecosystem_type, area)
        
        # Add services to asset
        for service in services:
            self.natural_capital.add_ecosystem_service(
                asset_id, service['service'], service['quantity']
            )
        
        # Calculate total value
        total_value = self.natural_capital.assets[asset_id]['value']
        
        analysis = {
            'asset_id': asset_id,
            'ecosystem_type': ecosystem_type,
            'location': location,
            'area': area,
            'total_value': total_value,
            'services': services,
            'value_per_hectare': total_value / area if area > 0 else 0
        }
        
        return analysis
    
    def _get_ecosystem_services(self, ecosystem_type: str, area: float) -> List[Dict[str, Any]]:
        """Get ecosystem services for a given ecosystem type."""
        services = []
        
        if ecosystem_type == 'forest':
            services = [
                {
                    'service': EcosystemService('provisioning', 'Timber', 'Wood products', 'm3', 50.0),
                    'quantity': area * 0.1  # 0.1 m3 per hectare
                },
                {
                    'service': EcosystemService('regulating', 'Carbon sequestration', 'CO2 absorption', 'tons', 100.0),
                    'quantity': area * 5.0  # 5 tons per hectare
                },
                {
                    'service': EcosystemService('cultural', 'Recreation', 'Recreational value', 'visits', 25.0),
                    'quantity': area * 2.0  # 2 visits per hectare
                }
            ]
        elif ecosystem_type == 'wetland':
            services = [
                {
                    'service': EcosystemService('regulating', 'Water purification', 'Water filtration', 'm3', 10.0),
                    'quantity': area * 100.0  # 100 m3 per hectare
                },
                {
                    'service': EcosystemService('regulating', 'Flood control', 'Flood mitigation', 'm3', 200.0),
                    'quantity': area * 50.0  # 50 m3 per hectare
                },
                {
                    'service': EcosystemService('supporting', 'Biodiversity', 'Species habitat', 'species', 1000.0),
                    'quantity': area * 0.5  # 0.5 species per hectare
                }
            ]
        elif ecosystem_type == 'grassland':
            services = [
                {
                    'service': EcosystemService('provisioning', 'Grazing', 'Livestock feed', 'tons', 30.0),
                    'quantity': area * 2.0  # 2 tons per hectare
                },
                {
                    'service': EcosystemService('regulating', 'Soil retention', 'Soil conservation', 'tons', 50.0),
                    'quantity': area * 1.0  # 1 ton per hectare
                }
            ]
        else:
            # Default services
            services = [
                {
                    'service': EcosystemService('supporting', 'General ecosystem', 'Basic ecosystem function', 'units', 10.0),
                    'quantity': area * 1.0
                }
            ]
        
        return services
    
    def calculate_ecosystem_service_value(self, 
                                        service_type: str,
                                        quantity: float,
                                        method: str = 'market_price') -> float:
        """
        Calculate economic value of ecosystem service.
        
        Args:
            service_type: Type of ecosystem service
            quantity: Quantity of the service
            method: Valuation method
            
        Returns:
            Economic value
        """
        if method not in self.valuation_methods:
            logger.warning(f"Unknown valuation method: {method}, using market_price")
            method = 'market_price'
        
        return self.valuation_methods[method](service_type, quantity)
    
    def _market_price_valuation(self, service_type: str, quantity: float) -> float:
        """Market price valuation method."""
        # Simplified market prices
        market_prices = {
            'timber': 50.0,
            'carbon': 25.0,
            'water': 1.0,
            'recreation': 25.0,
            'biodiversity': 1000.0,
            'grazing': 30.0,
            'soil': 50.0
        }
        
        price = market_prices.get(service_type.lower(), 10.0)
        return quantity * price
    
    def _replacement_cost_valuation(self, service_type: str, quantity: float) -> float:
        """Replacement cost valuation method."""
        # Simplified replacement costs
        replacement_costs = {
            'water_purification': 5.0,
            'flood_control': 100.0,
            'carbon_sequestration': 50.0,
            'soil_retention': 100.0
        }
        
        cost = replacement_costs.get(service_type.lower(), 20.0)
        return quantity * cost
    
    def _travel_cost_valuation(self, service_type: str, quantity: float) -> float:
        """Travel cost valuation method."""
        # Simplified travel cost model
        if service_type.lower() in ['recreation', 'tourism']:
            return quantity * 50.0  # $50 per visit
        return 0.0
    
    def _hedonic_pricing_valuation(self, service_type: str, quantity: float) -> float:
        """Hedonic pricing valuation method."""
        # Simplified hedonic pricing
        if service_type.lower() in ['scenic_view', 'proximity_to_nature']:
            return quantity * 1000.0  # $1000 per unit of scenic value
        return 0.0
    
    def _contingent_valuation_valuation(self, service_type: str, quantity: float) -> float:
        """Contingent valuation method."""
        # Simplified contingent valuation
        willingness_to_pay = {
            'biodiversity': 100.0,
            'clean_water': 50.0,
            'clean_air': 75.0,
            'recreation': 25.0
        }
        
        wtp = willingness_to_pay.get(service_type.lower(), 25.0)
        return quantity * wtp
    
    def _choice_experiment_valuation(self, service_type: str, quantity: float) -> float:
        """Choice experiment valuation method."""
        # Simplified choice experiment
        return self._contingent_valuation_valuation(service_type, quantity) * 0.8
    
    def perform_cost_benefit_analysis(self, 
                                    project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform cost-benefit analysis for environmental projects.
        
        Args:
            project_data: Project information
            
        Returns:
            Cost-benefit analysis results
        """
        logger.info("Performing cost-benefit analysis")
        
        # Extract project parameters
        initial_cost = project_data.get('initial_cost', 0)
        annual_benefits = project_data.get('annual_benefits', 0)
        annual_costs = project_data.get('annual_costs', 0)
        project_life = project_data.get('project_life', 20)
        discount_rate = project_data.get('discount_rate', self.config.discount_rate)
        
        # Calculate present values
        pv_benefits = 0
        pv_costs = initial_cost
        
        for year in range(1, project_life + 1):
            discount_factor = 1 / ((1 + discount_rate) ** year)
            pv_benefits += annual_benefits * discount_factor
            pv_costs += annual_costs * discount_factor
        
        # Calculate metrics
        net_present_value = pv_benefits - pv_costs
        benefit_cost_ratio = pv_benefits / pv_costs if pv_costs > 0 else float('inf')
        internal_rate_of_return = self._calculate_irr(initial_cost, annual_benefits - annual_costs, project_life)
        
        analysis = {
            'net_present_value': net_present_value,
            'benefit_cost_ratio': benefit_cost_ratio,
            'internal_rate_of_return': internal_rate_of_return,
            'present_value_benefits': pv_benefits,
            'present_value_costs': pv_costs,
            'project_life': project_life,
            'discount_rate': discount_rate,
            'recommendation': 'Accept' if net_present_value > 0 else 'Reject'
        }
        
        return analysis
    
    def _calculate_irr(self, initial_investment: float, annual_cash_flow: float, years: int) -> float:
        """Calculate internal rate of return."""
        # Simplified IRR calculation
        if annual_cash_flow <= 0:
            return 0.0
        
        # Use approximation: IRR ≈ annual_cash_flow / initial_investment
        return min(annual_cash_flow / initial_investment, 0.5)  # Cap at 50%
    
    def generate_ecosystem_service_report(self, 
                                        location: Dict[str, float],
                                        radius: float = 10.0) -> Dict[str, Any]:
        """
        Generate comprehensive ecosystem service report.
        
        Args:
            location: Center location
            radius: Analysis radius in km
            
        Returns:
            Ecosystem service report
        """
        logger.info(f"Generating ecosystem service report for location {location}")
        
        # Simulate ecosystem data around location
        ecosystems = self._generate_ecosystem_data(location, radius)
        
        total_value = 0
        service_summary = {}
        
        for ecosystem in ecosystems:
            analysis = self.analyze_ecosystem_services(
                ecosystem['location'],
                ecosystem['area'],
                ecosystem['type']
            )
            
            total_value += analysis['total_value']
            
            # Aggregate services
            for service in analysis['services']:
                service_name = service['service'].name
                if service_name not in service_summary:
                    service_summary[service_name] = 0
                service_summary[service_name] += service['value']
        
        report = {
            'location': location,
            'radius_km': radius,
            'total_ecosystem_value': total_value,
            'ecosystem_count': len(ecosystems),
            'service_summary': service_summary,
            'ecosystems': ecosystems,
            'recommendations': self._generate_recommendations(ecosystems, total_value)
        }
        
        return report
    
    def _generate_ecosystem_data(self, 
                               center_location: Dict[str, float],
                               radius: float) -> List[Dict[str, Any]]:
        """Generate simulated ecosystem data around a location."""
        import random
        
        ecosystems = []
        ecosystem_types = ['forest', 'wetland', 'grassland', 'agricultural']
        
        # Generate 5-10 ecosystems within radius
        n_ecosystems = random.randint(5, 10)
        
        for i in range(n_ecosystems):
            # Random location within radius
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(0, radius)
            
            lat_offset = distance * np.cos(angle) / 111  # Convert km to degrees
            lon_offset = distance * np.sin(angle) / (111 * np.cos(np.radians(center_location['lat'])))
            
            location = {
                'lat': center_location['lat'] + lat_offset,
                'lon': center_location['lon'] + lon_offset
            }
            
            ecosystem = {
                'id': f"eco_{i}",
                'type': random.choice(ecosystem_types),
                'location': location,
                'area': random.uniform(10, 100),  # hectares
                'condition': random.uniform(0.5, 1.0)
            }
            
            ecosystems.append(ecosystem)
        
        return ecosystems
    
    def _generate_recommendations(self, 
                                ecosystems: List[Dict[str, Any]],
                                total_value: float) -> List[str]:
        """Generate recommendations based on ecosystem analysis."""
        recommendations = []
        
        # Analyze ecosystem types
        ecosystem_types = [eco['type'] for eco in ecosystems]
        type_counts = pd.Series(ecosystem_types).value_counts()
        
        if 'wetland' not in type_counts:
            recommendations.append("Consider wetland restoration for water quality improvement")
        
        if type_counts.get('forest', 0) < 2:
            recommendations.append("Increase forest cover for carbon sequestration")
        
        if total_value < 1000000:  # $1M threshold
            recommendations.append("Implement ecosystem restoration projects to increase value")
        
        if not recommendations:
            recommendations.append("Ecosystem services appear well-balanced")
        
        return recommendations

# Convenience functions
def create_ecological_economics_engine(config: Optional[EcologicalEconomicsConfig] = None) -> EcologicalEconomicsEngine:
    """Create a new ecological economics engine."""
    return EcologicalEconomicsEngine(config)

def calculate_ecosystem_value(location: Dict[str, float], 
                            ecosystem_type: str,
                            area: float) -> float:
    """Calculate ecosystem value for a given location and type."""
    engine = EcologicalEconomicsEngine()
    analysis = engine.analyze_ecosystem_services(location, area, ecosystem_type)
    return analysis['total_value']

def perform_ecosystem_valuation(ecosystem_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Perform ecosystem valuation for multiple locations."""
    engine = EcologicalEconomicsEngine()
    
    results = []
    for eco in ecosystem_data:
        analysis = engine.analyze_ecosystem_services(
            eco['location'], eco['area'], eco['type']
        )
        results.append({
            'location': eco['location'],
            'ecosystem_type': eco['type'],
            'area': eco['area'],
            'total_value': analysis['total_value'],
            'value_per_hectare': analysis['value_per_hectare']
        })
    
    return pd.DataFrame(results) 