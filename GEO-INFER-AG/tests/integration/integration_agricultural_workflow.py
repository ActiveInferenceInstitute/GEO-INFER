"""Integration test for a complete agricultural analysis workflow."""

import pytest
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import tempfile
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

from geo_infer_ag.core.field_boundary import FieldBoundaryManager
from geo_infer_ag.core.agricultural_analysis import AgriculturalAnalysis
from geo_infer_ag.core.seasonal_analysis import SeasonalAnalysis
from geo_infer_ag.core.sustainability import SustainabilityAssessment
from geo_infer_ag.models.crop_yield import CropYieldModel
from geo_infer_ag.models.soil_health import SoilHealthModel
from geo_infer_ag.models.water_usage import WaterUsageModel


class TestAgriculturalWorkflow:
    """Integration test for a complete agricultural analysis workflow."""
    
    def test_end_to_end_workflow(self, sample_field_data, sample_soil_data, 
                                sample_weather_data, sample_time_series_data):
        """Test an end-to-end agricultural analysis workflow."""
        # Step 1: Field Boundary Management
        fbm = FieldBoundaryManager(fields=sample_field_data)
        
        # Add a new field
        new_field_id = fbm.add_field(
            geometry=Polygon([(50, 0), (50, 10), (60, 10), (60, 0)]),
            name="New Field",
            crop_type="corn"
        )
        
        # Get neighboring fields
        neighbors = fbm.get_neighboring_fields("field_1", buffer_distance=50.0)
        
        # Export fields to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.shp', delete=False) as tmp:
            output_path = tmp.name
            
        try:
            fbm.export_to_file(output_path)
            
            # Step 2: Seasonal Analysis
            sa = SeasonalAnalysis(time_series_data=sample_time_series_data)
            
            # Detect growing seasons
            growing_seasons = sa.detect_growing_season(
                variable="ndvi",
                method="threshold",
                threshold=0.3
            )
            
            # Identify phenological stages
            phenology = sa.identify_phenological_stages(
                crop_type="corn",
                variable="ndvi"
            )
            
            # Analyze temporal trends
            trends = sa.analyze_temporal_trends(
                variable="ndvi",
                period="daily"
            )
            
            # Step 3: Sustainability Assessment
            sus = SustainabilityAssessment(field_data=fbm.fields)
            
            # Assess carbon sequestration
            carbon_metrics = sus.assess_carbon_sequestration()
            
            # Assess water usage
            water_metrics = sus.assess_water_usage()
            
            # Assess soil health
            soil_metrics = sus.assess_soil_health(soil_data=sample_soil_data)
            
            # Assess biodiversity
            biodiversity_metrics = sus.assess_biodiversity()
            
            # Calculate sustainability index
            sustainability_index = sus.calculate_sustainability_index()
            
            # Step 4: Agricultural Analysis with Models
            # Create and train a yield model
            yield_model = CropYieldModel(crop_type="corn", model_type="machine_learning")
            
            # Create training data with yield
            field_data_with_yield = fbm.fields.copy()
            field_data_with_yield["yield"] = np.random.uniform(5.0, 10.0, len(field_data_with_yield))
            
            # Fit the model
            yield_model.fit(
                training_data={"field_data": field_data_with_yield},
                target_column="yield"
            )
            
            # Run agricultural analysis
            ag_analysis = AgriculturalAnalysis(model=yield_model)
            analysis_results = ag_analysis.run(
                field_data=fbm.fields,
                weather_data=sample_weather_data,
                soil_data=sample_soil_data
            )
            
            # Step 5: Soil Health Analysis
            soil_model = SoilHealthModel(model_type="index_based")
            soil_analysis = AgriculturalAnalysis(model=soil_model)
            soil_results = soil_analysis.run(
                field_data=fbm.fields,
                soil_data=sample_soil_data
            )
            
            # Step 6: Water Usage Analysis
            water_model = WaterUsageModel(crop_type="corn", model_type="reference_et")
            water_analysis = AgriculturalAnalysis(model=water_model)
            water_results = water_analysis.run(
                field_data=fbm.fields,
                weather_data=sample_weather_data
            )
            
            # Step 7: Visualization
            # Create a simple figure to test visualization capabilities
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # Plot field boundaries
            fbm.fields.plot(ax=axes[0, 0], column="crop_type", legend=True)
            axes[0, 0].set_title("Field Boundaries by Crop Type")
            
            # Plot growing season
            sa.plot_growing_season(ax=axes[0, 1])
            axes[0, 1].set_title("Growing Season Detection")
            
            # Plot yield predictions
            analysis_results.field_data.plot(
                ax=axes[1, 0],
                column="predicted_yield" if "predicted_yield" in analysis_results.field_data.columns else "field_id",
                legend=True
            )
            axes[1, 0].set_title("Predicted Yield")
            
            # Plot sustainability index
            sus.plot_sustainability_metrics(ax=axes[1, 1], metric_type="sustainability_index")
            axes[1, 1].set_title("Sustainability Index")
            
            plt.tight_layout()
            plt.close(fig)
            
            # Assertions to verify workflow execution
            assert len(fbm.fields) == len(sample_field_data) + 1  # Original fields + new field
            assert len(growing_seasons["seasons"]) > 0
            assert len(phenology["stages"]) > 0
            assert "trend_analysis" in trends
            assert carbon_metrics["total_carbon_sequestration"] > 0
            assert water_metrics["total_water_requirement"] > 0
            assert "field_data" in soil_metrics
            assert biodiversity_metrics["mean_biodiversity_score"] > 0
            assert "mean_sustainability_index" in sustainability_index
            assert "predictions" in analysis_results.results
            assert "soil_health_index" in soil_results.results.get("spatial_results", {})
            assert "water_requirement_mm" in water_results.results.get("spatial_results", {})
            
        finally:
            # Clean up temporary files
            if os.path.exists(output_path):
                # Need to remove all associated files (.dbf, .shx, etc.)
                base_path = output_path[:-4]  # Remove .shp extension
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    if os.path.exists(base_path + ext):
                        os.unlink(base_path + ext) 