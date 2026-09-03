"""
GEO-INFER-RISK: Geospatial Risk Analysis and Catastrophe Modeling Framework

A framework for modeling, analyzing, and visualizing geospatial risk
across multiple hazards, vulnerabilities, and exposure types.
"""

__version__ = "0.2.0"
__author__ = "GEO-INFER Team"
__license__ = "CC-BY-NC-SA-4.0"

from typing import Any, Optional

from geo_infer_risk.civic_intel import (
    CRESCENT_CITY_GEO_INTEL_SCHEMA,
    CivicHazardDomain,
    CrescentCityAnchor,
    CrescentCityBounds,
    CrescentCityHazardIntel,
    MunicipalCodeSection,
    crescent_city_hazard_weights,
    load_crescent_city_hazard,
    parse_crescent_city_hazard,
)

# Import core components for easier access
try:
    from geo_infer_risk.core import (
        EnhancedRiskEngine,
        RiskModel,
        HazardModel,
        VulnerabilityModel,
        ExposureModel,
        MultiHazardInteractionMatrix,
        calculate_compound_exceedance_probability,
    )
except ImportError:
    EnhancedRiskEngine = None  # type: ignore[assignment,misc]
    RiskModel = None  # type: ignore[assignment,misc]
    HazardModel = None  # type: ignore[assignment,misc]
    VulnerabilityModel = None  # type: ignore[assignment,misc]
    ExposureModel = None  # type: ignore[assignment,misc]
    MultiHazardInteractionMatrix = None  # type: ignore[assignment,misc]
    calculate_compound_exceedance_probability = None  # type: ignore[assignment]

# Import utility functions (optional)
try:
    from geo_infer_risk.utils import (
        config_loader,
        risk_metrics,
        validation,
    )
except ImportError:
    config_loader = None  # type: ignore[assignment]
    risk_metrics = None  # type: ignore[assignment]
    validation = None  # type: ignore[assignment]


# Import underwriting module (optional)
try:
    from geo_infer_risk.underwriting import (
        UnderwritingEngine,
        UnderwritingConfig,
        RiskAssessmentEngine,
        PolicyManager,
        ClaimsProcessor,
        PortfolioManager,
        UnderwritingRulesEngine,
        PricingEngine,
        UnderwritingDecisionEngine,
        Policy,
        Claim,
        UnderwritingCase,
        Decision,
        create_underwriting_engine,
        underwrite_policy,
        process_claim,
        assess_risk,
        calculate_premium,
    )

    UNDERWRITING_AVAILABLE = True
except ImportError:
    UNDERWRITING_AVAILABLE = False

# Import enhanced core components (optional)
try:
    from geo_infer_risk.core import (
        EnhancedRiskEngine,
        EnhancedHazardModel,
        EnhancedVulnerabilityModel,
        EnhancedCatastropheModel,
        CatastropheConfig,
        MultiHazardInteractionMatrix,
    )

    ENHANCED_CORE_AVAILABLE = True
except ImportError:
    ENHANCED_CORE_AVAILABLE = False

# Define module level constants
DEFAULT_CONFIDENCE_LEVEL = 0.95
DEFAULT_RETURN_PERIODS = [10, 25, 50, 100, 250, 500, 1000]


def create_risk_analysis(
    config_path: Optional[str] = None, **kwargs: Any
) -> Any:
    """
    Create a new risk analysis engine with the specified configuration.

    Args:
        config_path: Path to configuration file. If not provided,
                     default configuration will be used.
        **kwargs: Additional configuration parameters that override file settings.

    Returns:
        EnhancedRiskEngine: Configured risk analysis engine instance.
    """
    from geo_infer_risk.utils.config_loader import (
        load_config,
        load_config_with_defaults,
    )

    if config_path:
        config = load_config(config_path)
    else:
        config = load_config_with_defaults()

    for key, value in kwargs.items():
        config[key] = value

    return EnhancedRiskEngine(config)


def create_underwriting_system(config: Optional[Any] = None) -> Any:
    """
    Create an underwriting system.

    Args:
        config: Underwriting configuration. If None, uses defaults.

    Returns:
        UnderwritingEngine: Configured underwriting engine.
    """
    if not UNDERWRITING_AVAILABLE:
        raise ImportError("Underwriting module not available")

    return create_underwriting_engine(config)


def underwrite_insurance_policy(
    application_data: Any, config: Optional[Any] = None
) -> Any:
    """
    Underwrite an insurance policy application.

    Args:
        application_data: Policy application data
        config: Underwriting configuration

    Returns:
        UnderwritingCase: Completed underwriting case
    """
    if not UNDERWRITING_AVAILABLE:
        raise ImportError("Underwriting module not available")

    return underwrite_policy(application_data, config)


def process_insurance_claim(claim_data: Any, config: Optional[Any] = None) -> Any:
    """
    Process an insurance claim.

    Args:
        claim_data: Claim information
        config: Claims processing configuration

    Returns:
        Claim: Processed claim
    """
    if not UNDERWRITING_AVAILABLE:
        raise ImportError("Underwriting module not available")

    return process_claim(claim_data, config)

__all__ = [
    "CRESCENT_CITY_GEO_INTEL_SCHEMA",
    "CivicHazardDomain",
    "CrescentCityAnchor",
    "CrescentCityBounds",
    "CrescentCityHazardIntel",
    "MunicipalCodeSection",
    "EnhancedRiskEngine",
    "RiskModel",
    "HazardModel",
    "VulnerabilityModel",
    "ExposureModel",
    "MultiHazardInteractionMatrix",
    "calculate_compound_exceedance_probability",
    "UnderwritingEngine",
    "UnderwritingConfig",
    "RiskAssessmentEngine",
    "PolicyManager",
    "ClaimsProcessor",
    "PortfolioManager",
    "UnderwritingRulesEngine",
    "PricingEngine",
    "UnderwritingDecisionEngine",
    "Policy",
    "Claim",
    "UnderwritingCase",
    "Decision",
    "DEFAULT_CONFIDENCE_LEVEL",
    "DEFAULT_RETURN_PERIODS",
    "crescent_city_hazard_weights",
    "load_crescent_city_hazard",
    "parse_crescent_city_hazard",
    "create_risk_analysis",
    "create_underwriting_system",
    "underwrite_insurance_policy",
    "process_insurance_claim",
]
