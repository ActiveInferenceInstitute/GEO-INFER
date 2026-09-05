"""Tests for FastAPI dependency state management.

The API dependencies must return process-level singletons so that state
created by one request (registered vehicles, built networks, created
schedules) is visible to subsequent requests.
"""

from geo_infer_log.api.delivery import (
    get_delivery_scheduler,
    get_last_mile_router,
)
from geo_infer_log.api.routes import get_fleet_manager, get_route_optimizer
from geo_infer_log.api.supply_chain import get_supply_chain_model
from geo_infer_log.core.delivery import DeliveryScheduler, LastMileRouter
from geo_infer_log.core.routing import FleetManager, RouteOptimizer
from geo_infer_log.core.supply_chain import SupplyChainModel


class TestCachedDependencies:
    """Cached dependencies must return the same instance on every call."""

    def test_fleet_manager_is_singleton(self) -> None:
        assert get_fleet_manager() is get_fleet_manager()

    def test_route_optimizer_is_singleton(self) -> None:
        assert get_route_optimizer() is get_route_optimizer()

    def test_last_mile_router_is_singleton(self) -> None:
        assert get_last_mile_router() is get_last_mile_router()

    def test_supply_chain_model_is_singleton(self) -> None:
        assert get_supply_chain_model() is get_supply_chain_model()

    def test_delivery_scheduler_shares_router_state(self) -> None:
        """The scheduler wraps the same cached router instance."""
        scheduler_a: DeliveryScheduler = get_delivery_scheduler()
        scheduler_b: DeliveryScheduler = get_delivery_scheduler()

        assert isinstance(scheduler_a, DeliveryScheduler)
        assert isinstance(scheduler_a.router, LastMileRouter)
        assert scheduler_a.router is scheduler_b.router

    def test_vehicle_registration_persists_across_dependency_calls(self) -> None:
        """A vehicle added via the cached dependency is visible on the next call."""
        from geo_infer_log.core.routing import Vehicle, VehicleType

        fleet: FleetManager = get_fleet_manager()
        before = fleet.get_fleet_status()["total_vehicles"]

        fleet.add_vehicle(
            Vehicle(
                id="API-TEST-001",
                type=VehicleType.VAN,
                capacity=500,
                max_range=200,
                speed=40,
                cost_per_km=0.8,
                emissions_per_km=0.25,
                location=(-118.25, 34.05),
            )
        )

        # A fresh dependency call must observe the registered vehicle.
        assert (
            get_fleet_manager().get_fleet_status()["total_vehicles"] == before + 1
        )
