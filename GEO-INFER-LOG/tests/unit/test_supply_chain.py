"""Tests for supply chain module."""

import pytest
from geo_infer_log.core.supply_chain import (
    SupplyChainModel,
    FacilityLocator,
    InventoryManager,
)


class TestFacilityLocator:
    """Tests for facility location optimization."""

    def test_initialization(self) -> None:
        locator = FacilityLocator()
        assert locator.selected_facilities == []

    def test_locate_facilities_returns_list(self) -> None:
        locator = FacilityLocator()
        result = locator.locate_facilities(
            candidates=[{"id": "c1", "location": (0, 0)}],
            demand_points=[{"id": "d1", "location": (1, 1)}],
            num_facilities=1,
        )
        assert isinstance(result, list)

    def test_analyze_coverage_returns_dict(self) -> None:
        locator = FacilityLocator()
        result = locator.analyze_coverage(
            facilities=[{"id": "f1", "location": (0, 0)}],
            demand_points=[{"id": "d1", "location": (1, 1)}],
            max_distance=10.0,
        )
        assert "coverage_ratio" in result


class TestInventoryManager:
    """Tests for inventory management."""

    def test_initialization(self) -> None:
        manager = InventoryManager()
        assert manager.inventory_levels == {}
        assert manager.reorder_points == {}


class TestSupplyChainModel:
    """Tests for supply chain model."""

    def test_initialization(self) -> None:
        model = SupplyChainModel()
        assert model.network is None
        assert model.graph is None
