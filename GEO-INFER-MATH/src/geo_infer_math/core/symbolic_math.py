"""
Symbolic Mathematics Module

This module provides symbolic mathematics capabilities for geospatial analysis,
including symbolic expressions, derivatives, integrals, and equation solving.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional, Any
import logging
import warnings
import ast

logger = logging.getLogger(__name__)

# numpy members that reach the filesystem or pickle; expressions must not
# invoke them from the eval namespace.
_UNSAFE_NUMPY_MEMBERS = {
    "load",
    "loads",
    "loadtxt",
    "genfromtxt",
    "fromfile",
    "fromstring",
    "memmap",
    "save",
    "saves",
    "savetxt",
    "savez",
    "savez_compressed",
    "tofile",
    "dumps",
}


def _reject_unsafe_numpy_access(expression: str) -> None:
    """Raise ValueError if the expression reaches an unsafe numpy member."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in _UNSAFE_NUMPY_MEMBERS:
            raise ValueError(f"Unsafe numpy member in expression: np.{node.attr}")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in _UNSAFE_NUMPY_MEMBERS:
                raise ValueError(f"Unsafe call in expression: {func.id}")


class SymbolicMath:
    """Symbolic mathematics engine for geospatial analysis."""

    def __init__(self, backend: str = "sympy"):
        """
        Initialize symbolic mathematics engine.

        Args:
            backend: Symbolic computation backend ('sympy', 'symengine')
        """
        self.backend = backend
        self._engine: Any = None
        self._symbols: Dict[str, Any] = {}

        try:
            if backend == "sympy":
                import sympy as sp  # type: ignore[import-untyped]

                self._engine = sp
                self.Symbol = sp.Symbol
                self.symbols = sp.symbols
                self.diff = sp.diff
                self.integrate = sp.integrate
                self.solve = sp.solve
                self.simplify = sp.simplify
                self.expand = sp.expand
                self.factor = sp.factor
                self.Matrix = sp.Matrix
                self.Function = sp.Function
            elif backend == "symengine":
                import symengine as se

                self._engine = se
                self.Symbol = se.Symbol
                self.symbols = se.symbols
                self.diff = se.diff
                self.integrate = se.integrate
                self.solve = se.solve
                self.simplify = se.simplify
                self.expand = se.expand
                self.factor = se.factor
                self.Matrix = se.Matrix
                self.Function = se.Function
            else:
                raise ValueError(f"Unsupported backend: {backend}")

            logger.info(f"Initialized symbolic math with {backend} backend")

        except ImportError as e:
            warnings.warn(
                f"Backend {backend} not available: {e}. Using numpy-based symbolic operations."
            )
            self._engine = "numpy"
            self._setup_numpy_backend()

    def _setup_numpy_backend(self) -> None:
        """Set up the descriptor-based numpy backend."""
        # Bind the descriptor operations exposed by the numpy backend.
        self.Symbol = self._numpy_symbol
        self.symbols = self._numpy_symbols
        self.diff = self._numpy_diff
        self.integrate = self._numpy_integrate
        self.solve = self._numpy_solve
        self.simplify = self._numpy_simplify
        self.expand = self._numpy_expand
        self.factor = self._numpy_factor
        self.Matrix = self._numpy_matrix
        self.Function = self._numpy_function

    def _numpy_symbol(self, name: str) -> Dict[str, Any]:
        """Create a numpy-based symbolic symbol."""
        return {"type": "symbol", "name": name}

    def _numpy_symbols(self, *names: str) -> List[Dict[str, Any]]:
        """Create multiple numpy-based symbolic symbols."""
        return [self._numpy_symbol(name) for name in names]

    def _numpy_diff(self, expr: Any, var: Any) -> Any:
        """Numerical differentiation via central finite differences.

        If ``expr`` is callable, computes df/d(var) ≈ (f(x+h) - f(x-h)) / (2h)
        evaluated at x=1.0 (a neutral evaluation point for most analytic functions).

        If ``expr`` is a symbolic dict descriptor (as produced by ``_numpy_symbol``),
        applies simple analytic rules:
        - d/dx (x) = 1 when expr['name'] == var['name']
        - d/dx (const) = 0 for any other symbol

        For compound dict expressions (type='derivative', 'integral', 'solution'),
        returns a nested derivative descriptor.
        """
        var_name = var.get("name", str(var)) if isinstance(var, dict) else str(var)

        # Case 1: callable expression → numerical central difference
        if callable(expr):
            try:
                h = 1e-5
                x0 = 1.0  # evaluation point
                return (expr(x0 + h) - expr(x0 - h)) / (2 * h)
            except Exception:
                pass  # fall through to descriptor

        # Case 2: symbol dict → analytic identity / zero rule
        if isinstance(expr, dict):
            expr_type = expr.get("type", "")
            if expr_type == "symbol":
                # d/dx x = 1, d/dx y = 0
                return 1.0 if expr.get("name") == var_name else 0.0
            # For compound sub-expressions, return a derivative descriptor
            return {
                "type": "derivative",
                "expression": expr,
                "variable": var,
                "order": 1,
            }

        # Case 3: numeric constant → derivative is zero
        try:
            float(expr)  # numeric check
            return 0.0
        except (TypeError, ValueError):
            pass

        # Fallback descriptor
        return {"type": "derivative", "expression": expr, "variable": var, "order": 1}

    def _numpy_integrate(self, expr: Any, var: Any) -> Dict[str, Any]:
        """Numerical integration (simplified)."""
        return {"type": "integral", "expression": expr, "variable": var}

    def _numpy_solve(self, expr: Any, var: Any) -> Dict[str, Any]:
        """Numerical equation solving (simplified)."""
        return {"type": "solution", "expression": expr, "variable": var}

    def _numpy_simplify(self, expr: Any) -> Any:
        """Return a normalized descriptor for a numpy expression."""
        if isinstance(expr, dict):
            return dict(expr)
        return expr

    def _numpy_expand(self, expr: Any) -> Any:
        """Return an expanded descriptor when the numpy backend cannot rewrite it."""
        return expr

    def _numpy_factor(self, expr: Any) -> Any:
        """Return a factorization descriptor when symbolic factoring is unavailable."""
        return expr

    def _numpy_matrix(self, data: Any) -> np.ndarray:
        """Create a numeric matrix using numpy."""
        return np.array(data)

    def _numpy_function(self, name: str) -> Dict[str, Any]:
        """Create a callable descriptor for a named numpy-backend function."""
        return {"type": "function", "name": name}

    def define_spatial_model(
        self,
        variables: List[str],
        equations: List[str],
        constraints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Define a symbolic spatial model.

        Args:
            variables: List of variable names
            equations: List of equation strings
            constraints: Optional list of constraint strings

        Returns:
            Symbolic model definition
        """
        # Create symbols for variables
        var_symbols = self.symbols(",".join(variables))

        # Parse equations
        parsed_equations = []
        for eq in equations:
            try:
                # This is a simplified parser - real implementation would use the symbolic engine
                parsed_equations.append(
                    {"original": eq, "parsed": self._parse_equation(eq, var_symbols)}
                )
            except Exception as e:
                logger.warning(f"Failed to parse equation '{eq}': {e}")
                parsed_equations.append({"original": eq, "error": str(e)})

        # Parse constraints
        parsed_constraints = []
        if constraints:
            for constraint in constraints:
                try:
                    parsed_constraints.append(
                        {
                            "original": constraint,
                            "parsed": self._parse_constraint(constraint, var_symbols),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse constraint '{constraint}': {e}")
                    parsed_constraints.append({"original": constraint, "error": str(e)})

        return {
            "variables": variables,
            "symbols": var_symbols,
            "equations": parsed_equations,
            "constraints": parsed_constraints,
            "backend": self.backend,
        }

    def _parse_equation(self, equation: str, symbols: List[Any]) -> Any:
        """Parse an equation string into symbolic form."""
        if self.backend in ["sympy", "symengine"]:
            # Use the actual symbolic engine
            try:
                # This is a simplified approach - real implementation would need proper parsing
                return self._engine.sympify(equation)
            except Exception:
                return equation
        else:
            # Numpy backend
            return {"type": "equation", "string": equation}

    def _parse_constraint(self, constraint: str, symbols: List[Any]) -> Any:
        """Parse a constraint string."""
        if self.backend in ["sympy", "symengine"]:
            return self._engine.sympify(constraint)
        else:
            return {"type": "constraint", "string": constraint}

    def compute_gradients(
        self, model: Dict[str, Any], parameters: List[str]
    ) -> Dict[str, Any]:
        """
        Compute gradients of model equations with respect to parameters.

        Args:
            model: Symbolic model definition
            parameters: List of parameter names

        Returns:
            Dictionary of gradients
        """
        gradients: Dict[str, Any] = {}

        for param in parameters:
            try:
                # Create parameter symbol
                param_symbol = self.Symbol(param)

                # Compute gradients for each equation
                equation_gradients = []
                for eq in model["equations"]:
                    if "parsed" in eq and "error" not in eq:
                        try:
                            if self.backend in ["sympy", "symengine"]:
                                gradient = self.diff(eq["parsed"], param_symbol)
                                equation_gradients.append(gradient)
                            else:
                                equation_gradients.append(
                                    self._numpy_diff(eq["parsed"], param_symbol)
                                )
                        except Exception as e:
                            logger.warning(
                                f"Failed to compute gradient for {eq['original']}: {e}"
                            )
                            equation_gradients.append(None)

                gradients[param] = equation_gradients

            except Exception as e:
                logger.error(f"Error computing gradient for parameter {param}: {e}")
                gradients[param] = None

        return gradients

    def optimize_symbolic_model(
        self,
        model: Dict[str, Any],
        objective: str,
        parameters: List[str],
        bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize a symbolic model.

        Args:
            model: Symbolic model definition
            objective: Objective function string
            parameters: Parameter names to optimize
            bounds: Optional parameter bounds

        Returns:
            Optimization results
        """
        try:
            if self.backend in ["sympy", "symengine"]:
                # Parse the objective expression symbolically
                objective_expr = self._engine.sympify(objective)

                # Create parameter symbols
                param_symbols = [self.Symbol(p) for p in parameters]

                # Compute symbolic gradient and lambdify for scipy
                grad_exprs = [
                    self._engine.diff(objective_expr, ps) for ps in param_symbols
                ]

                try:
                    from scipy.optimize import minimize as sci_minimize

                    obj_fn = self._engine.lambdify(
                        param_symbols, objective_expr, modules="numpy"
                    )
                    jac_fn = self._engine.lambdify(
                        param_symbols, self._engine.Matrix(grad_exprs), modules="numpy"
                    )

                    def _f(x: Any) -> float:
                        return float(obj_fn(*x))

                    def _jac(x: Any) -> np.ndarray:
                        g = jac_fn(*x)
                        return np.array(g).flatten().astype(float)

                    # Apply bounds if provided
                    sci_bounds = (
                        [bounds.get(p, (None, None)) for p in parameters]
                        if bounds
                        else None
                    )

                    x0 = np.zeros(len(parameters))
                    result = sci_minimize(
                        _f, x0, jac=_jac, bounds=sci_bounds, method="L-BFGS-B"
                    )

                    return {
                        "success": bool(result.success),
                        "parameters": dict(zip(parameters, result.x.tolist())),
                        "objective_value": float(result.fun),
                        "iterations": result.nit,
                        "message": result.message,
                        "backend": self.backend,
                    }
                except ImportError:
                    return {
                        "success": False,
                        "message": "scipy required for symbolic optimization (pip install scipy)",
                        "backend": self.backend,
                    }

            else:
                # Numpy backend: objective must be callable; use scipy numerically
                try:
                    from scipy.optimize import minimize as sci_minimize

                    if not callable(objective):
                        raise TypeError("Numpy backend requires a callable objective")

                    sci_bounds = (
                        [bounds.get(p, (None, None)) for p in parameters]
                        if bounds
                        else None
                    )

                    x0 = np.zeros(len(parameters))
                    result = sci_minimize(
                        lambda x: float(objective(*x)),
                        x0,
                        bounds=sci_bounds,
                        method="L-BFGS-B",
                    )
                    return {
                        "success": bool(result.success),
                        "parameters": dict(zip(parameters, result.x.tolist())),
                        "objective_value": float(result.fun),
                        "iterations": result.nit,
                        "message": result.message,
                        "backend": self.backend,
                    }
                except ImportError:
                    return {
                        "success": False,
                        "message": "scipy required for numerical optimization (pip install scipy)",
                        "backend": self.backend,
                    }

        except Exception as e:
            logger.error(f"Error optimizing symbolic model: {e}")
            return {"success": False, "error": str(e), "backend": self.backend}

    def derive_spatial_relationships(
        self,
        coordinates: np.ndarray,
        values: np.ndarray,
        relationship_type: str = "polynomial",
    ) -> Dict[str, Any]:
        """
        Derive symbolic relationships between spatial coordinates and values.

        Args:
            coordinates: Spatial coordinates
            values: Observed values
            relationship_type: Type of relationship ('polynomial', 'exponential', 'logarithmic')

        Returns:
            Symbolic relationship model
        """
        try:
            # Create coordinate symbols
            x, y = self.symbols("x y")

            if relationship_type == "polynomial":
                # Fit polynomial relationship
                degree = min(3, len(coordinates) - 1)  # Adaptive degree

                # Simple polynomial fitting (simplified)
                if self.backend in ["sympy", "symengine"]:
                    # Use sympy for polynomial fitting
                    coeffs = np.polyfit(coordinates[:, 0], values, degree)
                    poly_expr = sum(c * x**i for i, c in enumerate(reversed(coeffs)))

                    return {
                        "type": "polynomial",
                        "degree": degree,
                        "expression": poly_expr,
                        "coefficients": coeffs,
                        "backend": self.backend,
                    }

            elif relationship_type == "exponential":
                # Exponential relationship
                if self.backend in ["sympy", "symengine"]:
                    # Simplified exponential model
                    exp_expr = self.Symbol("a") * self._engine.exp(
                        self.Symbol("b") * x + self.Symbol("c") * y
                    )

                    return {
                        "type": "exponential",
                        "expression": exp_expr,
                        "backend": self.backend,
                    }

            return {
                "type": relationship_type,
                "expression": None,
                "backend": self.backend,
                "message": f"Relationship type {relationship_type} not fully implemented",
            }

        except Exception as e:
            logger.error(f"Error deriving spatial relationships: {e}")
            return {
                "type": relationship_type,
                "expression": None,
                "error": str(e),
                "backend": self.backend,
            }

    def create_symbolic_spatial_field(
        self, domain: Dict[str, float], expression: str, variables: List[str]
    ) -> Dict[str, Any]:
        """
        Create a symbolic spatial field.

        Args:
            domain: Spatial domain bounds
            expression: Symbolic expression for the field
            variables: Variable names

        Returns:
            Symbolic spatial field definition
        """
        try:
            # Create variable symbols
            var_symbols = self.symbols(",".join(variables))

            # Parse the expression
            if self.backend in ["sympy", "symengine"]:
                field_expr = self._engine.sympify(expression)
            else:
                field_expr = {"type": "expression", "string": expression}

            # Define the spatial domain
            spatial_domain = {
                "x_range": (domain.get("x_min", 0), domain.get("x_max", 1)),
                "y_range": (domain.get("y_min", 0), domain.get("y_max", 1)),
                "resolution": domain.get("resolution", 0.1),
            }

            return {
                "expression": field_expr,
                "variables": variables,
                "symbols": var_symbols,
                "domain": spatial_domain,
                "backend": self.backend,
            }

        except Exception as e:
            logger.error(f"Error creating symbolic spatial field: {e}")
            return {"expression": None, "error": str(e), "backend": self.backend}

    def evaluate_symbolic_expression(
        self, expression: Any, variable_values: Dict[str, float]
    ) -> float:
        """
        Evaluate a symbolic expression with given variable values.

        Args:
            expression: Symbolic expression
            variable_values: Dictionary of variable names to values

        Returns:
            Numerical value of the expression
        """
        try:
            if self.backend in ["sympy", "symengine"]:
                # Substitute values and evaluate
                subs_dict = {
                    self.Symbol(var): val for var, val in variable_values.items()
                }
                result = expression.subs(subs_dict)
                return float(result.evalf())
            else:
                if callable(expression):
                    try:
                        return float(expression(**variable_values))
                    except TypeError:
                        return float(expression(*variable_values.values()))
                if isinstance(expression, dict):
                    if expression.get("type") == "symbol":
                        name = expression.get("name")
                        if name not in variable_values:
                            raise KeyError(f"Missing value for symbol: {name}")
                        return float(variable_values[name])
                    raise ValueError(
                        f"Cannot numerically evaluate descriptor: {expression.get('type')}"
                    )
                if isinstance(expression, str):
                    # Reject numpy members that reach the filesystem or
                    # pickle (np.load can unpickle arbitrary objects).
                    _reject_unsafe_numpy_access(expression)
                    return float(
                        eval(
                            expression, {"np": np, "__builtins__": {}}, variable_values
                        )
                    )
                return float(expression)

        except Exception as e:
            logger.error(f"Error evaluating symbolic expression: {e}")
            return np.nan

    def differentiate_spatially(
        self, expression: Any, variables: List[str]
    ) -> Dict[str, Any]:
        """
        Compute spatial derivatives of an expression.

        Args:
            expression: Symbolic expression
            variables: Variable names to differentiate with respect to

        Returns:
            Dictionary of derivatives
        """
        derivatives = {}

        for var in variables:
            try:
                var_symbol = self.Symbol(var)

                if self.backend in ["sympy", "symengine"]:
                    derivative = self.diff(expression, var_symbol)
                    derivatives[var] = derivative
                else:
                    derivatives[var] = self._numpy_diff(expression, var_symbol)

            except Exception as e:
                logger.error(f"Error computing derivative w.r.t. {var}: {e}")
                derivatives[var] = None

        return derivatives

    def integrate_spatially(
        self,
        expression: Any,
        variables: List[str],
        limits: Dict[str, Tuple[float, float]],
    ) -> Dict[str, Any]:
        """
        Compute spatial integrals of an expression.

        Args:
            expression: Symbolic expression
            variables: Variable names to integrate
            limits: Integration limits for each variable

        Returns:
            Dictionary of integrals
        """
        integrals = {}

        for var in variables:
            try:
                var_symbol = self.Symbol(var)
                lower, upper = limits.get(var, (0, 1))

                if self.backend in ["sympy", "symengine"]:
                    integral = self.integrate(expression, (var_symbol, lower, upper))
                    integrals[var] = integral
                else:
                    integrals[var] = self._numpy_integrate(expression, var_symbol)

            except Exception as e:
                logger.error(f"Error computing integral w.r.t. {var}: {e}")
                integrals[var] = None

        return integrals

    def solve_spatial_equations(
        self, equations: List[Any], variables: List[str]
    ) -> Dict[str, Any]:
        """
        Solve systems of spatial equations.

        Args:
            equations: List of symbolic equations
            variables: Variable names to solve for

        Returns:
            Solution dictionary
        """
        try:
            var_symbols = [self.Symbol(var) for var in variables]

            if self.backend in ["sympy", "symengine"]:
                # Solve the system
                solutions = self.solve(equations, var_symbols)
                return {
                    "solutions": solutions,
                    "variables": variables,
                    "backend": self.backend,
                }
            else:
                # Numpy backend - simplified
                return {
                    "solutions": None,
                    "variables": variables,
                    "backend": self.backend,
                    "message": "Equation solving is unavailable for the numpy backend",
                }

        except Exception as e:
            logger.error(f"Error solving spatial equations: {e}")
            return {"solutions": None, "error": str(e), "backend": self.backend}

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about the symbolic math backend.

        Returns:
            Backend information
        """
        return {
            "backend": self.backend,
            "engine_available": self._engine is not None and self._engine != "numpy",
            "supported_operations": [
                "differentiation",
                "integration",
                "equation_solving",
                "simplification",
                "expansion",
            ],
            "limitations": (
                []
                if self.backend in ["sympy", "symengine"]
                else [
                    "Limited symbolic operations",
                    "No advanced equation solving",
                    "Simplified differentiation and integration",
                ]
            ),
        }

    def generate_proof(
        self, expression: Any, operation: str, result: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate proof for a symbolic operation.

        Args:
            expression: Symbolic expression
            operation: Operation performed
            result: Optional result of operation

        Returns:
            Proof dictionary if available
        """
        try:
            from geo_infer_math.core.theorem_proving.integration import (
                generate_proof_from_symbolic,
            )

            proof_result = generate_proof_from_symbolic(expression, operation)

            if proof_result:
                return {
                    "status": proof_result.status.value,
                    "theorem": proof_result.theorem,
                    "proof": proof_result.proof,
                    "backend": proof_result.backend,
                }
        except ImportError:
            logger.debug("Theorem proving not available for proof generation")

        return None

    def verify_operation(self, original: Any, result: Any, operation: str) -> bool:
        """
        Verify a symbolic operation using theorem proving.

        Args:
            original: Original expression
            result: Result of operation
            operation: Operation name

        Returns:
            True if verified
        """
        try:
            from geo_infer_math.core.theorem_proving.integration import (
                verify_symbolic_operation,
            )

            return verify_symbolic_operation(original, result, operation)
        except ImportError:
            logger.debug("Theorem proving not available for verification")
            return False

    def improved_differentiate(
        self, expression: Any, variable: Any, order: int = 1, verify: bool = False
    ) -> Tuple[Any, Optional[Dict[str, Any]]]:
        """
        Improved automatic differentiation with optional proof generation.

        Args:
            expression: Symbolic expression
            variable: Variable to differentiate
            order: Order of derivative
            verify: Whether to verify the result

        Returns:
            Tuple of (derivative, proof_info)
        """
        # Perform differentiation
        if self.backend in ["sympy", "symengine"]:
            derivative = self.diff(expression, variable, order)
        else:
            derivative = self._numpy_diff(expression, variable)

        proof_info = None

        # Generate proof if requested
        if verify:
            proof_info = self.generate_proof(expression, "differentiate", derivative)

        return derivative, proof_info

    def verify_spatial_model(
        self, model: Dict[str, Any], constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify a spatial model using theorem proving.

        Args:
            model: Spatial model definition
            constraints: Optional constraints to verify

        Returns:
            Verification results
        """
        try:
            from geo_infer_math.core.theorem_proving.prover import TheoremProver

            prover = TheoremProver()
            results = {}

            # Verify each equation in the model
            for eq in model.get("equations", []):
                if "parsed" in eq:
                    theorem = str(eq["parsed"])
                    proof_result = prover.prove(theorem, constraints)
                    results[eq.get("original", theorem)] = {
                        "status": proof_result.status.value,
                        "verified": proof_result.status.value == "proven",
                    }

            return results
        except ImportError:
            logger.debug("Theorem proving not available for model verification")
            return {"error": "Theorem proving not available"}

    def symbolic_to_numeric_with_proof(
        self,
        expression: Any,
        variable_values: Dict[str, float],
        preserve_proof: bool = True,
    ) -> Tuple[float, Optional[Dict[str, Any]]]:
        """
        Convert symbolic expression to numeric with proof preservation.

        Args:
            expression: Symbolic expression
            variable_values: Variable values
            preserve_proof: Whether to preserve proof information

        Returns:
            Tuple of (numeric_value, proof_info)
        """
        # Evaluate expression
        numeric_value = self.evaluate_symbolic_expression(expression, variable_values)

        proof_info = None
        if preserve_proof:
            # Generate proof for evaluation
            proof_info = {
                "expression": str(expression),
                "variable_values": variable_values,
                "result": numeric_value,
                "evaluation_proof": "Direct substitution and evaluation",
            }

        return numeric_value, proof_info


# Convenience functions
def create_symbolic_math_engine(backend: str = "sympy") -> SymbolicMath:
    """Create a symbolic math engine."""
    return SymbolicMath(backend)


def define_spatial_model(
    variables: List[str], equations: List[str], constraints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Define a symbolic spatial model."""
    engine = SymbolicMath()
    return engine.define_spatial_model(variables, equations, constraints)


def compute_spatial_gradients(
    model: Dict[str, Any], parameters: List[str]
) -> Dict[str, Any]:
    """Compute gradients of spatial model."""
    engine = SymbolicMath()
    return engine.compute_gradients(model, parameters)


__all__ = [
    "SymbolicMath",
    "create_symbolic_math_engine",
    "define_spatial_model",
    "compute_spatial_gradients",
]
