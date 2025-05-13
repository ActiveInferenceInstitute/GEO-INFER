"""
HazardModel: Base class for hazard modeling and event generation.

This module provides the HazardModel class which serves as the foundation for
modeling different natural hazards, generating hazard events, and calculating 
hazard intensities at different locations.
"""

import abc
from typing import Dict, List, Any, Optional

import numpy as np


class HazardModel:
    """
    Base class for modeling natural hazards and generating hazard events.
    
    The HazardModel handles:
    - Generating stochastic hazard events
    - Calculating hazard intensities at specific locations
    - Applying climate change and other future projection scenarios
    """
    
    def __init__(self, hazard_type: str, params: Dict[str, Any]):
        """
        Initialize the hazard model with the specified parameters.
        
        Args:
            hazard_type (str): Type of hazard (e.g., 'flood', 'earthquake', 'hurricane')
            params (Dict[str, Any]): Parameters for the hazard model configuration
        """
        self.hazard_type = hazard_type
        self.params = params
        
        # Get specific parameters with defaults
        self.return_periods = params.get("return_periods", [10, 25, 50, 100, 500])
        self.data_source = params.get("data_source", "default")
        self.include_climate_change = params.get("include_climate_change", False)
        self.climate_scenario = params.get("climate_scenario", "rcp4.5")
        
        # Model-specific attributes to be set by subclasses
        self.intensity_measure_type = self._get_intensity_measure_type()
        self.intensity_measure_units = self._get_intensity_measure_units()
        
        # Load model data
        self._load_model_data()
    
    def _get_intensity_measure_type(self) -> str:
        """
        Get the appropriate intensity measure type for this hazard.
        
        Returns:
            str: Intensity measure type (e.g., 'depth', 'pga', 'wind_speed')
        """
        # Default mappings for common hazard types
        intensity_measure_map = {
            "flood": "depth",
            "earthquake": "pga",
            "hurricane": "wind_speed",
            "wildfire": "fireline_intensity",
            "drought": "spi",
            "landslide": "displacement",
            "tsunami": "wave_height",
            "tornado": "wind_speed",
            "hail": "hail_size",
            "winter_storm": "snow_depth"
        }
        
        return intensity_measure_map.get(self.hazard_type, "intensity")
    
    def _get_intensity_measure_units(self) -> str:
        """
        Get the appropriate units for the intensity measure of this hazard.
        
        Returns:
            str: Units for intensity measure (e.g., 'm', 'g', 'm/s')
        """
        # Default mappings for common hazard types
        unit_map = {
            "flood": "m",
            "earthquake": "g",
            "hurricane": "m/s",
            "wildfire": "kW/m",
            "drought": "index",
            "landslide": "m",
            "tsunami": "m",
            "tornado": "m/s",
            "hail": "mm",
            "winter_storm": "cm"
        }
        
        return unit_map.get(self.hazard_type, "")
    
    def _load_model_data(self):
        """
        Load necessary data for the hazard model.
        
        This method should be overridden by subclasses to load specific data
        required for modeling the particular hazard type.
        """
        # This is a placeholder implementation
        # In a real implementation, this would load data from files or databases
        self.model_data = {
            "historical_events": [],
            "hazard_map": None,
            "footprints": [],
            "event_rate": 1.0 / np.mean(self.return_periods),
            "climate_factors": self._get_climate_factors() if self.include_climate_change else None
        }
    
    def _get_climate_factors(self) -> Dict[str, float]:
        """
        Get climate change adjustment factors based on the specified scenario.
        
        Returns:
            Dict[str, float]: Climate change adjustment factors
        """
        # Placeholder implementation - in a real model, these would be loaded from
        # climate projection datasets or models
        climate_scenarios = {
            "rcp2.6": {
                "intensity_factor": 1.05,
                "frequency_factor": 1.1,
                "time_horizon": 2050
            },
            "rcp4.5": {
                "intensity_factor": 1.15,
                "frequency_factor": 1.2,
                "time_horizon": 2050
            },
            "rcp8.5": {
                "intensity_factor": 1.3,
                "frequency_factor": 1.4,
                "time_horizon": 2050
            }
        }
        
        # Return factors for the specified scenario, or default values
        return climate_scenarios.get(self.climate_scenario, {
            "intensity_factor": 1.0,
            "frequency_factor": 1.0,
            "time_horizon": 2050
        })
    
    def generate_events(self, num_events: int) -> List[Dict[str, Any]]:
        """
        Generate a specified number of stochastic hazard events.
        
        Args:
            num_events (int): Number of events to generate
            
        Returns:
            List[Dict[str, Any]]: List of generated hazard events
        """
        # Placeholder implementation for generating stochastic events
        events = []
        
        # Generate random events
        # In a real model, this would use more sophisticated methods specific to each hazard
        for i in range(num_events):
            # Create a unique event ID
            event_id = f"{self.hazard_type}_{i+1}"
            
            # Randomly select a return period
            return_period_idx = np.random.randint(0, len(self.return_periods))
            return_period = self.return_periods[return_period_idx]
            
            # Calculate exceedance probability
            exceedance_prob = 1.0 / return_period
            
            # Generate an event footprint - this would be more complex in a real model
            # For now, we'll create a simple placeholder
            event = {
                "id": event_id,
                "hazard_type": self.hazard_type,
                "return_period": return_period,
                "exceedance_probability": exceedance_prob,
                "intensity_measure_type": self.intensity_measure_type,
                "intensity_measure_units": self.intensity_measure_units,
                "footprint": self._generate_footprint(return_period),
                "metadata": {
                    "data_source": self.data_source,
                    "climate_adjusted": self.include_climate_change,
                    "climate_scenario": self.climate_scenario if self.include_climate_change else None
                }
            }
            
            events.append(event)
        
        return events
    
    def _generate_footprint(self, return_period: float) -> Dict[str, Any]:
        """
        Generate a hazard footprint for a given return period.
        
        A footprint represents the spatial distribution of hazard intensity.
        
        Args:
            return_period (float): Return period for the event
            
        Returns:
            Dict[str, Any]: Hazard footprint data
        """
        # This is a placeholder - in a real model, this would generate
        # a spatial distribution of hazard intensity based on statistical models
        
        # For simplicity, we'll return a placeholder footprint
        # In a real implementation, this would be a raster or grid of intensity values
        footprint = {
            "type": "grid",
            "resolution": "1km",
            "bounds": {
                "min_lon": -75.0,
                "max_lon": -74.0,
                "min_lat": 40.0,
                "max_lat": 41.0
            },
            "intensity_values": np.random.lognormal(
                mean=np.log(return_period/100),
                sigma=0.5,
                size=(100, 100)
            ).tolist()
        }
        
        # Apply climate change adjustment if enabled
        if self.include_climate_change and self.model_data.get("climate_factors"):
            intensity_factor = self.model_data["climate_factors"].get("intensity_factor", 1.0)
            
            # Adjust intensity values
            for i in range(len(footprint["intensity_values"])):
                for j in range(len(footprint["intensity_values"][i])):
                    footprint["intensity_values"][i][j] *= intensity_factor
        
        return footprint
    
    def get_intensity_at_location(self, event: Dict[str, Any], 
                                 latitude: float, longitude: float) -> float:
        """
        Get the hazard intensity at a specific location for a given event.
        
        Args:
            event (Dict[str, Any]): Hazard event
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            
        Returns:
            float: Hazard intensity at the specified location
        """
        # This is a placeholder - in a real model, this would interpolate
        # values from the hazard footprint raster
        
        # Get the footprint
        footprint = event.get("footprint", {})
        
        # Check if the location is within the footprint bounds
        bounds = footprint.get("bounds", {})
        if (bounds.get("min_lon", 0) <= longitude <= bounds.get("max_lon", 0) and
            bounds.get("min_lat", 0) <= latitude <= bounds.get("max_lat", 0)):
            
            # Calculate grid indices
            lon_range = bounds.get("max_lon", 0) - bounds.get("min_lon", 0)
            lat_range = bounds.get("max_lat", 0) - bounds.get("min_lat", 0)
            
            intensity_values = footprint.get("intensity_values", [[0]])
            grid_size = len(intensity_values)
            
            # Convert lat/lon to grid indices
            lon_idx = int((longitude - bounds.get("min_lon", 0)) / lon_range * (grid_size - 1))
            lat_idx = int((latitude - bounds.get("min_lat", 0)) / lat_range * (grid_size - 1))
            
            # Ensure indices are within bounds
            lon_idx = max(0, min(grid_size - 1, lon_idx))
            lat_idx = max(0, min(grid_size - 1, lat_idx))
            
            # Return the intensity value at the calculated indices
            return intensity_values[lat_idx][lon_idx]
        
        # Location is outside the footprint bounds
        return 0.0
    
    def get_return_period_map(self, return_period: float) -> Dict[str, Any]:
        """
        Get a hazard map for a specific return period.
        
        Args:
            return_period (float): Return period for the hazard map
            
        Returns:
            Dict[str, Any]: Hazard map data
        """
        # This is a placeholder - in a real model, this would return
        # a hazard map for the specified return period
        
        # Generate a simple hazard map
        hazard_map = {
            "type": "grid",
            "return_period": return_period,
            "resolution": "1km",
            "bounds": {
                "min_lon": -75.0,
                "max_lon": -74.0,
                "min_lat": 40.0,
                "max_lat": 41.0
            },
            "intensity_values": np.random.lognormal(
                mean=np.log(return_period/100),
                sigma=0.5,
                size=(100, 100)
            ).tolist()
        }
        
        return hazard_map


