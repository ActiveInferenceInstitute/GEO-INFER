"""Basic marine and oceanographic analysis example.

Demonstrates oceanographic data processing, coastal vulnerability,
sea-level projection, and marine ecosystem analysis with synthetic
xarray data.
"""

import numpy as np
import xarray as xr

from geo_infer_marine import (
    CoastalAnalyzer,
    MarineEcosystemModeler,
    OceanographicDataProcessor,
    SeaLevelAnalyzer,
)


def main():
    """Run basic marine analysis example."""
    print("GEO-INFER-MARINE: Basic Marine Analysis")
    print("=" * 50)

    # Initialize components
    ocean_data = OceanographicDataProcessor()
    coastal = CoastalAnalyzer()
    sea_level = SeaLevelAnalyzer()
    ecosystem = MarineEcosystemModeler()

    # Example: Current magnitude/direction from velocity components
    print("\n1. Processing Oceanographic Data")
    print("-" * 30)
    u = xr.DataArray([[0.1, 0.2], [0.3, 0.4]], dims=("y", "x"))
    v = xr.DataArray([[0.0, 0.1], [-0.1, 0.2]], dims=("y", "x"))
    currents = ocean_data.calculate_ocean_currents(u, v)
    print(f"Current magnitude (m/s):\n{float(currents['current_magnitude'].min()):.2f}"
          f" - {float(currents['current_magnitude'].max()):.2f}")

    # Example: Coastal vulnerability from elevation vs. sea level
    print("\n2. Analyzing Coastal Vulnerability")
    print("-" * 30)
    elevation = xr.DataArray([1.0, 3.0, 8.0, 15.0], dims="cell")
    sea_level_now = xr.DataArray(2.0)
    vulnerability = coastal.assess_coastal_vulnerability(elevation, sea_level_now)
    print(f"Vulnerability index: "
          f"{np.round(vulnerability['vulnerability_index'].values, 2)}")

    # Example: Sea-level rise projection
    print("\n3. Projecting Sea-Level Rise")
    print("-" * 30)
    years = np.arange(2000, 2011)
    history = xr.DataArray(
        (years - 2000) * 3.0,
        dims="time",
        coords={"time": np.array([f"{y}-01-01" for y in years], dtype="datetime64[ns]")},
    )
    projection = sea_level.project_sea_level_rise(history, scenario="rcp85")
    print(f"Projected sea level in 2100: {float(projection.sel(time='2100-01-01')):.1f} mm")

    # Example: Coral reef health and biodiversity
    print("\n4. Modeling Marine Ecosystem")
    print("-" * 30)
    temperature = xr.DataArray([26.5, 28.0, 29.5, 31.0], dims="location")
    ph = xr.DataArray([8.1, 8.0, 7.9, 7.7], dims="location")
    coral_health = ecosystem.assess_coral_reef_health(temperature, ph)
    print(f"Bleaching risk by site: "
          f"{np.round(coral_health['bleaching_risk'].values, 2)}")

    biodiversity = ecosystem.calculate_biodiversity_indices(
        {"Amphiprion ocellaris": 150, "Chromis viridis": 500, "Chaetodon lunula": 45},
        area_km2=0.5,
    )
    print(f"Shannon diversity: {biodiversity['shannon_diversity']:.3f}, "
          f"richness: {biodiversity['species_richness']}")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
