"""Unit tests for the SymbolicMath engine (M6-06 test half).

Covers both backends:

* the real ``sympy`` engine — differentiation/integration round-trips,
  spatial-model definition, gradients, numeric evaluation and linear
  solving;
* the ``numpy`` fallback backend (constructed by hiding ``sympy`` during
  engine setup) — its documented numeric capabilities and hard
  ``ValueError`` boundaries.

The ``:189-191`` handler and the ``:447-449`` sympify fallback are owned
by another lane; these tests only assert behavior that survives their
narrowing (valid inputs on every exercised path).
"""

import sys

import pytest

from geo_infer_math.core.symbolic_math import (
    SymbolicMath,
    create_symbolic_math_engine,
)


@pytest.fixture
def engine() -> SymbolicMath:
    return create_symbolic_math_engine("sympy")


class TestSympyBackendRoundTrips:
    """Closed-form operations on the real symbolic engine."""

    def test_backend_info_reports_live_engine(self, engine) -> None:
        info = engine.get_backend_info()
        assert info["backend"] == "sympy"
        assert info["engine_available"] is True

    def test_derivative_of_cubic(self, engine) -> None:
        x = engine.Symbol("x")
        assert str(engine.diff(x**3, x)) == "3*x**2"

    def test_definite_integral_hand_computed(self, engine) -> None:
        x = engine.Symbol("x")
        assert float(engine.integrate(x**2, (x, 0, 1))) == pytest.approx(1.0 / 3.0)

    def test_integrate_derivative_round_trip(self, engine) -> None:
        """∫₀² ∂/∂x x³ dx recovers the boundary value 2³."""
        x = engine.Symbol("x")
        derivative = engine.diff(x**3, x)
        recovered = engine.integrate(derivative, (x, 0, 2))
        assert float(recovered) == pytest.approx(8.0)

    def test_define_spatial_model_parses_equations_and_constraints(
        self, engine
    ) -> None:
        model = engine.define_spatial_model(
            ["x", "y"], ["x**2 + y**2"], constraints=["x > 0"]
        )

        assert model["variables"] == ["x", "y"]
        assert model["backend"] == "sympy"
        parsed = model["equations"][0]["parsed"]
        assert "error" not in model["equations"][0]
        assert str(parsed) == "x**2 + y**2"
        assert str(model["constraints"][0]["parsed"]) == "x > 0"

    def test_compute_gradients_hand_computed(self, engine) -> None:
        model = engine.define_spatial_model(["x", "y"], ["x**2 + y**2"])
        gradients = engine.compute_gradients(model, ["x"])

        assert gradients["x"] == [2 * engine.Symbol("x")]

    def test_evaluate_symbolic_expression(self, engine) -> None:
        model = engine.define_spatial_model(["x", "y"], ["x**2 + y**2"])
        parsed = model["equations"][0]["parsed"]
        value = engine.evaluate_symbolic_expression(parsed, {"x": 3.0, "y": 4.0})
        assert value == pytest.approx(25.0)

    def test_solve_spatial_equations_hand_computed(self, engine) -> None:
        x, y = engine.symbols("x,y")
        result = engine.solve_spatial_equations([x + y - 10, x - y - 2], ["x", "y"])

        assert result["backend"] == "sympy"
        solutions = result["solutions"]
        # sympy returns a dict for a unique solution, or a list of dicts.
        first = solutions[0] if isinstance(solutions, list) else solutions
        assert float(first[x]) == pytest.approx(6.0)
        assert float(first[y]) == pytest.approx(4.0)

    def test_improved_differentiate_with_proof(self, engine) -> None:
        x = engine.Symbol("x")
        derivative, proof = engine.improved_differentiate(x**3, x, verify=True)

        assert str(derivative) == "3*x**2"
        assert proof is not None
        # The proof pipeline records the theorem it attempted, whatever
        # status the local (non-network) prover assigns.
        assert set(proof) >= {"status", "theorem", "proof", "backend"}
        assert proof["theorem"].startswith("Derivative(")

    def test_symbolic_to_numeric_with_proof_carries_context(self, engine) -> None:
        x = engine.Symbol("x")
        value, proof = engine.symbolic_to_numeric_with_proof(
            x**2 + 1, {"x": 2.0}, preserve_proof=True
        )

        assert value == pytest.approx(5.0)
        assert proof is not None
        assert proof["result"] == pytest.approx(5.0)
        assert proof["variable_values"] == {"x": 2.0}
        assert "Direct substitution" in proof["evaluation_proof"]


