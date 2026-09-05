"""
Basic forest management analysis example.

Demonstrates forest inventory (biomass estimation), carbon stock and
credit modeling, and wildfire risk assessment using the real
``geo_infer_forest`` public API.
"""

import numpy as np
import xarray as xr

from geo_infer_forest import (
    CarbonSequestrationModeler,
    ForestInventory,
    WildfireRiskAnalyzer,
)


def main():
    """Run basic forest analysis example."""
    print("GEO-INFER-FOREST: Basic Forest Management Analysis")
    print("=" * 50)

    # Sample forest cover percentage grid (20x20)
    lat = np.linspace(42.0, 42.5, 20)
    lon = np.linspace(-124.0, -123.5, 20)
    coords = {"lat": lat, "lon": lon}

    # Initialize components
    inventory = ForestInventory()
    carbon = CarbonSequestrationModeler()
    wildfire = WildfireRiskAnalyzer()

    # 1. Estimate forest biomass from canopy cover and tree density
    print("\n1. Estimating Forest Biomass")
    print("-" * 30)
    forest_cover = xr.DataArray(
        np.random.uniform(20.0, 95.0, (20, 20)),
        dims=("lat", "lon"),
        coords=coords,
        attrs={"units": "percent"},
    )
    tree_density = xr.DataArray(
        np.random.uniform(100.0, 800.0, (20, 20)),
        dims=("lat", "lon"),
        coords=coords,
        attrs={"units": "trees/ha"},
    )
    biomass = inventory.estimate_biomass(forest_cover, tree_density)
    print(f"Estimated biomass (t/ha): {float(biomass.mean()):.1f} mean, "
          f"{float(biomass.min()):.1f}-{float(biomass.max()):.1f} range")

    # 2. Model carbon stock and sequestration value
    print("\n2. Modeling Carbon Sequestration")
    print("-" * 30)
    carbon_stock = carbon.calculate_carbon_stock(biomass)
    print(f"Carbon stock: {float(carbon_stock.mean()):.1f} tC/ha")

    biomass_growth = biomass * 0.03  # assume 3% annual growth
    sequestration_rate = carbon.estimate_sequestration_rate(biomass_growth)
    print(f"Sequestration rate: {float(sequestration_rate.mean()):.2f} tC/ha/year")

    area_ha = xr.full_like(forest_cover, 10.0)  # 10 ha per cell
    credit_value = carbon.calculate_carbon_credits(
        carbon_sequestration=sequestration_rate,
        area=area_ha,
        price_per_ton=50.0,
    )
    print(f"Credit value: ${float(credit_value.sum()):,.0f}/year")

    # 3. Assess wildfire risk from climate and fuel data
    print("\n3. Assessing Wildfire Risk")
    print("-" * 30)
    time = np.arange(12)
    temperature = xr.DataArray(
        np.random.uniform(15.0, 35.0, (12, 20, 20)),
        dims=("time", "lat", "lon"),
        coords={"time": time, **coords},
        attrs={"units": "degC"},
    )
    precipitation = xr.DataArray(
        np.random.uniform(0.0, 120.0, (12, 20, 20)),
        dims=("time", "lat", "lon"),
        coords={"time": time, **coords},
        attrs={"units": "mm"},
    )
    risk_result = wildfire.assess_wildfire_risk(
        temperature, precipitation, fuel_load=biomass
    )
    print(f"Mean wildfire risk: {float(risk_result['wildfire_risk'].mean()):.3f} "
          f"(range {float(risk_result['wildfire_risk'].min()):.3f}-"
          f"{float(risk_result['wildfire_risk'].max()):.3f})")
    print(f"Mean drought index: {float(risk_result['drought_index'].mean()):.3f}")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()