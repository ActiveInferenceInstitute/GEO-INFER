# Agent
: theorem_proving ## Scope
 This directory contains theorem_proving components for the module. It provides 18 classes and 8 functions. ## Classes
 and Functions ### SymbolicProofIntegrato
r
 Integrator between symbolic math and theorem proving. **Methods**: - `prove_symbolic_expression(expression: Any, assumptions: Optional[List[str]]) -> ProofResult`: Prove a symbolic expression. - `verify_differentiation(expression: Any, variable: str, derivative: Any) -> bool`: Verify a differentiation operation. - `verify_integration(expression: Any, variable: str, integral: Any) -> bool`: Verify an integration operation. - `generate_proof_for_operation(expression: Any, operation: str) -> Optional[ProofResult]`: Generate proof for a symbolic operation. ### ProofStrateg
y
 Abstract base class for proof strategies. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt to prove a theorem using this strategy. - `can_apply(theorem: str) -> bool`: Check if this strategy can be applied to a theorem. ### GeometricProofStrateg
y
 Proof strategy for geometric theorems. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove geometric theorem. - `can_apply(theorem: str) -> bool`: Check if geometric strategy applies. ### StatisticalProofStrateg
y
 Proof strategy for statistical theorems. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove statistical theorem. - `can_apply(theorem: str) -> bool`: Check if statistical strategy applies. ### DirectProofStrateg
y
 Direct proof strategy. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt direct proof. ### ContradictionProofStrateg
y
 Proof by contradiction strategy. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove by contradiction. ### InductionProofStrateg
y
 Proof by induction strategy. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Prove by induction. ### ProofStrategySelecto
r
 Selects appropriate proof strategy for a theorem. **Methods**: - `select_strategy(theorem: str, theorem_type: Optional[str]) -> ProofStrategy`: Select best strategy for a theorem. - `try_all_strategies(theorem: str, assumptions: Optional[List[str]]) -> List[ProofResult]`: Try all applicable strategies. ### ProofVerifie
r
 Proof verifier for spatial mathematics. **Methods**: - `verify(theorem: str, proof: str, assumptions: Optional[List[str]]) -> bool`: Verify a proof. - `check_proof_structure(proof: str) -> Dict[str, Any]`: Check the structure of a proof. - `validate_proof_steps(proof: str, theorem: str) -> List[Dict[str, Any]]`: Validate individual proof steps. ### ProofStatu
s
 Status of a proof attempt. ### ProofResul
t
 Result of a theorem proving attempt. ### TheoremProve
r
 Main theorem prover interface for spatial mathematics. **Methods**: - `prove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt to prove a theorem. - `verify(theorem: str, proof: str, **kwargs) -> bool`: Verify a given proof. - `disprove(theorem: str, assumptions: Optional[List[str]], **kwargs) -> ProofResult`: Attempt to find a counterexample (disprove). ### TheoremTyp
e
 Type of theorem. ### SpatialTheore
m
 Represents a spatial mathematics theorem. ### GeometricTheore
m
 Geometric theorem for spatial mathematics. ### StatisticalTheore
m
 Statistical theorem for spatial mathematics. ### TopologicalTheore
m
 Topological theorem for spatial mathematics. ### TheoremDatabas
e
 Database of proven spatial mathematics theorems. **Methods**: - `add_theorem(theorem: SpatialTheorem)`: Add a theorem to the database. - `get_theorem(name: str) -> Optional[SpatialTheorem]`: Retrieve a theorem by name. - `search_theorems(theorem_type: Optional[TheoremType], keyword: Optional[str]) -> List[SpatialTheorem]`: Search theorems by type or keyword. - `list_theorems() -> List[str]`: List all theorem names. - `get_theorems_by_type(theorem_type: TheoremType) -> List[SpatialTheorem]`: Get all theorems of a specific type. ### integrate_with_symbolic_mat
h
 `integrate_with_symbolic_math(symbolic_expression: Any, prover: Optional[TheoremProver]) -> ProofResult` Integrate symbolic math expression with theorem prover. ### generate_proof_from_symboli
c
 `generate_proof_from_symbolic(symbolic_expression: Any, operation: str, prover: Optional[TheoremProver]) -> Optional[ProofResult]` Generate proof for a symbolic operation. ### verify_symbolic_operatio
n
 `verify_symbolic_operation(original: Any, result: Any, operation: str, prover: Optional[TheoremProver]) -> bool` Verify a symbolic operation using theorem proving. ### verify_proo
f
 `verify_proof(theorem: str, proof: str, assumptions: Optional[List[str]], backend: str) -> bool` Verify a proof for a theorem. ### create_prove
r
 `create_prover(backend: str, **kwargs) -> TheoremProver` Create a theorem prover instance. ### get_theorem_databas
e
 `get_theorem_database() -> TheoremDatabase` Get the global theorem database. ## Capabilities
 - **18 classes** for core functionality - **8 functions** for utility operations ## Integration
 - **Location**: `src/geo_infer_math/core/theorem_proving` - **Type**: Directory Node 