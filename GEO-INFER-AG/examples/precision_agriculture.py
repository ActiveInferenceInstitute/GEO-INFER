"""
GEO-INFER-AG Example: Precision Agriculture Analysis

Demonstrates the model layer of GEO-INFER-AG on a small synthetic farm:
- Soil health scoring (SoilHealthModel, index-based)
- Crop water requirements (WaterUsageModel, FAO-56 reference-ET approach)
- Carbon sequestration (CarbonSequestrationModel, IPCC Tier 1)
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from geo_infer_ag.models.carbon_sequestration import CarbonSequestrationModel
from geo_infer_ag.models.soil_health import SoilHealthModel
from geo_infer_ag.models.water_usage import WaterUsageModel


def make_farm_data():
    """Create synthetic field, soil, and weather data for two fields."""
    fields = gpd.GeoDataFrame(
        {
            "field_id": ["F1", "F2"],
            "crop_type": ["corn", "wheat"],
            "area_ha": [12.0, 10.5],
        },
        geometry=[
            Polygon([(0, 0), (0, 300), (400, 300), (400, 0)]),
            Polygon([(0, -300), (0, 0), (350, 0), (350, -300)]),
        ],
        crs="EPSG:32610",
    )

    soil_data = pd.DataFrame(
        {
            "field_id": ["F1", "F2"],
            "organic_matter": [3.2, 2.1],      # %
            "ph": [6.5, 5.9],
            "bulk_density": [1.2, 1.5],        # g/cm3
            "clay": [28.0, 18.0],              # %
        }
    )

    dates = pd.date_range("2024-06-01", periods=30, freq="D")
    rng = np.random.default_rng(7)
    weather_data = pd.DataFrame(
        {
            "temperature": 22 + 4 * np.sin(2 * np.pi * np.arange(30) / 30) + rng.normal(0, 1, 30),
            "solar_radiation": np.clip(22 + rng.normal(0, 3, 30), 5, 35),  # MJ/m2/day
            "humidity": np.clip(65 + rng.normal(0, 8, 30), 20, 100),       # %
            "wind_speed": np.clip(2.0 + rng.normal(0, 0.6, 30), 0.2, 8),   # m/s
            "precipitation": np.clip(rng.exponential(1.5, 30), 0, 20),     # mm/day
        },
        index=dates,
    )
    return fields, soil_data, weather_data


def main() -> None:
    """Run the precision agriculture example."""
    print("=" * 60)
    print("GEO-INFER-AG: Precision Agriculture Analysis")
    print("=" * 60)

    fields, soil_data, weather_data = make_farm_data()

    # Soil health: weighted index of soil indicators
    print("\n[1] Soil health (index-based model)")
    soil_model = SoilHealthModel(model_type="index_based")
    soil_result = soil_model.predict({"field_data": fields, "soil_data": soil_data})
    for indicator, scores in soil_result["indicator_scores"].items():
        values = np.atleast_1d(np.asarray(scores, dtype=float))
        print(f"  {indicator:24s} mean score {values.mean():5.2f} / 10")
    overall = soil_result["summary"]["mean_soil_health_index"]
    print(f"  Overall soil health: {overall:.2f} / 10")

    # Water usage: FAO-56 style reference-ET approach
    print("\n[2] Crop water requirement (reference-ET model)")
    water_model = WaterUsageModel(crop_type="corn", model_type="reference_et")
    water_result = water_model.predict({"field_data": fields, "weather_data": weather_data})
    print(f"  Seasonal water requirement:      "
          f"{water_result['summary']['mean_water_requirement_mm']:.0f} mm/ha")
    print(f"  Seasonal irrigation requirement: "
          f"{water_result['summary']['mean_irrigation_requirement_mm']:.0f} mm/ha")
    print(f"  Total irrigation volume:         "
          f"{water_result['summary']['total_irrigation_requirement_m3']:.0f} m3")

    # Carbon sequestration: IPCC Tier 1 defaults
    print("\n[3] Carbon sequestration (Tier 1 model)")
    carbon_model = CarbonSequestrationModel(model_type="tier1", time_horizon=20)
    carbon_result = carbon_model.predict({"field_data": fields})
    for key in ("total_soil_carbon_annual", "total_biomass_carbon_annual",
                "total_annual_sequestration", "total_co2e_sequestration"):
        print(f"  {key}: {carbon_result['summary'][key]:.2f} t/yr")

    print("\nExample complete.")


if __name__ == "__main__":
    main()
