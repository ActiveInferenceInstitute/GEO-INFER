"""
Catastrophe Models for Risk Assessment

This module provides catastrophe modeling capabilities for natural disasters
and extreme events in the GEO-INFER framework.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class CatastropheConfig:
    """Configuration for catastrophe models."""
    
    # Model parameters
    simulation_years: int = 1000
    return_periods: List[int] = field(default_factory=lambda: [10, 25, 50, 100, 250, 500])
    
    # Geographic parameters
    spatial_resolution: float = 0.1  # degrees
    max_distance: float = 100.0  # km
    
    # Event parameters
    event_types: List[str] = field(default_factory=lambda: [
        'earthquake', 'hurricane', 'flood', 'wildfire', 'tornado'
    ])
    
    # Financial parameters
    currency: str = 'USD'
    inflation_rate: float = 0.02

class CatastropheModel(ABC):
    """Abstract base class for catastrophe models."""
    
    def __init__(self, config: Optional[CatastropheConfig] = None):
        """
        Initialize catastrophe model.
        
        Args:
            config: Model configuration
        """
        self.config = config or CatastropheConfig()
        self.is_fitted = False
        self.historical_data = None
    
    @abstractmethod
    def fit(self, historical_data: pd.DataFrame) -> 'CatastropheModel':
        """Fit the model to historical data."""
        pass
    
    @abstractmethod
    def simulate_events(self, n_simulations: int) -> List[Dict[str, Any]]:
        """Simulate catastrophe events."""
        pass
    
    @abstractmethod
    def calculate_loss(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate loss for a given event and exposure."""
        pass

