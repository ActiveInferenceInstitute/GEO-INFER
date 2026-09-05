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
    RegionProfile,
    SolowGrowthModel,
    EndogenousGrowthModels,
    SpatialGrowthModels,
    RegionalConvergenceAnalysis,
    TechnologyDiffusionModels,
)
from .aggregate_models import (
    AggregateGrowthModels,
    BusinessCycleModels,
    MonetaryPolicyModels,
    FiscalPolicyModels,
    TradeModels,
)

__all__ = [
    # Growth Models (growth_models)
    "RegionProfile",
    "SolowGrowthModel",
    "EndogenousGrowthModels",
    "SpatialGrowthModels",
    "RegionalConvergenceAnalysis",
    "TechnologyDiffusionModels",
    # Aggregate Growth (aggregate_models)
    "AggregateGrowthModels",
    # Business Cycles
    "BusinessCycleModels",
    # Monetary Policy
    "MonetaryPolicyModels",
    # Fiscal Policy
    "FiscalPolicyModels",
    # International Trade
    "TradeModels",
]
