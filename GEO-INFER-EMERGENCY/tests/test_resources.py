"""Tests for resource deployment module."""

import pytest

from geo_infer_emergency.core.resources import (
    ResourceDeployer,
    Resource,
    ResourceStatus,
    ResourceType,
)


class TestResourceDataclasses:
    """Tests for resource dataclass creation."""

    def test_resource_creation(self) -> None:
        resource = Resource(
            resource_id="r1",
            resource_type=ResourceType.ENGINE,
            name="Engine 1",
            location={"lat": 34.0, "lon": -118.0},
        )
        assert resource.resource_id == "r1"
        assert resource.status == ResourceStatus.AVAILABLE
        assert resource.resource_type == ResourceType.ENGINE

    def test_resource_status_values(self) -> None:
        assert ResourceStatus.AVAILABLE.value == "available"
        assert ResourceStatus.EN_ROUTE.value == "en_route"
        assert ResourceStatus.ON_SCENE.value == "on_scene"

    def test_resource_type_values(self) -> None:
        assert ResourceType.ENGINE.value == "engine"
        assert ResourceType.AMBULANCE.value == "ambulance"
        assert ResourceType.HELICOPTER.value == "helicopter"


class TestResourceDeployerInit:
    """Tests for ResourceDeployer initialization."""

    def test_default_initialization(self) -> None:
        deployer = ResourceDeployer()
        assert deployer is not None
        assert deployer.optimization_algorithm == "greedy_nearest_resource"
        assert deployer.real_time_updates is True
        assert "engines" in deployer.resource_types

    def test_custom_initialization(self) -> None:
        deployer = ResourceDeployer(
            resource_types=["helicopters"],
            optimization_algorithm="greedy",
            real_time_updates=False,
        )
        assert deployer.optimization_algorithm == "greedy"
        assert deployer.real_time_updates is False

    def test_register_resource(self) -> None:
        deployer = ResourceDeployer()
        resource = Resource(
            resource_id="r1",
            resource_type=ResourceType.ENGINE,
            name="Engine 1",
        )
        deployer.register_resource(resource)
        assert "r1" in deployer._resources


class TestOptimizeAllocation:
    """Tests for resource allocation optimization."""

    def test_optimize_allocation(self) -> None:
        deployer = ResourceDeployer()
        result = deployer.optimize_allocation(
            resources=[
                {
                    "id": "r1",
                    "type": "engine",
                    "name": "Engine 1",
                    "location": {"lat": 34.05, "lon": -118.25},
                    "status": "available",
                },
                {
                    "id": "r2",
                    "type": "ambulance",
                    "name": "Ambulance 1",
                    "location": {"lat": 34.06, "lon": -118.24},
                    "status": "available",
                },
            ],
            demand_points=[
                {"id": "d1", "location": {"lat": 34.05, "lon": -118.25}},
            ],
            constraints={"response_time": 15, "coverage": 0.8},
            objectives=["minimize_response_time"],
        )
        assert "allocations" in result
        assert result["metrics"]["total_demands"] == 1
        assert result["feasible"] is True

    def test_allocation_with_insufficient_resources(self) -> None:
        deployer = ResourceDeployer()
        result = deployer.optimize_allocation(
            resources=[
                {
                    "id": "r1",
                    "type": "engine",
                    "name": "Engine 1",
                    "location": {"lat": 34.05, "lon": -118.25},
                    "status": "available",
                },
            ],
            demand_points=[
                {"id": "d1", "location": {"lat": 34.05, "lon": -118.25}},
                {"id": "d2", "location": {"lat": 34.06, "lon": -118.24}},
                {"id": "d3", "location": {"lat": 34.07, "lon": -118.23}},
            ],
            constraints={"response_time": 15, "coverage": 0.8},
            objectives=["minimize_response_time"],
        )
        assert len(result["unallocated_demands"]) > 0
        assert result["metrics"]["coverage_rate"] < 1.0

    def test_get_resource_status(self) -> None:
        deployer = ResourceDeployer()
        resource = Resource(
            resource_id="r1",
            resource_type=ResourceType.ENGINE,
            name="Engine 1",
            location={"lat": 34.0, "lon": -118.0},
        )
        deployer.register_resource(resource)
        status = deployer.get_resource_status("r1")
        assert status is not None
        assert status["status"] == "available"

    def test_get_nonexistent_resource_status(self) -> None:
        deployer = ResourceDeployer()
        status = deployer.get_resource_status("nonexistent")
        assert status is None


class TestDynamicRedeploy:
    """Tests for dynamic redeployment."""

    def test_dynamic_redeploy(self) -> None:
        deployer = ResourceDeployer()
        resource = Resource(
            resource_id="r1",
            resource_type=ResourceType.ENGINE,
            name="Engine 1",
            location={"lat": 34.05, "lon": -118.25},
        )
        deployer.register_resource(resource)

        result = deployer.dynamic_redeploy(
            current_positions=[
                {"resource_id": "r1", "location": {"lat": 34.05, "lon": -118.25}}
            ],
            pending_incidents=[],
            predicted_demand={"high_risk_areas": [{"lat": 34.1, "lon": -118.3}]},
            strategy="move_up",
        )
        assert result["strategy"] == "move_up"
        assert "redeployments" in result


