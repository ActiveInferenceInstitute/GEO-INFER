"""
Bioregional Market Design Module

Implements comprehensive bioregional market mechanisms including:
- Ecosystem services markets and trading systems
- Natural capital accounting and trading
- Biodiversity credits and habitat banking
- Carbon markets and sequestration credits
- Water resource markets and watershed trading
- Local food systems and circular economy markets
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import geopandas as gpd
from scipy.optimize import minimize, linprog
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import networkx as nx


@dataclass
class BioregionalAsset:
    """Represents a bioregional asset with ecological and economic attributes"""
    asset_id: str
    asset_type: str  # forest, wetland, grassland, agricultural, etc.
    location: Tuple[float, float]  # (lat, lon)
    area_hectares: float
    ecological_attributes: Dict[str, float]  # biodiversity, carbon storage, etc.
    economic_attributes: Dict[str, float]  # market value, income potential, etc.
    ownership_type: str  # private, public, community, cooperative
    management_regime: str  # conservation, sustainable use, restoration
    ecosystem_services: Dict[str, float]  # provisioning, regulating, cultural, supporting


@dataclass
class MarketParticipant:
    """Represents a participant in bioregional markets"""
    participant_id: str
    participant_type: str  # landowner, buyer, intermediary, regulator
    location: Tuple[float, float]
    assets_owned: List[str]  # list of asset IDs
    market_preferences: Dict[str, float]
    budget_constraints: Dict[str, float]
    sustainability_goals: Dict[str, float]


@dataclass
class EcosystemServiceCredit:
    """Represents a tradeable ecosystem service credit"""
    credit_id: str
    service_type: str  # carbon, biodiversity, water, pollination, etc.
    quantity: float  # units of service
    quality_tier: str  # high, medium, low based on additionality and permanence
    location: Tuple[float, float]
    temporal_profile: str  # permanent, temporary, periodic
    verification_status: str  # verified, pending, self-reported
    price_per_unit: float
    expiration_date: Optional[datetime]
    co_benefits: Dict[str, float]  # additional ecological benefits


class BioregionalMarketDesign:
    """
    Core engine for designing and operating bioregional markets
    """
    
    def __init__(self, bioregion_boundary: gpd.GeoDataFrame):
        self.bioregion = bioregion_boundary
        self.assets = {}
        self.participants = {}
        self.credits = {}
        self.market_mechanisms = {}
        self.transaction_history = []
    
    def register_asset(self, asset: BioregionalAsset) -> bool:
        """Register a bioregional asset in the market system"""
        self.assets[asset.asset_id] = asset
        return True
    
    def register_participant(self, participant: MarketParticipant) -> bool:
        """Register a market participant"""
        self.participants[participant.participant_id] = participant
        return True
    
    def create_ecosystem_service_credit(self, asset_id: str, 
                                      service_type: str,
                                      quantity: float,
                                      quality_parameters: Dict[str, Any]) -> EcosystemServiceCredit:
        """
        Create ecosystem service credits from bioregional assets
        
        Args:
            asset_id: ID of the asset generating the service
            service_type: Type of ecosystem service
            quantity: Quantity of service units
            quality_parameters: Parameters for credit quality assessment
            
        Returns:
            EcosystemServiceCredit object
        """
        asset = self.assets[asset_id]
        
        # Quality assessment based on asset characteristics
        quality_score = self._assess_credit_quality(asset, service_type, quality_parameters)
        quality_tier = 'high' if quality_score > 0.8 else 'medium' if quality_score > 0.5 else 'low'
        
        # Price determination based on quality, location, and market conditions
        base_price = self._determine_base_price(service_type, quality_tier)
        location_multiplier = self._calculate_location_multiplier(asset.location, service_type)
        price_per_unit = base_price * location_multiplier
        
        credit = EcosystemServiceCredit(
            credit_id=f"{asset_id}_{service_type}_{datetime.now().isoformat()}",
            service_type=service_type,
            quantity=quantity,
            quality_tier=quality_tier,
            location=asset.location,
            temporal_profile=quality_parameters.get('temporal_profile', 'permanent'),
            verification_status='pending',
            price_per_unit=price_per_unit,
            expiration_date=quality_parameters.get('expiration_date'),
            co_benefits=self._calculate_co_benefits(asset, service_type)
        )
        
        self.credits[credit.credit_id] = credit
        return credit
    
    def _assess_credit_quality(self, asset: BioregionalAsset, 
                              service_type: str, 
                              parameters: Dict[str, Any]) -> float:
        """Assess the quality of ecosystem service credits"""
        quality_factors = {
            'additionality': 0.3,  # Would the service occur without the project?
            'permanence': 0.25,    # How long will the service be maintained?
            'measurability': 0.2,  # How accurately can we measure the service?
            'leakage_risk': 0.15,  # Risk of negative effects elsewhere  
            'co_benefits': 0.1     # Additional ecological benefits
        }
        
        score = 0
        for factor, weight in quality_factors.items():
            factor_score = parameters.get(factor, 0.5)  # Default to medium quality
            score += factor_score * weight
        
        return score
    
    def _determine_base_price(self, service_type: str, quality_tier: str) -> float:
        """Determine base price for ecosystem service credits"""
        base_prices = {
            'carbon': {'high': 50, 'medium': 30, 'low': 15},
            'biodiversity': {'high': 100, 'medium': 60, 'low': 30},
            'water_quality': {'high': 80, 'medium': 50, 'low': 25},
            'pollination': {'high': 120, 'medium': 70, 'low': 35},
            'flood_control': {'high': 90, 'medium': 55, 'low': 28}
        }
        
        return base_prices.get(service_type, {'high': 50, 'medium': 30, 'low': 15})[quality_tier]
    
    def _calculate_location_multiplier(self, location: Tuple[float, float], 
                                     service_type: str) -> float:
        """Calculate location-based price multiplier"""
        # Simple distance-based multiplier (can be made more sophisticated)
        # Closer to population centers or vulnerable areas gets higher prices
        
        # Placeholder: urban proximity multiplier
        # In practice, would use actual spatial analysis
        urban_proximity = 1.0  # Would calculate based on distance to urban areas
        
        # Ecosystem service specific location factors
        location_factors = {
            'carbon': 1.0,  # Global benefit
            'biodiversity': urban_proximity * 0.8 + 0.2,  # Higher value near cities
            'water_quality': urban_proximity,  # Higher value for urban watersheds
            'pollination': urban_proximity * 0.6 + 0.4,  # Value for agricultural areas
            'flood_control': urban_proximity  # Higher value protecting urban areas
        }
        
        return location_factors.get(service_type, 1.0)
    
    def _calculate_co_benefits(self, asset: BioregionalAsset, 
                              service_type: str) -> Dict[str, float]:
        """Calculate co-benefits of ecosystem service credits"""
        co_benefits = {}
        
        # Example co-benefit calculations
        if service_type == 'carbon':
            co_benefits['biodiversity'] = asset.ecological_attributes.get('biodiversity_index', 0) * 0.5
            co_benefits['water_quality'] = asset.ecological_attributes.get('water_filtration', 0) * 0.3
        
        elif service_type == 'biodiversity':
            co_benefits['carbon'] = asset.ecological_attributes.get('carbon_storage', 0) * 0.4
            co_benefits['recreation'] = asset.ecological_attributes.get('recreation_value', 0) * 0.6
        
        return co_benefits


class EcosystemServicesMarkets:
    """
    Specialized markets for different ecosystem services
    """
    
    def __init__(self, market_design: BioregionalMarketDesign):
        self.market_design = market_design
        self.order_book = {'buy': [], 'sell': []}
        self.market_clearing_mechanism = 'double_auction'
    
    def submit_buy_order(self, participant_id: str, service_type: str, 
                        quantity: float, max_price: float,
                        location_preferences: Dict[str, Any]) -> str:
        """Submit a buy order for ecosystem services"""
        order = {
            'order_id': f"buy_{participant_id}_{datetime.now().isoformat()}",
            'participant_id': participant_id,
            'order_type': 'buy',
            'service_type': service_type,
            'quantity': quantity,
            'price': max_price,
            'location_preferences': location_preferences,
            'timestamp': datetime.now()
        }
        
        self.order_book['buy'].append(order)
        return order['order_id']
    
    def submit_sell_order(self, participant_id: str, credit_id: str, 
                         min_price: float) -> str:
        """Submit a sell order for ecosystem service credits"""
        credit = self.market_design.credits[credit_id]
        
        order = {
            'order_id': f"sell_{participant_id}_{datetime.now().isoformat()}",
            'participant_id': participant_id,
            'order_type': 'sell',
            'credit_id': credit_id,
            'service_type': credit.service_type,
            'quantity': credit.quantity,
            'price': max(min_price, credit.price_per_unit),
            'quality_tier': credit.quality_tier,
            'location': credit.location,
            'timestamp': datetime.now()
        }
        
        self.order_book['sell'].append(order)
        return order['order_id']
    
    def clear_market(self) -> List[Dict[str, Any]]:
        """Clear the market and execute trades"""
        if self.market_clearing_mechanism == 'double_auction':
            return self._double_auction_clearing()
        elif self.market_clearing_mechanism == 'call_auction':
            return self._call_auction_clearing()
        else:
            return []
    
    def _double_auction_clearing(self) -> List[Dict[str, Any]]:
        """Double auction market clearing mechanism"""
        transactions = []
        
        # Sort buy orders by price (descending) and sell orders by price (ascending)
        buy_orders = sorted(self.order_book['buy'], key=lambda x: x['price'], reverse=True)
        sell_orders = sorted(self.order_book['sell'], key=lambda x: x['price'])
        
        for buy_order in buy_orders:
            for sell_order in sell_orders:
                # Check if orders can be matched
                if (buy_order['service_type'] == sell_order['service_type'] and
                    buy_order['price'] >= sell_order['price'] and
                    buy_order['quantity'] > 0 and sell_order['quantity'] > 0):
                    
                    # Check location preferences
                    if self._check_location_compatibility(buy_order, sell_order):
                        # Execute trade
                        trade_quantity = min(buy_order['quantity'], sell_order['quantity'])
                        trade_price = (buy_order['price'] + sell_order['price']) / 2
                        
                        transaction = {
                            'transaction_id': f"trade_{datetime.now().isoformat()}",
                            'buy_order_id': buy_order['order_id'],
                            'sell_order_id': sell_order['order_id'],
                            'service_type': buy_order['service_type'],
                            'quantity': trade_quantity,
                            'price': trade_price,
                            'timestamp': datetime.now()
                        }
                        
                        transactions.append(transaction)
                        
                        # Update order quantities
                        buy_order['quantity'] -= trade_quantity
                        sell_order['quantity'] -= trade_quantity
                        
                        # Record transaction
                        self.market_design.transaction_history.append(transaction)
        
        # Remove completed orders
        self.order_book['buy'] = [order for order in self.order_book['buy'] if order['quantity'] > 0]
        self.order_book['sell'] = [order for order in self.order_book['sell'] if order['quantity'] > 0]
        
        return transactions
    
    def _check_location_compatibility(self, buy_order: Dict, sell_order: Dict) -> bool:
        """Check if buy and sell orders are locationally compatible"""
        location_prefs = buy_order.get('location_preferences', {})
        
        if not location_prefs:
            return True  # No location preferences
        
        # Calculate distance between buyer preference and asset location
        max_distance = location_prefs.get('max_distance_km', float('inf'))
        preferred_location = location_prefs.get('preferred_location')
        
        if preferred_location:
            distance = np.sqrt(
                (sell_order['location'][0] - preferred_location[0])**2 +
                (sell_order['location'][1] - preferred_location[1])**2
            ) * 111  # Approximate km per degree
            
            return distance <= max_distance
        
        return True
    
    def _call_auction_clearing(self) -> List[Dict[str, Any]]:
        """Call auction market clearing mechanism"""
        # Placeholder for call auction implementation
        return []


class BiodiversityMarkets:
    """
    Specialized markets for biodiversity credits and habitat banking
    """
    
    def __init__(self, market_design: BioregionalMarketDesign):
        self.market_design = market_design
        self.habitat_banks = {}
        self.mitigation_requirements = {}
    
    def create_habitat_bank(self, bank_id: str, asset_ids: List[str], 
                           credit_types: List[str]) -> Dict[str, Any]:
        """Create a habitat bank for biodiversity credit generation"""
        total_area = sum(self.market_design.assets[aid].area_hectares 
                        for aid in asset_ids)
        
        # Calculate biodiversity credit potential
        credit_potential = {}
        for credit_type in credit_types:
            total_potential = sum(
                self.market_design.assets[aid].ecological_attributes.get(credit_type, 0)
                for aid in asset_ids
            )
            credit_potential[credit_type] = total_potential
        
        bank = {
            'bank_id': bank_id,
            'asset_ids': asset_ids,
            'total_area': total_area,
            'credit_types': credit_types,
            'credit_potential': credit_potential,
            'credits_sold': {ct: 0 for ct in credit_types},
            'status': 'approved'
        }
        
        self.habitat_banks[bank_id] = bank
        return bank
    
    def calculate_mitigation_requirement(self, impact_location: Tuple[float, float],
                                       impact_area: float,
                                       habitat_type: str) -> Dict[str, float]:
        """Calculate biodiversity mitigation requirements for development impacts"""
        # Biodiversity offset ratios based on habitat type and location
        offset_ratios = {
            'wetland': 3.0,  # 3:1 restoration ratio
            'forest': 2.0,   # 2:1 restoration ratio  
            'grassland': 1.5, # 1.5:1 restoration ratio
            'coastal': 4.0    # 4:1 restoration ratio
        }
        
        base_ratio = offset_ratios.get(habitat_type, 2.0)
        
        # Location-based multipliers (higher ratios for ecologically sensitive areas)
        # This would integrate with spatial biodiversity priority maps
        location_multiplier = 1.0  # Placeholder
        
        required_credits = impact_area * base_ratio * location_multiplier
        
        return {
            'habitat_type': habitat_type,
            'impact_area': impact_area,
            'required_credits': required_credits,
            'offset_ratio': base_ratio * location_multiplier
        }
    
    def match_credits_to_requirements(self, requirement_id: str) -> List[Dict[str, Any]]:
        """Match available biodiversity credits to mitigation requirements"""
        requirement = self.mitigation_requirements[requirement_id]
        available_credits = []
        
        # Find suitable habitat banks
        for bank_id, bank in self.habitat_banks.items():
            if requirement['habitat_type'] in bank['credit_types']:
                available_credits.append({
                    'bank_id': bank_id,
                    'available_credits': (bank['credit_potential'][requirement['habitat_type']] - 
                                        bank['credits_sold'][requirement['habitat_type']]),
                    'location': self._get_bank_centroid(bank),
                    'distance_to_impact': self._calculate_distance(
                        self._get_bank_centroid(bank), 
                        requirement['impact_location']
                    )
                })
        
        # Sort by distance and credit availability
        available_credits.sort(key=lambda x: (x['distance_to_impact'], -x['available_credits']))
        
        return available_credits
    
    def _get_bank_centroid(self, bank: Dict[str, Any]) -> Tuple[float, float]:
        """Calculate centroid of habitat bank assets"""
        locations = [self.market_design.assets[aid].location for aid in bank['asset_ids']]
        centroid_lat = sum(loc[0] for loc in locations) / len(locations)
        centroid_lon = sum(loc[1] for loc in locations) / len(locations)
        return (centroid_lat, centroid_lon)
    
    def _calculate_distance(self, loc1: Tuple[float, float], 
                           loc2: Tuple[float, float]) -> float:
        """Calculate distance between two locations"""
        return np.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2) * 111  # km


class LocalFoodSystems:
    """
    Markets and systems for local and regional food production and distribution
    """
    
    def __init__(self, market_design: BioregionalMarketDesign):
        self.market_design = market_design
        self.food_producers = {}
        self.food_consumers = {}
        self.distribution_networks = {}
    
    def optimize_local_food_system(self, optimization_objectives: List[str]) -> Dict[str, Any]:
        """
        Optimize local food system for multiple objectives
        
        Args:
            optimization_objectives: List of objectives like 'minimize_transport',
                                   'maximize_nutrition', 'minimize_environmental_impact'
        
        Returns:
            Dictionary with optimization results
        """
        # This would implement multi-objective optimization for local food systems
        # Considering factors like transport costs, nutritional needs, environmental impact,
        # seasonal production, storage capacity, etc.
        
        results = {
            'production_allocation': {},
            'distribution_plan': {},
            'environmental_impact': {},
            'economic_metrics': {},
            'nutritional_adequacy': {}
        }
        
        return results
    
    def calculate_food_miles(self, producer_id: str, consumer_id: str) -> float:
        """Calculate food miles between producer and consumer"""
        producer_loc = self.food_producers[producer_id]['location']
        consumer_loc = self.food_consumers[consumer_id]['location']
        
        return self._calculate_distance(producer_loc, consumer_loc)
    
    def _calculate_distance(self, loc1: Tuple[float, float], 
                           loc2: Tuple[float, float]) -> float:
        """Calculate distance between two locations"""
        return np.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2) * 111  # km


# Example usage and testing functions
def example_bioregional_market():
    """
    Example usage of bioregional market design
    """
    print("=== Bioregional Market Design Example ===")
    
    # Create bioregion boundary (placeholder)
    bioregion = gpd.GeoDataFrame()
    
    # Initialize market design
    market = BioregionalMarketDesign(bioregion)
    
    # Create sample bioregional asset
    forest_asset = BioregionalAsset(
        asset_id="forest_001",
        asset_type="forest",
        location=(45.0, -120.0),
        area_hectares=100.0,
        ecological_attributes={
            'carbon_storage': 500.0,  # tons CO2
            'biodiversity_index': 0.8,
            'water_filtration': 0.9
        },
        economic_attributes={
            'market_value': 500000,
            'annual_income': 10000
        },
        ownership_type="community",
        management_regime="sustainable_forestry",
        ecosystem_services={
            'carbon_sequestration': 10.0,  # tons CO2/year
            'biodiversity_habitat': 0.8,
            'water_regulation': 0.9,
            'recreation': 0.7
        }
    )
    
    # Register asset
    market.register_asset(forest_asset)
    
    # Create ecosystem service credit
    quality_params = {
        'additionality': 0.9,
        'permanence': 0.8,
        'measurability': 0.85,
        'leakage_risk': 0.1,
        'co_benefits': 0.7,
        'temporal_profile': 'permanent'
    }
    
    carbon_credit = market.create_ecosystem_service_credit(
        asset_id="forest_001",
        service_type="carbon",
        quantity=10.0,
        quality_parameters=quality_params
    )
    
    print(f"Created Carbon Credit: {carbon_credit.credit_id}")
    print(f"Quality Tier: {carbon_credit.quality_tier}")
    print(f"Price per Unit: ${carbon_credit.price_per_unit:.2f}")
    print(f"Co-benefits: {carbon_credit.co_benefits}")
    
    return market


if __name__ == "__main__":
    # Run example
    example_market = example_bioregional_market() 