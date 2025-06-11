"""
Macroeconomics Module for GEO-INFER-ECON

This module provides comprehensive macroeconomic modeling capabilities including:
- Aggregate growth models (Solow, endogenous growth)
- Business cycle analysis and DSGE models
- Monetary policy modeling 
- Fiscal policy analysis
- International trade and spatial macroeconomics
- Regional and spatial macroeconomic modeling
"""

# Import available modules - only growth_models exists currently
from .growth_models import (
    RegionProfile,
    SolowGrowthModel,
    EndogenousGrowthModels,
    SpatialGrowthModels,
    RegionalConvergenceAnalysis,
    TechnologyDiffusionModels
)

# Placeholder classes for modules not yet implemented
class AggregateGrowthModels:
    """Main aggregate growth modeling class."""
    pass

class BusinessCycleModels:
    """Main business cycle modeling class."""
    pass

class MonetaryPolicyModels:
    """Main monetary policy modeling class."""
    pass

class FiscalPolicyModels:
    """Main fiscal policy modeling class."""
    pass

class TradeModels:
    """Main trade modeling class."""
    pass

__all__ = [
    # Growth Models
    'SolowGrowthModel',
    'EndogenousGrowthModels',
    'SpatialGrowthModels',
    'RegionalConvergenceAnalysis',
    'TechnologyDiffusionModels',
    
    # Business Cycles
    'DSGEModels',
    'RealBusinessCycleModels', 
    'NewKeynesianModels',
    'SpatialBusinessCycles',
    'RegionalSynchronization',
    
    # Monetary Policy
    'MonetaryPolicyRules',
    'InflationTargeting',
    'ExchangeRateModels',
    'SpatialMonetaryTransmission',
    'RegionalMonetaryEffects',
    
    # Fiscal Policy
    'FiscalMultiplierModels',
    'DebtSustainabilityAnalysis',
    'SpatialFiscalPolicy',
    'IntergovernmentalTransfers',
    'TaxCompetitionModels',
    
    # International Trade
    'GravityModels',
    'TradeCreationDiversion',
    'SpatialTradeModels', 
    'RegionalTradeAgreements',
    'GlobalValueChains',
    
    # Spatial Macroeconomics
    'MultiRegionalModels',
    'SpatialEquilibriumMacro',
    'RegionalInterdependence',
    'SpatialShockTransmission',
    'MacroeconomicGeography'
] 