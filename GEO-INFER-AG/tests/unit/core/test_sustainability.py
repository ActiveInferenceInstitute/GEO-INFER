"""Unit tests for the Sustainability Assessment core functionality."""

import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

from geo_infer_ag.core.sustainability import SustainabilityAssessment


class TestSustainabilityAssessment:
    """Test suite for SustainabilityAssessment class."""

    def test_initialization(self, sample_field_data):
        """Test initialization of SustainabilityAssessment."""
        # Test basic initialization
        sa = SustainabilityAssessment()
        assert sa.field_data is None
        assert isinstance(sa.config, dict)
        assert sa.metrics == {}
        
        # Test with field data
        sa = SustainabilityAssessment(field_data=sample_field_data)
        assert sa.field_data is sample_field_data

    def test_assess_carbon_sequestration(self, sample_field_data):
        """Test carbon sequestration assessment."""
        sa = SustainabilityAssessment()
        
        # Test with explicit field data
        metrics = sa.assess_carbon_sequestration(
            field_data=sample_field_data
        )
        
        assert "total_carbon_sequestration" in metrics
        assert metrics["total_carbon_sequestration"] > 0
        assert "mean_carbon_sequestration_per_ha" in metrics
        assert "carbon_sequestration_by_crop" in metrics
        assert "field_data" in metrics
        assert "carbon_sequestration" in metrics["field_data"].columns
        
        # Test with field data set in constructor
        sa = SustainabilityAssessment(field_data=sample_field_data)
        metrics = sa.assess_carbon_sequestration()
        
        assert "total_carbon_sequestration" in metrics
        assert metrics["total_carbon_sequestration"] > 0
        
        # Test with management practices
        management_practices = {
            "field_1": ["no_till", "cover_crops"],
            "field_2": ["reduced_till"],
            "field_3": ["conventional_till"]
        }
        
        metrics = sa.assess_carbon_sequestration(
            field_data=sample_field_data,
            management_practices=management_practices
        )
        
        assert "total_carbon_sequestration" in metrics
        assert "management_modifier" in metrics["field_data"].columns
        
        # Check field with good practices has higher modifier
        field1_modifier = metrics["field_data"].loc[
            metrics["field_data"]["field_id"] == "field_1", 
            "management_modifier"
        ].iloc[0]
        
        field3_modifier = metrics["field_data"].loc[
            metrics["field_data"]["field_id"] == "field_3", 
            "management_modifier"
        ].iloc[0]
        
        assert field1_modifier > field3_modifier
        
        # Test with no field data
        sa = SustainabilityAssessment()
        with pytest.raises(ValueError):
            sa.assess_carbon_sequestration()

    def test_assess_water_usage(self, sample_field_data):
        """Test water usage assessment."""
        sa = SustainabilityAssessment()
        
        # Test with explicit field data
        metrics = sa.assess_water_usage(
            field_data=sample_field_data
        )
        
        assert "total_water_requirement" in metrics
        assert metrics["total_water_requirement"] > 0
        assert "mean_water_requirement_per_ha" in metrics
        assert "water_requirement_by_crop" in metrics
        assert "field_data" in metrics
        assert "water_requirement_m3" in metrics["field_data"].columns
        
        # Test with field data set in constructor
        sa = SustainabilityAssessment(field_data=sample_field_data)
        metrics = sa.assess_water_usage()
        
        assert "total_water_requirement" in metrics
        assert metrics["total_water_requirement"] > 0
        
        # Test with precipitation and irrigation data
        field_data_with_water = sample_field_data.copy()
        field_data_with_water["precipitation"] = [400, 300, 450]
        field_data_with_water["irrigation"] = [100, 150, 50]
        
        metrics = sa.assess_water_usage(
            field_data=field_data_with_water,
            precipitation_column="precipitation",
            irrigation_column="irrigation"
        )
        
        assert "total_water_requirement" in metrics
        assert "mean_water_efficiency" in metrics
        assert "mean_irrigation_efficiency" in metrics
        
        # Test with no field data
        sa = SustainabilityAssessment()
        with pytest.raises(ValueError):
            sa.assess_water_usage()

    def test_assess_soil_health(self, sample_field_data, sample_soil_data):
        """Test soil health assessment."""
        sa = SustainabilityAssessment()
        
        # Test with explicit field and soil data
        metrics = sa.assess_soil_health(
            field_data=sample_field_data,
            soil_data=sample_soil_data
        )
        
        assert "field_data" in metrics
        
        # Test with field data set in constructor
        sa = SustainabilityAssessment(field_data=sample_field_data)
        metrics = sa.assess_soil_health(soil_data=sample_soil_data)
        
        assert "field_data" in metrics
        
        # Check if soil health score was calculated
        if "mean_soil_health_score" in metrics:
            assert metrics["mean_soil_health_score"] >= 0
            assert metrics["mean_soil_health_score"] <= 10
            assert "healthy_soil_percentage" in metrics
        
        # Test with management practices
        management_practices = {
            "field_1": ["no_till", "cover_crops"],
            "field_2": ["reduced_till"],
            "field_3": ["conventional_till"]
        }
        
        metrics = sa.assess_soil_health(
            field_data=sample_field_data,
            soil_data=sample_soil_data,
            management_practices=management_practices
        )
        
        assert "field_data" in metrics
        
        # Test with no field data
        sa = SustainabilityAssessment()
        with pytest.raises(ValueError):
            sa.assess_soil_health()

    def test_assess_biodiversity(self, sample_field_data):
        """Test biodiversity assessment."""
        sa = SustainabilityAssessment()
        
        # Test with explicit field data
        metrics = sa.assess_biodiversity(
            field_data=sample_field_data
        )
        
        assert "mean_biodiversity_score" in metrics
        assert metrics["mean_biodiversity_score"] >= 0
        assert metrics["mean_biodiversity_score"] <= 10
        assert "mean_edge_density" in metrics
        assert "total_edge_habitat_ha" in metrics
        assert "field_data" in metrics
        assert "biodiversity_score" in metrics["field_data"].columns
        
        # Test with field data set in constructor
        sa = SustainabilityAssessment(field_data=sample_field_data)
        metrics = sa.assess_biodiversity()
        
        assert "mean_biodiversity_score" in metrics
        assert metrics["mean_biodiversity_score"] >= 0
        assert metrics["mean_biodiversity_score"] <= 10
        
        # Test with management practices
        management_practices = {
            "field_1": ["organic_farming", "hedgerows"],
            "field_2": ["reduced_pesticide"],
            "field_3": ["conventional_till"]
        }
        
        metrics = sa.assess_biodiversity(
            field_data=sample_field_data,
            management_practices=management_practices
        )
        
        assert "mean_biodiversity_score" in metrics
        assert "biodiversity_modifier" in metrics["field_data"].columns
        
        # Check field with good practices has higher modifier
        field1_modifier = metrics["field_data"].loc[
            metrics["field_data"]["field_id"] == "field_1", 
            "biodiversity_modifier"
        ].iloc[0]
        
        field3_modifier = metrics["field_data"].loc[
            metrics["field_data"]["field_id"] == "field_3", 
            "biodiversity_modifier"
        ].iloc[0]
        
        assert field1_modifier > field3_modifier
        
        # Test with protected areas
        protected_areas = gpd.GeoDataFrame(
            {
                "name": ["Protected Area 1"],
                "geometry": [Polygon([(15, 15), (15, 25), (25, 25), (25, 15)])]
            },
            crs="EPSG:4326"
        )
        
        metrics = sa.assess_biodiversity(
            field_data=sample_field_data,
            protected_areas=protected_areas
        )
        
        assert "mean_biodiversity_score" in metrics
        assert "mean_distance_to_protected_m" in metrics
        assert "distance_to_protected_m" in metrics["field_data"].columns
        
        # Test with no field data
        sa = SustainabilityAssessment()
        with pytest.raises(ValueError):
            sa.assess_biodiversity()

    def test_calculate_sustainability_index(self, sample_field_data, sample_soil_data):
        """Test calculation of sustainability index."""
        sa = SustainabilityAssessment(field_data=sample_field_data)
        
        # Run assessments for individual components
        sa.assess_carbon_sequestration()
        sa.assess_water_usage()
        sa.assess_soil_health(soil_data=sample_soil_data)
        sa.assess_biodiversity()
        
        # Test with default weights
        index = sa.calculate_sustainability_index()
        
        assert "mean_sustainability_index" in index
        assert index["mean_sustainability_index"] >= 0
        assert index["mean_sustainability_index"] <= 10
        assert "min_sustainability_index" in index
        assert "max_sustainability_index" in index
        assert "weights" in index
        assert "available_components" in index
        assert "field_data" in index
        assert "sustainability_index" in index["field_data"].columns
        
        # Percentages should sum to 100 (allowing for floating point errors)
        total_percentage = (
            index["high_sustainability_percentage"] +
            index["medium_sustainability_percentage"] +
            index["low_sustainability_percentage"]
        )
        assert abs(total_percentage - 100) < 0.001
        
        # Test with custom weights
        custom_weights = {
            "carbon_sequestration": 0.5,
            "water_usage": 0.2,
            "soil_health": 0.2,
            "biodiversity": 0.1
        }
        
        index = sa.calculate_sustainability_index(weights=custom_weights)
        
        assert "weights" in index
        for component, weight in index["weights"].items():
            assert component in custom_weights
            # Check normalized weights approximately match expected values
            expected = custom_weights[component] / sum(custom_weights.values())
            assert abs(weight - expected) < 0.001
            
        # Test with no metrics calculated
        sa = SustainabilityAssessment(field_data=sample_field_data)
        with pytest.raises(ValueError):
            sa.calculate_sustainability_index()
            
        # Test with only one metric calculated
        sa = SustainabilityAssessment(field_data=sample_field_data)
        sa.assess_carbon_sequestration()
        index = sa.calculate_sustainability_index()
        
        assert "mean_sustainability_index" in index
        assert len(index["available_components"]) == 1
        assert index["available_components"][0] == "carbon_sequestration"

    def test_plot_sustainability_metrics(self, sample_field_data, sample_soil_data):
        """Test plotting of sustainability metrics."""
        sa = SustainabilityAssessment(field_data=sample_field_data)
        
        # Run assessments and calculate index
        sa.assess_carbon_sequestration()
        sa.assess_water_usage()
        sa.assess_soil_health(soil_data=sample_soil_data)
        sa.assess_biodiversity()
        sa.calculate_sustainability_index()
        
        # Test plotting sustainability index
        fig, ax = plt.subplots()
        result_ax = sa.plot_sustainability_metrics(ax=ax, metric_type='sustainability_index')
        
        # Check that plotting was successful
        assert result_ax is ax
        
        # Check that legend is present
        assert ax.get_legend() is not None
        
        # Clean up
        plt.close(fig)
        
        # Test plotting individual metrics
        for metric_type in ['carbon', 'water', 'soil', 'biodiversity']:
            fig, ax = plt.subplots()
            result_ax = sa.plot_sustainability_metrics(ax=ax, metric_type=metric_type)
            
            # Check that plotting was successful
            assert result_ax is ax
            
            # Clean up
            plt.close(fig)
            
        # Test without calculating index
        sa = SustainabilityAssessment(field_data=sample_field_data)
        sa.assess_carbon_sequestration()
        
        with pytest.raises(ValueError):
            sa.plot_sustainability_metrics(metric_type='sustainability_index')
            
        # Test with invalid metric type
        with pytest.raises(ValueError):
            sa.plot_sustainability_metrics(metric_type='invalid_metric') 