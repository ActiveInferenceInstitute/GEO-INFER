"""
Unit tests for GEO-INFER-COMMS core functionality.
"""

import pytest

from geo_infer_comms import __version__, GeospatialCommunicationSystem


class TestCommsModule:
    """Test basic module functionality."""

    def test_module_import(self) -> None:
        """Test that the module can be imported."""
        import geo_infer_comms
        assert geo_infer_comms is not None

    def test_module_version(self) -> None:
        """Test that module has a version."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_communication_system_initialization(self) -> None:
        """Test GeospatialCommunicationSystem initialization."""
        system = GeospatialCommunicationSystem()
        assert system is not None
        assert hasattr(system, 'message_broker')
        assert hasattr(system, 'notification_manager')
        assert hasattr(system, 'channel_manager')
        assert hasattr(system, 'event_manager')

    def test_communication_system_start_stop(self) -> None:
        """Test system start and stop functionality."""
        system = GeospatialCommunicationSystem()
        system.start()
        assert system._started is True
        assert system.start_time is not None
        
        health = system.get_system_health()
        assert health['status'] in ['healthy', 'degraded']
        
        system.stop()
        assert system._started is False

    def test_communication_system_context_manager(self) -> None:
        """Test system as context manager."""
        with GeospatialCommunicationSystem() as system:
            assert system._started is True
        assert system._started is False

