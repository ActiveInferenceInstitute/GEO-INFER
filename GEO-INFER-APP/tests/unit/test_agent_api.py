"""Tests for agent API client and manager."""

import pytest
import asyncio
from geo_infer_app.api.agent_api import AgentAPIClient, AgentManager


@pytest.fixture
def api_client():
    return AgentAPIClient(config={"agents_config_path": "/tmp/test_agents.json"})


@pytest.fixture
def manager():
    return AgentManager(config={"api_config": {"agents_config_path": "/tmp/test_mgr_agents.json"}})


class TestAgentAPIClient:
    @pytest.mark.asyncio
    async def test_create_agent(self, api_client):
        import uuid
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        assert agent_id is not None
        # IDs are UUIDs — validate format
        parsed = uuid.UUID(agent_id)
        assert str(parsed) == agent_id

    @pytest.mark.asyncio
    async def test_create_agent_normalizes_rl_alias(self, api_client):
        agent_id = await api_client.create_agent("rl", {"name": "Test"})
        status = await api_client.get_agent_status(agent_id)
        assert status["type"] == "reinforcement_learning"

    @pytest.mark.asyncio
    async def test_create_agent_rejects_unknown_type(self, api_client):
        with pytest.raises(ValueError, match="Unknown agent type"):
            await api_client.create_agent("telepathic", {"name": "Test"})

    @pytest.mark.asyncio
    async def test_start_agent(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        result = await api_client.start_agent(agent_id)
        assert result is True
        status = await api_client.get_agent_status(agent_id)
        assert status["status"] == "running"

    @pytest.mark.asyncio
    async def test_stop_agent(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        await api_client.start_agent(agent_id)
        result = await api_client.stop_agent(agent_id)
        assert result is True
        status = await api_client.get_agent_status(agent_id)
        assert status["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_delete_agent(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        result = await api_client.delete_agent(agent_id)
        assert result is True
        status = await api_client.get_agent_status(agent_id)
        assert status is None

    @pytest.mark.asyncio
    async def test_list_agents(self, api_client):
        await api_client.create_agent("bdi", {"name": "A1"})
        await api_client.create_agent("rl", {"name": "A2"})
        agents = await api_client.list_agents()
        assert len(agents) == 2

    @pytest.mark.asyncio
    async def test_send_command(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        await api_client.start_agent(agent_id)
        result = await api_client.send_command(agent_id, {"command_type": "query"})
        assert result is not None
        assert result["status"] == "success"
        assert result["command_type"] == "query"
        assert "result" in result
        assert result["result"]["type"] == "bdi"

    @pytest.mark.asyncio
    async def test_send_update_command(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        await api_client.start_agent(agent_id)
        result = await api_client.send_command(agent_id, {
            "command_type": "update",
            "parameters": {"config": {"priority": "high"}}
        })
        assert result is not None
        assert result["status"] == "success"
        status = await api_client.get_agent_status(agent_id)
        assert status["config"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_get_agent_metrics(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        await api_client.start_agent(agent_id)
        await api_client.send_command(agent_id, {"command_type": "query"})
        await api_client.send_command(agent_id, {"command_type": "query"})
        metrics = await api_client.get_agent_metrics(agent_id)
        assert metrics is not None
        assert metrics["decision_count"] == 2
        assert metrics["command_count"] == 2
        assert metrics["success_rate"] == 1.0
        assert metrics["uptime_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_send_command_not_running(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        result = await api_client.send_command(agent_id, {"command_type": "query"})
        assert result is None

    @pytest.mark.asyncio
    async def test_status_callback(self, api_client):
        agent_id = await api_client.create_agent("bdi", {"name": "Test"})
        callback_data = []
        api_client.register_status_callback(agent_id, lambda aid, s: callback_data.append(s))
        await api_client.start_agent(agent_id)
        assert "running" in callback_data


class TestAgentManager:
    @pytest.mark.asyncio
    async def test_create_and_start(self, manager):
        agent_id = await manager.create_agent("bdi", "TestBot", {"param": "val"})
        assert agent_id is not None
        result = await manager.start_agent(agent_id)
        assert result is True
        assert agent_id in manager.active_agents

    @pytest.mark.asyncio
    async def test_stop_removes_from_active(self, manager):
        agent_id = await manager.create_agent("bdi", "TestBot", {})
        await manager.start_agent(agent_id)
        await manager.stop_agent(agent_id)
        assert agent_id not in manager.active_agents

    @pytest.mark.asyncio
    async def test_list_with_filter(self, manager):
        await manager.create_agent("bdi", "BDI1", {})
        await manager.create_agent("rl", "RL1", {})
        bdi_agents = await manager.list_agents(filter_type="bdi")
        assert len(bdi_agents) == 1
