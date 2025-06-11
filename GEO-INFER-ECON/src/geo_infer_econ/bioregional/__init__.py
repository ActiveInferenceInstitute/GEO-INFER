"""
Bioregional Economics Module for GEO-INFER-ECON

This module provides comprehensive bioregional economic modeling capabilities including:
- Ecological economics principles and models
- Natural capital accounting and valuation
- Bioregional market design and governance
- Ecosystem services valuation and trading
- Circular economy and regenerative models
- Bioregional resilience and sustainability analysis
"""

from .ecological_economics import (
    EcologicalEconomicsEngine,
    BiophysicalEquilibriumModels,
    ThermoeconomicModels,
    EcologicalFootprintAnalysis,
    CarryingCapacityModels
)

from .natural_capital import (
    NaturalCapitalAccounting,
    EcosystemAssetsValuation,
    BiodiversityCredits,
    CarbonAccounting,
    WaterResourceAccounting
)

from .bioregional_markets import (
    BioregionalMarketDesign,
    EcosystemServicesMarkets,
    BiodiversityMarkets,
    CarbonMarkets,
    WaterMarkets,
    LocalFoodSystems
)

from .ecosystem_services import (
    EcosystemServicesValuation,
    ProvisioningServices,
    RegulatingServices,
    CulturalServices,
    SupportingServices,
    ServiceFlowModeling
)

from .circular_economy import (
    CircularEconomyModels,
    MaterialFlowAnalysis,
    IndustrialEcologyModels,
    WasteToResourceSystems,
    RegenerativeDesign
)

from .bioregional_governance import (
    BioregionalGovernanceModels,
    CommunityResourceManagement,
    AdaptiveManagementSystems,
    StakeholderEngagement,
    CooperativeEconomics
)

from .sustainability_metrics import (
    SustainabilityIndicators,
    ResilienceMetrics,
    RegenerativeMetrics,
    WellbeingIndicators,
    PlanetaryBoundaries
)

from .spatial_ecology import (
    LandscapeEconomics,
    HabitatConnectivity,
    EcosystemNetworkAnalysis,
    ConservationPrioritization,
    RestorationEconomics
)

__all__ = [
    # Ecological Economics
    'EcologicalEconomicsEngine',
    'BiophysicalEquilibriumModels',
    'ThermoeconomicModels',
    'EcologicalFootprintAnalysis',
    'CarryingCapacityModels',
    
    # Natural Capital
    'NaturalCapitalAccounting',
    'EcosystemAssetsValuation',
    'BiodiversityCredits',
    'CarbonAccounting',
    'WaterResourceAccounting',
    
    # Bioregional Markets
    'BioregionalMarketDesign',
    'EcosystemServicesMarkets',
    'BiodiversityMarkets',
    'CarbonMarkets',
    'WaterMarkets',
    'LocalFoodSystems',
    
    # Ecosystem Services
    'EcosystemServicesValuation',
    'ProvisioningServices',
    'RegulatingServices',
    'CulturalServices',
    'SupportingServices',
    'ServiceFlowModeling',
    
    # Circular Economy
    'CircularEconomyModels',
    'MaterialFlowAnalysis',
    'IndustrialEcologyModels',
    'WasteToResourceSystems',
    'RegenerativeDesign',
    
    # Bioregional Governance
    'BioregionalGovernanceModels',
    'CommunityResourceManagement',
    'AdaptiveManagementSystems',
    'StakeholderEngagement',
    'CooperativeEconomics',
    
    # Sustainability Metrics
    'SustainabilityIndicators',
    'ResilienceMetrics',
    'RegenerativeMetrics',
    'WellbeingIndicators',
    'PlanetaryBoundaries',
    
    # Spatial Ecology
    'LandscapeEconomics',
    'HabitatConnectivity',
    'EcosystemNetworkAnalysis',
    'ConservationPrioritization',
    'RestorationEconomics'
] 