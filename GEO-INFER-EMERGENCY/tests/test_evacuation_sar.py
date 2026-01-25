"""
Unit tests for EvacuationPlanner, SituationalAwareness, and SearchAndRescue.
"""

import pytest
from datetime import datetime
from geo_infer_emergency.core.evacuation import (
    EvacuationPlanner,
    EvacuationZone,
    Shelter,
    EvacuationLevel
)
from geo_infer_emergency.core.awareness import (
    SituationalAwareness,
    ThreatLevel,
    DataSource
)
from geo_infer_emergency.core.sar import (
    SearchAndRescue,
    SearchPattern,
    SubjectType
)


class TestEvacuationPlanner:
    """Test suite for EvacuationPlanner class."""
    
    @pytest.fixture
    def planner(self):
        """Create an EvacuationPlanner instance."""
        return EvacuationPlanner(
            shelters=[
                {"id": "shelter_1", "name": "Community Center", "capacity": 500, "location": {"lat": 34.0, "lon": -118.0}}
            ]
        )
    
    def test_init_default(self):
        """Test default initialization."""
        planner = EvacuationPlanner()
        assert "hospitals" in planner.special_needs
    
    def test_register_shelter(self, planner):
        """Test registering a shelter."""
        shelter = planner.register_shelter({
            "id": "shelter_2",
            "name": "High School",
            "capacity": 1000,
            "location": {"lat": 34.1, "lon": -118.1}
        })
        
        assert shelter.shelter_id == "shelter_2"
        assert shelter.capacity == 1000
    
    def test_plan_evacuation(self, planner):
        """Test creating an evacuation plan."""
        result = planner.plan(
            affected_zone={
                "id": "zone_1",
                "name": "Coastal Zone",
                "geometry": {},
                "level": "order"
            },
            population={"total": 10000, "special_populations": ["hospitals"]},
            destinations=[
                {"id": "shelter_1", "name": "Community Center", "capacity": 500, "location": {"lat": 34.0, "lon": -118.0}}
            ],
            phasing="staged",
            contraflow=False
        )
        
        assert result["affected_zone"]["population"] == 10000
        assert result["phasing"]["strategy"] == "staged"
        assert len(result["phasing"]["phases"]) > 0
    
    def test_optimize_routes(self, planner):
        """Test evacuation route optimization."""
        result = planner.optimize_routes(
            origins=["zone_1"],
            destinations=["shelter_1"],
            objectives=["clearance_time", "safety"],
            constraints={"road_capacity": True}
        )
        
        assert len(result["routes"]) == 1
        assert result["routes"][0]["origin"] == "zone_1"
    
    def test_plan_shelters(self, planner):
        """Test shelter planning."""
        result = planner.plan_shelters(
            shelter_locations=[
                {"id": "s1", "name": "Shelter 1", "capacity": 500, "location": {}},
                {"id": "s2", "name": "Shelter 2", "capacity": 300, "location": {}}
            ],
            population_estimate=600,
            duration_days=3,
            services=["food", "medical", "pet_friendly"]
        )
        
        assert result["total_shelter_capacity"] >= 800
        assert result["capacity_sufficient"] is True
        assert "cots" in result["resource_requirements"]
    
    def test_plan_special_populations(self, planner):
        """Test special populations planning."""
        result = planner.plan_special_populations(
            facilities=[
                {"id": "hosp_1", "name": "City Hospital", "type": "hospital", "population": 200}
            ],
            transportation=[{"id": "amb_1", "type": "ambulance"}],
            receiving_facilities=[
                {"id": "region_hosp", "type": "hospital", "available_capacity": 300}
            ],
            medical_support=True
        )
        
        assert result["total_facilities"] == 1
        assert result["total_population"] == 200
        assert result["facility_plans"][0]["priority"] == "high"
    
    def test_estimate_clearance_time(self, planner):
        """Test clearance time estimation."""
        # Create a simple zone
        zone = {"population": 10000}
        
        result = planner.estimate_clearance_time(
            evacuation_plan={"zone": zone, "routes": []},
            traffic_model="dynamic_assignment",
            scenarios=["expected"]
        )
        
        assert "expected" in result
        assert result["expected"]["clearance_hours"] > 0


