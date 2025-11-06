"""
Convenience API Layer for GEO-INFER-MATH

This package provides domain-specific convenience methods and facades
for common mathematical operations used by other GEO-INFER modules.
"""

from geo_infer_math.api.convenience.act_convenience import (
    ActiveInferenceConvenience,
    free_energy_calculation,
    variational_inference_helper,
)

from geo_infer_math.api.convenience.bayes_convenience import (
    BayesianConvenience,
    posterior_helper,
    prior_builder,
    mcmc_wrapper,
)

from geo_infer_math.api.convenience.ai_convenience import (
    AIConvenience,
    gradient_helper,
    spatial_loss_function,
    optimization_wrapper,
)

from geo_infer_math.api.convenience.information_convenience import (
    InformationTheoryConvenience,
    spatial_entropy_helper,
    mutual_information_helper,
    kl_divergence_helper,
)

from geo_infer_math.api.convenience.spatial_convenience import (
    SpatialConvenience,
    enhanced_spatial_analysis,
)

from geo_infer_math.api.convenience.integration_convenience import (
    IntegrationConvenience,
    cross_module_helper,
)

__all__ = [
    # ACT Convenience
    "ActiveInferenceConvenience",
    "free_energy_calculation",
    "variational_inference_helper",
    # Bayes Convenience
    "BayesianConvenience",
    "posterior_helper",
    "prior_builder",
    "mcmc_wrapper",
    # AI Convenience
    "AIConvenience",
    "gradient_helper",
    "spatial_loss_function",
    "optimization_wrapper",
    # Information Theory Convenience
    "InformationTheoryConvenience",
    "spatial_entropy_helper",
    "mutual_information_helper",
    "kl_divergence_helper",
    # Spatial Convenience
    "SpatialConvenience",
    "enhanced_spatial_analysis",
    # Integration Convenience
    "IntegrationConvenience",
    "cross_module_helper",
]

