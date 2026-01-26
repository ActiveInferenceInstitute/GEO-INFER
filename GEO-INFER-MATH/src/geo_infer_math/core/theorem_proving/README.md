# theorem_proving
 ## Overview
 This directory contains theorem_proving components. It includes 5 Python modules. ## Components
 ### integratio
n
.py Integration with Symbolic Math Module **Classes**: `SymbolicProofIntegrator` **Functions**: `integrate_with_symbolic_math`, `generate_proof_from_symbolic`, `_symbolic_to_theorem`, `_operation_to_theorem`, `verify_symbolic_operation` ### proof_strategie
s
.py Automated Proof Strategies **Classes**: `ProofStrategy`, `GeometricProofStrategy`, `StatisticalProofStrategy`, `DirectProofStrategy`, `ContradictionProofStrategy`, `InductionProofStrategy`, `ProofStrategySelector` ### proof_verificatio
n
.py Proof Verification **Classes**: `ProofVerifier` **Functions**: `verify_proof` ### prove
r
.py Theorem Prover Interface **Classes**: `ProofStatus`, `ProofResult`, `TheoremProver` **Functions**: `create_prover` ### spatial_theorem
s
.py Spatial Mathematics Theorems Library **Classes**: `TheoremType`, `SpatialTheorem`, `GeometricTheorem`, `StatisticalTheorem`, `TopologicalTheorem`, `TheoremDatabase` **Functions**: `get_theorem_database` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 