class EarthquakeModel(CatastropheModel):
    """Earthquake catastrophe model."""
    
    def __init__(self, config: Optional[CatastropheConfig] = None):
        super().__init__(config)
        self.fault_lines = []
        self.seismicity_rates = {}
    
    def fit(self, historical_data: pd.DataFrame) -> 'EarthquakeModel':
        """Fit earthquake model to historical data."""
        logger.info("Fitting earthquake catastrophe model...")
        
        self.historical_data = historical_data.copy()
        
        # Extract fault line information
        if 'fault_line' in historical_data.columns:
            self.fault_lines = historical_data['fault_line'].unique().tolist()
        
        # Calculate seismicity rates
        if 'magnitude' in historical_data.columns:
            self.seismicity_rates = {
                'mean_magnitude': historical_data['magnitude'].mean(),
                'magnitude_std': historical_data['magnitude'].std(),
                'annual_rate': len(historical_data) / 100  # Assuming 100 years of data
            }
        
        self.is_fitted = True
        logger.info("Earthquake model fitted successfully")
        return self
    
    def simulate_events(self, n_simulations: int) -> List[Dict[str, Any]]:
        """Simulate earthquake events."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before simulation")
        
        events = []
        
        for i in range(n_simulations):
            # Generate random earthquake parameters
            magnitude = np.random.normal(
                self.seismicity_rates['mean_magnitude'],
                self.seismicity_rates['magnitude_std']
            )
            
            # Limit magnitude to realistic range
            magnitude = np.clip(magnitude, 4.0, 9.0)
            
            # Generate random location
            lat = np.random.uniform(-90, 90)
            lon = np.random.uniform(-180, 180)
            
            # Calculate depth (shallow earthquakes are more damaging)
            depth = np.random.exponential(10.0)  # km
            
            event = {
                'event_id': f"EQ_{i:06d}",
                'event_type': 'earthquake',
                'magnitude': magnitude,
                'latitude': lat,
                'longitude': lon,
                'depth': depth,
                'timestamp': datetime.now() + timedelta(days=np.random.randint(0, 365)),
                'intensity': self._calculate_intensity(magnitude, depth)
            }
            
            events.append(event)
        
        return events
    
    def calculate_loss(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate earthquake loss."""
        magnitude = event['magnitude']
        distance = self._calculate_distance(event, exposure)
        intensity = event['intensity']
        
        # Simple loss model based on magnitude, distance, and building value
        base_loss = exposure.get('building_value', 100000)
        
        # Distance attenuation
        distance_factor = 1.0 / (1.0 + distance / 50.0)
        
        # Magnitude factor
        magnitude_factor = (magnitude - 4.0) / 5.0
        
        # Vulnerability factor
        vulnerability = exposure.get('vulnerability', 0.5)
        
        loss = base_loss * distance_factor * magnitude_factor * vulnerability * intensity
        
        return min(loss, base_loss)  # Loss cannot exceed building value
    
    def _calculate_intensity(self, magnitude: float, depth: float) -> float:
        """Calculate earthquake intensity."""
        # Modified Mercalli Intensity approximation
        if magnitude < 4.0:
            return 1.0
        elif magnitude < 5.0:
            return 2.0
        elif magnitude < 6.0:
            return 4.0
        elif magnitude < 7.0:
            return 6.0
        elif magnitude < 8.0:
            return 8.0
        else:
            return 10.0
    
    def _calculate_distance(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate distance between event and exposure."""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = event['latitude'], event['longitude']
        lat2, lon2 = exposure.get('latitude', 0), exposure.get('longitude', 0)
        
        # Haversine formula
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth's radius in km
        
        return c * r

class HurricaneModel(CatastropheModel):
    """Hurricane catastrophe model."""
    
    def __init__(self, config: Optional[CatastropheConfig] = None):
        super().__init__(config)
        self.track_data = []
        self.intensity_data = {}
    
    def fit(self, historical_data: pd.DataFrame) -> 'HurricaneModel':
        """Fit hurricane model to historical data."""
        logger.info("Fitting hurricane catastrophe model...")
        
        self.historical_data = historical_data.copy()
        
        # Extract track information
        if 'track_points' in historical_data.columns:
            self.track_data = historical_data['track_points'].tolist()
        
        # Calculate intensity statistics
        if 'wind_speed' in historical_data.columns:
            self.intensity_data = {
                'mean_wind_speed': historical_data['wind_speed'].mean(),
                'wind_speed_std': historical_data['wind_speed'].std(),
                'max_wind_speed': historical_data['wind_speed'].max(),
                'annual_frequency': len(historical_data) / 100  # Assuming 100 years
            }
        
        self.is_fitted = True
        logger.info("Hurricane model fitted successfully")
        return self
    
    def simulate_events(self, n_simulations: int) -> List[Dict[str, Any]]:
        """Simulate hurricane events."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before simulation")
        
        events = []
        
        for i in range(n_simulations):
            # Generate random hurricane parameters
            wind_speed = np.random.weibull(2.0) * 50 + 30  # km/h
            wind_speed = np.clip(wind_speed, 30, 300)
            
            # Generate track
            start_lat = np.random.uniform(10, 30)  # Tropical latitudes
            start_lon = np.random.uniform(-100, -60)  # Atlantic basin
            track_length = np.random.randint(5, 20)
            
            track = []
            current_lat, current_lon = start_lat, start_lon
            
            for j in range(track_length):
                # Simple track movement (northward and eastward)
                current_lat += np.random.normal(0.5, 0.2)
                current_lon += np.random.normal(0.3, 0.1)
                track.append([current_lat, current_lon])
            
            event = {
                'event_id': f"HUR_{i:06d}",
                'event_type': 'hurricane',
                'wind_speed': wind_speed,
                'category': self._get_category(wind_speed),
                'track': track,
                'start_latitude': start_lat,
                'start_longitude': start_lon,
                'timestamp': datetime.now() + timedelta(days=np.random.randint(0, 365)),
                'storm_surge': self._calculate_storm_surge(wind_speed)
            }
            
            events.append(event)
        
        return events
    
    def calculate_loss(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate hurricane loss."""
        wind_speed = event['wind_speed']
        distance = self._calculate_minimum_distance(event, exposure)
        storm_surge = event['storm_surge']
        
        base_value = exposure.get('property_value', 200000)
        
        # Wind damage
        wind_factor = min(wind_speed / 100.0, 1.0)
        
        # Distance factor (closer = more damage)
        distance_factor = max(0.1, 1.0 - distance / 100.0)
        
        # Storm surge damage
        surge_factor = min(storm_surge / 5.0, 1.0)
        
        # Vulnerability
        vulnerability = exposure.get('vulnerability', 0.6)
        
        total_loss = base_value * (wind_factor + surge_factor) * distance_factor * vulnerability
        
        return min(total_loss, base_value)
    
    def _get_category(self, wind_speed: float) -> int:
        """Get hurricane category based on wind speed."""
        if wind_speed < 119:
            return 0  # Tropical storm
        elif wind_speed < 154:
            return 1
        elif wind_speed < 178:
            return 2
        elif wind_speed < 209:
            return 3
        elif wind_speed < 252:
            return 4
        else:
            return 5
    
    def _calculate_storm_surge(self, wind_speed: float) -> float:
        """Calculate storm surge height."""
        # Simplified storm surge calculation
        return wind_speed * 0.01  # meters
    
    def _calculate_minimum_distance(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate minimum distance from hurricane track to exposure."""
        exposure_lat = exposure.get('latitude', 0)
        exposure_lon = exposure.get('longitude', 0)
        
        min_distance = float('inf')
        
        for track_point in event['track']:
            track_lat, track_lon = track_point
            
            # Simple distance calculation
            distance = np.sqrt((exposure_lat - track_lat)**2 + (exposure_lon - track_lon)**2)
            min_distance = min(min_distance, distance)
        
        return min_distance * 111  # Convert degrees to km

class FloodModel(CatastropheModel):
    """Flood catastrophe model."""
    
    def __init__(self, config: Optional[CatastropheConfig] = None):
        super().__init__(config)
        self.river_data = {}
        self.rainfall_data = {}
    
    def fit(self, historical_data: pd.DataFrame) -> 'FloodModel':
        """Fit flood model to historical data."""
        logger.info("Fitting flood catastrophe model...")
        
        self.historical_data = historical_data.copy()
        
        # Extract river and rainfall information
        if 'river_name' in historical_data.columns:
            river_stats = historical_data.groupby('river_name').agg({
                'water_level': ['mean', 'std', 'max'],
                'rainfall': ['mean', 'std']
            }).to_dict()
            self.river_data = river_stats
        
        self.is_fitted = True
        logger.info("Flood model fitted successfully")
        return self
    
    def simulate_events(self, n_simulations: int) -> List[Dict[str, Any]]:
        """Simulate flood events."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before simulation")
        
        events = []
        
        for i in range(n_simulations):
            # Generate random flood parameters
            rainfall = np.random.exponential(50.0)  # mm
            duration = np.random.randint(1, 7)  # days
            water_level = np.random.normal(5.0, 2.0)  # meters
            
            # Generate affected area
            center_lat = np.random.uniform(-90, 90)
            center_lon = np.random.uniform(-180, 180)
            radius = np.random.uniform(10, 100)  # km
            
            event = {
                'event_id': f"FLD_{i:06d}",
                'event_type': 'flood',
                'rainfall': rainfall,
                'duration': duration,
                'water_level': water_level,
                'center_latitude': center_lat,
                'center_longitude': center_lon,
                'affected_radius': radius,
                'timestamp': datetime.now() + timedelta(days=np.random.randint(0, 365)),
                'severity': self._calculate_severity(rainfall, water_level)
            }
            
            events.append(event)
        
        return events
    
    def calculate_loss(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate flood loss."""
        distance = self._calculate_distance(event, exposure)
        water_level = event['water_level']
        severity = event['severity']
        
        base_value = exposure.get('property_value', 150000)
        
        # Distance factor
        if distance > event['affected_radius']:
            return 0.0
        
        distance_factor = 1.0 - (distance / event['affected_radius'])
        
        # Water level factor
        water_factor = min(water_level / 3.0, 1.0)
        
        # Severity factor
        severity_factor = severity / 10.0
        
        # Vulnerability
        vulnerability = exposure.get('vulnerability', 0.7)
        
        total_loss = base_value * distance_factor * water_factor * severity_factor * vulnerability
        
        return min(total_loss, base_value)
    
    def _calculate_severity(self, rainfall: float, water_level: float) -> float:
        """Calculate flood severity."""
        return min(10.0, (rainfall / 100.0 + water_level / 5.0) * 5.0)
    
    def _calculate_distance(self, event: Dict[str, Any], exposure: Dict[str, Any]) -> float:
        """Calculate distance from flood center to exposure."""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = event['center_latitude'], event['center_longitude']
        lat2, lon2 = exposure.get('latitude', 0), exposure.get('longitude', 0)
        
        # Haversine formula
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth's radius in km
        
        return c * r

class CatastropheModelManager:
    """Manager for multiple catastrophe models."""
    
    def __init__(self, config: Optional[CatastropheConfig] = None):
        """
        Initialize catastrophe model manager.
        
        Args:
            config: Configuration for all models
        """
        self.config = config or CatastropheConfig()
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all catastrophe models."""
        self.models['earthquake'] = EarthquakeModel(self.config)
        self.models['hurricane'] = HurricaneModel(self.config)
        self.models['flood'] = FloodModel(self.config)
        
        logger.info(f"Initialized {len(self.models)} catastrophe models")
    
    def fit_model(self, event_type: str, historical_data: pd.DataFrame) -> bool:
        """
        Fit a specific catastrophe model.
        
        Args:
            event_type: Type of catastrophe event
            historical_data: Historical event data
            
        Returns:
            True if fitting was successful
        """
        if event_type not in self.models:
            logger.error(f"Unknown event type: {event_type}")
            return False
        
        try:
            self.models[event_type].fit(historical_data)
            return True
        except Exception as e:
            logger.error(f"Failed to fit {event_type} model: {e}")
            return False
    
    def simulate_events(self, event_type: str, n_simulations: int) -> List[Dict[str, Any]]:
        """
        Simulate events for a specific catastrophe type.
        
        Args:
            event_type: Type of catastrophe event
            n_simulations: Number of simulations
            
        Returns:
            List of simulated events
        """
        if event_type not in self.models:
            raise ValueError(f"Unknown event type: {event_type}")
        
        model = self.models[event_type]
        if not model.is_fitted:
            raise ValueError(f"{event_type} model must be fitted before simulation")
        
        return model.simulate_events(n_simulations)
    
    def calculate_portfolio_loss(self, 
                               events: List[Dict[str, Any]],
                               exposures: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate portfolio loss for multiple events and exposures.
        
        Args:
            events: List of catastrophe events
            exposures: List of exposure locations
            
        Returns:
            Dictionary with loss statistics
        """
        total_losses = []
        
        for event in events:
            event_losses = []
            event_type = event['event_type']
            
            if event_type not in self.models:
                continue
            
            model = self.models[event_type]
            
            for exposure in exposures:
                loss = model.calculate_loss(event, exposure)
                event_losses.append(loss)
            
            total_losses.append(sum(event_losses))
        
        if not total_losses:
            return {
                'total_loss': 0.0,
                'mean_loss': 0.0,
                'max_loss': 0.0,
                'std_loss': 0.0
            }
        
        return {
            'total_loss': sum(total_losses),
            'mean_loss': np.mean(total_losses),
            'max_loss': np.max(total_losses),
            'std_loss': np.std(total_losses)
        }
    
    def generate_loss_exceedance_curve(self, 
                                     events: List[Dict[str, Any]],
                                     exposures: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Generate loss exceedance curve.
        
        Args:
            events: List of catastrophe events
            exposures: List of exposure locations
            
        Returns:
            DataFrame with return period and loss data
        """
        portfolio_losses = []
        
        # Calculate losses for each event
        for event in events:
            event_type = event['event_type']
            if event_type not in self.models:
                continue
            
            model = self.models[event_type]
            event_loss = sum(model.calculate_loss(event, exposure) for exposure in exposures)
            portfolio_losses.append(event_loss)
        
        if not portfolio_losses:
            return pd.DataFrame()
        
        # Sort losses in descending order
        portfolio_losses.sort(reverse=True)
        
        # Calculate return periods
        n_events = len(portfolio_losses)
        return_periods = []
        losses = []
        
        for i, loss in enumerate(portfolio_losses):
            rank = i + 1
            return_period = n_events / rank
            return_periods.append(return_period)
            losses.append(loss)
        
        return pd.DataFrame({
            'return_period': return_periods,
            'loss': losses
        })

# Convenience functions
def create_catastrophe_manager(config: Optional[CatastropheConfig] = None) -> CatastropheModelManager:
    """Create a new catastrophe model manager."""
    return CatastropheModelManager(config)

def create_earthquake_model(config: Optional[CatastropheConfig] = None) -> EarthquakeModel:
    """Create a new earthquake model."""
    return EarthquakeModel(config)

def create_hurricane_model(config: Optional[CatastropheConfig] = None) -> HurricaneModel:
    """Create a new hurricane model."""
    return HurricaneModel(config)

def create_flood_model(config: Optional[CatastropheConfig] = None) -> FloodModel:
    """Create a new flood model."""
    return FloodModel(config) 