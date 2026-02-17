"""Tests for transport routing module."""

import pytest
from geo_infer_transport.core.routing import (
    RoutingEngine,
    RoutingAlgorithm,
    OptimizationCriteria,
    Route,
)


class TestRoutingDataclasses:
    """Tests for routing dataclass and enum creation."""

    def test_routing_algorithm_values(self) -> None:
        assert RoutingAlgorithm.DIJKSTRA.value == "dijkstra"
        assert RoutingAlgorithm.A_STAR.value == "a_star"

    def test_optimization_criteria_values(self) -> None:
        assert OptimizationCriteria.TIME.value == "time"
        assert OptimizationCriteria.DISTANCE.value == "distance"
        assert OptimizationCriteria.COST.value == "cost"


class TestRoutingEngineInit:
    """Tests for RoutingEngine initialization."""

    def test_import(self) -> None:
        assert RoutingEngine is not None

    def test_initialization(self) -> None:
        engine = RoutingEngine()
        assert engine is not None
