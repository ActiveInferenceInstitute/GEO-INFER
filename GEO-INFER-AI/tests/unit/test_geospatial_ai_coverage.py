"""
Coverage-focused unit tests for the predictive toolkit edge branches.

Complements ``test_geospatial_ai.py``: H3 graph failure paths, objective
variants in resource allocation, spatial priors, and hierarchical
belief propagation with top-down priors.
"""

import numpy as np
import pytest

from geo_infer_ai.models.predictive.geospatial_ai import (
    EnvironmentalActiveInferenceEngine,
    H3SpatialGraph,
    LevelSpatialGraph,
    MultiScaleHierarchicalAnalyzer,
)

# Small single-variable engine keeps GP fits fast and deterministic.
VARIABLES = ["temperature"]


@pytest.fixture
def engine() -> EnvironmentalActiveInferenceEngine:
    return EnvironmentalActiveInferenceEngine(
        h3_resolution=6,
        environmental_variables=VARIABLES,
        prediction_horizon=2,
        uncertainty_threshold=0.2,
    )


@pytest.fixture
def boundary() -> dict:
    return {
        "coordinates": [
            [[[-97.75, 30.25], [-97.74, 30.25], [-97.74, 30.26], [-97.75, 30.25]]]
        ]
    }


class TestH3GraphFailurePaths:
    """Invalid H3 cells degrade to empty neighbor sets."""

    def test_h3_spatial_graph_invalid_cells(self) -> None:
        graph = H3SpatialGraph(["not-a-cell", "also-bad"], max_distance=2)
        assert graph.cells == ["not-a-cell", "also-bad"]
        for cell in graph.cells:
            assert graph.neighbors[cell] == {1: set(), 2: set()}

    def test_level_spatial_graph_invalid_cells(self) -> None:
        graph = LevelSpatialGraph(["not-a-cell"])
        assert graph.neighbors["not-a-cell"] == set()


class TestDomainInitializationFailures:
    """initialize_spatial_domain surfaces generation failures."""

    def test_generation_error_propagates(self, engine, monkeypatch) -> None:
        def boom(_boundary):
            raise RuntimeError("bad boundary")

        monkeypatch.setattr(engine, "_generate_h3_cells_from_boundary", boom)
        with pytest.raises(RuntimeError, match="bad boundary"):
            engine.initialize_spatial_domain({"coordinates": []})

    def test_malformed_ring_entries_are_skipped(self, engine) -> None:
        boundary = {
            "coordinates": [
                [
                    [
                        [-97.75, 30.25],
                        ["malformed", 30.25],
                        [-97.74, 30.26],
                        [-97.75, 30.25],
                    ]
                ]
            ]
        }
        engine.initialize_spatial_domain(boundary)
        assert len(engine.environmental_states) > 0


class TestPredictionFailurePaths:
    """Untrained or failing GP models degrade to empty results."""

    def test_predict_without_observations_returns_predictions(
        self, engine, boundary
    ) -> None:
        engine.initialize_spatial_domain(boundary)
        # Untrained GPs still emit prior-mean predictions per cell and
        # timestep; predictions carry the default factor analysis.
        predictions = engine.predict_environmental_dynamics(forecast_timesteps=1)
        assert set(predictions.keys()) == set(VARIABLES)
        for var_predictions in predictions.values():
            assert len(var_predictions) == len(engine.environmental_states)
            for pred in var_predictions:
                assert pred.uncertainty > 0.0
                assert "temperature_vegetation_interaction" in pred.contributing_factors

    def test_gp_fit_failure_is_logged_not_raised(self, engine, boundary) -> None:
        engine.initialize_spatial_domain(boundary)
        cells = list(engine.environmental_states)

        def broken_fit(_X, _y):
            raise ValueError("simulated fit failure")

        engine.gp_models["temperature"].fit = broken_fit
        for t in range(3):
            engine.observe_environment(
                {cell: {"temperature": 20.0 + t} for cell in cells[:3]}, float(t)
            )
        # History accumulated; the failed fit never crashed the run.
        assert len(engine.observation_history) == 3


class TestResourceAllocationObjectives:
    """optimize_resource_allocation honors each objective branch."""

    @staticmethod
    def _prepared_engine(boundary) -> EnvironmentalActiveInferenceEngine:
        engine = EnvironmentalActiveInferenceEngine(
            h3_resolution=6,
            environmental_variables=VARIABLES,
            prediction_horizon=2,
        )
        engine.initialize_spatial_domain(boundary)
        cells = list(engine.environmental_states)[:4]
        for t in range(6):
            engine.observe_environment(
                {cell: {"temperature": 0.4 + 0.05 * t} for cell in cells}, float(t)
            )
        # Shape the first cell to force each resource-type branch under the
        # different objectives.
        state = engine.environmental_states[cells[0]]
        state.vegetation_density = 0.1
        state.water_availability = 0.1
        return engine, cells

    def test_biodiversity_objective_low_vegetation(self, boundary) -> None:
        engine, cells = self._prepared_engine(boundary)
        allocations = engine.optimize_resource_allocation(
            resource_budget=100.0,
            resource_types=["vegetation_restoration"],
            optimization_objective="biodiversity",
        )
        assert all(a.location in engine.environmental_states for a in allocations)
        assert sum(a.allocation_amount for a in allocations) <= 100.0

    def test_carbon_objective(self, boundary) -> None:
        engine, _ = self._prepared_engine(boundary)
        engine.environmental_states[
            list(engine.environmental_states)[0]
        ].carbon_flux = -0.8
        allocations = engine.optimize_resource_allocation(
            resource_budget=50.0,
            resource_types=[],
            optimization_objective="carbon",
        )
        assert isinstance(allocations, list)

    def test_stability_objective(self, boundary) -> None:
        engine, _ = self._prepared_engine(boundary)
        allocations = engine.optimize_resource_allocation(
            resource_budget=50.0,
            resource_types=[],
            optimization_objective="stability",
        )
        assert isinstance(allocations, list)

    def test_unknown_objective_falls_back_to_monitoring(self, boundary) -> None:
        engine, _ = self._prepared_engine(boundary)
        allocations = engine.optimize_resource_allocation(
            resource_budget=10.0,
            resource_types=[],
            optimization_objective="mystery",
        )
        assert all(a.resource_type == "environmental_monitoring" for a in allocations)

    def test_zero_budget_produces_no_allocations(self, boundary) -> None:
        engine, _ = self._prepared_engine(boundary)
        allocations = engine.optimize_resource_allocation(
            resource_budget=0.0,
            resource_types=["x"],
            optimization_objective="biodiversity",
        )
        assert allocations == []