class TestStagingManagement:
    """Tests for staging area management."""

    def test_manage_staging(self) -> None:
        deployer = ResourceDeployer()
        result = deployer.manage_staging(
            staging_areas=[
                {
                    "id": "stg1",
                    "location": {"lat": 34.0, "lon": -118.0},
                    "capacity": 50,
                },
            ],
            incoming_resources=[{"id": "r1"}, {"id": "r2"}],
            assignment_queue=[
                {"id": "a1", "incident": "inc1", "resources_needed": 2, "severity": 3},
                {"id": "a2", "incident": "inc2", "resources_needed": 1, "severity": 5},
            ],
            prioritization="incident_severity",
        )
        assert result["prioritization"] == "incident_severity"
        assert len(result["staging_areas"]) == 1
        assert len(result["pending_queue"]) == 2


class TestResourceTracking:
    """Tests for resource tracking."""

    def test_track_resources(self) -> None:
        deployer = ResourceDeployer()
        result = deployer.track_resources(
            resources=[
                {
                    "id": "r1",
                    "type": "engine",
                    "status": "available",
                    "location": {"lat": 34.0, "lon": -118.0},
                },
                {
                    "id": "r2",
                    "type": "ambulance",
                    "status": "en_route",
                    "location": {"lat": 34.1, "lon": -118.1},
                },
                {"id": "r3", "type": "rescue_unit", "status": "on_scene"},
            ],
        )
        assert result["summary"]["total"] == 3
        assert result["summary"]["available"] == 1
        assert result["summary"]["en_route"] == 1
        assert result["summary"]["on_scene"] == 1


class TestResourceTypeResolution:
    """GS-152: resource_types config and ResourceType vocabulary."""

    def test_plural_alias_types_are_resolved(self) -> None:
        """optimize_allocation accepts the module's plural vocabulary."""
        deployer = ResourceDeployer()
        result = deployer.optimize_allocation(
            resources=[
                {
                    "id": "r1",
                    "type": "engines",
                    "location": {"lat": 34.05, "lon": -118.25},
                },
                {
                    "id": "r2",
                    "type": "ambulances",
                    "location": {"lat": 34.06, "lon": -118.24},
                },
                {
                    "id": "r3",
                    "type": "rescue_units",
                    "location": {"lat": 34.07, "lon": -118.23},
                },
            ],
            demand_points=[
                {"id": "d1", "location": {"lat": 34.05, "lon": -118.25}},
            ],
            constraints={"response_time": 15, "coverage": 0.8},
            objectives=["minimize_response_time"],
        )
        assert result["metrics"]["demands_covered"] == 1
        assert result["allocations"][0]["resource_type"] == "engine"

    def test_unknown_type_error_names_valid_types(self) -> None:
        """Unknown type raises ValueError listing valid ResourceType values."""
        deployer = ResourceDeployer()
        with pytest.raises(ValueError, match="Valid types"):
            deployer.optimize_allocation(
                resources=[
                    {
                        "id": "r1",
                        "type": "boat",
                        "location": {"lat": 34.0, "lon": -118.0},
                    },
                ],
                demand_points=[],
                constraints={"response_time": 15, "coverage": 0.8},
                objectives=[],
            )

    def test_type_outside_configured_resource_types_is_rejected(self) -> None:
        """The configured resource_types act as an allowed-type filter."""
        deployer = ResourceDeployer(resource_types=["ambulances"])
        with pytest.raises(ValueError, match="allowed types"):
            deployer.optimize_allocation(
                resources=[
                    {
                        "id": "r1",
                        "type": "engine",
                        "location": {"lat": 34.0, "lon": -118.0},
                    },
                ],
                demand_points=[],
                constraints={"response_time": 15, "coverage": 0.8},
                objectives=[],
            )


class TestDynamicRedeployHeuristic:
    """GS-153: move_up picks the unit farthest from pending incidents."""

    def _register(self, deployer, resource_id, lat, lon):
        deployer.register_resource(
            Resource(
                resource_id=resource_id,
                resource_type=ResourceType.ENGINE,
                name=resource_id,
                location={"lat": lat, "lon": lon},
            )
        )

    def test_move_up_selects_unit_farthest_from_incident(self) -> None:
        """The unit farthest from the pending incident is redeployed."""
        deployer = ResourceDeployer()
        self._register(deployer, "near", 34.01, -118.0)
        self._register(deployer, "far", 35.5, -119.5)

        result = deployer.dynamic_redeploy(
            current_positions=[],
            pending_incidents=[{"id": "i1", "location": {"lat": 34.0, "lon": -118.0}}],
            predicted_demand={"high_risk_areas": [{"lat": 35.0, "lon": -119.0}]},
            strategy="move_up",
        )
        assert result["units_redeployed"] == 1
        assert result["redeployments"][0]["resource_id"] == "far"

    def test_move_up_without_incidents_keeps_first_available_order(self) -> None:
        """With no pending incidents the first-available unit is moved."""
        deployer = ResourceDeployer()
        self._register(deployer, "first", 34.01, -118.0)
        self._register(deployer, "second", 35.5, -119.5)

        result = deployer.dynamic_redeploy(
            current_positions=[],
            pending_incidents=[],
            predicted_demand={"high_risk_areas": [{"lat": 35.0, "lon": -119.0}]},
            strategy="move_up",
        )
        assert result["redeployments"][0]["resource_id"] == "first"

    def test_move_up_rejects_incomplete_gap_location(self) -> None:
        """Gap entries without complete coordinates raise ValueError."""
        deployer = ResourceDeployer()
        self._register(deployer, "r1", 34.0, -118.0)

        with pytest.raises(ValueError, match="high_risk_areas"):
            deployer.dynamic_redeploy(
                current_positions=[],
                pending_incidents=[],
                predicted_demand={"high_risk_areas": [{"lat": 35.0}]},
                strategy="move_up",
            )
