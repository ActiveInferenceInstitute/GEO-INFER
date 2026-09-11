"""Tests for the agent widget lifecycle and web rendering."""

import asyncio

import pytest
from geo_infer_app.components.agent_widget import AgentWidget, WebAgentWidget


class StubAgentManager:
    """Minimal AgentManager stand-in recording lifecycle interactions."""

    def __init__(self):
        self.status_callbacks = {}
        self.info = {}
        self.metrics = {}
        self.start_results = {}
        self.stop_results = {}
        self.command_results = {}
        self.started = []
        self.stopped = []
        self.commands = []

    def register_status_callback(self, agent_id, callback):
        self.status_callbacks.setdefault(agent_id, []).append(callback)

    def unregister_status_callback(self, agent_id, callback):
        callbacks = self.status_callbacks.get(agent_id, [])
        if callback in callbacks:
            callbacks.remove(callback)
            return True
        return False

    async def start_agent(self, agent_id):
        self.started.append(agent_id)
        return self.start_results.get(agent_id, True)

    async def stop_agent(self, agent_id):
        self.stopped.append(agent_id)
        return self.stop_results.get(agent_id, True)

    async def send_command(self, agent_id, command_type, parameters=None):
        self.commands.append((agent_id, command_type, parameters))
        return self.command_results.get(command_type)

    async def list_agents(self):
        return [{"agent_id": aid} for aid in self.status_callbacks]

    async def get_agent_info(self, agent_id):
        return self.info.get(agent_id)

    async def get_agent_metrics(self, agent_id):
        return self.metrics.get(agent_id)


def make_widget(**config):
    manager = StubAgentManager()
    config.setdefault("update_interval", 0)
    widget = AgentWidget(manager, agent_id="agent-1", config=config)
    return widget, manager


class TestAgentWidgetLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_registers_callback_and_fetches_info(self):
        widget, manager = make_widget()
        manager.info["agent-1"] = {"agent_id": "agent-1", "status": "running"}

        await widget.initialize()

        assert widget.status == "initialized"
        assert widget._handle_status_change in manager.status_callbacks["agent-1"]
        assert widget.agent_info == {"agent_id": "agent-1", "status": "running"}
        assert widget._update_task is not None
        await widget.shutdown()

    @pytest.mark.asyncio
    async def test_shutdown_cancels_update_task_and_unregisters(self):
        widget, manager = make_widget()
        await widget.initialize()

        await widget.shutdown()

        assert widget.status == "shutdown"
        assert widget._update_task.cancelled()
        assert widget._handle_status_change not in manager.status_callbacks["agent-1"]

    @pytest.mark.asyncio
    async def test_update_loop_polls_with_injected_interval(self):
        # update_interval=0 makes the loop poll back-to-back with no real sleep;
        # poll counts are asserted on collected calls, not wall-clock timing.
        widget, manager = make_widget(update_interval=0)
        manager.info["agent-1"] = {"agent_id": "agent-1"}
        await widget.initialize()

        # Collect polls by wrapping _update_agent_info
        polls = []
        original = widget._update_agent_info

        async def counting_update():
            await original()
            polls.append(1)

        widget._update_agent_info = counting_update

        async def run_until_three_polls():
            while len(polls) < 3:
                await asyncio.sleep(0)

        await asyncio.wait_for(run_until_three_polls(), timeout=2)
        await widget.shutdown()
        assert widget._update_task.cancelled()
        assert len(polls) >= 3

    @pytest.mark.asyncio
    async def test_set_agent_rebinds_callbacks_and_clears_history(self):
        widget, manager = make_widget()
        await widget.initialize()
        manager.info["agent-2"] = {"agent_id": "agent-2", "status": "idle"}

        assert await widget.set_agent("agent-2") is True

        assert widget.agent_id == "agent-2"
        assert widget._handle_status_change not in manager.status_callbacks["agent-1"]
        assert widget._handle_status_change in manager.status_callbacks["agent-2"]
        assert widget.agent_info == {"agent_id": "agent-2", "status": "idle"}
        assert widget.command_history == []
        await widget.shutdown()

    @pytest.mark.asyncio
    async def test_start_stop_agent_delegate_to_manager(self):
        widget, manager = make_widget()
        manager.stop_results["agent-1"] = False
        await widget.initialize()

        assert await widget.start_agent() is True
        assert await widget.stop_agent() is False
        assert manager.started == ["agent-1"]
        assert manager.stopped == ["agent-1"]
        await widget.shutdown()

    @pytest.mark.asyncio
    async def test_start_stop_agent_without_agent_id_fails(self):
        widget, manager = make_widget()
        widget.agent_id = None

        assert await widget.start_agent() is False
        assert await widget.stop_agent() is False
        assert manager.started == []
        assert manager.stopped == []