class FloodModel(HazardModel):
    """
    Model for flood hazards, including riverine, coastal, and pluvial flooding.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the flood model with the specified parameters.
        
        Args:
            params (Dict[str, Any]): Parameters for the flood model configuration
        """
        super().__init__(hazard_type="flood", params=params)
        
        # Flood-specific parameters
        self.flood_type = params.get("type", "riverine")
        self.dem_resolution = params.get("dem_resolution", 30)  # in meters
    
    def _load_model_data(self):
        """
        Load necessary data for the flood model.
        """
        super()._load_model_data()
        
        # Add flood-specific data
        self.model_data.update({
            "dem": None,  # Digital Elevation Model would be loaded here
            "river_network": None,  # River network data would be loaded here
            "gauge_data": None,  # Stream gauge data would be loaded here
            "flood_plains": None  # Flood plain delineations would be loaded here
        })
    
    def _generate_footprint(self, return_period: float) -> Dict[str, Any]:
        """
        Generate a flood footprint for a given return period.
        
        Args:
            return_period (float): Return period for the event
            
        Returns:
            Dict[str, Any]: Flood footprint data
        """
        # Call the parent method to get the basic footprint
        footprint = super()._generate_footprint(return_period)
        
        # Add flood-specific data to the footprint
        footprint.update({
            "flood_type": self.flood_type,
            "water_depth": True,  # Indicates that intensity values represent water depth
            "flow_velocity": False  # Indicates that flow velocity is not included
        })
        
        return footprint


