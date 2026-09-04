"""
DOMAIN-02 Acceptance tests for GEO-INFER-EMERGENCY documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. SearchAndRescue — mission planning, probability of detection (POD),
   search pattern generation, subject/team registration.
2. EmergencyCoordinator — ICS coordination, incident command establishment,
   situation reports (SITREP), mutual aid requests.
3. EvacuationPlanner — evacuation planning, route optimization, clearance
   time estimation, shelter planning.
4. SituationalAwareness — sensor integration, COP building, threat assessment,
   data fusion.
5. ResourceDeployer — resource allocation optimization, dynamic redeployment,
   resource tracking.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import pytest

from geo_infer_emergency.core.sar import (
    SearchAndRescue,
    SearchPattern,
    SubjectType,
    SearchSubject,
    SearchTeam,
)
from geo_infer_emergency.core.coordinator import (
    EmergencyCoordinator,
    IncidentType,
    IncidentScale,
    Agency,
    IncidentCommand,
)
from geo_infer_emergency.core.evacuation import (
    EvacuationPlanner,
    EvacuationLevel,
    EvacuationZone,
    Shelter,
)
from geo_infer_emergency.core.awareness import (
    SituationalAwareness,
    ThreatLevel,
    DataSource,
)
from geo_infer_emergency.core.resources import (
    ResourceDeployer,
    ResourceStatus,
    ResourceType,
    Resource,
)


# ---------------------------------------------------------------------------
# SearchAndRescue
# ---------------------------------------------------------------------------

class TestSearchAndRescue:
    """Acceptance: SAR mission planning and probability modeling."""

    @pytest.fixture
    def sar(self) -> SearchAndRescue:
        return SearchAndRescue()

    def test_register_subject(self, sar):
        """register_subject creates a SearchSubject with correct type."""
        subject = sar.register_subject({
            "id": "s1",
            "name": "John Doe",
            "type": "hiker",
            "age": 35,
        })
        assert subject.subject_id == "s1"
        assert subject.subject_type == SubjectType.HIKER
        assert subject.name == "John Doe"
        assert "s1" in sar._subjects

    def test_register_team(self, sar):
        """register_team creates a SearchTeam with capabilities."""
        team = sar.register_team({
            "id": "t1",
            "name": "Alpha Team",
            "size": 6,
            "capabilities": ["ground", "k9"],
        })
        assert team.team_id == "t1"
        assert team.size == 6
        assert "k9" in team.capabilities
        assert "t1" in sar._teams

    def test_plan_mission(self, sar):
        """plan_mission creates a complete SAR mission plan."""
        mission = sar.plan_mission(
            subject={"id": "s2", "name": "Jane", "type": "child"},
            last_known_point={"lat": 45.5, "lon": -122.6},
            search_radius=3.0,
            terrain_type="forest",
        )
        assert mission["subject"]["type"] == "child"
        assert mission["search_radius_km"] == 3.0
        assert len(mission["probability_areas"]) > 0
        assert "recommended_pattern" in mission
        assert mission["status"] == "planned"
        assert mission["resource_estimate"]["ground_teams"] >= 1

    def test_calculate_pod(self, sar):
        """calculate_pod uses exponential model POD = 1 - e^(-coverage*effort)."""
        result = sar.calculate_pod(
            subject={"type": "hiker"},
            search_area={"center": {"lat": 45, "lon": -122}, "radius_km": 5},
            search_effort=1.0,
            terrain_coverable="moderate",
        )
        assert result["pod"] > 0  # moderate terrain, effort 1.0
        assert result["pod"] < 1.0
        assert result["coverage_factor"] == 0.7  # moderate terrain
        assert len(result["areas"]) == 4  # concentric rings
        assert result["total_area_sq_km"] > 0

    def test_pod_terrain_affects_detection(self, sar):
        """Easy terrain yields higher POD than extreme terrain."""
        easy = sar.calculate_pod(
            subject={"type": "hiker"},
            search_area={"center": {"lat": 0, "lon": 0}, "radius_km": 5},
            search_effort=1.0,
            terrain_coverable="easy",
        )
        extreme = sar.calculate_pod(
            subject={"type": "hiker"},
            search_area={"center": {"lat": 0, "lon": 0}, "radius_km": 5},
            search_effort=1.0,
            terrain_coverable="extreme",
        )
        assert easy["pod"] > extreme["pod"]

    def test_generate_pattern_expanding_square(self, sar):
        """generate_pattern produces expanding square waypoints."""
        pattern = sar.generate_pattern(
            area={"center": {"lat": 45.0, "lon": -122.0}, "radius_km": 1.0},
            pattern_type="expanding_square",
            team_size=4,
            visibility_distance=50,
        )
        assert pattern["pattern_type"] == "expanding_square"
        assert len(pattern["waypoints"]) > 1
        assert pattern["estimated_distance_km"] > 0
        assert pattern["estimated_search_time_hours"] > 0
        assert pattern["track_spacing_m"] == 100  # 2 × visibility

    def test_generate_pattern_sector(self, sar):
        """Sector search pattern generates radial waypoints."""
        pattern = sar.generate_pattern(
            area={"center": {"lat": 45.0, "lon": -122.0}, "radius_km": 0.5},
            pattern_type="sector",
            team_size=2,
        )
        assert len(pattern["waypoints"]) > 2
        # Sector pattern returns to center between each sector
        assert pattern["waypoints"][0] == {"lat": 45.0, "lon": -122.0}

    def test_search_radius_by_subject_type(self, sar):
        """Different subject types have different search radii."""
        assert sar.SEARCH_RADIUS[SubjectType.CHILD] == 2.0
        assert sar.SEARCH_RADIUS[SubjectType.HIKER] == 10.0


# ---------------------------------------------------------------------------
# EmergencyCoordinator
# ---------------------------------------------------------------------------

class TestEmergencyCoordinator:
    """Acceptance: ICS coordination and situation reporting."""

    @pytest.fixture
    def coordinator(self) -> EmergencyCoordinator:
        return EmergencyCoordinator(
            command_structure="ics",
            agencies=["fire", "police", "medical"],
        )

    def test_init_registers_agencies(self, coordinator):
        """__init__ registers provided agencies."""
        assert len(coordinator.agencies) == 3
        assert "agency_fire" in coordinator.agencies
        assert "agency_police" in coordinator.agencies
        assert "agency_medical" in coordinator.agencies

    def test_coordinate(self, coordinator):
        """coordinate creates an incident and returns a coordination plan."""
        plan = coordinator.coordinate(
            incident={"id": "inc1", "type": "wildfire", "name": "Hill Fire", "scale": "type_3"},
            agencies=["agency_fire", "agency_police"],
            resources={"engines": ["e1", "e2"], "patrol_units": ["p1"]},
        )
        assert plan["incident_id"] == "inc1"
        assert plan["command_structure"] == "ics"
        assert len(plan["responding_agencies"]) == 2
        assert "communication_channels" in plan
        assert len(plan["resource_assignments"]) == 2
        # Fire agency gets engines
        fire_assignment = [a for a in plan["resource_assignments"] if a["agency"] == "agency_fire"][0]
        assert any(r["type"] == "engines" for r in fire_assignment["resources"])

    def test_establish_command(self, coordinator):
        """establish_command creates an ICS command structure."""
        result = coordinator.establish_command(
            incident_type="wildfire",
            location={"lat": 45.5, "lon": -122.6},
            scale="type_2",
            command_structure={
                "incident_commander": "Capt. Smith",
                "operations": "Lt. Jones",
                "planning": "Sgt. Brown",
            },
        )
        assert result["status"] == "established"
        assert result["command_structure"]["incident_commander"] == "Capt. Smith"
        assert result["command_structure"]["operations_section"] == "Lt. Jones"

    def test_generate_sitrep(self, coordinator):
        """generate_sitrep produces an ICS-209 format situation report."""
        sitrep = coordinator.generate_sitrep(
            incident={
                "id": "inc2",
                "name": "Flood Event",
                "status": "active",
                "percent_contained": 25,
                "personnel_count": 50,
                "injuries": 3,
            },
            update_frequency="hourly",
            distribution=["eoc", "state_eoc"],
        )
        assert sitrep["format"] == "ics_209"
        assert sitrep["incident_id"] == "inc2"
        assert sitrep["current_status"]["percent_contained"] == 25
        assert sitrep["resources_committed"]["personnel"] == 50
        assert sitrep["casualties"]["injuries"] == 3
        assert "next_update" in sitrep

    def test_request_mutual_aid(self, coordinator):
        """request_mutual_aid finds partners and creates assignments."""
        request = coordinator.request_mutual_aid(
            requesting_agency="agency_fire",
            resource_needs=["engines"],
            duration_hours=12,
            staging_areas=[{"id": "staging1", "lat": 45.5, "lon": -122.6}],
        )
        assert request["status"] in ["assigned", "pending"]
        assert len(request["potential_providers"]) >= 2  # other agencies
        assert request["duration_hours"] == 12

    def test_get_active_incidents(self, coordinator):
        """get_active_incidents returns registered incidents."""
        coordinator.coordinate(
            incident={"id": "inc3", "type": "flood", "name": "River Flood"},
            agencies=["agency_fire"],
            resources={},
        )
        incidents = coordinator.get_active_incidents()
        assert len(incidents) == 1
        assert incidents[0]["incident_id"] == "inc3"
        assert incidents[0]["type"] == "flood"


# ---------------------------------------------------------------------------
# EvacuationPlanner
# ---------------------------------------------------------------------------

class TestEvacuationPlanner:
    """Acceptance: evacuation planning and shelter management."""

    @pytest.fixture
    def road_network(self):
        """Synthetic road network spanning the zone and shelter nodes used below."""
        import networkx as nx

        graph = nx.DiGraph()
        for origin, destination in [
            ("zone1", "sh1"), ("zone1", "sh2"),
            ("zone2", "sh1"), ("zone2", "sh2"),
            ("zone_a", "shelter_1"), ("zone_a", "shelter_2"),
            ("zone_b", "shelter_1"), ("zone_b", "shelter_2"),
        ]:
            graph.add_edge(origin, destination, distance=8.0, travel_time=12.0, capacity=1500)
        return graph

    @pytest.fixture
    def planner(self, road_network) -> EvacuationPlanner:
        return EvacuationPlanner(road_network=road_network)

    def test_register_shelter(self, planner):
        """register_shelter stores a Shelter."""
        shelter = planner.register_shelter({
            "id": "sh1",
            "name": "High School Gym",
            "location": {"lat": 45.5, "lon": -122.6},
            "capacity": 500,
            "services": ["medical", "food"],
        })
        assert shelter.shelter_id == "sh1"
        assert shelter.capacity == 500
        assert "sh1" in planner._shelters

    def test_plan_creates_evacuation_plan(self, planner):
        """plan() creates a complete evacuation plan with routes and phases."""
        plan = planner.plan(
            affected_zone={"id": "zone1", "name": "Riverside", "geometry": {}, "level": "order"},
            population={"total": 5000, "special_populations": ["hospitals"]},
            destinations=[{"id": "sh1", "name": "Shelter A", "capacity": 2000}],
            phasing="staged",
            contraflow=True,
        )
        assert plan["affected_zone"]["population"] == 5000
        assert plan["affected_zone"]["level"] == "order"
        assert len(plan["routes"]) > 0
        assert plan["phasing"]["strategy"] == "staged"
        assert len(plan["phasing"]["phases"]) == 3
        assert plan["contraflow"]["enabled"] is True
        assert plan["status"] == "planned"

    def test_plan_simultaneous_phasing(self, planner):
        """Simultaneous phasing produces a single phase."""
        plan = planner.plan(
            affected_zone={"id": "zone2", "name": "Downtown"},
            population={"total": 1000},
            destinations=[{"id": "sh2", "name": "Shelter B", "capacity": 1000}],
            phasing="simultaneous",
        )
        assert len(plan["phasing"]["phases"]) == 1
        assert plan["phasing"]["phases"][0]["population_pct"] == 100

    def test_optimize_routes(self, planner):
        """optimize_routes generates routes for each origin-destination pair."""
        result = planner.optimize_routes(
            origins=["zone_a", "zone_b"],
            destinations=["shelter_1", "shelter_2"],
            objectives=["clearance_time", "safety"],
            constraints={"road_capacity": True},
        )
        assert result["total_routes"] == 4  # 2 origins × 2 destinations
        assert len(result["routes"]) == 4
        assert all(r["distance_km"] > 0 for r in result["routes"])

    def test_estimate_clearance_time(self, planner):
        """estimate_clearance_time returns scenario-based estimates."""
        estimates = planner.estimate_clearance_time(
            evacuation_plan={
                "zone": EvacuationZone(
                    zone_id="z1",
                    name="Zone 1",
                    geometry={},
                    population=5000,
                ),
                "routes": [{"capacity_vehicles_per_hour": 2000}],
            },
            traffic_model="dynamic_assignment",
            scenarios=["best_case", "expected", "worst_case"],
        )
        assert "best_case" in estimates
        assert "expected" in estimates
        assert "worst_case" in estimates
        # Worst case > expected > best case
        assert estimates["worst_case"]["clearance_hours"] > estimates["expected"]["clearance_hours"]
        assert estimates["expected"]["clearance_hours"] > estimates["best_case"]["clearance_hours"]

    def test_plan_shelters(self, planner):
        """plan_shelters allocates population across shelters."""
        plan = planner.plan_shelters(
            shelter_locations=[
                {"id": "sh1", "name": "School", "capacity": 500},
                {"id": "sh2", "name": "Church", "capacity": 200},
            ],
            population_estimate=600,
            duration_days=3,
            services=["medical", "food"],
        )
        assert plan["total_shelter_capacity"] == 700
        assert plan["capacity_sufficient"] is True
        assert plan["overflow_population"] == 0
        assert len(plan["shelters"]) == 2
        assert plan["resource_requirements"]["cots"] == 600

    def test_plan_shelters_overflow(self, planner):
        """plan_shelters reports overflow when capacity is insufficient."""
        plan = planner.plan_shelters(
            shelter_locations=[{"id": "sh1", "name": "Small Shelter", "capacity": 100}],
            population_estimate=500,
            duration_days=2,
            services=["food"],
        )
        assert plan["capacity_sufficient"] is False
        assert plan["overflow_population"] == 400


# ---------------------------------------------------------------------------
# SituationalAwareness
# ---------------------------------------------------------------------------

class TestSituationalAwareness:
    """Acceptance: sensor integration, COP, and threat assessment."""

    @pytest.fixture
    def sa(self) -> SituationalAwareness:
        return SituationalAwareness()

    def test_integrate_sensors(self, sa):
        """integrate_sensors registers sensor inputs and returns status."""
        result = sa.integrate_sensors(
            sensor_network={
                "sensors": [
                    {"id": "temp1", "type": "temperature", "location": {"lat": 45, "lon": -122}, "readings": {"temp": 72}},
                    {"id": "wind1", "type": "wind", "location": {"lat": 45.1, "lon": -122.1}, "readings": {"speed": 15}},
                ]
            },
            data_types=["temperature", "wind"],
            sampling_rate="continuous",
        )
        assert result["sensor_count"] == 2
        assert result["integration_status"] == "active"
        assert len(result["sensors"]) == 2
        assert "temp1" in sa._sensor_data

    def test_build_cop(self, sa):
        """build_cop creates a common operating picture with layers."""
        cop = sa.build_cop(
            layers=[
                {"id": "l1", "name": "Hazards", "type": "hazard", "visible": True},
                {"id": "l2", "name": "Resources", "type": "resource"},
            ],
            extent={"min_lat": 45, "max_lat": 46, "min_lon": -123, "max_lon": -122},
            symbology={"hazard": {"color": "red"}},
            refresh_rate=30,
        )
        assert cop["status"] == "active"
        assert len(cop["layers"]) == 2
        assert cop["refresh_rate_seconds"] == 30
        assert "l1" in sa._layers

    def test_assess_threat_low(self, sa):
        """Low-intensity, low-population hazard yields LOW threat level."""
        result = sa.assess_threat(
            hazard={"type": "minor_flood", "intensity": 0.1, "speed": 5},
            affected_area={"area_sq_km": 10},
            assets_at_risk=[{"population": 1000}],
        )
        assert result["threat_level"] == ThreatLevel.LOW.value
        assert result["threat_score"] < 0.2
        assert len(result["recommendations"]) >= 1

    def test_assess_threat_extreme(self, sa):
        """High-intensity, high-population hazard yields high threat level."""
        result = sa.assess_threat(
            hazard={"type": "wildfire", "intensity": 0.9, "speed": 40},
            affected_area={"area_sq_km": 100},
            assets_at_risk=[{"population": 80000, "critical": True}],
        )
        assert result["threat_score"] >= 0.6
        assert result["threat_level"] in [ThreatLevel.EXTREME.value, ThreatLevel.CATASTROPHIC.value]
        assert "Issue evacuation orders" in result["recommendations"] or "Mass evacuation" in result["recommendations"]

    def test_fuse_data_weighted_average(self, sa):
        """fuse_data computes weighted average of numeric fields."""
        fused = sa.fuse_data(
            sources=[
                {"data": {"temp": 70}, "confidence": 0.9},
                {"data": {"temp": 72}, "confidence": 0.6},
            ],
            fusion_method="weighted_average",
        )
        assert fused["fusion_method"] == "weighted_average"
        # Weighted avg: (70*0.9 + 72*0.6) / (0.9 + 0.6) = (63 + 43.2) / 1.5 = 70.8
        assert abs(fused["fused_data"]["temp"] - 70.8) < 0.1

    def test_fuse_data_empty_returns_error(self, sa):
        """fuse_data with no sources returns an error."""
        result = sa.fuse_data(sources=[])
        assert "error" in result

    def test_get_current_threat_level(self, sa):
        """get_current_threat_level returns the current level string."""
        assert sa.get_current_threat_level() == ThreatLevel.LOW.value
        sa.assess_threat(
            hazard={"intensity": 0.5, "speed": 10},
            affected_area={"area_sq_km": 50},
            assets_at_risk=[{"population": 20000}],
        )
        assert sa.get_current_threat_level() != ThreatLevel.LOW.value


# ---------------------------------------------------------------------------
# ResourceDeployer
# ---------------------------------------------------------------------------

class TestResourceDeployer:
    """Acceptance: resource deployment and tracking."""

    @pytest.fixture
    def deployer(self) -> ResourceDeployer:
        return ResourceDeployer()

    def test_register_resource(self, deployer):
        """register_resource stores a Resource."""
        resource = Resource(
            resource_id="r1",
            resource_type=ResourceType.ENGINE,
            name="Engine 1",
            location={"lat": 45.5, "lon": -122.6},
        )
        deployer.register_resource(resource)
        assert "r1" in deployer._resources
        status = deployer.get_resource_status("r1")
        assert status["resource_id"] == "r1"
        assert status["type"] == "engine"

    def test_optimize_allocation(self, deployer):
        """optimize_allocation assigns nearest resources to demand points."""
        result = deployer.optimize_allocation(
            resources=[
                {"id": "r1", "type": "engine", "location": {"lat": 45.5, "lon": -122.6}},
                {"id": "r2", "type": "ambulance", "location": {"lat": 45.4, "lon": -122.7}},
            ],
            demand_points=[
                {"id": "d1", "location": {"lat": 45.51, "lon": -122.61}},
            ],
            constraints={"response_time": 30, "coverage": 0.8},
            objectives=["minimize_time"],
        )
        assert result["metrics"]["total_resources"] == 2
        assert result["metrics"]["demands_covered"] == 1
        assert result["metrics"]["coverage_rate"] == 1.0
        assert len(result["allocations"]) == 1
        assert result["allocations"][0]["estimated_response_time"] < 30

    def test_optimize_allocation_unreachable_demand(self, deployer):
        """Demands beyond response time constraint are left unallocated."""
        result = deployer.optimize_allocation(
            resources=[
                {"id": "r1", "type": "engine", "location": {"lat": 0, "lon": 0}},
            ],
            demand_points=[
                {"id": "d1", "location": {"lat": 40, "lon": 40}},
            ],
            constraints={"response_time": 15},
            objectives=["minimize_time"],
        )
        assert result["metrics"]["demands_covered"] == 0
        assert "d1" in result["unallocated_demands"]

    def test_track_resources(self, deployer):
        """track_resources summarizes status counts."""
        result = deployer.track_resources(
            resources=[
                {"id": "r1", "type": "engine", "status": "available"},
                {"id": "r2", "type": "ambulance", "status": "en_route"},
                {"id": "r3", "type": "truck", "status": "on_scene"},
            ],
        )
        assert result["summary"]["total"] == 3
        assert result["summary"]["available"] == 1
        assert result["summary"]["en_route"] == 1
        assert result["summary"]["on_scene"] == 1
        assert len(result["resources"]) == 3

    def test_dynamic_redeploy(self, deployer):
        """dynamic_redeploy moves available units to coverage gaps."""
        # Register resources first
        deployer.optimize_allocation(
            resources=[
                {"id": "r1", "type": "engine", "location": {"lat": 45.5, "lon": -122.6}, "status": "available"},
                {"id": "r2", "type": "engine", "location": {"lat": 45.4, "lon": -122.7}, "status": "available"},
            ],
            demand_points=[],
            constraints={},
            objectives=[],
        )
        result = deployer.dynamic_redeploy(
            current_positions=[
                {"resource_id": "r1", "location": {"lat": 45.5, "lon": -122.6}},
            ],
            pending_incidents=[{"id": "inc1"}],
            predicted_demand={"high_risk_areas": [{"lat": 45.6, "lon": -122.5}]},
            strategy="move_up",
        )
        assert len(result["redeployments"]) >= 1
        assert result["units_redeployed"] >= 1

    def test_get_resource_status_not_found(self, deployer):
        """get_resource_status returns None for unknown resource."""
        assert deployer.get_resource_status("nonexistent") is None