class TestAgentWidgetCommands:
    @pytest.mark.asyncio
    async def test_send_command_records_history(self):
        widget, manager = make_widget()
        manager.command_results["query"] = {"status": "ok"}
        await widget.initialize()

        result = await widget.send_command("query", {"q": "hello"})

        assert result == {"status": "ok"}
        assert len(widget.command_history) == 1
        entry = widget.command_history[0]
        assert entry["command_type"] == "query"
        assert entry["parameters"] == {"q": "hello"}
        assert entry["result"] == {"status": "ok"}
        assert "timestamp" in entry
        await widget.shutdown()

    @pytest.mark.asyncio
    async def test_send_command_without_agent_returns_none(self):
        widget, manager = make_widget()
        widget.agent_id = None

        assert await widget.send_command("query") is None
        assert manager.commands == []

    @pytest.mark.asyncio
    async def test_failed_command_is_not_history_recorded(self):
        widget, manager = make_widget()
        await widget.initialize()

        assert await widget.send_command("unknown") is None
        assert widget.command_history == []
        await widget.shutdown()

    @pytest.mark.asyncio
    async def test_command_history_trimmed_to_max_history(self):
        widget, manager = make_widget(max_history=2)
        manager.command_results["query"] = {"status": "ok"}
        await widget.initialize()

        for i in range(5):
            await widget.send_command("query", {"i": i})

        assert len(widget.command_history) == 2
        assert [e["parameters"]["i"] for e in widget.command_history] == [3, 4]
        await widget.shutdown()

    @pytest.mark.asyncio
    async def test_get_agent_list_delegates(self):
        widget, manager = make_widget()
        manager.status_callbacks["agent-9"] = []

        assert await widget.get_agent_list() == [{"agent_id": "agent-9"}]


class TestAgentWidgetStatusCallbacks:
    def test_register_and_unregister_widget_callback(self):
        widget, _ = make_widget()
        seen = []
        widget.register_status_callback(seen.append)

        assert widget.unregister_status_callback(seen.append) is True
        assert widget.unregister_status_callback(seen.append) is False

    def test_handle_status_change_for_own_agent_notifies(self):
        widget, _ = make_widget()
        seen = []
        widget.register_status_callback(seen.append)

        widget._handle_status_change("agent-1", "running")

        assert widget.status == "agent_running"
        assert seen == ["agent_running"]

    def test_handle_status_change_for_other_agent_ignored(self):
        widget, _ = make_widget()
        seen = []
        widget.register_status_callback(seen.append)

        widget._handle_status_change("other-agent", "running")

        assert widget.status == "initializing"
        assert seen == []

    def test_failing_callback_does_not_break_notification(self):
        widget, _ = make_widget()
        seen = []

        def broken(_status):
            raise RuntimeError("boom")

        widget.register_status_callback(broken)
        widget.register_status_callback(seen.append)

        widget._notify_status_change()

        assert seen == ["initializing"]


