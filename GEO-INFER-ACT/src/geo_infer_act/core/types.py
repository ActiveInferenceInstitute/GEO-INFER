"""
Typed result objects for active inference contracts.

These dataclasses provide stable, inspectable return shapes for callers that
need mathematical diagnostics without breaking the older float/dict APIs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class FreeEnergyBreakdown:
    """Decomposed free-energy terms for a single inference calculation."""

    free_energy: float
    accuracy: float = 0.0
    complexity: float = 0.0
    entropy: float = 0.0
    pragmatic_value: float = 0.0
    epistemic_value: float = 0.0
    risk: float = 0.0
    ambiguity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyEvaluation:
    """Expected-free-energy evaluation for a policy candidate."""

    policy: Any
    expected_free_energy: float
    probability: float
    index: int
    epistemic_value: float = 0.0
    pragmatic_value: float = 0.0
    risk: float = 0.0
    ambiguity: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActiveInferenceStepResult:
    """Typed result for a complete perceive-act step."""

    beliefs: Any
    action: Any
    free_energy: float
    expected_free_energy: Optional[float] = None
    policy_evaluation: Optional[PolicyEvaluation] = None
    observation: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class H3SpatialConsistency:
    """Spatial coherence diagnostics for H3-indexed active inference."""

    global_coherence: float
    neighbor_correlations: float
    cell_count: int = 0
    edge_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return the legacy dictionary shape used by existing callers."""
        return {
            "global_coherence": self.global_coherence,
            "neighbor_correlations": self.neighbor_correlations,
            "cell_count": self.cell_count,
            "edge_count": self.edge_count,
            **self.metadata,
        }


@dataclass
class H3BeliefUpdateResult:
    """Typed result for H3-indexed belief updates."""

    h3_beliefs: Dict[str, Any]
    average: Any
    spatial_consistency: H3SpatialConsistency
    aggregate_free_energy: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return the legacy dictionary shape used by existing callers."""
        return {
            "h3_beliefs": self.h3_beliefs,
            "average": self.average,
            "spatial_consistency": self.spatial_consistency.to_dict(),
            "aggregate_free_energy": self.aggregate_free_energy,
            **self.metadata,
        }


@dataclass
class H3GridInferenceResult:
    """Typed result for active inference over an H3 observation grid."""

    cell_results: Dict[str, ActiveInferenceStepResult]
    aggregate_free_energy: float
    spatial_consistency: H3SpatialConsistency
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-like dictionary containing typed cell diagnostics."""
        return {
            "cell_results": self.cell_results,
            "aggregate_free_energy": self.aggregate_free_energy,
            "spatial_consistency": self.spatial_consistency.to_dict(),
            **self.metadata,
        }
