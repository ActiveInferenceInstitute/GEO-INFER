"""
Integration tests for the full GEO-INFER-APP agent pipeline.

Covers: configuration → factory → interface → visualization → API,
verifying that the components work together end-to-end.
"""

import math
import pytest

from geo_infer_app.models.agent_interface import AgentState, AgentType
from geo_infer_app.models.agent_factory import AgentFactory
from geo_infer_app.models.agent_configuration import AgentConfiguration
from geo_infer_app.models.agent_visualization import AgentVisualization
from geo_infer_app.models.interfaces.bdi_interface import BDIAgentInterface
from geo_infer_app.api.agent_api import AgentAPIClient, AgentManager


# ---------------------------------------------------------------------------
# Configuration → Interface pipeline
# ---------------------------------------------------------------------------

class TestConfigurationToInterface:
    """Schema config drives BDI interface creation and agent lifecycle."""

    def test_default_config_drives_agent_creation(self) -> None:
        defaults = AgentConfiguration.get_default_config(AgentType.BDI)
        # Defaults include spatial parameters
        assert "movement_speed" in defaults
        assert defaults["movement_speed"] == 1.0

        interface = BDIAgentInterface()
        agent_id = interface.create_agent(AgentType.BDI, {
            "name": "IntegrationBot",
            "beliefs": {"temperature": 20},
            "desires": ["patrol"],
            "initial_location": {"lat": 51.5, "lng": -0.1},
        })
        state = interface.get_agent_state(agent_id)
        assert state.agent_type == AgentType.BDI
        assert state.beliefs["temperature"] == 20
        assert state.goals == ["patrol"]

    def test_schema_validation_then_create(self) -> None:
        config = {
            "name": "ValidBot",
            "beliefs": {"wind": "low"},
            "desires": ["monitor"],
        }
        errors = AgentConfiguration.validate_config(AgentType.BDI, config)
        assert errors == [], f"Unexpected validation errors: {errors}"

        interface = BDIAgentInterface()
        agent_id = interface.create_agent(AgentType.BDI, config)
        assert agent_id is not None

    def test_invalid_config_produces_errors(self) -> None:
        errors = AgentConfiguration.validate_config(AgentType.BDI, {
            "name": 42,  # must be string
        })
        assert any("string" in e for e in errors)


# ---------------------------------------------------------------------------
# Factory → Interface lifecycle
# ---------------------------------------------------------------------------

class TestFactoryInterfaceLifecycle:
    """AgentFactory creates the right interface; interface manages full lifecycle."""

    def test_factory_creates_bdi_interface(self) -> None:
        interface = AgentFactory.create_interface(AgentType.BDI)
        assert isinstance(interface, BDIAgentInterface)

    def test_full_bdi_lifecycle(self) -> None:
        interface = BDIAgentInterface()

        agent_id = interface.create_agent(AgentType.BDI, {
            "name": "LifecycleBot",
            "beliefs": {"fuel": 100},
            "desires": ["explore"],
            "initial_location": {"lat": 40.7128, "lng": -74.0060},
        })

        # Add belief and desire
        interface.send_command(agent_id, "add_belief", {"belief": {"obstacle": True}})
        interface.send_command(agent_id, "add_desire", {"desire": "avoid_obstacle"})

        # Deliberate → intention formed
        interface.send_command(agent_id, "deliberate", {})
        state = interface.get_agent_state(agent_id)
        assert "explore" in state.metadata["intentions"] or "avoid_obstacle" in state.metadata["intentions"]

        # Execute → intention consumed
        interface.send_command(agent_id, "execute", {})

        # Move
        new_loc = {"lat": 40.72, "lng": -74.01}
        interface.send_command(agent_id, "move", {"location": new_loc})
        state = interface.get_agent_state(agent_id)
        assert state.location == new_loc

    def test_multiple_agents_independent(self) -> None:
        interface = BDIAgentInterface()
        id_a = interface.create_agent(AgentType.BDI, {"name": "A"})
        id_b = interface.create_agent(AgentType.BDI, {"name": "B"})
        assert id_a != id_b

        interface.send_command(id_a, "add_belief", {"belief": {"x": 1}})
        state_a = interface.get_agent_state(id_a)
        state_b = interface.get_agent_state(id_b)
        assert "x" in state_a.beliefs
        assert state_b.beliefs == {} or "x" not in state_b.beliefs


# ---------------------------------------------------------------------------
# Interface → Visualization pipeline
# ---------------------------------------------------------------------------