class TestWebAgentWidgetRender:
    def make_web_widget(self, manager=None):
        manager = manager or StubAgentManager()
        manager.info["agent-1"] = {
            "agent_id": "agent-1",
            "type": "bdi",
            "status": "running",
            "config": {"name": "Planner <script>alert(1)</script>"},
        }
        manager.metrics["agent-1"] = {"decision_count": 7, "success_rate": 0.914}
        widget = WebAgentWidget(manager, agent_id="agent-1")
        return widget, manager

    def test_render_known_state(self):
        widget, _ = self.make_web_widget()
        widget.agent_id = "agent-1"
        widget.agent_info = {
            "type": "bdi",
            "status": "running",
            "config": {"name": "Planner"},
        }
        widget.agent_metrics = {"decision_count": 7, "success_rate": 0.914}

        markup = widget.render()

        assert '<div id="agent-widget" class="agent-widget">' in markup
        assert "<h3>Planner</h3>" in markup
        assert '<span class="agent-type">bdi</span>' in markup
        assert '<span class="agent-status status-running">running</span>' in markup
        assert "startAgent('agent-1')" in markup
        assert "stopAgent('agent-1')" in markup
        assert '<span class="metric-value">7</span>' in markup
        assert '<span class="metric-value">0.91</span>' in markup

    def test_render_escapes_untrusted_agent_name(self):
        widget, _ = self.make_web_widget()
        widget.agent_info = {
            "type": "bdi",
            "status": "running",
            "config": {"name": "Eve<script>x</script>"},
        }

        markup = widget.render()

        assert "Eve&lt;script&gt;x&lt;/script&gt;" in markup
        assert "<script>" not in markup

    def test_render_defaults_for_unknown_agent(self):
        manager = StubAgentManager()
        widget = WebAgentWidget(manager, agent_id=None)

        markup = widget.render()

        assert "Unknown Agent" in markup
        assert '<span class="agent-type">unknown</span>' in markup
        assert '<span class="agent-status status-unknown">unknown</span>' in markup
        assert "startAgent('')" in markup

    def test_render_includes_recent_command_history_newest_first(self):
        widget, _ = self.make_web_widget()
        widget.command_history = [
            {
                "timestamp": "2026-09-11T10:00:01.100000",
                "command_type": "query",
                "parameters": None,
                "result": {"status": "ok"},
            },
            {
                "timestamp": "2026-09-11T10:00:02.200000",
                "command_type": "update",
                "parameters": None,
                "result": {"status": "failed"},
            },
        ]

        markup = widget.render()

        assert '<span class="timestamp">10:00:02</span>' in markup
        assert '<span class="command">update</span>' in markup
        assert '<span class="result">failed</span>' in markup
        assert '<span class="timestamp">10:00:01</span>' in markup
        assert '<span class="command">query</span>' in markup
        assert markup.index("10:00:02") < markup.index("10:00:01")

    def test_render_escapes_command_type_in_history(self):
        widget, _ = self.make_web_widget()
        widget.command_history = [
            {
                "timestamp": "2026-09-11T10:00:03.000000",
                "command_type": "<img src=x>",
                "parameters": None,
                "result": {"status": "ok"},
            },
        ]

        markup = widget.render()

        assert "&lt;img src=x&gt;" in markup
        assert "<img src=x>" not in markup

    def test_get_javascript_exposes_agent_endpoints(self):
        widget, _ = self.make_web_widget()

        js = widget.get_javascript()

        assert "/api/agents/${agentId}/start" in js
        assert "/api/agents/${agentId}/stop" in js
        assert "/api/agents/${agentId}/command" in js

    def test_web_config_overrides_element_and_css(self):
        manager = StubAgentManager()
        widget = WebAgentWidget(
            manager,
            agent_id="agent-1",
            config={
                "element_id": "custom-id",
                "css_class": "custom-class",
                "template": "compact",
            },
        )

        assert widget.element_id == "custom-id"
        assert widget.css_class == "custom-class"
        assert widget.template == "compact"
        assert 'id="custom-id"' in widget.render()