class TestSituationalAwareness:
    """Test suite for SituationalAwareness class."""
    
    @pytest.fixture
    def awareness(self):
        """Create a SituationalAwareness instance."""
        return SituationalAwareness(
            data_sources=["sensors", "field_reports"],
            fusion_algorithms=["kalman"],
            update_interval=30
        )
    
    def test_init_default(self):
        """Test default initialization."""
        sa = SituationalAwareness()
        assert "sensors" in sa.data_sources
    
    def test_integrate_sensors(self, awareness):
        """Test sensor integration."""
        result = awareness.integrate_sensors(
            sensor_network={
                "sensors": [
                    {"id": "sensor_1", "type": "smoke", "location": {"lat": 34.0, "lon": -118.0}, "readings": {"smoke_level": 0.3}},
                    {"id": "sensor_2", "type": "temperature", "location": {"lat": 34.1, "lon": -118.1}, "readings": {"temp": 85}}
                ]
            },
            data_types=["smoke", "temperature"],
            sampling_rate="continuous"
        )
        
        assert result["sensor_count"] == 2
        assert result["integration_status"] == "active"
    
    def test_build_cop(self, awareness):
        """Test building common operating picture."""
        result = awareness.build_cop(
            layers=[
                {"id": "incidents", "name": "Active Incidents", "source": "cad", "type": "point"},
                {"id": "resources", "name": "Resources", "source": "avl", "type": "point"}
            ],
            extent={"min_lat": 33.5, "max_lat": 34.5, "min_lon": -118.5, "max_lon": -117.5},
            symbology={"point": {"size": 10, "color": "red"}},
            refresh_rate=30
        )
        
        assert len(result["layers"]) == 2
        assert result["status"] == "active"
    
    def test_assess_threat(self, awareness):
        """Test threat assessment."""
        result = awareness.assess_threat(
            hazard={"type": "wildfire", "intensity": 0.8, "speed": 20, "direction": "NE"},
            affected_area={"area_sq_km": 100, "geometry": {}},
            assets_at_risk=[
                {"name": "Town A", "population": 5000, "critical": False},
                {"name": "Hospital", "population": 200, "critical": True}
            ],
            projection_hours=24
        )
        
        assert result["threat_level"] in ["low", "moderate", "high", "extreme", "catastrophic"]
        assert result["threat_score"] >= 0
        assert "recommendations" in result
    
    def test_fuse_data(self, awareness):
        """Test data fusion."""
        result = awareness.fuse_data(
            sources=[
                {"id": "src_1", "confidence": 0.9, "data": {"temperature": 80, "wind_speed": 15}},
                {"id": "src_2", "confidence": 0.7, "data": {"temperature": 85, "humidity": 30}}
            ],
            fusion_method="weighted_average",
            confidence_weighting=True
        )
        
        assert result["source_count"] == 2
        assert "temperature" in result["fused_data"]
    
    def test_generate_dashboard(self, awareness):
        """Test dashboard generation."""
        result = awareness.generate_dashboard(
            widgets=[
                {"id": "w1", "type": "map", "title": "Situation Map"},
                {"id": "w2", "type": "chart", "title": "Resource Status"}
            ],
            layout="standard",
            update_frequency=30
        )
        
        assert len(result["widgets"]) == 2
        assert result["status"] == "active"
    
    def test_get_current_threat_level(self, awareness):
        """Test getting current threat level."""
        level = awareness.get_current_threat_level()
        assert level in ["low", "moderate", "high", "extreme", "catastrophic"]


