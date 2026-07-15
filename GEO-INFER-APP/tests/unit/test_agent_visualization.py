"""Tests for agent visualization utilities."""

import pytest
import json
from geo_infer_app.models.agent_visualization import (
    AgentVisualization,
    VisualizationType,
)
from geo_infer_app.models.agent_interface import AgentState, AgentType


class TestAgentVisualization:
    def test_default_configs(self):
        configs = AgentVisualization.get_default_config(AgentType.BDI)
        assert "map" in configs
        assert "dashboard" in configs
        assert "network" in configs
        assert configs["map"].vis_type == VisualizationType.MAP_MARKER

    def test_bdi_color(self):
        configs = AgentVisualization.get_default_config(AgentType.BDI)
        assert configs["map"].color == "#e74c3c"

    def test_rl_color(self):
        configs = AgentVisualization.get_default_config(AgentType.RL)
        assert configs["map"].color == "#9b59b6"

    def test_state_to_map_feature(self):
        state = AgentState(
            agent_id="a1",
            agent_type=AgentType.BDI,
            status="active",
            location={"lat": 40.7128, "lng": -74.0060},
        )
        feature = AgentVisualization.state_to_map_feature(state)
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert feature["properties"]["id"] == "a1"

    def test_state_to_map_feature_no_location_raises(self):
        state = AgentState(
            agent_id="a2",
            agent_type=AgentType.RL,
            status="idle",
        )
        with pytest.raises(ValueError, match="no location"):
            AgentVisualization.state_to_map_feature(state)

    def test_state_to_map_feature_rejects_invalid_coordinates(self):
        state = AgentState(
            agent_id="a-invalid",
            agent_type=AgentType.RL,
            status="idle",
            location={"lat": 91.0, "lng": 0.0},
        )
        with pytest.raises(ValueError, match="latitude"):
            AgentVisualization.state_to_map_feature(state)

    def test_map_feature_metadata_is_json_safe(self):
        state = AgentState(
            agent_id="a-json",
            agent_type=AgentType.ACTIVE_INFERENCE,
            status="active",
            location={"lat": 40.0, "lng": -124.0},
            metadata={"score": object()},
        )
        feature = AgentVisualization.state_to_map_feature(state)
        json.dumps(feature)

    def test_state_to_dashboard(self):
        state = AgentState(
            agent_id="a3",
            agent_type=AgentType.BDI,
            status="active",
            tasks=[{"name": "explore"}],
            beliefs={"temp": 25},
            goals=["patrol"],
        )
        data = AgentVisualization.state_to_dashboard_data(state)
        assert data["id"] == "a3"
        assert "widgets" in data
        assert "status" in data["widgets"]

    def test_dashboard_bdi_intentions(self):
        state = AgentState(
            agent_id="a4",
            agent_type=AgentType.BDI,
            status="active",
            metadata={"intentions": ["go_home"]},
        )
        data = AgentVisualization.state_to_dashboard_data(state)
        assert "intentions" in data["widgets"]

    def test_dashboard_active_inference_predictions(self):
        state = AgentState(
            agent_id="a5",
            agent_type=AgentType.ACTIVE_INFERENCE,
            status="active",
            metadata={"predictions": {"next": 0.8}},
        )
        data = AgentVisualization.state_to_dashboard_data(state)
        assert data["widgets"]["predictions"]["value"]["next"] == 0.8
