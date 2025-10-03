"""
Spatial backend dispatcher for GEO-INFER-SPACE.

This module provides the central dispatch system that routes spatial operations
to the appropriate backend (H3, SRAI, etc.) based on configuration and operation type.
"""

import importlib
import logging
from typing import Dict, Any, Optional, Union, Protocol, Type
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SpatialBackendInterface(Protocol):
    """Protocol defining the interface that all spatial backends must implement."""

    @property
    def name(self) -> str:
        """Return the backend name."""
        ...

    @property
    def version(self) -> str:
        """Return the backend version."""
        ...

    def is_available(self) -> bool:
        """Check if the backend is available and functional."""
        ...

    def get_capabilities(self) -> Dict[str, Any]:
        """Return the backend's capabilities."""
        ...


class SpatialIndexingBackend(SpatialBackendInterface):
    """Interface for spatial indexing backends."""

    @abstractmethod
    def latlng_to_cell(self, lat: float, lng: float, resolution: int) -> str:
        """Convert lat/lng coordinates to spatial index cell."""
        ...

    @abstractmethod
    def cell_to_latlng(self, cell: str) -> tuple[float, float]:
        """Convert spatial index cell to lat/lng coordinates."""
        ...

    @abstractmethod
    def polygon_to_cells(self, polygon: Dict[str, Any], resolution: int) -> list[str]:
        """Convert polygon to list of spatial index cells."""
        ...


class SpatialAnalyticsBackend(SpatialBackendInterface):
    """Interface for spatial analytics backends."""

    @abstractmethod
    def analyze_hotspots(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spatial hotspots in the data."""
        ...

    @abstractmethod
    def compute_proximity(self, points: list[tuple[float, float]]) -> Dict[str, Any]:
        """Compute proximity analysis between points."""
        ...


class SpatialBackendDispatcher:
    """
    Central dispatcher for spatial operations across different backends.

    This class manages backend registration, selection, and operation dispatch
    based on configuration and operation requirements.
    """

    def __init__(self):
        self.backends: Dict[str, SpatialBackendInterface] = {}
        self.default_backends: Dict[str, str] = {}
        self.backend_capabilities: Dict[str, Dict[str, Any]] = {}
        self._load_backends()

    def _load_backends(self):
        """Load available spatial backends."""
        # Load H3 backend if available
        try:
            h3_backend = self._load_h3_backend()
            if h3_backend:
                self.register_backend('h3', h3_backend)
                logger.info("H3 backend loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load H3 backend: {e}")

        # Load SRAI backend if available
        try:
            srai_backend = self._load_srai_backend()
            if srai_backend:
                self.register_backend('srai', srai_backend)
                logger.info("SRAI backend loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load SRAI backend: {e}")

    def _load_h3_backend(self) -> Optional[SpatialBackendInterface]:
        """Load H3 backend implementation."""
        try:
            from ..backends.h3 import H3Backend
            return H3Backend()
        except ImportError:
            return None

    def _load_srai_backend(self) -> Optional[SpatialBackendInterface]:
        """Load SRAI backend implementation."""
        try:
            from ..backends.srai import SraiBackend
            return SraiBackend()
        except ImportError:
            return None

    def register_backend(self, name: str, backend: SpatialBackendInterface):
        """Register a spatial backend."""
        self.backends[name] = backend
        self.backend_capabilities[name] = backend.get_capabilities()
        logger.info(f"Registered spatial backend: {name}")

    def get_backend(self, name: str) -> Optional[SpatialBackendInterface]:
        """Get a specific backend by name."""
        return self.backends.get(name)

    def get_available_backends(self) -> list[str]:
        """Get list of available backend names."""
        return [name for name, backend in self.backends.items() if backend.is_available()]

    def set_default_backend(self, operation_type: str, backend_name: str):
        """Set the default backend for a specific operation type."""
        if backend_name not in self.backends:
            raise ValueError(f"Backend '{backend_name}' is not registered")
        self.default_backends[operation_type] = backend_name

    def get_default_backend(self, operation_type: str) -> str:
        """Get the default backend for an operation type."""
        return self.default_backends.get(operation_type, 'h3')  # Default to H3

    def dispatch_indexing_operation(self, operation: str, *args, backend: Optional[str] = None, **kwargs) -> Any:
        """Dispatch a spatial indexing operation to the appropriate backend."""
        backend_name = backend or self.get_default_backend('indexing')

        if backend_name not in self.backends:
            raise ValueError(f"Backend '{backend_name}' is not available")

        backend_instance = self.backends[backend_name]

        if not isinstance(backend_instance, SpatialIndexingBackend):
            raise ValueError(f"Backend '{backend_name}' does not support indexing operations")

        # Map operation names to backend methods
        operation_map = {
            'latlng_to_cell': 'latlng_to_cell',
            'cell_to_latlng': 'cell_to_latlng',
            'polygon_to_cells': 'polygon_to_cells',
            'get_neighbors': 'get_cell_neighbors',
            'get_distance': 'get_cell_distance',
            'compact_cells': 'compact_cells',
            'uncompact_cells': 'uncompact_cells',
        }

        if operation not in operation_map:
            raise ValueError(f"Unknown indexing operation: {operation}")

        method_name = operation_map[operation]
        method = getattr(backend_instance, method_name)

        return method(*args, **kwargs)

    def dispatch_analytics_operation(self, operation: str, *args, backend: Optional[str] = None, **kwargs) -> Any:
        """Dispatch a spatial analytics operation to the appropriate backend."""
        backend_name = backend or self.get_default_backend('analytics')

        if backend_name not in self.backends:
            raise ValueError(f"Backend '{backend_name}' is not available")

        backend_instance = self.backends[backend_name]

        if not isinstance(backend_instance, SpatialAnalyticsBackend):
            raise ValueError(f"Backend '{backend_name}' does not support analytics operations")

        # Map operation names to backend methods
        operation_map = {
            'analyze_hotspots': 'analyze_hotspots',
            'compute_proximity': 'compute_proximity',
        }

        if operation not in operation_map:
            raise ValueError(f"Unknown analytics operation: {operation}")

        method_name = operation_map[operation]
        method = getattr(backend_instance, method_name)

        return method(*args, **kwargs)

    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about all registered backends."""
        return {
            name: {
                'available': backend.is_available(),
                'capabilities': self.backend_capabilities.get(name, {}),
                'version': getattr(backend, 'version', 'unknown')
            }
            for name, backend in self.backends.items()
        }


# Global dispatcher instance
_dispatcher: Optional[SpatialBackendDispatcher] = None


def get_backend_dispatcher() -> SpatialBackendDispatcher:
    """Get the global backend dispatcher instance."""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = SpatialBackendDispatcher()
    return _dispatcher


def configure_backends(config: Dict[str, Any]):
    """Configure backend defaults from configuration."""
    dispatcher = get_backend_dispatcher()

    if 'default_backends' in config:
        for operation_type, backend_name in config['default_backends'].items():
            dispatcher.set_default_backend(operation_type, backend_name)

    logger.info("Backend configuration applied")


def reset_dispatcher():
    """Reset the global dispatcher (mainly for testing)."""
    global _dispatcher
    _dispatcher = None
