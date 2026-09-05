"""
Basic agricultural analysis example using GEO-INFER-AG.

This example demonstrates:
- Field boundary management (FieldBoundaryManager)
- Crop yield modeling (CropYieldModel: fit + predict)
- Seasonal analysis (SeasonalAnalysis: growing season + trends)
- Sustainability assessment (SustainabilityAssessment)
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

from geo_infer_ag.core.field_boundary import FieldBoundaryManager
from geo_infer_ag.core.seasonal_analysis import SeasonalAnalysis
from geo_infer_ag.core.sustainability import SustainabilityAssessment
from geo_infer_ag.models.crop_yield import CropYieldModel


def make_field_gdf() -> gpd.GeoDataFrame:
    """Create a small synthetic field dataset in a projected (metric) CRS."""
    return gpd.GeoDataFrame(
        {
            "field_id": ["field_001", "field_002"],
            "name": ["North Field", "South Field"],
            "crop_type": ["corn", "soybean"],
            "ph": [6.5, 6.2],
            "nitrogen_kg_ha": [160.0, 60.0],
            "precip_mm": [520.0, 480.0],
        },
        geometry=[
            Polygon([(0, 0), (0, 300), (400, 300), (400, 0)]),      # 12 ha
            Polygon([(0, -300), (0, 0), (350, 0), (350, -300)]),    # 10.5 ha
        ],
        crs="EPSG:32610",  # UTM zone 10N, meters
    )


def make_ndvi_series() -> pd.Series:
    """Create a daily NDVI time series with a clear growing season."""
    dates = pd.date_range("2024-04-01", periods=180, freq="D")
    days = np.arange(len(dates))
    ndvi = 0.15 + 0.65 * np.sin(np.pi * days / 150) ** 2
    ndvi += np.random.default_rng(42).normal(0, 0.02, len(dates))
    return pd.Series(np.clip(ndvi, 0.05, 0.95), index=dates, name="ndvi")


def main() -> None:
    """Run the basic agricultural analysis example."""
    print("=" * 60)
    print("GEO-INFER-AG: Basic Agricultural Analysis Example")
    print("=" * 60)

    # Step 1: Field boundary management
    print("\n[Step 1] Field boundary management")
    fields = make_field_gdf()
    manager = FieldBoundaryManager(fields=fields, crs="EPSG:32610")
    print(manager.fields[["field_id", "name", "crop_type", "area_ha"]].to_string(index=False))

    north = manager.get_field("field_001")
    print(f"Retrieved '{north['name']}' ({north['area_ha']:.2f} ha of {north['crop_type']})")

    # Step 2: Crop yield modeling (fit on historical fields, predict on new)
    print("\n[Step 2] Crop yield modeling (corn)")
    historical = pd.DataFrame(
        {
            "ph": [6.1, 6.4, 6.8, 7.0, 6.3, 6.6],
            "nitrogen_kg_ha": [120.0, 150.0, 170.0, 180.0, 140.0, 165.0],
            "precip_mm": [450.0, 500.0, 540.0, 560.0, 480.0, 530.0],
            "yield": [9.0, 10.2, 11.4, 11.8, 9.8, 11.0],  # t/ha
        }
    )
    crop_model = CropYieldModel(crop_type="corn", model_type="machine_learning")
    crop_model.fit({"field_data": historical}, target_column="yield")

    targets = fields[fields["crop_type"] == "corn"].drop(columns="geometry")
    prediction = crop_model.predict({"field_data": targets})
    print(f"Predicted yield for {len(targets)} corn field(s):")
    print(f"  mean {prediction['summary']['mean_yield']:.2f} t/ha "
          f"(range {prediction['summary']['min_yield']:.2f}-{prediction['summary']['max_yield']:.2f})")

    # Step 3: Seasonal analysis
    print("\n[Step 3] Seasonal analysis")
    seasonal = SeasonalAnalysis(time_series_data=pd.DataFrame({"ndvi": make_ndvi_series()}))
    season = seasonal.detect_growing_season(variable="ndvi", method="threshold", threshold=0.3)
    detected = season["seasons"][0]
    print(f"Growing season: {detected['start_date'].date()} to {detected['end_date'].date()} "
          f"({detected['length_days']} days, peak NDVI {detected['peak_value']:.2f})")

    trends = seasonal.analyze_temporal_trends(variable="ndvi", period="monthly")
    print(f"Monthly NDVI mean: {trends['statistics']['mean']:.2f} "
          f"(trend slope {trends['trend_analysis']['slope']:.4f}/month)")

    # Step 4: Sustainability assessment
    print("\n[Step 4] Sustainability assessment")
    assessment = SustainabilityAssessment(field_data=manager.fields)
    carbon = assessment.assess_carbon_sequestration()
    water = assessment.assess_water_usage()
    print(f"Total carbon sequestration: {carbon['total_carbon_sequestration']:.1f} t C/yr "
          f"({carbon['mean_carbon_sequestration_per_ha']:.2f} t/ha mean)")
    print(f"Total water requirement:    {water['total_water_requirement']:.0f} m3/yr "
          f"({water['mean_water_requirement_per_ha']:.0f} m3/ha mean)")

    print("\nExample complete.")


if __name__ == "__main__":
    main()
