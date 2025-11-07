"""
Basic forest management analysis example.

Demonstrates forest inventory, carbon sequestration modeling,
and wildfire risk assessment.
"""

from geo_infer_forest import (
    ForestInventory,
    CarbonSequestrationModeler,
    WildfireRiskAnalyzer
)


def main():
    """Run basic forest analysis example."""
    print("GEO-INFER-FOREST: Basic Forest Management Analysis")
    print("=" * 50)
    
    # Initialize components
    inventory = ForestInventory()
    carbon = CarbonSequestrationModeler()
    wildfire = WildfireRiskAnalyzer()
    
    # Example: Estimate forest biomass
    print("\n1. Estimating Forest Biomass")
    print("-" * 30)
    biomass = inventory.estimate_biomass(
        tree_density=100,  # trees per hectare
        average_dbh=30.0,  # cm
        height=20.0  # meters
    )
    print(f"Estimated biomass: {biomass}")
    
    # Example: Model carbon sequestration
    print("\n2. Modeling Carbon Sequestration")
    print("-" * 30)
    carbon_result = carbon.model_sequestration(
        biomass=biomass,
        forest_area_ha=1000.0
    )
    print(f"Carbon sequestration: {carbon_result}")
    
    # Example: Assess wildfire risk
    print("\n3. Assessing Wildfire Risk")
    print("-" * 30)
    risk_result = wildfire.assess_risk(
        fuel_load=biomass,
        weather_conditions={"temperature": 30.0, "humidity": 20.0},
        topography="steep"
    )
    print(f"Wildfire risk assessment: {risk_result}")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()


