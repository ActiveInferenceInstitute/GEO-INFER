"""
ExposureModel: Base class for modeling asset exposure to hazards.

This module provides the ExposureModel class which serves as the foundation for
representing and quantifying assets at risk in specified geographic areas.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
import os
import json


class ExposureModel:
    """
    Base class for modeling asset exposure to hazards.
    
    The ExposureModel handles:
    - Representing assets at risk (buildings, infrastructure, population)
    - Determining the spatial distribution of exposure
    - Quantifying the value of assets at risk
    """
    
    def __init__(self, exposure_type: str, params: Dict[str, Any]):
        """
        Initialize the exposure model with the specified parameters.
        
        Args:
            exposure_type (str): Type of exposure model (e.g., 'property', 'infrastructure', 'population')
            params (Dict[str, Any]): Parameters for the exposure model configuration
        """
        self.exposure_type = exposure_type
        self.params = params
        
        # Get specific parameters with defaults
        self.data_sources = params.get("data_sources", ["default"])
        self.value_type = params.get("value_type", "replacement_cost")
        self.aggregation_level = params.get("aggregation_level", "asset")
        self.include_contents = params.get("include_contents", False)
        
        # Load exposure data
        self._load_exposure_data()
    
    def _load_exposure_data(self):
        """
        Load exposure data from configured sources.
        
        This method should be overridden by subclasses to load specific exposure
        data for the particular asset types.
        """
        # This is a placeholder implementation
        # In a real implementation, this would load data from files or databases
        
        # Create a simple exposure dataset
        # In a real model, this would be loaded from external files or databases
        
        # Generate a sample exposure dataset with random properties
        # This is just for demonstration purposes
        self.exposure_data = self._generate_sample_exposure()
    
    def _generate_sample_exposure(self) -> pd.DataFrame:
        """
        Generate a sample exposure dataset for demonstration purposes.
        
        Returns:
            pd.DataFrame: DataFrame containing sample exposure data
        """
        # Number of exposure points to generate
        num_points = 1000
        
        # Create random coordinates in a bounded area
        # For example, New York City area
        min_lon, max_lon = -74.1, -73.9
        min_lat, max_lat = 40.7, 40.9
        
        longitudes = np.random.uniform(min_lon, max_lon, num_points)
        latitudes = np.random.uniform(min_lat, max_lat, num_points)
        
        # Create asset types based on exposure type
        if self.exposure_type == "property":
            asset_types = np.random.choice(
                ["residential", "commercial", "industrial", "public"], 
                num_points, 
                p=[0.6, 0.25, 0.1, 0.05]
            )
            
            # Generate property values (in thousands of dollars)
            base_values = {
                "residential": np.random.lognormal(mean=6.0, sigma=0.5, size=num_points),
                "commercial": np.random.lognormal(mean=7.0, sigma=0.7, size=num_points),
                "industrial": np.random.lognormal(mean=7.5, sigma=0.8, size=num_points),
                "public": np.random.lognormal(mean=6.5, sigma=0.6, size=num_points)
            }
            
            values = np.zeros(num_points)
            for i, asset_type in enumerate(asset_types):
                values[i] = base_values[asset_type][i]
            
            # Convert to dollars
            values = values * 1000
            
            # Generate building characteristics
            num_stories = np.random.choice([1, 2, 3, 4, 5, 10, 20], num_points, 
                                          p=[0.2, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05])
            
            year_built = np.random.randint(1900, 2023, num_points)
            
            construction_types = np.random.choice(
                ["wood", "masonry", "concrete", "steel"], 
                num_points, 
                p=[0.4, 0.3, 0.2, 0.1]
            )
            
            occupancy_types = np.random.choice(
                ["residential", "commercial", "industrial", "public"], 
                num_points, 
                p=[0.6, 0.25, 0.1, 0.05]
            )
            
            # Create DataFrame
            exposure_df = pd.DataFrame({
                "id": [f"prop_{i+1}" for i in range(num_points)],
                "longitude": longitudes,
                "latitude": latitudes,
                "type": asset_types,
                "value": values,
                "stories": num_stories,
                "year_built": year_built,
                "construction_type": construction_types,
                "occupancy_type": occupancy_types
            })
            
        elif self.exposure_type == "population":
            # Generate population data
            values = np.random.lognormal(mean=5.0, sigma=1.0, size=num_points)
            
            # Generate demographic information
            median_age = np.random.normal(40, 10, num_points)
            median_age = np.maximum(0, median_age)  # Ensure non-negative
            
            median_income = np.random.lognormal(mean=10.5, sigma=0.5, size=num_points)
            
            social_vulnerability = np.random.beta(2, 5, num_points)  # Higher values indicate higher vulnerability
            
            population_density = values / np.random.uniform(0.1, 2.0, num_points)  # people per sq km
            
            # Create DataFrame
            exposure_df = pd.DataFrame({
                "id": [f"pop_{i+1}" for i in range(num_points)],
                "longitude": longitudes,
                "latitude": latitudes,
                "type": "population",
                "value": values,
                "median_age": median_age,
                "median_income": median_income,
                "social_vulnerability": social_vulnerability,
                "population_density": population_density
            })
            
        elif self.exposure_type == "infrastructure":
            # Generate infrastructure data
            asset_types = np.random.choice(
                ["road", "bridge", "power_line", "water_supply", "communication"], 
                num_points, 
                p=[0.4, 0.1, 0.2, 0.2, 0.1]
            )
            
            # Generate infrastructure values
            base_values = {
                "road": np.random.lognormal(mean=6.0, sigma=0.6, size=num_points),
                "bridge": np.random.lognormal(mean=7.0, sigma=0.8, size=num_points),
                "power_line": np.random.lognormal(mean=5.5, sigma=0.5, size=num_points),
                "water_supply": np.random.lognormal(mean=5.8, sigma=0.5, size=num_points),
                "communication": np.random.lognormal(mean=5.5, sigma=0.6, size=num_points)
            }
            
            values = np.zeros(num_points)
            for i, asset_type in enumerate(asset_types):
                values[i] = base_values[asset_type][i]
            
            # Convert to thousands of dollars
            values = values * 1000
            
            # Generate infrastructure characteristics
            year_built = np.random.randint(1950, 2023, num_points)
            
            condition = np.random.choice(
                ["excellent", "good", "fair", "poor"], 
                num_points, 
                p=[0.1, 0.4, 0.3, 0.2]
            )
            
            criticality = np.random.choice(
                ["high", "medium", "low"], 
                num_points, 
                p=[0.2, 0.5, 0.3]
            )
            
            # Create DataFrame
            exposure_df = pd.DataFrame({
                "id": [f"infra_{i+1}" for i in range(num_points)],
                "longitude": longitudes,
                "latitude": latitudes,
                "type": asset_types,
                "value": values,
                "year_built": year_built,
                "condition": condition,
                "criticality": criticality
            })
        
        else:
            # Default exposure data
            exposure_df = pd.DataFrame({
                "id": [f"asset_{i+1}" for i in range(num_points)],
                "longitude": longitudes,
                "latitude": latitudes,
                "type": "generic",
                "value": np.random.lognormal(mean=5.0, sigma=1.0, size=num_points) * 1000
            })
        
        return exposure_df
    
    def get_exposure_for_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the exposure affected by a hazard event.
        
        Args:
            event (Dict[str, Any]): Hazard event information
            
        Returns:
            List[Dict[str, Any]]: List of exposed assets with their properties
        """
        # Extract event footprint bounds
        footprint = event.get("footprint", {})
        bounds = footprint.get("bounds", {})
        
        min_lon = bounds.get("min_lon", -180)
        max_lon = bounds.get("max_lon", 180)
        min_lat = bounds.get("min_lat", -90)
        max_lat = bounds.get("max_lat", 90)
        
        # Filter exposure data to assets within the event footprint
        if self.exposure_data is not None:
            filtered_exposure = self.exposure_data[
                (self.exposure_data["longitude"] >= min_lon) &
                (self.exposure_data["longitude"] <= max_lon) &
                (self.exposure_data["latitude"] >= min_lat) &
                (self.exposure_data["latitude"] <= max_lat)
            ]
            
            # For each asset, calculate the hazard intensity at its location
            exposed_assets = []
            
            for _, asset in filtered_exposure.iterrows():
                # Create a dictionary for the asset
                asset_dict = asset.to_dict()
                
                # Add the hazard intensity at this asset location
                asset_dict["intensity_at_asset"] = self._calculate_intensity_at_location(
                    event, asset["latitude"], asset["longitude"]
                )
                
                exposed_assets.append(asset_dict)
            
            return exposed_assets
        
        # If no exposure data is loaded, return an empty list
        return []
    
    def _calculate_intensity_at_location(self, event: Dict[str, Any], 
                                        latitude: float, longitude: float) -> float:
        """
        Calculate the hazard intensity at a specific location for an event.
        
        Args:
            event (Dict[str, Any]): Hazard event
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            
        Returns:
            float: Hazard intensity at the specified location
        """
        # Extract event footprint
        footprint = event.get("footprint", {})
        
        # Check if the location is within the footprint bounds
        bounds = footprint.get("bounds", {})
        if (bounds.get("min_lon", 0) <= longitude <= bounds.get("max_lon", 0) and
            bounds.get("min_lat", 0) <= latitude <= bounds.get("max_lat", 0)):
            
            # Calculate grid indices
            lon_range = bounds.get("max_lon", 0) - bounds.get("min_lon", 0)
            lat_range = bounds.get("max_lat", 0) - bounds.get("min_lat", 0)
            
            intensity_values = footprint.get("intensity_values", [[0]])
            
            # Handle the case where intensity_values is a nested list (2D grid)
            if isinstance(intensity_values, list) and intensity_values and isinstance(intensity_values[0], list):
                grid_size = len(intensity_values)
                
                # Convert lat/lon to grid indices
                lon_idx = int((longitude - bounds.get("min_lon", 0)) / lon_range * (grid_size - 1))
                lat_idx = int((latitude - bounds.get("min_lat", 0)) / lat_range * (grid_size - 1))
                
                # Ensure indices are within bounds
                lon_idx = max(0, min(grid_size - 1, lon_idx))
                lat_idx = max(0, min(grid_size - 1, lat_idx))
                
                # Return the intensity value at the calculated indices
                return intensity_values[lat_idx][lon_idx]
            
            # Simple case - constant intensity across the footprint
            else:
                return float(intensity_values[0]) if intensity_values else 0.0
        
        # Location is outside the footprint bounds
        return 0.0
    
    def calculate_total_exposure(self, bounds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate the total exposure within optional geographic bounds.
        
        Args:
            bounds (Dict[str, float], optional): Geographic bounds (min_lon, max_lon, min_lat, max_lat)
            
        Returns:
            Dict[str, Any]: Dictionary with total exposure statistics
        """
        # Filter exposure data to assets within the specified bounds
        if bounds and self.exposure_data is not None:
            min_lon = bounds.get("min_lon", -180)
            max_lon = bounds.get("max_lon", 180)
            min_lat = bounds.get("min_lat", -90)
            max_lat = bounds.get("max_lat", 90)
            
            filtered_exposure = self.exposure_data[
                (self.exposure_data["longitude"] >= min_lon) &
                (self.exposure_data["longitude"] <= max_lon) &
                (self.exposure_data["latitude"] >= min_lat) &
                (self.exposure_data["latitude"] <= max_lat)
            ]
        else:
            filtered_exposure = self.exposure_data
        
        # If no exposure data is available, return zeros
        if filtered_exposure is None or len(filtered_exposure) == 0:
            return {
                "total_value": 0,
                "count": 0,
                "by_type": {}
            }
        
        # Calculate total value
        total_value = filtered_exposure["value"].sum()
        count = len(filtered_exposure)
        
        # Calculate value by type
        by_type = {}
        for asset_type, group in filtered_exposure.groupby("type"):
            by_type[asset_type] = {
                "value": group["value"].sum(),
                "count": len(group)
            }
        
        return {
            "total_value": total_value,
            "count": count,
            "by_type": by_type
        }
    
    def get_exposure_at_location(self, latitude: float, longitude: float, 
                                radius: float = 1.0) -> Dict[str, Any]:
        """
        Get exposure within a radius of a specific location.
        
        Args:
            latitude (float): Latitude of the center point
            longitude (float): Longitude of the center point
            radius (float, optional): Radius in kilometers. Default is 1.0 km.
            
        Returns:
            Dict[str, Any]: Dictionary with exposure at the location
        """
        if self.exposure_data is None or len(self.exposure_data) == 0:
            return {
                "total_value": 0,
                "count": 0,
                "assets": []
            }
        
        # Calculate distance from each asset to the specified location
        distances = self._calculate_distances(latitude, longitude)
        
        # Convert radius from kilometers to degrees (approximate)
        radius_deg = radius / 111.0  # 1 degree is approximately 111 km
        
        # Filter to assets within the radius
        mask = distances <= radius_deg
        filtered_exposure = self.exposure_data[mask].copy()
        
        # Add distance to each asset
        filtered_exposure["distance_km"] = distances[mask] * 111.0
        
        # Return results
        return {
            "total_value": filtered_exposure["value"].sum(),
            "count": len(filtered_exposure),
            "assets": filtered_exposure.to_dict(orient="records")
        }
    
    def _calculate_distances(self, latitude: float, longitude: float) -> np.ndarray:
        """
        Calculate distances from each asset to a specified location.
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            
        Returns:
            np.ndarray: Array of distances in degrees
        """
        # Simple Euclidean distance in degrees
        # This is an approximation and doesn't account for Earth's curvature
        # For more precise calculations, use Haversine formula
        lat_diff = self.exposure_data["latitude"] - latitude
        lon_diff = self.exposure_data["longitude"] - longitude
        
        distances = np.sqrt(lat_diff**2 + lon_diff**2)
        
        return distances
    
    def save_exposure_data(self, output_file: str):
        """
        Save exposure data to a CSV file.
        
        Args:
            output_file (str): Path to the output file
        """
        if self.exposure_data is not None:
            # Create directory if it doesn't exist
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Save to CSV
            self.exposure_data.to_csv(output_file, index=False)
    
    def load_exposure_data(self, input_file: str):
        """
        Load exposure data from a CSV file.
        
        Args:
            input_file (str): Path to the input file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Exposure data file not found: {input_file}")
        
        # Load from CSV
        self.exposure_data = pd.read_csv(input_file)


class PropertyExposureModel(ExposureModel):
    """
    Specialized exposure model for property (buildings and contents).
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the property exposure model with the specified parameters.
        
        Args:
            params (Dict[str, Any]): Parameters for the property exposure model
        """
        super().__init__(exposure_type="property", params=params)
        
        # Property-specific parameters
        self.include_contents = params.get("include_contents", True)
        self.contents_value_factor = params.get("contents_value_factor", 0.5)  # Contents value as fraction of building value
    
    def get_exposure_for_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the property exposure affected by a hazard event.
        
        Args:
            event (Dict[str, Any]): Hazard event information
            
        Returns:
            List[Dict[str, Any]]: List of exposed properties with their characteristics
        """
        # Get basic exposure from parent method
        exposed_assets = super().get_exposure_for_event(event)
        
        # For property exposure, add contents value if configured
        if self.include_contents:
            for asset in exposed_assets:
                # Add contents value based on building value
                asset["contents_value"] = asset["value"] * self.contents_value_factor
                
                # Add combined value
                asset["total_value"] = asset["value"] + asset["contents_value"]
        
        return exposed_assets


class InfrastructureExposureModel(ExposureModel):
    """
    Specialized exposure model for infrastructure.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the infrastructure exposure model with the specified parameters.
        
        Args:
            params (Dict[str, Any]): Parameters for the infrastructure exposure model
        """
        super().__init__(exposure_type="infrastructure", params=params)
        
        # Infrastructure-specific parameters
        self.infrastructure_types = params.get("types", ["transportation", "utilities", "communications"])
    
    def get_exposure_for_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the infrastructure exposure affected by a hazard event.
        
        Args:
            event (Dict[str, Any]): Hazard event information
            
        Returns:
            List[Dict[str, Any]]: List of exposed infrastructure with their characteristics
        """
        # Get basic exposure from parent method
        exposed_assets = super().get_exposure_for_event(event)
        
        # For infrastructure exposure, add network connectivity if available
        # This is a placeholder - in a real model, this would implement more sophisticated
        # network analysis to account for interdependencies
        
        return exposed_assets


class PopulationExposureModel(ExposureModel):
    """
    Specialized exposure model for population.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the population exposure model with the specified parameters.
        
        Args:
            params (Dict[str, Any]): Parameters for the population exposure model
        """
        super().__init__(exposure_type="population", params=params)
        
        # Population-specific parameters
        self.time_of_day_scenarios = params.get("time_of_day_scenarios", ["day", "night", "commute"])
        self.current_scenario = params.get("current_scenario", "day")
    
    def _load_exposure_data(self):
        """
        Load population-specific exposure data.
        """
        super()._load_exposure_data()
        
        # If we have basic population data, create time-of-day variants
        if self.exposure_data is not None and "value" in self.exposure_data.columns:
            # Create time-of-day population distributions
            # These are simplistic adjustments - in a real model, these would be based on
            # commuting patterns, land use, etc.
            
            # Create a copy to avoid modifying the original
            base_population = self.exposure_data["value"].values
            
            # Day scenario: Shift population from residential to commercial/industrial areas
            day_factors = {
                "residential": 0.7,  # 70% of people at home during day
                "commercial": 1.5,   # More people in commercial areas during day
                "industrial": 1.3,   # More people in industrial areas during day
                "public": 1.4        # More people in public areas during day
            }
            
            # Night scenario: Most people at home
            night_factors = {
                "residential": 1.2,  # More people at home during night
                "commercial": 0.2,   # Fewer people in commercial areas during night
                "industrial": 0.1,   # Fewer people in industrial areas during night
                "public": 0.3        # Fewer people in public areas during night
            }
            
            # Commute scenario: People on transportation networks
            commute_factors = {
                "residential": 0.8,  # Some people leaving/returning home
                "commercial": 0.9,   # Some people arriving/leaving work
                "industrial": 0.9,   # Some people arriving/leaving work
                "public": 1.1        # More people in transit areas
            }
            
            # Apply factors based on asset type if available
            if "type" in self.exposure_data.columns:
                self.exposure_data["day_population"] = base_population.copy()
                self.exposure_data["night_population"] = base_population.copy()
                self.exposure_data["commute_population"] = base_population.copy()
                
                for asset_type in day_factors:
                    mask = self.exposure_data["type"] == asset_type
                    self.exposure_data.loc[mask, "day_population"] = base_population[mask] * day_factors[asset_type]
                    self.exposure_data.loc[mask, "night_population"] = base_population[mask] * night_factors[asset_type]
                    self.exposure_data.loc[mask, "commute_population"] = base_population[mask] * commute_factors[asset_type]
            
            # If no type column, apply a general adjustment
            else:
                self.exposure_data["day_population"] = base_population
                self.exposure_data["night_population"] = base_population
                self.exposure_data["commute_population"] = base_population
    
    def get_exposure_for_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get the population exposure affected by a hazard event.
        
        Args:
            event (Dict[str, Any]): Hazard event information
            
        Returns:
            List[Dict[str, Any]]: List of exposed population with their characteristics
        """
        # Get basic exposure from parent method
        exposed_assets = super().get_exposure_for_event(event)
        
        # For population exposure, use the appropriate time-of-day population
        for asset in exposed_assets:
            if f"{self.current_scenario}_population" in asset:
                # Use the current scenario population as the value
                asset["value"] = asset[f"{self.current_scenario}_population"]
            
            # Add evacuation information if available
            # This is a placeholder - in a real model, this would implement more sophisticated
            # evacuation modeling based on warning time, mobility, etc.
            
            # Simple evacuation model - higher social vulnerability means less effective evacuation
            if "social_vulnerability" in asset:
                # Evacuation effectiveness is inversely related to social vulnerability
                evacuation_effectiveness = 1.0 - (0.8 * asset["social_vulnerability"])
                asset["evacuation_effectiveness"] = evacuation_effectiveness
                
                # Adjusted population after evacuation (for advanced warning events like hurricanes)
                if event.get("hazard_type") in ["hurricane", "flood"] and event.get("warning_time", 0) > 24:
                    asset["adjusted_value"] = asset["value"] * (1.0 - evacuation_effectiveness)
                else:
                    asset["adjusted_value"] = asset["value"]
        
        return exposed_assets
    
    def set_time_scenario(self, scenario: str):
        """
        Set the current time-of-day scenario for population exposure.
        
        Args:
            scenario (str): Scenario name ("day", "night", "commute")
        """
        if scenario in self.time_of_day_scenarios:
            self.current_scenario = scenario
        else:
            raise ValueError(f"Invalid time scenario: {scenario}. Valid options are {self.time_of_day_scenarios}")
    
    def calculate_total_exposure(self, bounds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate the total population exposure within optional geographic bounds.
        
        Args:
            bounds (Dict[str, float], optional): Geographic bounds (min_lon, max_lon, min_lat, max_lat)
            
        Returns:
            Dict[str, Any]: Dictionary with total exposure statistics for each time scenario
        """
        # Get basic exposure statistics
        basic_stats = super().calculate_total_exposure(bounds)
        
        # Add time-of-day statistics if available
        if self.exposure_data is not None and "day_population" in self.exposure_data.columns:
            # Filter exposure data to assets within the specified bounds
            if bounds:
                min_lon = bounds.get("min_lon", -180)
                max_lon = bounds.get("max_lon", 180)
                min_lat = bounds.get("min_lat", -90)
                max_lat = bounds.get("max_lat", 90)
                
                filtered_exposure = self.exposure_data[
                    (self.exposure_data["longitude"] >= min_lon) &
                    (self.exposure_data["longitude"] <= max_lon) &
                    (self.exposure_data["latitude"] >= min_lat) &
                    (self.exposure_data["latitude"] <= max_lat)
                ]
            else:
                filtered_exposure = self.exposure_data
            
            # Calculate total for each time scenario
            time_scenarios = {}
            for scenario in self.time_of_day_scenarios:
                scenario_col = f"{scenario}_population"
                if scenario_col in filtered_exposure.columns:
                    time_scenarios[scenario] = {
                        "total_population": filtered_exposure[scenario_col].sum(),
                        "count": len(filtered_exposure)
                    }
            
            basic_stats["time_scenarios"] = time_scenarios
        
        return basic_stats 