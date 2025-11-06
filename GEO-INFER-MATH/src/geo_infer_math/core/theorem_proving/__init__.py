"""
Theorem Proving Environment for Spatial Mathematics

This module provides theorem proving capabilities for spatial mathematics,
including proof verification, theorem databases, and automated proof strategies.
"""

from geo_infer_math.core.theorem_proving.prover import (
    TheoremProver,
    ProofResult,
    create_prover,
)

from geo_infer_math.core.theorem_proving.spatial_theorems import (
    SpatialTheorem,
    GeometricTheorem,
    StatisticalTheorem,
    TopologicalTheorem,
    TheoremDatabase,
)

from geo_infer_math.core.theorem_proving.proof_verification import (
    verify_proof,
    ProofVerifier,
)

from geo_infer_math.core.theorem_proving.proof_strategies import (
    ProofStrategy,
    GeometricProofStrategy,
    StatisticalProofStrategy,
)

from geo_infer_math.core.theorem_proving.integration import (
    integrate_with_symbolic_math,
    generate_proof_from_symbolic,
)

__all__ = [
    # Prover
    "TheoremProver",
    "ProofResult",
    "create_prover",
    # Theorems
    "SpatialTheorem",
    "GeometricTheorem",
    "StatisticalTheorem",
    "TopologicalTheorem",
    "TheoremDatabase",
    # Verification
    "verify_proof",
    "ProofVerifier",
    # Strategies
    "ProofStrategy",
    "GeometricProofStrategy",
    "StatisticalProofStrategy",
    # Integration
    "integrate_with_symbolic_math",
    "generate_proof_from_symbolic",
]