class TestSearchAndRescue:
    """Test suite for SearchAndRescue class."""
    
    @pytest.fixture
    def sar(self):
        """Create a SearchAndRescue instance."""
        return SearchAndRescue(
            team_capabilities=["ground", "k9", "aerial"]
        )
    
    def test_init_default(self):
        """Test default initialization."""
        sar = SearchAndRescue()
        assert "ground" in sar.team_capabilities
    
    def test_plan_mission(self, sar):
        """Test SAR mission planning."""
        result = sar.plan_mission(
            subject={"id": "sub_1", "name": "John Doe", "type": "hiker", "age": 35},
            last_known_point={"lat": 34.0, "lon": -118.0},
            search_radius=5.0,
            terrain_type="mountainous",
            weather={"conditions": "clear", "temperature": 70}
        )
        
        assert result["subject"]["name"] == "John Doe"
        assert result["search_radius_km"] == 5.0
        assert "probability_areas" in result
        assert "resource_estimate" in result
    
    def test_calculate_pod(self, sar):
        """Test probability of detection calculation."""
        result = sar.calculate_pod(
            subject={"type": "hiker"},
            search_area={"center": {"lat": 34.0, "lon": -118.0}, "radius_km": 5},
            search_effort=1.0,
            terrain_coverable="moderate"
        )
        
        assert 0 <= result["pod"] <= 1
        assert len(result["areas"]) > 0
    
    def test_generate_pattern(self, sar):
        """Test search pattern generation."""
        patterns = ["expanding_square", "parallel", "sector"]
        
        for pattern_type in patterns:
            result = sar.generate_pattern(
                area={"center": {"lat": 34.0, "lon": -118.0}, "radius_km": 2},
                pattern_type=pattern_type,
                team_size=4,
                visibility_distance=50
            )
            
            assert result["pattern_type"] == pattern_type
            assert len(result["waypoints"]) > 0
    
    def test_coordinate_teams(self, sar):
        """Test team coordination."""
        result = sar.coordinate_teams(
            teams=[
                {"id": "team_1", "name": "Alpha Team", "size": 4, "capabilities": ["ground"]},
                {"id": "team_2", "name": "K9 Team", "size": 3, "capabilities": ["k9"]}
            ],
            search_areas=[
                {"id": "area_1", "priority": 1, "probability": 0.6},
                {"id": "area_2", "priority": 2, "probability": 0.3}
            ],
            assignments={"team_1": "area_1", "team_2": "area_2"},
            briefing_time=datetime.now()
        )
        
        assert len(result["teams"]) == 2
        assert len(result["assignments"]) == 2
        assert "communication_plan" in result
    
    def test_update_probability(self, sar):
        """Test probability update after search."""
        # First, set up an initial area
        result = sar.update_probability(
            area_id="area_1",
            search_result="negative",
            new_information=None
        )
        
        assert result["area_id"] == "area_1"
        assert result["search_result"] == "negative"
        assert result["searched"] is True
        # After negative search, probability should decrease
        assert result["updated_probability"] < result["previous_probability"]
    
    def test_register_subject(self, sar):
        """Test registering a search subject."""
        subject = sar.register_subject({
            "id": "sub_1",
            "name": "Jane Doe",
            "type": "child",
            "age": 8,
            "clothing": "Red jacket, blue jeans"
        })
        
        assert subject.subject_id == "sub_1"
        assert subject.subject_type == SubjectType.CHILD
    
    def test_register_team(self, sar):
        """Test registering a search team."""
        team = sar.register_team({
            "id": "team_alpha",
            "name": "Alpha Team",
            "size": 6,
            "capabilities": ["ground", "technical_rescue"]
        })
        
        assert team.team_id == "team_alpha"
        assert team.size == 6


class TestEvacuationZone:
    """Test suite for EvacuationZone dataclass."""
    
    def test_create_zone(self):
        """Test creating an evacuation zone."""
        zone = EvacuationZone(
            zone_id="zone_1",
            name="Coastal Evacuation Zone",
            geometry={},
            population=50000,
            level=EvacuationLevel.ORDER
        )
        
        assert zone.zone_id == "zone_1"
        assert zone.population == 50000


class TestThreatLevel:
    """Test suite for ThreatLevel enum."""
    
    def test_threat_levels(self):
        """Test all threat levels exist."""
        levels = [
            ThreatLevel.LOW,
            ThreatLevel.MODERATE,
            ThreatLevel.HIGH,
            ThreatLevel.EXTREME,
            ThreatLevel.CATASTROPHIC
        ]
        
        assert len(levels) == 5
        assert ThreatLevel.LOW.value == "low"
