"""
Information Theory Module for Spatial Data

This module provides comprehensive information theory tools for analyzing
spatial data, including entropy measures, mutual information, KL divergence,
information geometry, channel capacity, and spatial coding.
"""

from geo_infer_math.core.information_theory.entropy import (
    shannon_entropy,
    renyi_entropy,
    tsallis_entropy,
    spatial_entropy,
    conditional_entropy,
    joint_entropy,
    EntropyCalculator,
)

from geo_infer_math.core.information_theory.mutual_information import (
    mutual_information,
    conditional_mutual_information,
    spatial_mutual_information,
    MutualInformationCalculator,
)

from geo_infer_math.core.information_theory.kl_divergence import (
    kl_divergence,
    js_divergence,
    spatial_kl_divergence,
    KLDivergenceCalculator,
)

from geo_infer_math.core.information_theory.information_geometry import (
    fisher_information_matrix,
    information_metric,
    geodesic_distance,
    InformationGeometryCalculator,
)

from geo_infer_math.core.information_theory.channel_capacity import (
    channel_capacity,
    spatial_channel_capacity,
    ChannelCapacityCalculator,
)

from geo_infer_math.core.information_theory.spatial_coding import (
    spatial_encoding_efficiency,
    compression_ratio,
    coding_gain,
    SpatialCodingCalculator,
)

__all__ = [
    # Entropy
    "shannon_entropy",
    "renyi_entropy",
    "tsallis_entropy",
    "spatial_entropy",
    "conditional_entropy",
    "joint_entropy",
    "EntropyCalculator",
    # Mutual Information
    "mutual_information",
    "conditional_mutual_information",
    "spatial_mutual_information",
    "MutualInformationCalculator",
    # KL Divergence
    "kl_divergence",
    "js_divergence",
    "spatial_kl_divergence",
    "KLDivergenceCalculator",
    # Information Geometry
    "fisher_information_matrix",
    "information_metric",
    "geodesic_distance",
    "InformationGeometryCalculator",
    # Channel Capacity
    "channel_capacity",
    "spatial_channel_capacity",
    "ChannelCapacityCalculator",
    # Spatial Coding
    "spatial_encoding_efficiency",
    "compression_ratio",
    "coding_gain",
    "SpatialCodingCalculator",
]

