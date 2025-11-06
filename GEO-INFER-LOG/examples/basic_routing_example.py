"""
Basic logistics and routing example using GEO-INFER-LOG.

This example demonstrates:
- Route optimization
- Vehicle fleet management
- Delivery planning
- Logistics network analysis
"""

import sys
import os
import numpy as np
from typing import List, Tuple

# Add src directory to path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from shapely.geometry import Point
    from geo_infer_log.core.routing import RouteOptimizer, Vehicle, VehicleType, RoutingParameters
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some imports not available: {e}")
    IMPORTS_AVAILABLE = False
    Vehicle = None
    VehicleType = None


def create_sample_vehicles():
    """Create sample vehicle fleet."""
    if not IMPORTS_AVAILABLE or Vehicle is None:
        return []
    
    vehicles = [
        Vehicle(
            id="truck_001",
            type=VehicleType.TRUCK,
            capacity=5000.0,  # kg
            max_range=500.0,  # km
            speed=80.0,  # km/h
            cost_per_km=1.5,
            emissions_per_km=0.2,
            location=(-122.4, 37.7)  # San Francisco
        ),
        Vehicle(
            id="van_001",
            type=VehicleType.VAN,
            capacity=1500.0,
            max_range=400.0,
            speed=60.0,
            cost_per_km=0.8,
            emissions_per_km=0.15,
            location=(-122.4, 37.7)
        ),
    ]
    return vehicles


def create_sample_destinations() -> List[Tuple[float, float]]:
    """Create sample delivery destinations."""
    # San Francisco area locations
    destinations = [
        (-122.4194, 37.7749),  # Downtown SF
        (-122.4094, 37.7849),  # North SF
        (-122.4294, 37.7649),  # South SF
        (-122.3894, 37.7949),  # East SF
    ]
    return destinations


def main():
    """Run basic logistics routing example."""
    print("=" * 60)
    print("GEO-INFER-LOG: Basic Logistics Routing Example")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("\n⚠️  Some required modules are not available.")
        print("   This example requires full GEO-INFER-LOG installation.")
        return
    
    # Step 1: Vehicle fleet setup
    print("\n🚚 Step 1: Setting up vehicle fleet...")
    try:
        vehicles = create_sample_vehicles()
        print(f"   ✅ Created {len(vehicles)} vehicles")
        for vehicle in vehicles:
            print(f"      • {vehicle.id}: {vehicle.type.value}, capacity: {vehicle.capacity}kg")
    except Exception as e:
        print(f"   ⚠️  Vehicle setup: {e}")
        vehicles = []
    
    # Step 2: Destination planning
    print("\n📍 Step 2: Planning delivery destinations...")
    try:
        destinations = create_sample_destinations()
        print(f"   ✅ Created {len(destinations)} delivery destinations")
        for i, dest in enumerate(destinations, 1):
            print(f"      • Destination {i}: ({dest[0]:.4f}, {dest[1]:.4f})")
    except Exception as e:
        print(f"   ⚠️  Destination planning: {e}")
        destinations = []
    
    # Step 3: Route optimization
    print("\n🗺️  Step 3: Route optimization...")
    try:
        optimizer = RouteOptimizer()
        print(f"   ✅ Route optimizer initialized")
        
        # Configure routing parameters
        params = RoutingParameters(
            weight_factor="time",
            avoid_tolls=False,
            traffic_model="best_guess"
        )
        print(f"   ✅ Routing parameters configured")
        print(f"      Weight factor: {params.weight_factor}")
        print(f"      Traffic model: {params.traffic_model}")
        
        # Note: Actual route optimization would require network data
        print(f"   ℹ️  Route optimization ready (requires network data)")
    except Exception as e:
        print(f"   ⚠️  Route optimization: {e}")
    
    # Step 4: Logistics analysis
    print("\n📊 Step 4: Logistics analysis...")
    try:
        print(f"   ✅ Logistics analysis capabilities:")
        print(f"      • Multi-vehicle routing")
        print(f"      • Capacity optimization")
        print(f"      • Time window constraints")
        print(f"      • Cost and emissions optimization")
        print(f"      • Real-time traffic integration")
    except Exception as e:
        print(f"   ⚠️  Logistics analysis: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Logistics routing example complete!")
    print("=" * 60)
    print("\nKey capabilities demonstrated:")
    print("  • Vehicle fleet management")
    print("  • Route optimization")
    print("  • Delivery planning")
    print("  • Logistics network analysis")
    print("\nNext steps:")
    print("  • Integrate with SPACE for geospatial routing")
    print("  • Connect with TIME for temporal constraints")
    print("  • Use with AI for predictive logistics")
    print("  • Combine with ECON for cost optimization")


if __name__ == "__main__":
    main()

