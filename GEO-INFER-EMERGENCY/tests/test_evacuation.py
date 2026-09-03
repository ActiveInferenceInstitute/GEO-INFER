"""Tests for evacuation planning module."""

import networkx as nx
import pytest

from geo_infer_emergency.core.evacuation import (
    EvacuationPlanner,
    EvacuationZone,
    EvacuationLevel,
    EvacuationRoute,
    Shelter,
)


@pytest.fixture
def road_network() -> nx.DiGraph:
    """Small road network: zone z1 routes to shelters s1 and s2.

    Edge attributes: distance (km), travel_time (minutes),
    capacity (vehicles/hour), and one contraflow-capable segment.
    """
    graph = nx.DiGraph()
    graph.add_edge("z1", "a", distance=4.0, travel_time=6.0, capacity=1000)
    graph.add_edge("a", "b", distance=3.0, travel_time=4.0, capacity=800)
    graph.add_edge("b", "s1", distance=3.0, travel_time=5.0, capacity=600, contraflow_capable=True)
    graph.add_edge("z1", "b", distance=10.0, travel_time=15.0, capacity=900)
    graph.add_edge("a", "s1", distance=9.0, travel_time=12.0)
    graph.add_edge("b", "s2", distance=6.0, travel_time=9.0, capacity=700)
    return graph


@pytest.fixture
def planner(road_network: nx.DiGraph) -> EvacuationPlanner:
    """EvacuationPlanner over the synthetic road network."""
    return EvacuationPlanner(road_network=road_network)


class TestEvacuationDataclasses:
    """Tests for evacuation dataclass creation."""

    def test_evacuation_zone_creation(self) -> None:
        zone = EvacuationZone(
            zone_id="z1",
            name="Zone A",
            geometry={"type": "Polygon", "coordinates": []},
            population=5000,
        )
        assert zone.zone_id == "z1"
        assert zone.population == 5000
        assert zone.level == EvacuationLevel.WARNING

    def test_shelter_creation(self) -> None:
        shelter = Shelter(
            shelter_id="s1",
            name="Main Shelter",
            location={"lat": 34.0, "lon": -118.0},
            capacity=200,
        )
        assert shelter.capacity == 200
        assert shelter.current_occupancy == 0
        assert shelter.accessible is True

    def test_evacuation_route_creation(self) -> None:
        route = EvacuationRoute(
            route_id="r1",
            origin_zone="z1",
            destination_shelter="s1",
            path=[{"lat": 34.0, "lon": -118.0}],
            distance_km=15.0,
            estimated_time_minutes=30.0,
            capacity_vehicles_per_hour=2000,
        )
        assert route.distance_km == 15.0

    def test_evacuation_level_values(self) -> None:
        assert EvacuationLevel.WARNING.value == "warning"
        assert EvacuationLevel.ORDER.value == "order"
        assert EvacuationLevel.LIFT.value == "lift"


class TestEvacuationPlannerInit:
    """Tests for EvacuationPlanner initialization."""

    def test_default_initialization(self) -> None:
        planner = EvacuationPlanner()
        assert planner is not None
        assert planner.road_network is None
        assert "hospitals" in planner.special_needs

    def test_with_shelters(self) -> None:
        shelters = [
            {"id": "s1", "name": "School", "capacity": 300},
            {"id": "s2", "name": "Church", "capacity": 150},
        ]
        planner = EvacuationPlanner(shelters=shelters)
        assert len(planner._shelters) == 2

    def test_register_shelter(self) -> None:
        planner = EvacuationPlanner()
        shelter = planner.register_shelter({
            "id": "s1", "name": "Gym", "capacity": 500, "services": ["medical"],
        })
        assert shelter.shelter_id == "s1"
        assert shelter.capacity == 500
        assert "medical" in shelter.services


