"""Tests for search and rescue module."""

import pytest
from geo_infer_emergency.core.sar import (
    SearchAndRescue,
    SearchPattern,
    SubjectType,
    SearchSubject,
    SearchTeam,
    SearchArea,
)


class TestSARDataclasses:
    """Tests for SAR dataclass and enum creation."""

    def test_search_pattern_values(self) -> None:
        assert SearchPattern.EXPANDING_SQUARE.value == "expanding_square"
        assert SearchPattern.PARALLEL.value == "parallel"
        assert SearchPattern.SECTOR.value == "sector"

    def test_subject_type_values(self) -> None:
        assert SubjectType.HIKER.value == "hiker"
        assert SubjectType.CHILD.value == "child"
        assert SubjectType.DEMENTIA.value == "dementia"

    def test_search_subject_creation(self) -> None:
        subject = SearchSubject(
            subject_id="sub1",
            subject_type=SubjectType.HIKER,
            name="John Doe",
            age=35,
        )
        assert subject.name == "John Doe"
        assert subject.experience_level == "unknown"

    def test_search_team_creation(self) -> None:
        team = SearchTeam(
            team_id="t1",
            name="Alpha Team",
            size=6,
            capabilities=["ground", "k9"],
        )
        assert team.size == 6
        assert team.status == "available"

    def test_search_area_creation(self) -> None:
        area = SearchArea(area_id="a1", geometry={}, probability=0.7)
        assert area.probability == 0.7
        assert area.searched is False


class TestSearchAndRescueInit:
    """Tests for SearchAndRescue initialization."""

    def test_default_initialization(self) -> None:
        sar = SearchAndRescue()
        assert sar is not None
        assert "ground" in sar.team_capabilities
        assert "k9" in sar.team_capabilities

    def test_register_subject(self) -> None:
        sar = SearchAndRescue()
        subject = sar.register_subject({
            "id": "sub1",
            "type": "hiker",
            "name": "Jane Smith",
            "age": 28,
            "experience": "intermediate",
        })
        assert subject.name == "Jane Smith"
        assert subject.subject_type == SubjectType.HIKER
        assert subject.age == 28

    def test_register_team(self) -> None:
        sar = SearchAndRescue()
        team = sar.register_team({
            "id": "t1",
            "name": "Bravo",
            "size": 4,
            "capabilities": ["ground"],
        })
        assert team.team_id == "t1"
        assert team.size == 4


class TestMissionPlanning:
    """Tests for SAR mission planning."""

    def test_plan_mission(self) -> None:
        sar = SearchAndRescue()
        mission = sar.plan_mission(
            subject={"type": "hiker", "name": "Lost Hiker", "age": 45},
            last_known_point={"lat": 36.5, "lon": -118.8},
            terrain_type="difficult",
        )
        assert "mission_id" in mission
        assert mission["status"] == "planned"
        assert mission["last_known_point"]["lat"] == 36.5
        assert mission["search_radius_km"] == 10.0  # Hiker default
        assert "resource_estimate" in mission

    def test_plan_mission_child(self) -> None:
        sar = SearchAndRescue()
        mission = sar.plan_mission(
            subject={"type": "child", "name": "Missing Child", "age": 6},
            last_known_point={"lat": 34.0, "lon": -118.0},
        )
        assert mission["search_radius_km"] == 2.0  # Child default

    def test_plan_mission_custom_radius(self) -> None:
        sar = SearchAndRescue()
        mission = sar.plan_mission(
            subject={"type": "hiker", "name": "Hiker"},
            last_known_point={"lat": 34.0, "lon": -118.0},
            search_radius=3.0,
        )
        assert mission["search_radius_km"] == 3.0


