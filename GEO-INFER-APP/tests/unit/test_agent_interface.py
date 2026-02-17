"""Tests for agent interface types and data classes."""

import pytest
from geo_infer_app.models.agent_interface import (
    AgentType,
    AgentState,
    AgentInterface,
)


class TestAgentType:
    def test_enum_values(self):
        assert AgentType.BDI.value == "bdi"
        assert AgentType.ACTIVE_INFERENCE.value == "active_inference"
        assert AgentType.RL.value == "reinforcement_learning"
        assert AgentType.RULE_BASED.value == "rule_based"
        assert AgentType.HYBRID.value == "hybrid"

    def test_all_types_present(self):
        assert len(AgentType) == 5


class TestAgentState:
    def test_create_state(self):
        state = AgentState(
            agent_id="a1",
            agent_type=AgentType.BDI,
            status="active",
            location={"lat": 40.7, "lng": -74.0},
            goals=["explore", "collect"],
        )
        assert state.agent_id == "a1"
        assert state.agent_type == AgentType.BDI
        assert state.location["lat"] == 40.7

    def test_state_defaults(self):
        state = AgentState(agent_id="a2", agent_type=AgentType.RL, status="idle")
        assert state.location is None
        assert state.tasks is None
        assert state.beliefs is None

    def test_agent_interface_is_abstract(self):
        with pytest.raises(TypeError):
            AgentInterface()
