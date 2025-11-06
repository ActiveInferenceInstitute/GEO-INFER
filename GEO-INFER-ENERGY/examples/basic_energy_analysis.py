"""
Basic energy analysis example.

Demonstrates renewable resource assessment, energy demand forecasting,
and grid optimization.
"""

from geo_infer_energy import (
    RenewableResourceAssessor,
    EnergyDemandForecaster,
    EnergyGridOptimizer
)


def main():
    """Run basic energy analysis example."""
    print("GEO-INFER-ENERGY: Basic Energy Analysis Example")
    print("=" * 50)
    
    # Initialize components
    resource_assessor = RenewableResourceAssessor()
    demand_forecaster = EnergyDemandForecaster()
    grid_optimizer = EnergyGridOptimizer()
    
    # Example: Assess solar potential for San Francisco
    print("\n1. Assessing Solar Potential")
    print("-" * 30)
    latitude = 37.7749
    longitude = -122.4194
    solar_result = resource_assessor.assess_solar_potential(latitude, longitude)
    print(f"Solar potential assessment: {solar_result}")
    
    # Example: Forecast energy demand
    print("\n2. Forecasting Energy Demand")
    print("-" * 30)
    demand_result = demand_forecaster.forecast_demand(
        region="San Francisco",
        forecast_horizon=24  # hours
    )
    print(f"Energy demand forecast: {demand_result}")
    
    # Example: Optimize grid
    print("\n3. Optimizing Energy Grid")
    print("-" * 30)
    grid_result = grid_optimizer.optimize_grid(
        demand_data=demand_result,
        renewable_capacity=solar_result
    )
    print(f"Grid optimization result: {grid_result}")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()