class TestEvacuationPlan:
    """Tests for evacuation plan creation."""

    def test_create_plan(self, planner: EvacuationPlanner) -> None:
        plan = planner.plan(
            affected_zone={"id": "z1", "name": "Downtown", "level": "order", "geometry": {}},
            population={"total": 10000, "special_populations": ["hospitals"]},
            destinations=[{"id": "s1", "name": "Stadium", "capacity": 5000}],
            phasing="staged",
        )
        assert "plan_id" in plan
        assert plan["status"] == "planned"
        assert plan["affected_zone"]["population"] == 10000
        assert len(plan["phasing"]["phases"]) == 3
        assert plan["estimated_clearance_time_hours"] > 0

    def test_create_plan_simultaneous(self, planner: EvacuationPlanner) -> None:
        plan = planner.plan(
            affected_zone={"id": "z1", "name": "Coast", "level": "order", "geometry": {}},
            population={"total": 5000},
            destinations=[{"id": "s1", "name": "Inland Shelter", "capacity": 5000}],
            phasing="simultaneous",
        )
        assert len(plan["phasing"]["phases"]) == 1

    def test_contraflow_enabled(self, planner: EvacuationPlanner) -> None:
        plan = planner.plan(
            affected_zone={"id": "z1", "name": "Area", "level": "order", "geometry": {}},
            population={"total": 2000},
            destinations=[{"id": "s1", "name": "Shelter", "capacity": 2000}],
            contraflow=True,
        )
        assert plan["contraflow"]["enabled"] is True
        assert len(plan["contraflow"]["segments"]) > 0
        assert plan["contraflow"]["segments"][0]["from_node"] == "b"

    def test_plan_requires_road_network(self) -> None:
        planner = EvacuationPlanner()
        with pytest.raises(ValueError, match="road_network required"):
            planner.plan(
                affected_zone={"id": "z1", "name": "Area", "level": "order", "geometry": {}},
                population={"total": 2000},
                destinations=[{"id": "s1", "name": "Shelter", "capacity": 2000}],
            )


class TestOptimizeRoutes:
    """Tests for route optimization."""

    def test_routes_match_networkx_shortest_paths(
        self, planner: EvacuationPlanner, road_network: nx.DiGraph
    ) -> None:
        result = planner.optimize_routes(
            origins=["z1"],
            destinations=["s1", "s2"],
            objectives=["clearance_time"],
            constraints={"road_capacity": True},
        )
        assert result["total_routes"] == 2
        for route in result["routes"]:
            origin, destination = route["origin"], route["destination"]
            assert route["path"][0] == origin
            assert route["path"][-1] == destination
            assert route["distance_km"] == pytest.approx(
                nx.shortest_path_length(road_network, origin, destination, weight="distance")
            )
            assert route["estimated_time_minutes"] == pytest.approx(
                nx.shortest_path_length(road_network, origin, destination, weight="travel_time")
            )
            assert route["capacity_vehicles_per_hour"] > 0

    def test_route_distance_prefers_shorter_path(
        self, planner: EvacuationPlanner
    ) -> None:
        """z1->a->b->s1 (10 km) must beat the direct z1->b edge (10 km + detour)."""
        result = planner.optimize_routes(
            origins=["z1"],
            destinations=["s1"],
            objectives=["clearance_time"],
            constraints={},
        )
        route = result["routes"][0]
        assert route["path"] == ["z1", "a", "b", "s1"]
        assert route["distance_km"] == pytest.approx(10.0)

    def test_capacity_is_binding_edge_minimum(self, planner: EvacuationPlanner) -> None:
        result = planner.optimize_routes(
            origins=["z1"],
            destinations=["s1"],
            objectives=["clearance_time"],
            constraints={},
        )
        # Path z1->a->b->s1 has capacities 1000, 800, 600.
        assert result["routes"][0]["capacity_vehicles_per_hour"] == 600

    def test_unreachable_destination_yields_no_route(
        self, road_network: nx.DiGraph
    ) -> None:
        road_network.add_node("s3")
        planner = EvacuationPlanner(road_network=road_network)
        result = planner.optimize_routes(
            origins=["z1"],
            destinations=["s3"],
            objectives=["clearance_time"],
            constraints={},
        )
        assert result["routes"] == []
        assert result["total_routes"] == 0

    def test_missing_network_raises(self) -> None:
        planner = EvacuationPlanner()
        with pytest.raises(ValueError, match="road_network required"):
            planner.optimize_routes(
                origins=["z1"],
                destinations=["s1"],
                objectives=["clearance_time"],
                constraints={},
            )

    def test_unknown_endpoint_raises(self, planner: EvacuationPlanner) -> None:
        with pytest.raises(ValueError, match="not found in road_network"):
            planner.optimize_routes(
                origins=["nowhere"],
                destinations=["s1"],
                objectives=["clearance_time"],
                constraints={},
            )