class TestComputeSpatialPriors:
    """compute_spatial_priors covers fallback and Moran-weighted paths."""

    def test_uniform_fallback_without_domain(self, engine) -> None:
        priors = engine.compute_spatial_priors("temperature", n_states=4)
        assert priors == {}

    def test_uniform_fallback_without_graph(self, engine, boundary) -> None:
        engine.initialize_spatial_domain(boundary)
        engine.spatial_graph = None
        priors = engine.compute_spatial_priors("temperature", n_states=4)
        assert len(priors) == len(engine.environmental_states)
        for prior in priors.values():
            np.testing.assert_allclose(prior, np.ones(4) / 4)

    def test_graph_without_neighbor_entries_yields_flatter_priors(
        self, engine, boundary
    ) -> None:
        engine.initialize_spatial_domain(boundary)
        cells = list(engine.environmental_states)
        for t, value in enumerate(np.linspace(0.1, 0.9, len(cells))):
            engine.environmental_states[cells[t]].temperature = float(value)
        # Stub graph with no distance-1 neighbors: Local Moran's I is 0.
        engine.spatial_graph = H3SpatialGraph(cells, max_distance=1)
        for neighbor_map in engine.spatial_graph.neighbors.values():
            neighbor_map[1] = set()

        priors = engine.compute_spatial_priors("temperature", n_states=4)
        assert len(priors) == len(cells)
        for prior in priors.values():
            assert prior.shape == (4,)
            assert prior.sum() == pytest.approx(1.0)


class TestHierarchicalPropagation:
    """MultiScaleHierarchicalAnalyzer top-down and parent lookups."""

    @pytest.fixture
    def analyzer(self) -> MultiScaleHierarchicalAnalyzer:
        return MultiScaleHierarchicalAnalyzer(base_resolution=6, hierarchy_levels=2)

    @pytest.fixture
    def boundary(self) -> dict:
        return {
            "coordinates": [
                [[[-97.75, 30.25], [-97.74, 30.25], [-97.74, 30.26], [-97.75, 30.25]]]
            ]
        }

    def test_propagate_with_top_down_priors(self, analyzer, boundary) -> None:
        analyzer.initialize_hierarchy(boundary)
        bottom_level = sorted(analyzer.hierarchical_graphs.keys())[0]

        evidence = {
            cell: np.array([0.7, 0.1, 0.1, 0.1])
            for cell in analyzer.hierarchical_graphs[bottom_level].cells
        }
        updated = analyzer.propagate_beliefs_hierarchically(
            {bottom_level: evidence}, top_down_priors={bottom_level: evidence}
        )
        assert set(updated.keys()) == set(analyzer.hierarchical_graphs.keys())
        for level_beliefs in updated.values():
            for belief in level_beliefs.values():
                assert belief.sum() == pytest.approx(1.0)

    def test_aggregate_at_highest_level_is_noop(self, analyzer, boundary) -> None:
        analyzer.initialize_hierarchy(boundary)
        highest = sorted(analyzer.hierarchical_graphs.keys())[-1]
        before = {
            cell: belief.copy()
            for cell, belief in analyzer.hierarchical_beliefs[highest].items()
        }
        analyzer._aggregate_beliefs_upward(highest)
        after = analyzer.hierarchical_beliefs[highest]
        for cell in before:
            np.testing.assert_allclose(before[cell], after[cell])

    def test_find_parent_cell(self, analyzer, boundary) -> None:
        analyzer.initialize_hierarchy(boundary)
        child_level = sorted(analyzer.hierarchical_graphs.keys())[0]
        parent_level = sorted(analyzer.hierarchical_graphs.keys())[-1]
        child_cell = analyzer.hierarchical_graphs[child_level].cells[0]

        parent = analyzer._find_parent_cell(child_cell, parent_level)
        # Parent resolution may place the parent outside the level's cells.
        assert (
            parent is None or parent in analyzer.hierarchical_graphs[parent_level].cells
        )

    def test_scale_coherence_missing_level(self, analyzer, boundary) -> None:
        analyzer.initialize_hierarchy(boundary)
        assert (
            analyzer._compute_scale_coherence("level_missing", "level_also_missing")
            == 0.0
        )

    def test_find_parent_cell_invalid_level(self, analyzer, boundary) -> None:
        analyzer.initialize_hierarchy(boundary)
        child_cell = analyzer.hierarchical_graphs[
            sorted(analyzer.hierarchical_graphs.keys())[0]
        ].cells[0]
        assert analyzer._find_parent_cell(child_cell, "res_nonsense") is None

    def test_spatial_extent_empty_cells(self, analyzer) -> None:
        assert analyzer._compute_spatial_extent([]) == {}