class TestInterfaceToVisualization:
    """Agent states from the interface produce valid visualization artefacts."""

    def test_bdi_state_to_map_feature(self) -> None:
        interface = BDIAgentInterface()
        agent_id = interface.create_agent(AgentType.BDI, {
            "name": "MapBot",
            "initial_location": {"lat": 48.8566, "lng": 2.3522},
        })
        state = interface.get_agent_state(agent_id)
        feature = AgentVisualization.state_to_map_feature(state)

        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        coords = feature["geometry"]["coordinates"]
        assert coords[0] == pytest.approx(2.3522)  # lng first (GeoJSON)
        assert coords[1] == pytest.approx(48.8566)
        assert feature["properties"]["id"] == agent_id
        assert feature["properties"]["color"] == "#e74c3c"  # BDI colour

    def test_bdi_state_to_dashboard(self) -> None:
        interface = BDIAgentInterface()
        agent_id = interface.create_agent(AgentType.BDI, {
            "name": "DashBot",
            "beliefs": {"sensor": "active"},
            "desires": ["report"],
            "initial_location": {"lat": 0.0, "lng": 0.0},
        })
        interface.send_command(agent_id, "deliberate", {})
        state = interface.get_agent_state(agent_id)
        data = AgentVisualization.state_to_dashboard_data(state)

        assert data["id"] == agent_id
        assert "widgets" in data
        assert "status" in data["widgets"]
        assert "beliefs" in data["widgets"]
        assert "intentions" in data["widgets"]


# ---------------------------------------------------------------------------
# Haversine distance correctness
# ---------------------------------------------------------------------------

class TestHaversineDistance:
    """_is_location_in_radius uses real haversine, not Euclidean approximation."""

    def test_nearby_points_within_radius(self) -> None:
        interface = BDIAgentInterface()
        # London ~0 km from itself
        loc = {"lat": 51.5074, "lng": -0.1278}
        assert interface._is_location_in_radius(loc, loc, 1.0) is True

    def test_distant_points_outside_radius(self) -> None:
        interface = BDIAgentInterface()
        london = {"lat": 51.5074, "lng": -0.1278}
        paris = {"lat": 48.8566, "lng": 2.3522}
        # London–Paris ~340 km — not within 10 km
        assert interface._is_location_in_radius(london, paris, 10.0) is False

    def test_known_distance_threshold(self) -> None:
        """1 degree of latitude ≈ 111 km — a 200 km radius should include it."""
        interface = BDIAgentInterface()
        base = {"lat": 0.0, "lng": 0.0}
        one_degree_north = {"lat": 1.0, "lng": 0.0}
        assert interface._is_location_in_radius(one_degree_north, base, 200.0) is True
        assert interface._is_location_in_radius(one_degree_north, base, 50.0) is False

    def test_zero_radius_always_false(self) -> None:
        interface = BDIAgentInterface()
        loc = {"lat": 10.0, "lng": 10.0}
        assert interface._is_location_in_radius(loc, loc, 0.0) is False

    def test_none_inputs_return_false(self) -> None:
        interface = BDIAgentInterface()
        assert interface._is_location_in_radius(None, {"lat": 0.0, "lng": 0.0}, 10.0) is False
        assert interface._is_location_in_radius({"lat": 0.0, "lng": 0.0}, None, 10.0) is False


# ---------------------------------------------------------------------------
# Async API pipeline
# ---------------------------------------------------------------------------

class TestAsyncAPIPipeline:
    """Full async create → start → command → metrics → stop → delete cycle."""

    @pytest.mark.asyncio
    async def test_complete_agent_lifecycle(self) -> None:
        client = AgentAPIClient(config={"agents_config_path": "/tmp/test_pipeline_agents.json"})

        agent_id = await client.create_agent("bdi", {"name": "PipelineBot"})
        assert agent_id  # non-empty UUID string

        started = await client.start_agent(agent_id)
        assert started is True

        # Send several commands
        for _ in range(3):
            result = await client.send_command(agent_id, {"command_type": "query"})
            assert result is not None
            assert result["status"] == "success"

        metrics = await client.get_agent_metrics(agent_id)
        assert metrics is not None
        assert metrics["decision_count"] == 3
        assert metrics["success_rate"] == 1.0
        assert metrics["uptime_seconds"] >= 0

        stopped = await client.stop_agent(agent_id)
        assert stopped is True
        status = await client.get_agent_status(agent_id)
        assert status["status"] == "stopped"

        deleted = await client.delete_agent(agent_id)
        assert deleted is True
        assert await client.get_agent_status(agent_id) is None

    @pytest.mark.asyncio
    async def test_update_command_persists(self) -> None:
        client = AgentAPIClient(config={"agents_config_path": "/tmp/test_pipeline_update.json"})
        agent_id = await client.create_agent("rl", {"name": "UpdateBot"})
        await client.start_agent(agent_id)

        result = await client.send_command(agent_id, {
            "command_type": "update",
            "parameters": {"config": {"learning_rate": 0.05}},
        })
        assert result["status"] == "success"

        status = await client.get_agent_status(agent_id)
        assert status["config"]["learning_rate"] == 0.05

    @pytest.mark.asyncio
    async def test_manager_full_lifecycle(self) -> None:
        manager = AgentManager(config={
            "api_config": {"agents_config_path": "/tmp/test_manager_pipeline.json"}
        })

        agent_id = await manager.create_agent("bdi", "ManagerBot", {})
        await manager.start_agent(agent_id)
        assert agent_id in manager.active_agents

        result = await manager.send_command(agent_id, "query")
        assert result is not None
        assert result["status"] == "success"

        metrics = await manager.get_agent_metrics(agent_id)
        assert metrics["decision_count"] >= 1

        await manager.stop_agent(agent_id)
        assert agent_id not in manager.active_agents
