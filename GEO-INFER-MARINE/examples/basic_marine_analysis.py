"""
Basic marine and oceanographic analysis example.

Demonstrates oceanographic data processing, coastal analysis,
and marine ecosystem modeling.
"""

from geo_infer_marine import (
    OceanographicDataProcessor,
    CoastalAnalyzer,
    MarineEcosystemModeler
)


def main():
    """Run basic marine analysis example."""
    print("GEO-INFER-MARINE: Basic Marine Analysis")
    print("=" * 50)
    
    # Initialize components
    ocean_data = OceanographicDataProcessor()
    coastal = CoastalAnalyzer()
    ecosystem = MarineEcosystemModeler()
    
    # Example: Process oceanographic data
    print("\n1. Processing Oceanographic Data")
    print("-" * 30)
    ocean_result = ocean_data.process_temperature_data(
        temperature_data=[20.0, 21.0, 22.0],
        depth_levels=[0, 10, 20]
    )
    print(f"Oceanographic data processing: {ocean_result}")
    
    # Example: Analyze coastal zone
    print("\n2. Analyzing Coastal Zone")
    print("-" * 30)
    coastal_result = coastal.analyze_coastal_zone(
        coordinates=[(37.7749, -122.4194)],
        buffer_distance_km=5.0
    )
    print(f"Coastal analysis: {coastal_result}")
    
    # Example: Model marine ecosystem
    print("\n3. Modeling Marine Ecosystem")
    print("-" * 30)
    ecosystem_result = ecosystem.model_ecosystem(
        species_data={"fish": 100, "coral": 50},
        habitat_type="reef"
    )
    print(f"Ecosystem modeling: {ecosystem_result}")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()

