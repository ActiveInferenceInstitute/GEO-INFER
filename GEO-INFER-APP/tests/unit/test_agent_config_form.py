"""Tests for the agent configuration form data model."""

import pytest
from geo_infer_app.components.agent.agent_config_form import AgentConfigForm


def make_form(**overrides):
    values = {
        "schema": {"fields": ["name", "priority"]},
        "initial_values": {"name": "planner", "priority": 2},
    }
    values.update(overrides)
    return AgentConfigForm(**values)


class TestAgentConfigFormConstruction:
    def test_requires_schema_and_initial_values(self):
        with pytest.raises(TypeError):
            AgentConfigForm()  # type: ignore[call-arg]

    def test_defaults_for_optional_fields(self):
        form = make_form()

        assert form.on_submit is None
        assert form.on_cancel is None
        assert form.is_loading is False
        assert form.error is None


class TestAgentConfigFormSubmit:
    def test_submit_without_overrides_returns_initial_values_copy(self):
        form = make_form()

        payload = form.submit()

        assert payload == {"name": "planner", "priority": 2}
        assert payload is not form.initial_values
        form.initial_values["name"] = "mutated"
        assert payload["name"] == "planner"

    def test_submit_merges_overrides_over_initial_values(self):
        form = make_form()

        payload = form.submit({"priority": 5})

        assert payload == {"name": "planner", "priority": 5}
        # Original values are untouched
        assert form.initial_values == {"name": "planner", "priority": 2}

    def test_empty_overrides_dict_leaves_initial_values(self):
        form = make_form()

        assert form.submit({}) == {"name": "planner", "priority": 2}

    def test_falsy_initial_values_allowed(self):
        form = make_form(initial_values={})

        assert form.submit({"name": "x"}) == {"name": "x"}

    def test_submit_invokes_handler_with_normalized_payload(self):
        seen = []
        form = make_form(on_submit=lambda payload: seen.append(payload) or payload)

        result = form.submit({"priority": 9})

        assert result == {"name": "planner", "priority": 9}
        assert seen == [{"name": "planner", "priority": 9}]

    def test_submit_without_handler_returns_payload_directly(self):
        form = make_form()

        assert form.submit() == {"name": "planner", "priority": 2}


class TestAgentConfigFormCancel:
    def test_cancel_without_handler_returns_none(self):
        assert make_form().cancel() is None

    def test_cancel_invokes_handler(self):
        cancelled = []
        form = make_form(on_cancel=lambda: cancelled.append(True) or True)

        result = form.cancel()

        assert result is True
        assert cancelled == [True]

    def test_submit_ignores_cancel_handler(self):
        cancelled = []

        def submit_handler(payload):
            assert payload == {"name": "planner", "priority": 2}
            return "submitted"

        form = make_form(
            on_submit=submit_handler, on_cancel=lambda: cancelled.append(True)
        )

        assert form.submit() == "submitted"
        assert cancelled == []