class TestBackendSelection:
    """Unknown engine names fail loudly instead of silently degrading."""

    def test_unsupported_backend_name_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported backend"):
            SymbolicMath("numpy")


@pytest.fixture
def numpy_engine(monkeypatch) -> SymbolicMath:
    """An engine forced into the numpy fallback by hiding sympy.

    The context monkeypatch is undone before the fixture returns, so the
    lazy ``import sympy`` inside the numeric helpers keeps working.
    """
    with monkeypatch.context() as m:
        m.setitem(sys.modules, "sympy", None)
        with pytest.warns(UserWarning, match="not available"):
            engine = SymbolicMath("sympy")
    assert engine.get_backend_info()["engine_available"] is False
    return engine


class TestNumpyFallbackBackend:
    """Documented CAN-do capabilities of the numeric fallback."""

    def test_numeric_integration_hand_computed(self, numpy_engine) -> None:
        result = numpy_engine.integrate("x**2", numpy_engine.Symbol("x"), 0.0, 1.0)
        assert result == pytest.approx(1.0 / 3.0, abs=1e-6)

    def test_linear_system_solved_hand_computed(self, numpy_engine) -> None:
        solution = numpy_engine.solve(
            ["x + y = 10", "x - y = 2"],
            [numpy_engine.Symbol("x"), numpy_engine.Symbol("y")],
        )
        assert solution == {"x": pytest.approx(6.0), "y": pytest.approx(4.0)}

    def test_callable_derivative_by_finite_difference(self, numpy_engine) -> None:
        derivative = numpy_engine.diff(lambda v: v**3, numpy_engine.Symbol("x"))
        assert derivative == pytest.approx(3.0, rel=1e-4)

    def test_symbol_descriptor_identity_and_zero_rules(self, numpy_engine) -> None:
        assert (
            numpy_engine.diff(numpy_engine.Symbol("x"), numpy_engine.Symbol("x")) == 1.0
        )
        assert (
            numpy_engine.diff(numpy_engine.Symbol("y"), numpy_engine.Symbol("x")) == 0.0
        )
        assert numpy_engine.diff(5, numpy_engine.Symbol("x")) == 0.0

    def test_compound_descriptor_yields_unevaluated_derivative(
        self, numpy_engine
    ) -> None:
        """Compound expressions are NOT symbolically differentiated — the
        documented boundary returns an unevaluated derivative descriptor."""
        expr = {"type": "expression", "string": "x**2"}
        result = numpy_engine.diff(expr, numpy_engine.Symbol("x"))

        assert result["type"] == "derivative"
        assert result["order"] == 1
        assert result["expression"] == expr

    def test_nonlinear_system_rejected(self, numpy_engine) -> None:
        with pytest.raises(ValueError, match="linear systems"):
            numpy_engine.solve(["x**2 = 4"], [numpy_engine.Symbol("x")])

    def test_singular_system_rejected(self, numpy_engine) -> None:
        with pytest.raises(ValueError, match="singular"):
            numpy_engine.solve(
                ["x + y = 2", "2*x + 2*y = 4"],
                [numpy_engine.Symbol("x"), numpy_engine.Symbol("y")],
            )

    def test_unsafe_numpy_member_rejected(self, numpy_engine) -> None:
        """np.load can unpickle arbitrary objects — the AST guard must
        refuse it instead of evaluating."""
        with pytest.raises(ValueError, match="Unsafe"):
            numpy_engine.integrate(
                "np.load('dump.bin')", numpy_engine.Symbol("x"), 0.0, 1.0
            )
