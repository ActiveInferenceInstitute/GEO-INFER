"""Configuration model for emergent behavior pattern analysis in GEO-INFER-ANT."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisConfiguration:
    """Configuration for pattern analysis."""

    analysis_types: List[str] = field(
        default_factory=lambda: [
            "spatial_patterns",
            "temporal_patterns",
            "interaction_networks",
        ]
    )
    statistical_methods: List[str] = field(
        default_factory=lambda: [
            "cluster_analysis",
            "network_analysis",
            "information_theory",
        ]
    )
    visualization_tools: List[str] = field(
        default_factory=lambda: [
            "trajectory_plots",
            "interaction_graphs",
            "phase_diagrams",
        ]
    )
    complexity_measures: List[str] = field(
        default_factory=lambda: [
            "fractal_dimension",
            "lyapunov_exponents",
            "correlation_dimension",
        ]
    )

    # Analysis parameters
    spatial_scale: float = 1000.0  # meters
    temporal_window: float = 3600.0  # seconds
    significance_threshold: float = 0.05
    min_pattern_size: int = 5

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        valid_analysis_types = [
            "spatial_patterns",
            "temporal_patterns",
            "interaction_networks",
            "emergent_phenomena",
        ]
        for analysis_type in self.analysis_types:
            if analysis_type not in valid_analysis_types:
                raise ValueError(f"Invalid analysis type: {analysis_type}")
