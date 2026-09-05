"""Tests for agent factory pattern."""

import pytest
from geo_infer_app.models.agent_factory import AgentFactory
from geo_infer_app.models.agent_interface import AgentInterface, AgentType


class TestAgentFactory:
    def test_bdi_interface_registered(self):
        """BDI interface should be auto-registered on import."""
        from geo_infer_app.models.interfaces.bdi_interface import BDIAgentInterface
        types = AgentFactory.get_available_agent_types()
        assert "bdi" in types

    def test_create_bdi_interface(self):
        from geo_infer_app.models.interfaces.bdi_interface import BDIAgentInterface
        interface = AgentFactory.create_interface(AgentType.BDI)
        assert isinstance(interface, BDIAgentInterface)

    def test_create_unknown_type_raises(self):
        with pytest.raises(ValueError):
            AgentFactory.create_interface(AgentType.HYBRID)

    def test_unknown_type_error_is_specific(self):
        with pytest.raises(ValueError, match="reinforcement_learning"):
            AgentFactory.create_interface(AgentType.RL)

    def test_interfaces_package_import_registers_bdi(self):
        # Importing the interfaces package (not just the module) must register
        # the bundled interfaces with the factory.
        import importlib
        import geo_infer_app.models.interfaces as interfaces_pkg
        importlib.reload(interfaces_pkg)
        assert "bdi" in AgentFactory.get_available_agent_types()

    def test_register_invalid_class_raises(self):
        class NotAnInterface:
            pass
        with pytest.raises(TypeError):
            AgentFactory.register_interface(AgentType.HYBRID, NotAnInterface)
