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

from .growth_models import (
    SolowGrowthModel,
    EndogenousGrowthModels,
    SpatialGrowthModels,
    RegionalConvergenceAnalysis,
    TechnologyDiffusionModels
)

from .business_cycles import (
    DSGEModels,
    RealBusinessCycleModels,
    NewKeynesianModels,
    SpatialBusinessCycles,
    RegionalSynchronization
)

from .monetary_policy import (
    MonetaryPolicyRules,
    InflationTargeting,
    ExchangeRateModels,
    SpatialMonetaryTransmission,
    RegionalMonetaryEffects
)

from .fiscal_policy import (
    FiscalMultiplierModels,
    DebtSustainabilityAnalysis,
    SpatialFiscalPolicy,
    IntergovernmentalTransfers,
    TaxCompetitionModels
)

from .international_trade import (
    GravityModels,
    TradeCreationDiversion,
    SpatialTradeModels,
    RegionalTradeAgreements,
    GlobalValueChains
)

from .spatial_macro import (
    MultiRegionalModels,
    SpatialEquilibriumMacro,
    RegionalInterdependence,
    SpatialShockTransmission,
    MacroeconomicGeography
)

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