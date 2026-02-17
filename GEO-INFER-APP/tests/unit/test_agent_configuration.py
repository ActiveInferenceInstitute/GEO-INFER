"""Tests for agent configuration schemas and validation."""

import pytest
from geo_infer_app.models.agent_configuration import (
    AgentConfiguration,
    AgentConfigSchema,
    ConfigField,
    ConfigFieldType,
)
from geo_infer_app.models.agent_interface import AgentType


class TestAgentConfiguration:
    def test_get_default_schema(self):
        schema = AgentConfiguration.get_schema(AgentType.BDI)
        assert schema.agent_type == AgentType.BDI
        assert len(schema.fields) > 0

    def test_bdi_schema_has_beliefs_field(self):
        schema = AgentConfiguration.get_schema(AgentType.BDI)
        field_names = {f.name for f in schema.fields}
        assert "beliefs" in field_names
        assert "desires" in field_names

    def test_rl_schema_has_learning_rate(self):
        schema = AgentConfiguration.get_schema(AgentType.RL)
        field_names = {f.name for f in schema.fields}
        assert "learning_rate" in field_names
        assert "discount_factor" in field_names

    def test_validate_valid_config(self):
        errors = AgentConfiguration.validate_config(AgentType.BDI, {
            "name": "TestAgent",
            "beliefs": {"temperature": 25},
            "desires": ["explore"],
        })
        assert len(errors) == 0

    def test_validate_missing_required(self):
        errors = AgentConfiguration.validate_config(AgentType.BDI, {})
        assert any("name" in e for e in errors)

    def test_validate_wrong_type(self):
        errors = AgentConfiguration.validate_config(AgentType.BDI, {
            "name": 123,  # Should be string
        })
        assert any("string" in e for e in errors)

    def test_validate_number_range(self):
        errors = AgentConfiguration.validate_config(AgentType.ACTIVE_INFERENCE, {
            "name": "AI Agent",
            "precision": 15.0,  # max is 10.0
        })
        assert any("at most" in e for e in errors)

    def test_get_default_config(self):
        defaults = AgentConfiguration.get_default_config(AgentType.RL)
        assert "learning_rate" in defaults
        assert defaults["learning_rate"] == 0.1


class TestConfigField:
    def test_field_creation(self):
        field = ConfigField(
            name="test",
            field_type=ConfigFieldType.STRING,
            label="Test Field",
            required=True,
        )
        assert field.name == "test"
        assert field.required is True
        assert field.advanced is False