class EarthquakeModel(HazardModel):
    """
    Model for earthquake hazards, including ground shaking and secondary perils.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the earthquake model with the specified parameters.
        
        Args:
            params (Dict[str, Any]): Parameters for the earthquake model configuration
        """
        super().__init__(hazard_type="earthquake", params=params)
        
        # Earthquake-specific parameters
        self.eq_type = params.get("type", "probabilistic")
        self.include_secondary_perils = params.get("include_secondary_perils", False)
        self.secondary_perils = params.get("secondary_perils", ["liquefaction", "landslide"])
    
    def _load_model_data(self):
        """
        Load necessary data for the earthquake model.
        """
        super()._load_model_data()
        
        # Add earthquake-specific data
        self.model_data.update({
            "fault_lines": None,  # Fault line data would be loaded here
            "historical_earthquakes": None,  # Historical earthquake data would be loaded here
            "soil_conditions": None,  # Soil condition data would be loaded here
            "vs30": None  # Vs30 data (shear wave velocity) would be loaded here
        })
    
    def _generate_footprint(self, return_period: float) -> Dict[str, Any]:
        """
        Generate an earthquake footprint for a given return period.
        
        Args:
            return_period (float): Return period for the event
            
        Returns:
            Dict[str, Any]: Earthquake footprint data
        """
        # Call the parent method to get the basic footprint
        footprint = super()._generate_footprint(return_period)
        
        # Add earthquake-specific data to the footprint
        footprint.update({
            "eq_type": self.eq_type,
            "magnitude": 4.0 + np.random.exponential(scale=1.0),  # Random magnitude
            "depth": 5.0 + np.random.exponential(scale=10.0),  # Random depth in km
            "epicenter": {
                "latitude": footprint["bounds"]["min_lat"] + (footprint["bounds"]["max_lat"] - footprint["bounds"]["min_lat"]) * np.random.random(),
                "longitude": footprint["bounds"]["min_lon"] + (footprint["bounds"]["max_lon"] - footprint["bounds"]["min_lon"]) * np.random.random()
            }
        })
        
        # Add secondary peril footprints if enabled
        if self.include_secondary_perils:
            secondary_footprints = {}
            for peril in self.secondary_perils:
                # Generate simple secondary peril footprints
                # In a real model, these would be more sophisticated
                secondary_footprints[peril] = {
                    "type": "grid",
                    "resolution": "1km",
                    "bounds": footprint["bounds"],
                    "intensity_values": np.random.exponential(
                        scale=0.1,
                        size=(100, 100)
                    ).tolist()
                }
            
            footprint["secondary_perils"] = secondary_footprints
        
        return footprint


