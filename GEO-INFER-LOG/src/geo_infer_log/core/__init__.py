"""
Core functionality for the GEO-INFER-LOG module.

This submodule contains the essential components for logistics, supply chain
optimization, and transportation modeling with geospatial intelligence.
"""

# Import core components with explicit imports
from .routing import (
    VehicleType,
    Vehicle,
    RoutingParameters,
    RouteOptimizer,
    FleetManager,
    VehicleRouter,
    TravelTimeEstimator,
)

from .supply_chain import (
    SupplyChainModel,
    ResilienceAnalyzer,
    NetworkOptimizer,
    FacilityLocator,
    InventoryManager,
)

from .delivery import (
    LastMileRouter,
    DeliveryScheduler,
    ServiceAreaAnalyzer,
)

from .transport import (
    MultiModalPlanner,
    TransportationNetworkAnalyzer,
    TrafficSimulator,
    EmissionsCalculator,
)

# Package exports
__all__ = [
    # Routing optimization
    "VehicleType",
    "Vehicle",
    "RoutingParameters",
    "RouteOptimizer",
    "FleetManager",
    "VehicleRouter",
    "TravelTimeEstimator",
    
    # Supply chain modeling
    "SupplyChainModel",
    "ResilienceAnalyzer",
    "NetworkOptimizer",
    "FacilityLocator",
    "InventoryManager",
    
    # Last-mile delivery
    "LastMileRouter",
    "DeliveryScheduler",
    "ServiceAreaAnalyzer",
    
    # Transportation planning
    "MultiModalPlanner",
    "TransportationNetworkAnalyzer",
    "TrafficSimulator",
    "EmissionsCalculator",
] 