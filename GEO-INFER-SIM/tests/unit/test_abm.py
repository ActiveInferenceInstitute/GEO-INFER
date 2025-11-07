"""
Unit tests for agent-based modeling.
"""

import pytest
import numpy as np
from geo_infer_sim.paradigms.abm import AgentBasedModel, Agent


class TestAgent:
    """Test Agent class."""

    def test_agent_creation(self) -> None:
        """Test agent creation."""
        agent = Agent(
            agent_id="agent1",
            position=np.array([0.0, 0.0]),
            properties={"type": "mobile"},
        )

        assert agent.agent_id == "agent1"
        assert np.array_equal(agent.position, np.array([0.0, 0.0]))
        assert agent.properties["type"] == "mobile"


class TestAgentBasedModel:
    """Test AgentBasedModel class."""

    @pytest.fixture
    def abm(self) -> AgentBasedModel:
        """Create an ABM instance."""
        return AgentBasedModel()

    def test_add_agent(self, abm: AgentBasedModel) -> None:
        """Test adding agents."""
        agent = Agent(agent_id="agent1", position=np.array([0.0, 0.0]))
        abm.add_agent(agent)

        assert "agent1" in abm.agents
        assert abm.get_agent("agent1") == agent

    def test_find_neighbors(self, abm: AgentBasedModel) -> None:
        """Test finding neighboring agents."""
        agent1 = Agent(agent_id="agent1", position=np.array([0.0, 0.0]))
        agent2 = Agent(agent_id="agent2", position=np.array([1.0, 0.0]))
        agent3 = Agent(agent_id="agent3", position=np.array([100.0, 100.0]))

        abm.add_agent(agent1)
        abm.add_agent(agent2)
        abm.add_agent(agent3)

        neighbors = abm.find_neighbors(agent1, radius=5.0)

        assert len(neighbors) == 1
        assert neighbors[0].agent_id == "agent2"

    def test_step(self, abm: AgentBasedModel) -> None:
        """Test ABM step execution."""
        agent = Agent(agent_id="agent1", position=np.array([0.0, 0.0]))
        abm.add_agent(agent)

        abm.step(time_step=1.0)

        assert abm.time == 1.0