class TestContraflowIdentification:
    """Tests for contraflow segment identification."""

    def test_contraflow_from_edge_attributes(self, planner: EvacuationPlanner) -> None:
        segments = planner._identify_contraflow_segments()
        assert segments == [
            {"road": "b->s1", "from_node": "b", "to_node": "s1", "lanes_reversed": 1}
        ]

    def test_contraflow_empty_without_capability_attributes(self) -> None:
        graph = nx.DiGraph()
        graph.add_edge("z1", "s1", distance=5.0, travel_time=8.0)
        planner = EvacuationPlanner(road_network=graph)
        assert planner._identify_contraflow_segments() == []

    def test_contraflow_empty_without_network(self) -> None:
        assert EvacuationPlanner()._identify_contraflow_segments() == []


class TestShelterPlanning:
    """Tests for shelter planning."""

    def test_plan_shelters(self) -> None:
        planner = EvacuationPlanner()
        result = planner.plan_shelters(
            shelter_locations=[
                {"id": "s1", "name": "School", "capacity": 300},
                {"id": "s2", "name": "Church", "capacity": 200},
            ],
            population_estimate=400,
            duration_days=3,
            services=["food", "medical"],
        )
        assert result["capacity_sufficient"] is True
        assert result["total_shelter_capacity"] == 500
        assert result["overflow_population"] == 0
        assert "medical" in result["services"]

    def test_plan_shelters_overflow(self) -> None:
        planner = EvacuationPlanner()
        result = planner.plan_shelters(
            shelter_locations=[{"id": "s1", "name": "Small", "capacity": 50}],
            population_estimate=200,
            duration_days=1,
            services=[],
        )
        assert result["capacity_sufficient"] is False
        assert result["overflow_population"] > 0


class TestClearanceTimeEstimate:
    """Tests for clearance time estimation."""

    def test_estimate_clearance_time(self) -> None:
        planner = EvacuationPlanner()
        zone = EvacuationZone(
            zone_id="z1", name="Zone", geometry={}, population=10000
        )
        estimates = planner.estimate_clearance_time(
            evacuation_plan={"zone": zone, "routes": []},
            scenarios=["best_case", "expected", "worst_case"],
        )
        assert "best_case" in estimates
        assert "expected" in estimates
        assert "worst_case" in estimates
        assert estimates["best_case"]["clearance_hours"] < estimates["worst_case"]["clearance_hours"]

    def test_special_populations_plan(self) -> None:
        planner = EvacuationPlanner()
        result = planner.plan_special_populations(
            facilities=[
                {"id": "h1", "name": "Hospital", "type": "hospital", "population": 100},
                {"id": "n1", "name": "Nursing Home", "type": "nursing_home", "population": 50},
            ],
            transportation=[{"type": "ambulance", "count": 5}],
            receiving_facilities=[
                {"name": "Regional Hospital", "type": "hospital", "available_capacity": 200},
            ],
        )
        assert result["total_facilities"] == 2
        assert result["total_population"] == 150
        assert len(result["facility_plans"]) == 2
