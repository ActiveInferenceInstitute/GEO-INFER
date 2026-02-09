# Agent
: theorem_proving

## Scope
 This directory contains theorem_proving components for the module. It provides 18 classes and 8 functions.

## Classes
 and Functions

### SymbolicProofIntegrator
 Integrator between symbolic math and theorem proving.

**Methods**:
- `prove_symbolic_expression(expression: Any, assumptions: Optional[List[str]]) -> ProofResult`: Prove a symbolic expression.
- `verify_differentiation(expression: Any, variable: str, derivative: Any) -> bool`: Verify a differentiation operation.
- `verify_integration(expression: Any, variable: str, integral: Any) -> bool`: Verify an integration operation.
- `generate_proof_for_operation(expression: Any, operation: str) -> Optional[ProofResult]`: Generate proof for a symbolic operation.

### ProofStrategy
 Abstract base class for proof strategies.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt to prove a theorem using this strategy.
- `can_apply(theorem: str) -> bool`: Check if this strategy can be applied to a theorem.

### GeometricProofStrategy
 Proof strategy for geometric theorems.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove geometric theorem.
- `can_apply(theorem: str) -> bool`: Check if geometric strategy applies.

### StatisticalProofStrategy
 Proof strategy for statistical theorems.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove statistical theorem.
- `can_apply(theorem: str) -> bool`: Check if statistical strategy applies.

### DirectProofStrategy
 Direct proof strategy.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt direct proof.

### ContradictionProofStrategy
 Proof by contradiction strategy.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove by contradiction.

### InductionProofStrategy
 Proof by induction strategy.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove by induction.

### ProofStrategySelector
 Selects appropriate proof strategy for a theorem.

**Methods**:
- `select_strategy(theorem: str, theorem_type: Optional[str]) -> ProofStrategy`: Select best strategy for a theorem.
- `try_all_strategies(theorem: str, assumptions: Optional[List[str]]) -> List[ProofResult]`: Try all applicable strategies.

### ProofVerifier
 Proof verifier for spatial mathematics.

**Methods**:
- `verify(theorem: str, proof: str, assumptions: Optional[List[str]]) -> bool`: Verify a proof.
- `check_proof_structure(proof: str) -> Dict[str, Any]`: Check the structure of a proof.
- `validate_proof_steps(proof: str, theorem: str) -> List[Dict[str, Any]]`: Validate individual proof steps.

### ProofStatus
 Status of a proof attempt.

### ProofResult
 Result of a theorem proving attempt.

### TheoremProver
 Main theorem prover interface for spatial mathematics.

**Methods**:
- `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt to prove a theorem.
- `verify(theorem: str, proof: str, **kwargs) -> bool`: Verify a given proof.
- `disprove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt to find a counterexample (disprove).

### TheoremType
 Type of theorem.

### SpatialTheorem
 Represents a spatial mathematics theorem.

### GeometricTheorem
 Geometric theorem for spatial mathematics.

### StatisticalTheorem
 Statistical theorem for spatial mathematics.

### TopologicalTheorem
 Topological theorem for spatial mathematics.

### TheoremDatabase
 Database of proven spatial mathematics theorems.

**Methods**:
- `add_theorem(theorem: SpatialTheorem)`: Add a theorem to the database.
- `get_theorem(name: str) -> Optional[SpatialTheorem]`: Retrieve a theorem by name.
- `search_theorems(theorem_type: Optional[TheoremType], keyword: Optional[str]) -> List[SpatialTheorem]`: Search theorems by type or keyword.
- `list_theorems() -> List[str]`: List all theorem names.
- `get_theorems_by_type(theorem_type: TheoremType) -> List[SpatialTheorem]`: Get all theorems of a specific type.

### integrate_with_symbolic_math
 `integrate_with_symbolic_math(symbolic_expression: Any, prover: Optional[TheoremProver]) -> ProofResult` Integrate symbolic math expression with theorem prover.

### generate_proof_from_symbolic
 `generate_proof_from_symbolic(symbolic_expression: Any, operation: str, prover: Optional[TheoremProver]) -> Optional[ProofResult]` Generate proof for a symbolic operation.

### verify_symbolic_operation
 `verify_symbolic_operation(original: Any, result: Any, operation: str, prover: Optional[TheoremProver]) -> bool` Verify a symbolic operation using theorem proving.

### verify_proof
 `verify_proof(theorem: str, proof: str, assumptions: Optional[List[str]], backend: str) -> bool` Verify a proof for a theorem.

### create_prover
 `create_prover(backend: str, **kwargs) -> TheoremProver` Create a theorem prover instance.

### get_theorem_database
 `get_theorem_database() -> TheoremDatabase` Get the global theorem database.

## Capabilities

- **18 classes** for core functionality
- **8 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_math/core/theorem_proving`
- **Type**: Directory Node
