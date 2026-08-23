"""
Core functionality for the GEO-INFER-RISK module.

This submodule contains the essential components for risk modeling, catastrophe
assessment, and insurance analytics with geospatial dimensions.
"""

# Import core components with explicit imports
from .risk_models import (
    RiskParameters,
    RiskModel,
    HazardModel,
    VulnerabilityModel,
    ExposureModel,
)

from .catastrophe_models import (
    CatastropheConfig,
    EnhancedCatastropheModel,
    MultiHazardInteractionMatrix,
    calculate_compound_exceedance_probability,
)

from .insurance_models import (
    InsuranceConfig,
    InsuranceModel,
    PropertyInsuranceModel,
    LiabilityInsuranceModel,
    CatastropheInsuranceModel,
    InsuranceManager,
    create_insurance_manager,
    calculate_property_premium,
)

from .risk_engine import EnhancedRiskEngine, AnalysisJob, ModelIntegrationStatus
from .hazard_model import (
    EnhancedHazardModel,
    EnhancedFloodModel,
    EnhancedEarthquakeModel,
    EnhancedHurricaneModel,
    EnhancedWildfireModel,
    create_enhanced_flood_model,
    create_enhanced_earthquake_model,
    create_enhanced_hurricane_model,
    create_enhanced_wildfire_model,
)
from .catastrophe_models import (
    EnhancedEarthquakeModel as EnhancedEarthquakeCatModel,
    EnhancedHurricaneModel as EnhancedHurricaneCatModel,
    EnhancedFloodModel as EnhancedFloodCatModel,
    create_enhanced_earthquake_model as create_enhanced_earthquake_cat_model,
    create_enhanced_hurricane_model as create_enhanced_hurricane_cat_model,
    create_enhanced_flood_model as create_enhanced_flood_cat_model,
)
from .vulnerability_model import (
    EnhancedVulnerabilityModel,
    EnhancedBuildingVulnerabilityModel,
    EnhancedInfrastructureVulnerabilityModel,
    EnhancedPopulationVulnerabilityModel,
    create_enhanced_building_vulnerability_model,
    create_enhanced_infrastructure_vulnerability_model,
    create_enhanced_population_vulnerability_model,
)

# Package exports
__all__ = [
    # Enhanced Risk Engine (primary)
    "EnhancedRiskEngine",
    # Enhanced Hazard Models
    "EnhancedHazardModel",
    "EnhancedFloodModel",
    "EnhancedEarthquakeModel",
    "EnhancedHurricaneModel",
    "EnhancedWildfireModel",
    # Hazard model factory functions
    "create_enhanced_flood_model",
    "create_enhanced_earthquake_model",
    "create_enhanced_hurricane_model",
    "create_enhanced_wildfire_model",
    # Enhanced Vulnerability Models
    "EnhancedVulnerabilityModel",
    "EnhancedBuildingVulnerabilityModel",
    "EnhancedInfrastructureVulnerabilityModel",
    "EnhancedPopulationVulnerabilityModel",
    # Vulnerability model factory functions
    "create_enhanced_building_vulnerability_model",
    "create_enhanced_infrastructure_vulnerability_model",
    "create_enhanced_population_vulnerability_model",
    # Risk modeling components
    "RiskModel",
    "ExposureModel",
    # Enhanced Catastrophe modeling
    "EnhancedCatastropheModel",
    "CatastropheConfig",
    "MultiHazardInteractionMatrix",
    "calculate_compound_exceedance_probability",
    "EnhancedEarthquakeCatModel",
    "EnhancedHurricaneCatModel",
    "EnhancedFloodCatModel",
    "create_enhanced_earthquake_cat_model",
    "create_enhanced_hurricane_cat_model",
    "create_enhanced_flood_cat_model",
    # Insurance modeling
    "InsuranceConfig",
    "InsuranceModel",
    "PropertyInsuranceModel",
    "LiabilityInsuranceModel",
    "CatastropheInsuranceModel",
    "InsuranceManager",
    "create_insurance_manager",
    "calculate_property_premium",
    # Analysis job management
    "AnalysisJob",
    "ModelIntegrationStatus",
]