class HurricaneModel(HazardModel):
    """
    Model for hurricane/cyclone hazards, including wind, storm surge, and rainfall.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the hurricane model with the specified parameters.
        
        Args:
            params (Dict[str, Any]): Parameters for the hurricane model configuration
        """
        super().__init__(hazard_type="hurricane", params=params)
        
        # Hurricane-specific parameters
        self.include_components = params.get("include_components", ["wind", "storm_surge", "rainfall"])
        self.track_data_source = params.get("track_data_source", "hurdat2")
    
    def _load_model_data(self):
        """
        Load necessary data for the hurricane model.
        """
        super()._load_model_data()
        
        # Add hurricane-specific data
        self.model_data.update({
            "historical_tracks": None,  # Historical hurricane track data would be loaded here
            "sea_surface_temperatures": None,  # SST data would be loaded here
            "bathymetry": None,  # Bathymetry data for storm surge modeling would be loaded here
            "topography": None  # Topography data would be loaded here
        })
    
    def _generate_footprint(self, return_period: float) -> Dict[str, Any]:
        """
        Generate a hurricane footprint for a given return period.
        
        Args:
            return_period (float): Return period for the event
            
        Returns:
            Dict[str, Any]: Hurricane footprint data
        """
        # Call the parent method to get the basic footprint
        footprint = super()._generate_footprint(return_period)
        
        # Generate a random hurricane track
        # In a real model, this would use a more sophisticated track model
        track_points = []
        
        # Start point for the track
        start_lon = footprint["bounds"]["min_lon"] - 2.0
        start_lat = footprint["bounds"]["min_lat"] + (footprint["bounds"]["max_lat"] - footprint["bounds"]["min_lat"]) / 2
        
        # Generate track points
        num_points = 20
        for i in range(num_points):
            # Simple track model - moves generally eastward with some random variation
            point = {
                "time": i * 6,  # Hours from start
                "longitude": start_lon + i * 0.2 + np.random.normal(0, 0.05),
                "latitude": start_lat + np.random.normal(0, 0.1),
                "pressure": 950 + i * 2,  # hPa, increasing as storm weakens
                "wind_speed": 120 - i * 3,  # km/h, decreasing as storm weakens
                "radius_max_wind": 50 + np.random.normal(0, 5)  # km
            }
            track_points.append(point)
        
        # Add hurricane-specific data to the footprint
        footprint.update({
            "hurricane_category": min(5, max(1, int(return_period / 20))),  # Simple mapping of return period to category
            "track": track_points,
            "landfall": {
                "time": 10 * 6,  # Hours from start
                "longitude": start_lon + 10 * 0.2,
                "latitude": start_lat
            }
        })
        
        # Add component footprints based on configuration
        component_footprints = {}
        for component in self.include_components:
            # Generate simple component footprints
            # In a real model, these would be more sophisticated
            component_footprints[component] = {
                "type": "grid",
                "resolution": "1km",
                "bounds": footprint["bounds"],
                "intensity_values": np.random.exponential(
                    scale=0.5 if component == "wind" else 0.2,
                    size=(100, 100)
                ).tolist()
            }
        
        footprint["components"] = component_footprints
        
        return footprint 