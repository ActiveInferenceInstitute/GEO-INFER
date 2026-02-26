"""
Integration tests for the BDI agent lifecycle.

These tests exercise the full perception→belief-update→deliberation→action
cycle using real agent components (no mocks).  They verify that multiple
agents can be instantiated independently and that the BDI architecture
produces consistent, deterministic behaviour for a simple task.
"""

import asyncio
import pytest

from geo_infer_agent.models.bdi.agent import BDIAgent, BDIState, Belief, Desire, Plan


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_agent(agent_id: str, *, plans=None, beliefs=None, desires=None) -> BDIAgent:
    """Create a BDIAgent with optional pre-loaded config."""
    config = {
        "plans": plans or [],
        "initial_beliefs": beliefs or {},
        "initial_desires": desires or [],
    }
    return BDIAgent(agent_id=agent_id, config=config)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBDIAgentLifecycle:
    """Full lifecycle tests: initialize → perceive → update_beliefs → decide → act."""

    async def test_initialize_and_perceive(self):
        """Agent initializes without error and perceive() returns a dict."""
        agent = make_agent("lifecycle-1")
        await agent.initialize()
        perception = await agent.perceive()
        assert isinstance(perception, dict)
        assert "timestamp" in perception
        assert "agent_id" in perception
        assert perception["agent_id"] == "lifecycle-1"

    async def test_belief_update_from_perception(self):
        """Sensor perceptions are reflected in agent beliefs after update_beliefs()."""
        agent = make_agent(
            "lifecycle-2",
            config_override={
                "sensor_readings": {"temperature": 22.5, "humidity": 60},
            },
        )
        await agent.initialize()
        perception = await agent.perceive()
        agent.update_beliefs(perception)

        temp_belief = agent.state.get_belief("sensor.temperature")
        assert temp_belief is not None
        assert temp_belief.value == 22.5

        hum_belief = agent.state.get_belief("sensor.humidity")
        assert hum_belief is not None
        assert hum_belief.value == 60

    async def test_deliberation_selects_highest_priority_desire(self):
        """decide() selects a plan for the highest-priority unachieved desire."""
        plans = [
            {
                "name": "plan_low",
                "desire_name": "low_priority_goal",
                "actions": [{"type": "log", "message": "low priority"}],
            },
            {
                "name": "plan_high",
                "desire_name": "high_priority_goal",
                "actions": [{"type": "log", "message": "high priority"}],
            },
        ]
        desires = [
            {"name": "low_priority_goal", "description": "Low priority", "priority": 0.2},
            {"name": "high_priority_goal", "description": "High priority", "priority": 0.9},
        ]
        agent = make_agent("lifecycle-3", plans=plans, desires=desires)
        await agent.initialize()

        action = await agent.decide()
        assert action is not None
        # The high-priority plan's action should be selected
        assert action.get("message") == "high priority"

    async def test_action_execution_updates_intention(self):
        """Acting on a single-step plan marks the intention as complete."""
        plans = [
            {
                "name": "simple_plan",
                "desire_name": "simple_goal",
                "actions": [{"type": "log", "message": "executed"}],
            }
        ]
        desires = [
            {"name": "simple_goal", "description": "A simple one-step goal", "priority": 0.8}
        ]
        agent = make_agent("lifecycle-4", plans=plans, desires=desires)
        await agent.initialize()

        action = await agent.decide()
        assert action is not None

        result = await agent.act(action)
        assert result["success"] is True

        # Advance the intention
        intention = agent.state.get_current_intention()
        if intention is not None:
            assert intention.current_action_index >= 1 or intention.complete

    async def test_full_perception_action_loop(self):
        """Complete three-cycle loop: perceive → update_beliefs → decide → act."""
        plans = [
            {
                "name": "monitor_plan",
                "desire_name": "monitor_region",
                "actions": [
                    {"type": "log", "message": "cycle 1"},
                    {"type": "log", "message": "cycle 2"},
                    {"type": "log", "message": "cycle 3"},
                ],
            }
        ]
        desires = [
            {"name": "monitor_region", "description": "Monitor region continuously", "priority": 1.0}
        ]
        agent = make_agent("lifecycle-5", plans=plans, desires=desires)
        await agent.initialize()

        for _ in range(3):
            perception = await agent.perceive()
            agent.update_beliefs(perception)
            action = await agent.decide()
            if action:
                result = await agent.act(action)
                assert result["success"] is True

    async def test_shutdown_after_lifecycle(self):
        """shutdown() completes cleanly after a full lifecycle."""
        agent = make_agent("lifecycle-6")
        await agent.initialize()
        await agent.perceive()
        await agent.shutdown()  # Must not raise


class TestMultiAgentCoordination:
    """Tests verifying that multiple independent BDI agents operate concurrently."""

    async def test_two_agents_independent_beliefs(self):
        """Two agents maintain independent belief bases."""
        a1 = make_agent("coord-1", config_override={"sensor_readings": {"level": 10}})
        a2 = make_agent("coord-2", config_override={"sensor_readings": {"level": 99}})

        await a1.initialize()
        await a2.initialize()

        p1 = await a1.perceive()
        p2 = await a2.perceive()
        a1.update_beliefs(p1)
        a2.update_beliefs(p2)

        b1 = a1.state.get_belief("sensor.level")
        b2 = a2.state.get_belief("sensor.level")

        assert b1 is not None and b2 is not None
        assert b1.value == 10
        assert b2.value == 99

    async def test_concurrent_agents(self):
        """Multiple agents can run their lifecycle concurrently."""

        async def run_agent(agent_id: str) -> str:
            agent = make_agent(agent_id)
            await agent.initialize()
            await agent.perceive()
            await agent.shutdown()
            return agent_id

        results = await asyncio.gather(
            run_agent("concurrent-1"),
            run_agent("concurrent-2"),
            run_agent("concurrent-3"),
        )
        assert set(results) == {"concurrent-1", "concurrent-2", "concurrent-3"}

    async def test_belief_sharing_via_update(self):
        """One agent's output can be fed as a belief into another agent."""
        sender = make_agent("coord-sender")
        receiver = make_agent("coord-receiver")

        await sender.initialize()
        await receiver.initialize()

        # Sender computes a value and stores it as a belief
        sender.state.update_belief("computed_value", 42)
        sender_belief = sender.state.get_belief("computed_value")
        assert sender_belief is not None

        # Receiver ingests the value as a belief
        receiver.state.update_belief("received_value", sender_belief.value)
        recv_belief = receiver.state.get_belief("received_value")
        assert recv_belief is not None
        assert recv_belief.value == 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_agent(agent_id: str, *, plans=None, beliefs=None, desires=None,
               config_override=None) -> BDIAgent:  # type: ignore[override]
    """Create a BDIAgent with optional pre-loaded config."""
    config = {
        "plans": plans or [],
        "initial_beliefs": beliefs or {},
        "initial_desires": desires or [],
    }
    if config_override:
        config.update(config_override)
    return BDIAgent(agent_id=agent_id, config=config)