class TestProbabilityOfDetection:
    """Tests for POD calculations."""

    def test_calculate_pod(self) -> None:
        sar = SearchAndRescue()
        result = sar.calculate_pod(
            subject={"type": "hiker"},
            search_area={"center": {"lat": 34.0, "lon": -118.0}, "radius_km": 5},
            search_effort=1.0,
            terrain_coverable="moderate",
        )
        assert "pod" in result
        assert 0 < result["pod"] < 1
        assert result["coverage_factor"] == 0.7
        assert len(result["areas"]) == 4

    def test_pod_easy_terrain_higher(self) -> None:
        sar = SearchAndRescue()
        easy = sar.calculate_pod(
            subject={}, search_area={"center": {"lat": 0, "lon": 0}, "radius_km": 1},
            search_effort=1.0, terrain_coverable="easy",
        )
        hard = sar.calculate_pod(
            subject={}, search_area={"center": {"lat": 0, "lon": 0}, "radius_km": 1},
            search_effort=1.0, terrain_coverable="difficult",
        )
        assert easy["pod"] > hard["pod"]


class TestSearchPatterns:
    """Tests for search pattern generation."""

    def test_expanding_square_pattern(self) -> None:
        sar = SearchAndRescue()
        pattern = sar.generate_pattern(
            area={"center": {"lat": 34.0, "lon": -118.0}, "radius_km": 1},
            pattern_type="expanding_square",
            team_size=4,
            visibility_distance=50,
        )
        assert pattern["pattern_type"] == "expanding_square"
        assert len(pattern["waypoints"]) > 0
        assert pattern["estimated_search_time_hours"] > 0

    def test_parallel_pattern(self) -> None:
        sar = SearchAndRescue()
        pattern = sar.generate_pattern(
            area={"center": {"lat": 34.0, "lon": -118.0}, "radius_km": 1},
            pattern_type="parallel",
        )
        assert pattern["pattern_type"] == "parallel"
        assert len(pattern["waypoints"]) > 0

    def test_sector_pattern(self) -> None:
        sar = SearchAndRescue()
        pattern = sar.generate_pattern(
            area={"center": {"lat": 34.0, "lon": -118.0}, "radius_km": 1},
            pattern_type="sector",
        )
        assert pattern["pattern_type"] == "sector"
        # Sector: center + 8 sectors * (edge + return) = 17 waypoints
        assert len(pattern["waypoints"]) == 17


class TestTeamCoordination:
    """Tests for team coordination."""

    def test_coordinate_teams(self) -> None:
        sar = SearchAndRescue()
        result = sar.coordinate_teams(
            teams=[
                {"id": "t1", "name": "Alpha", "size": 4, "capabilities": ["ground"]},
                {"id": "t2", "name": "Bravo", "size": 3, "capabilities": ["k9"]},
            ],
            search_areas=[
                {"id": "a1", "priority": 1, "probability": 0.6},
                {"id": "a2", "priority": 2, "probability": 0.3},
            ],
            assignments={"t1": "a1", "t2": "a2"},
        )
        assert len(result["teams"]) == 2
        assert len(result["assignments"]) == 2
        assert "communication_plan" in result
        assert "safety" in result


class TestProbabilityUpdate:
    """Tests for Bayesian probability updating."""

    def test_negative_search_reduces_probability(self) -> None:
        sar = SearchAndRescue()
        sar._search_areas["a1"] = SearchArea(area_id="a1", geometry={}, probability=0.5)
        result = sar.update_probability("a1", "negative")
        assert result["updated_probability"] < result["previous_probability"]

    def test_clue_found_increases_probability(self) -> None:
        sar = SearchAndRescue()
        sar._search_areas["a1"] = SearchArea(area_id="a1", geometry={}, probability=0.3)
        result = sar.update_probability("a1", "clue_found")
        assert result["updated_probability"] > result["previous_probability"]

    def test_subject_found_sets_probability_one(self) -> None:
        sar = SearchAndRescue()
        sar._search_areas["a1"] = SearchArea(area_id="a1", geometry={}, probability=0.5)
        result = sar.update_probability("a1", "subject_found")
        assert result["updated_probability"] == 1.0

    def test_update_creates_area_if_missing(self) -> None:
        sar = SearchAndRescue()
        result = sar.update_probability("new_area", "negative")
        assert result["area_id"] == "new_area"
