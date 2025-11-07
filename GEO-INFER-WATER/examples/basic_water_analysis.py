"""
Basic water resources analysis example.

Demonstrates hydrological modeling, watershed analysis,
and water quality assessment.
"""

from geo_infer_water import (
    HydrologicalModeler,
    WatershedAnalyzer,
    WaterQualityAssessor
)


def main():
    """Run basic water analysis example."""
    print("GEO-INFER-WATER: Basic Water Resources Analysis")
    print("=" * 50)
    
    # Initialize components
    hydrology = HydrologicalModeler()
    watershed = WatershedAnalyzer()
    quality = WaterQualityAssessor()
    
    # Example: Calculate water balance
    print("\n1. Calculating Water Balance")
    print("-" * 30)
    balance = hydrology.calculate_water_balance(
        precipitation=100.0,
        evapotranspiration=50.0,
        runoff=30.0
    )
    print(f"Water balance: {balance}")
    
    # Example: Analyze watershed
    print("\n2. Analyzing Watershed")
    print("-" * 30)
    watershed_result = watershed.analyze_watershed(
        coordinates=[(37.7749, -122.4194)],
        area_km2=100.0
    )
    print(f"Watershed analysis: {watershed_result}")
    
    # Example: Assess water quality
    print("\n3. Assessing Water Quality")
    print("-" * 30)
    quality_result = quality.assess_quality(
        ph=7.0,
        dissolved_oxygen=8.5,
        turbidity=5.0
    )
    print(f"Water quality assessment: {quality_result}")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()


